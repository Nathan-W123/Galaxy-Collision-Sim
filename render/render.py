"""Render simulation snapshots to PNG frames and an MP4.

    python -m render.render render/configs/preview_5k.yaml [--workers 4] [--no-video]

Reads *only* snapshot files (plus the run's static particle table and metadata).
One snapshot per frame: particle positions are drawn exactly as the integrator wrote
them -- no interpolation, no tweening, no frame blending.  Hand-authored presentation
is limited to the camera path, colours, glow and overlays.  The on-screen time is read
from the snapshot.

Writes ``frames_manifest.csv`` (frame -> snapshot file, step, time, energy, plus the
simulation's git commit and parameter-file hash) next to the frames.
"""
import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import yaml
from numba import njit
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from nbody.io import PTYPE_BULGE, PTYPE_DISK, read_json, read_snapshot, read_static  # noqa: E402
from nbody.params import git_commit  # noqa: E402
from render.camera import Camera, keyframed  # noqa: E402

FONT_DIR = Path("/usr/share/fonts/opentype/inter")
DEFAULT_COLORS = [[0.42, 0.66, 1.00],    # galaxy 0: cool blue
                  [1.00, 0.68, 0.32]]    # galaxy 1: warm amber


def font(weight, size):
    for name in (f"Inter-{weight}.otf", "Inter-Regular.otf"):
        p = FONT_DIR / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


@njit(cache=True)
def splat_bilinear(px, py, w, ch, out):
    """Additive bilinear deposit of weights w into channel ch of out[c, y, x]."""
    nc, H, W = out.shape
    for k in range(px.shape[0]):
        x = px[k] - 0.5
        y = py[k] - 0.5
        if not (x > -1.0 and x < W and y > -1.0 and y < H):
            continue
        x0 = int(np.floor(x))
        y0 = int(np.floor(y))
        fx = x - x0
        fy = y - y0
        c = ch[k]
        for dy in range(2):
            yy = y0 + dy
            if yy < 0 or yy >= H:
                continue
            wy = fy if dy == 1 else 1.0 - fy
            for dx in range(2):
                xx = x0 + dx
                if xx < 0 or xx >= W:
                    continue
                wx = fx if dx == 1 else 1.0 - fx
                out[c, yy, xx] += w[k] * wx * wy


