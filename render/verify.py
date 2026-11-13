"""Verify that a rendered clip is backed, frame by frame, by saved simulation snapshots.

    python -m render.verify output/renders/<clip>/clip.mp4 [--manifest PATH]
                            [--energy-tol 0.01] [--rerender 3]

Checks
  1. the manifest has one row per video frame, frames numbered 0..n-1;
  2. every row points to a snapshot file that exists, and the snapshot's own step,
     time and energy equal the manifest's;
  3. each snapshot step is one the run scheduled, and time == step * dt exactly;
  4. simulation time never decreases;
  5. |E - E0| / |E0| <= energy tolerance for every frame (E0 = energy at step 0);
  6. provenance: git commit and parameter-file hash agree with the run metadata;
  7. (--rerender K) K frames re-rendered from their snapshots match the video frames.
Exit status is 0 only if every check passes.  A report is written next to the clip.
"""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from nbody.io import read_json, read_snapshot_header  # noqa: E402


def ffprobe_frames(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries", "stream=nb_read_frames,r_frame_rate,width,height",
         "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return int(s["nb_read_frames"]), float(num) / float(den), int(s["width"]), int(s["height"])


def decode_frame(path, index, w, h):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"select=eq(n\\,{index})",
         "-vsync", "0", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)


def psnr(a, b):
    mse = np.mean((a.astype(float) - b.astype(float)) ** 2)
    return float("inf") if mse == 0 else 10 * np.log10(255.0 ** 2 / mse)


def verify(clip, manifest=None, energy_tol=0.01, rerender=0, render_config=None):
    clip = Path(clip)
    manifest = Path(manifest) if manifest else clip.parent / "frames_manifest.csv"
    lines, ok = [], True

    def check(cond, msg):
        nonlocal ok
        lines.append(("PASS " if cond else "FAIL ") + msg)
        ok &= bool(cond)

    rows = list(csv.DictReader(open(manifest)))
    side_path = manifest.with_suffix(".json")
    side = json.load(open(side_path)) if side_path.exists() else {}
    lines.append(f"clip: {clip}")
    lines.append(f"manifest: {manifest} ({len(rows)} rows)")

    # 1. frame count
    nvid, fps, w, h = ffprobe_frames(clip)
    lines.append(f"video: {nvid} frames, {fps:g} fps, {w}x{h}")
    check(nvid == len(rows), f"video frame count ({nvid}) == manifest rows ({len(rows)})")
    frames = [int(r["frame"]) for r in rows]
    check(frames == list(range(len(rows))), "manifest frames are 0..n-1 in order")

    # 2-6. snapshots
    run_dirs = {str(Path(r["snapshot_file"]).parent.parent) for r in rows}
    metas = {d: read_json(REPO / d / "run_meta.json") for d in run_dirs}
    sched = {d: set(m["render_steps"]) for d, m in metas.items()}
    missing, mismatch, unscheduled, badtime, prov = 0, 0, 0, 0, 0
    times, dEs = [], []
    for r in rows:
        sp = REPO / r["snapshot_file"]
        if not sp.exists():
            missing += 1
            continue
        hd = read_snapshot_header(sp)
        rd = str(Path(r["snapshot_file"]).parent.parent)
        meta = metas[rd]
        step = int(r["step"])
        if (int(hd["step"]) != step or not np.isclose(float(hd["time_gyr"]), float(r["time_gyr"]), rtol=1e-9, atol=1e-12)
                or not np.isclose(float(hd["energy"]), float(r["total_energy"]), rtol=1e-10, atol=0)):
            mismatch += 1
        if step not in sched[rd]:
            unscheduled += 1
        if not np.isclose(float(hd["time"]), step * meta["dt_internal"], rtol=1e-14, atol=0):
            badtime += 1
        if r["sim_git_commit"] != meta["git_commit"] or r["param_sha256"] != meta["param_sha256"]:
            prov += 1
        times.append(float(hd["time_gyr"]))
        dEs.append(abs(float(hd["energy"]) - meta["E0"]) / abs(meta["E0"]))
    check(missing == 0, f"every manifest row points to an existing snapshot ({missing} missing)")
    check(mismatch == 0, f"snapshot step/time/energy equal the manifest ({mismatch} mismatches)")
    check(unscheduled == 0, f"every snapshot step is in the run's output schedule ({unscheduled} not)")
    check(badtime == 0, f"snapshot time == step * dt exactly ({badtime} not)")
    t = np.array(times)
    check(t.size > 0 and bool(np.all(np.diff(t) >= 0)), "simulation time never decreases")
    if t.size:
        lines.append(f"      time range {t.min():.4f} .. {t.max():.4f} Gyr")
    dE = np.array(dEs) if dEs else np.array([np.inf])
    check(dE.max() <= energy_tol, f"max |E-E0|/|E0| = {dE.max():.3e} <= {energy_tol:g}")
    check(prov == 0, f"git commit and param hash match run metadata ({prov} rows differ)")
    for d, meta in metas.items():
        lines.append(f"      run {d}: git {meta['git_commit']}, params sha256 {meta['param_sha256'][:16]}..."
                     + (f", schedule sha256 {meta['schedule_sha256'][:16]}..." if meta.get("schedule_sha256") else ""))
        pf = REPO / meta["param_file"]
        if pf.exists():
            import hashlib
            cur = hashlib.sha256(pf.read_bytes()).hexdigest()
            lines.append(("      " if cur == meta["param_sha256"] else "WARN ")
                         + f"current {meta['param_file']} hash {'matches' if cur == meta['param_sha256'] else 'DIFFERS'}")

    # 7. re-render spot checks
    if rerender:
        cfg_path = render_config or side.get("render_config")
        if not cfg_path:
            check(False, "re-render check needs the render config")
        else:
            import yaml
            from render.render import Renderer
            cfg = yaml.safe_load(open(REPO / cfg_path if not Path(cfg_path).is_absolute() else cfg_path))
            R = Renderer(cfg)
            plan = dict(R.frames)
            rng = np.random.default_rng(0)
            picks = sorted(set([0, len(rows) - 1] + list(rng.integers(0, len(rows), rerender))))
            worst = np.inf
            for fi in picks:
                step = int(rows[fi]["step"])
                same_plan = plan.get(fi) == step
                im, _ = R.render_frame(fi, step)
                ref = np.asarray(im)
                vid = decode_frame(clip, fi, w, h)
                p = psnr(ref, vid)
                worst = min(worst, p)
                lines.append(f"      frame {fi}: step {step}, plan match {same_plan}, PSNR {p:.1f} dB")
            check(worst >= 35.0, f"re-rendered frames match the video (min PSNR {worst:.1f} dB >= 35)")

    lines.append("RESULT: " + ("ALL CHECKS PASSED" if ok else "VERIFICATION FAILED"))
    report = "\n".join(lines)
    (clip.parent / (clip.stem + "_verify.txt")).write_text(report + "\n")
    return ok, report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--manifest")
    ap.add_argument("--energy-tol", type=float, default=0.01)
    ap.add_argument("--rerender", type=int, default=0)
    ap.add_argument("--render-config")
    a = ap.parse_args(argv)
    ok, report = verify(a.clip, a.manifest, a.energy_tol, a.rerender, a.render_config)
    print(report)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
