"""Benchmark: wall time per KDK step vs N, and an estimate for the final run.

    python benchmarks/bench_step.py [--max-n 200000] [--out output/logs/benchmark.md]

Two configurations per N, both built from the engine's own disk-galaxy ICs:
  separated : two galaxies 100 kpc apart (the long approach phase)
  merging   : the same galaxies 3 kpc apart (dense, overlapping centres)
Timings are the best of 3 steps after JIT warm-up.  Direct summation is timed up to 20k.
"""
import argparse
import copy
import json
import sys
import tempfile
import time
from pathlib import Path

import numba
import numpy as np
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from nbody.direct import direct_accel  # noqa: E402
from nbody.ics import make_initial_conditions  # noqa: E402
from nbody.integrator import diagnostics  # noqa: E402
from nbody.io import render_snapshot_arrays, _atomic_savez  # noqa: E402
from nbody.tree import Octree  # noqa: E402
from nbody.units import G  # noqa: E402


def make(n, sep):
    p = yaml.safe_load((REPO / "scenarios" / "test_collision_5k.yaml").read_text())
    p = copy.deepcopy(p)
    per = n // 2
    for g in p["galaxies"]:
        m = copy.deepcopy(g["model"])
        m["halo"]["n"], m["bulge"]["n"] = int(0.5 * per), int(0.1 * per)
        m["disk"]["n"] = per - m["halo"]["n"] - m["bulge"]["n"]
        g["model"] = m
    p["orbit"] = {"type": "radial_tangential", "separation_kpc": sep, "v_radial_kms": -100.0,
                  "v_tangential_kms": 50.0}
    ics = make_initial_conditions(p)
    return ics["pos"], ics["vel"], ics["mass"]


def time_step(pos, vel, mass, eps, dt=1e-3, reps=3):
    best = None
    for _ in range(reps):
        t0 = time.perf_counter()
        tr = Octree(pos, mass, 0.6, 8, True)
        t1 = time.perf_counter()
        acc, pot, cnt = tr.accel(eps, G, return_counts=True)
        t2 = time.perf_counter()
        v = vel + 0.5 * dt * acc
        x = pos + dt * v
        v += 0.5 * dt * acc
        diagnostics(x, v, mass, pot)
        t3 = time.perf_counter()
        r = (t3 - t0, t1 - t0, t2 - t1, t3 - t2, float(cnt.mean()))
        best = r if best is None or r[0] < best[0] else best
    return best


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=200000)
    ap.add_argument("--out", default=str(REPO / "output" / "logs" / "benchmark.md"))
    a = ap.parse_args(argv)
    Ns = [n for n in (5000, 10000, 20000, 50000, 100000, 200000) if n <= a.max_n]
    rows = []
    # warm-up / JIT
    p, v, m = make(5000, 100.0)
    time_step(p, v, m, 0.4, reps=1)
    direct_accel(p[:500], m[:500], 0.4, G)
    for n in Ns:
        eps = 0.4 * (5000 / n) ** (1 / 3)
        rec = {"N": n, "eps": eps}
        for label, sep in (("separated", 100.0), ("merging", 3.0)):
            p, v, m = make(n, sep)
            tot, build, walk, rest, nint = time_step(p, v, m, eps)
            rec[label] = {"step_s": tot, "build_s": build, "walk_s": walk, "other_s": rest,
                          "interactions_per_particle": nint}
        if n <= 20000:
            p, v, m = make(n, 3.0)
            t0 = time.perf_counter()
            direct_accel(p, m, eps, G)
            rec["direct_s"] = time.perf_counter() - t0
        rows.append(rec)
        print(json.dumps(rec), flush=True)

    # snapshot write cost at 100k (float32 positions, compressed .npz)
    pos = np.random.default_rng(0).normal(size=(100000, 3)) * 50
    d = {"energy": -1.0, "kinetic": 1.0, "potential": -2.0, "momentum": np.zeros(3), "angmom": np.zeros(3)}
    with tempfile.TemporaryDirectory() as td:
        t0 = time.perf_counter()
        for k in range(5):
            _atomic_savez(f"{td}/s{k}.npz", **render_snapshot_arrays(pos, k, 0.0, 0.0, d))
        snap_s = (time.perf_counter() - t0) / 5
        size_mb = Path(f"{td}/s0.npz").stat().st_size / 1e6

    lines = [f"# Step-time benchmark ({numba.get_num_threads()} threads, theta=0.6, quadrupole, leaf=8)", "",
             "| N | eps (kpc) | separated: s/step | build | walk | int/particle | merging: s/step | int/particle | direct force (s) |",
             "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        s, mg = r["separated"], r["merging"]
        lines.append(f"| {r['N']:,} | {r['eps']:.3f} | {s['step_s']:.4f} | {s['build_s']:.4f} | {s['walk_s']:.4f} | "
                     f"{s['interactions_per_particle']:.0f} | {mg['step_s']:.4f} | {mg['interactions_per_particle']:.0f} | "
                     f"{r.get('direct_s', float('nan')):.3f} |")
    lines += ["", f"Render snapshot (100k float32 positions, compressed .npz): {snap_s * 1e3:.0f} ms to write "
              f"(on a background thread), {size_mb:.2f} MB on disk.", ""]
    # scaling fit t ~ N^p over N >= 20k
    big = [r for r in rows if r["N"] >= 20000]
    if len(big) >= 2:
        for label in ("separated", "merging"):
            x = np.log([r["N"] for r in big])
            y = np.log([r[label]["step_s"] for r in big])
            pw = np.polyfit(x, y, 1)[0]
            lines.append(f"Scaling ({label}, N >= 20k): t_step ~ N^{pw:.2f}")
        lines.append("")
    r100 = next((r for r in rows if r["N"] == 100000), None)
    if r100:
        lines.append("## Wall-time estimate for the final run (N = 100,000, 10 Gyr)")
        lines.append("")
        lines.append("Assumes ~40 % of steps in the separated phase and ~60 % merging/merged, plus "
                     "~1,500 render snapshots written asynchronously.")
        lines.append("")
        lines.append("| dt (Myr) | steps | estimated wall time |")
        lines.append("|---:|---:|---:|")
        ts = 0.4 * r100["separated"]["step_s"] + 0.6 * r100["merging"]["step_s"]
        for dt in (2.0, 1.0, 0.5):
            n = int(round(10000 / dt))
            lines.append(f"| {dt} | {n:,} | {n * ts / 60:.0f} min |")
        lines.append("")
    text = "\n".join(lines)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(text + "\n")
    Path(a.out).with_suffix(".json").write_text(json.dumps(rows, indent=2))
    print(text)


if __name__ == "__main__":
    main()