def _abs(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Renderer:
    def __init__(self, cfg, cfg_path=None):
        self.cfg = cfg
        self.run_dir = _abs(cfg["run"])
        self.meta = read_json(self.run_dir / "run_meta.json")
        st = read_static(self.run_dir / "static.npz")
        self.ptype = st["ptype"]
        self.galaxy = st["galaxy"]
        self.mass = st["mass"]
        self.galaxy_names = [str(x) for x in st["galaxy_names"]]
        stars = np.isin(self.ptype, [PTYPE_DISK, PTYPE_BULGE])
        if cfg.get("style", {}).get("show_dark_matter", False):
            stars[:] = True
        self.sel = np.nonzero(stars)[0]
        self.W = int(cfg["width"])
        self.H = int(cfg["height"])
        self.fps = int(cfg.get("fps", 30))
        self.out_dir = _abs(cfg["out"])
        self.frames = self.plan_frames()

    # ------------------------------------------------------------ frame plan
    def plan_frames(self):
        """List of (frame_index, step).  Each frame is exactly one saved snapshot."""
        steps = np.asarray(self.meta["render_steps"], dtype=np.int64)
        dt_gyr = self.meta["dt_internal"] * self.meta["time_unit_gyr"]
        fr = self.cfg.get("frames", {})
        t = steps * dt_gyr
        sel = np.ones(steps.size, bool)
        if "start_gyr" in fr:
            sel &= t >= float(fr["start_gyr"]) - 1e-9
        if "end_gyr" in fr:
            sel &= t <= float(fr["end_gyr"]) + 1e-9
        steps = steps[sel]
        snap_dir = self.run_dir / "snapshots"
        steps = [int(s) for s in steps if (snap_dir / f"snap_{int(s):07d}.npz").exists()]
        return list(enumerate(steps))

    # ------------------------------------------------------------ camera
    def camera_for(self, frame, t_gyr, pos_stars, m_stars):
        c = self.cfg["camera"]
        x = t_gyr if c.get("key", "time_gyr") == "time_gyr" else frame
        tgt = c.get("target", [0.0, 0.0, 0.0])
        if tgt == "stars_com":
            tgt = (m_stars[:, None] * pos_stars).sum(0) / m_stars.sum()
        az = float(c.get("azimuth_deg", 0.0)) + float(c.get("azimuth_rate_deg_per_frame", 0.0)) * frame
        if "azimuth_keys" in c:
            az += float(keyframed(c["azimuth_keys"], x))
        el = float(keyframed(c.get("elevation_deg", 30.0), x))
        dist = float(keyframed(c.get("distance_kpc", 150.0), x))
        return Camera(tgt, dist, az, el, float(c.get("fov_deg", 40.0)), self.W, self.H,
                      float(c.get("roll_deg", 0.0)))

    # ------------------------------------------------------------ one frame
    def render_frame(self, frame, step):
        snap_path = self.run_dir / "snapshots" / f"snap_{step:07d}.npz"
        snap = read_snapshot(snap_path)
        assert int(snap["step"]) == step
        pos = snap["pos"][self.sel].astype(np.float64)
        m = self.mass[self.sel]
        gal = self.galaxy[self.sel].astype(np.int64)
        t_gyr = float(snap["time_gyr"])
        cam = self.camera_for(frame, t_gyr, pos, m)
        px, py, z = cam.project(pos)
        ok = z > 1e-3
        # weight = mass * f^2 / z^2  ->  image value = surface density (1e10 Msun / kpc^2)
        w = np.where(ok, m * cam.f ** 2 / np.where(ok, z, 1.0) ** 2, 0.0)
        ng = max(2, int(gal.max()) + 1)
        acc = np.zeros((ng, self.H, self.W))
        splat_bilinear(np.where(ok, px, -10.0), np.where(ok, py, -10.0), w, gal, acc)
        st = self.cfg.get("style", {})
        kpp = cam.kpc_per_pixel_at_target()
        sig_px = max(float(st.get("smooth_kpc", 0.35)) / kpp, float(st.get("smooth_min_px", 0.8)))
        for g in range(ng):
            acc[g] = gaussian_filter(acc[g], sig_px, mode="constant")
        dens = acc.sum(0) * 1e10                      # Msun / kpc^2
        lo = float(st.get("density_lo", 3e5))
        hi = float(st.get("density_hi", 2e9))
        L = np.log1p(dens / lo) / np.log1p(hi / lo)
        L = np.clip(L, 0.0, 1.2) ** float(st.get("gamma", 1.0))
        colors = np.asarray(st.get("colors", DEFAULT_COLORS), float)[:ng]
        tot = np.maximum(acc.sum(0), 1e-300)
        cmix = np.einsum("ghw,gc->hwc", acc, colors) / tot[..., None]
        rgb = L[..., None] * cmix
        # bright cores desaturate towards white
        wcore = np.clip((L - float(st.get("core_start", 0.65))) / 0.35, 0, 1)[..., None] ** 2
        rgb = rgb * (1 - wcore) + wcore * L[..., None]
        glow = np.zeros_like(rgb)
        for sig_kpc, amp in st.get("glow", [[1.5, 0.35], [6.0, 0.25]]):
            s = max(float(sig_kpc) / kpp, 1.0)
            for c in range(3):
                glow[..., c] += float(amp) * gaussian_filter(rgb[..., c], s, mode="constant")
        x = rgb + glow
        k = float(st.get("shoulder", 1.6))
        x = (1.0 - np.exp(-k * x)) / (1.0 - np.exp(-k))
        bg = np.asarray(st.get("background", [0.031, 0.043, 0.071]), float)
        img = bg + (1.0 - bg) * np.clip(x, 0, 1)
        im = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
        self.draw_overlay(im, t_gyr, cam)
        return im, snap

    def draw_overlay(self, im, t_gyr, cam):
        ov = self.cfg.get("overlay", {})
        d = ImageDraw.Draw(im, "RGBA")
        H, W = self.H, self.W
        u = H / 1080.0                                  # layout unit
        pad = int(round(ov.get("margin", 56) * u))
        txt = (236, 240, 248, 255)
        dim = (170, 180, 198, 255)
        if ov.get("time", True):
            f = font("SemiBold", int(round(44 * u)))
            label = ov.get("time_format", "t = {t:.2f} Gyr").format(t=t_gyr + float(ov.get("time_offset_gyr", 0.0)))
            d.text((pad, pad), label, font=f, fill=txt)
        if ov.get("caption"):
            f = font("Regular", int(round(26 * u)))
            d.text((pad, pad + int(62 * u)), ov["caption"], font=f, fill=dim)
        if ov.get("scale_bar", True):
            kpp = cam.kpc_per_pixel_at_target()
            target_px = 0.22 * W
            nice = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000]
            L = min(nice, key=lambda v: abs(v / kpp - target_px))
            Lpx = L / kpp
            y = H - pad
            x0 = pad
            lw = max(2, int(round(3 * u)))
            d.line([(x0, y), (x0 + Lpx, y)], fill=txt, width=lw)
            for xx in (x0, x0 + Lpx):
                d.line([(xx, y - 8 * u), (xx, y + 8 * u)], fill=txt, width=lw)
            f = font("Medium", int(round(30 * u)))
            d.text((x0, y - 50 * u), f"{L:g} kpc", font=f, fill=txt)
        if ov.get("credit"):
            f = font("Regular", int(round(24 * u)))
            tw = d.textlength(ov["credit"], font=f)
            d.text((W - pad - tw, H - pad - 30 * u), ov["credit"], font=f, fill=dim)
        if ov.get("label"):
            f = font("Medium", int(round(26 * u)))
            tw = d.textlength(ov["label"], font=f)
            d.text((W - pad - tw, pad + 10 * u), ov["label"], font=f, fill=dim)


# ---------------------------------------------------------------- driver
_R = None


def _init(cfg):
    global _R
    _R = Renderer(cfg)


def _work(item):
    frame, step = item
    im, snap = _R.render_frame(frame, step)
    path = _R.out_dir / "frames" / f"{frame:05d}.png"
    im.save(path, compress_level=1)
    return frame, step, float(snap["time_gyr"]), float(snap["energy"])


def encode_video(frames_dir, fps, out_mp4, crf=17):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
           "-i", str(Path(frames_dir) / "%05d.png"), "-c:v", "libx264", "-preset", "slow",
           "-crf", str(crf), "-pix_fmt", "yuv420p", "-r", str(fps), "-movflags", "+faststart",
           str(out_mp4)]
    subprocess.run(cmd, check=True)


def render(cfg_path, workers=4, video=True):
    cfg = yaml.safe_load(Path(cfg_path).read_text())
    R = Renderer(cfg)
    out = R.out_dir
    (out / "frames").mkdir(parents=True, exist_ok=True)
    for old in (out / "frames").glob("*.png"):
        old.unlink()
    print(f"rendering {len(R.frames)} frames from {R.run_dir} -> {out}", flush=True)
    with ProcessPoolExecutor(workers, initializer=_init, initargs=(cfg,)) as ex:
        results = sorted(ex.map(_work, R.frames, chunksize=4))
    meta = R.meta
    rows = []
    for frame, step, tg, E in results:
        rows.append({
            "frame": frame,
            "snapshot_file": os.path.relpath(R.run_dir / "snapshots" / f"snap_{step:07d}.npz", REPO),
            "step": step,
            "time_gyr": f"{tg:.9f}",
            "total_energy": f"{E:.12e}",
            "sim_git_commit": meta["git_commit"],
            "param_sha256": meta["param_sha256"],
        })
    with open(out / "frames_manifest.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    side = {
        "run_dir": os.path.relpath(R.run_dir, REPO),
        "run_name": meta["name"],
        "sim_git_commit": meta["git_commit"],
        "param_file": meta["param_file"],
        "param_sha256": meta["param_sha256"],
        "schedule_file": meta.get("schedule_file"),
        "schedule_sha256": meta.get("schedule_sha256"),
        "render_git_commit": git_commit(),
        "render_config": str(cfg_path),
        "render_config_sha256": sha256_file(cfg_path),
        "n_frames": len(rows),
        "fps": R.fps,
        "width": R.W,
        "height": R.H,
    }
    with open(out / "frames_manifest.json", "w") as fh:
        json.dump(side, fh, indent=2)
    if video:
        mp4 = out / cfg.get("video_name", "clip.mp4")
        encode_video(out / "frames", R.fps, mp4, int(cfg.get("crf", 17)))
        print("wrote", mp4)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-video", action="store_true")
    a = ap.parse_args(argv)
    render(a.config, a.workers, not a.no_video)


if __name__ == "__main__":
    main()
