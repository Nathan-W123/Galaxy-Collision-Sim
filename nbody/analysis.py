"""Run analysis: find the interesting moments of a (coarse) run.

    python -m nbody.analysis output/runs/test_collision_5k_coarse

Prints galaxy separation vs. time and the pericentre passages, which are used to choose
the dense-output windows (slow motion) for the deterministic rerun.
"""
import argparse
import sys
from pathlib import Path

import numpy as np

from .io import PTYPE_BULGE, PTYPE_DISK, read_json, read_snapshot, read_static


def shrinking_sphere_center(x, r0=None, shrink=0.8, n_min=50):
    """Robust density centre (Power et al. 2003 style)."""
    c = np.median(x, axis=0)
    r = r0 if r0 is not None else np.percentile(np.linalg.norm(x - c, axis=1), 90)
    sel = x
    while sel.shape[0] > n_min:
        d = np.linalg.norm(sel - c, axis=1)
        sel = sel[d < r]
        if sel.shape[0] == 0:
            break
        c = sel.mean(axis=0)
        r *= shrink
    return c


def galaxy_track(run_dir, stride=1):
    run_dir = Path(run_dir)
    st = read_static(run_dir / "static.npz")
    stars = np.isin(st["ptype"], [PTYPE_DISK, PTYPE_BULGE])
    ng = int(st["galaxy"].max()) + 1
    files = sorted((run_dir / "snapshots").glob("snap_*.npz"))[::stride]
    t, centers = [], []
    for f in files:
        s = read_snapshot(f)
        pos = s["pos"].astype(np.float64)
        t.append(float(s["time_gyr"]))
        centers.append([shrinking_sphere_center(pos[stars & (st["galaxy"] == g)]) for g in range(ng)])
    return np.array(t), np.array(centers)


def pericentres(t, sep, min_prominence=0.3):
    """Local minima of the separation that are real passages: the separation must
    rise by at least ``min_prominence`` (fraction) on both sides before the next minimum."""
    i = np.nonzero((sep[1:-1] < sep[:-2]) & (sep[1:-1] <= sep[2:]))[0] + 1
    out = []
    for k in i:
        left = sep[:k].max() if k > 0 else sep[k]
        nxt = [j for j in i if j > k]
        right = sep[k:nxt[0]].max() if nxt else sep[k:].max()
        if min(left, right) > sep[k] * (1 + min_prominence) + 2.0:
            out.append((float(t[k]), float(sep[k])))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--merge-kpc", type=float, default=3.0)
    ap.add_argument("--camera-keys", action="store_true",
                    help="suggest camera distance keys: distance = factor * separation + margin")
    ap.add_argument("--camera-factor", type=float, default=1.9)
    ap.add_argument("--camera-margin", type=float, default=160.0)
    a = ap.parse_args(argv)
    meta = read_json(Path(a.run_dir) / "run_meta.json")
    t, c = galaxy_track(a.run_dir, a.stride)
    if c.shape[1] < 2:
        print("single galaxy run")
        return
    sep = np.linalg.norm(c[:, 1] - c[:, 0], axis=1)
    print(f"run {meta['name']}  N={meta['n_particles']}  dt={meta['dt_myr']} Myr")
    for ti, si in zip(t[::max(1, len(t) // 30)], sep[::max(1, len(t) // 30)]):
        print(f"  t={ti:7.3f} Gyr  separation={si:8.2f} kpc")
    print("pericentre passages (local minima of the sampled separation):")
    for tp, sp in pericentres(t, sep):
        print(f"  t={tp:.3f} Gyr  d={sp:.2f} kpc")
    peri = pericentres(t, sep)
    print("apocentres (maxima between passages):")
    for (t0, _), (t1, _) in zip(peri, peri[1:]):
        sel = (t > t0) & (t < t1)
        if sel.any():
            k = np.argmax(np.where(sel, sep, -1))
            print(f"  t={t[k]:.3f} Gyr  d={sep[k]:.2f} kpc")
    if a.camera_keys:
        keys = []
        for tk in np.unique(np.concatenate([np.arange(0, t[-1] + 1e-9, 0.5), [p[0] for p in peri]])):
            sk = float(np.interp(tk, t, sep))
            keys.append([round(float(tk), 2), round(a.camera_factor * sk + a.camera_margin)])
        print("suggested camera distance_kpc keys:", keys)
    merged = np.nonzero(sep < a.merge_kpc)[0]
    if merged.size:
        # first time after which the centres stay within merge_kpc
        k = next((k for k in merged if np.all(sep[k:] < a.merge_kpc)), None)
        if k is not None:
            print(f"centres stay within {a.merge_kpc} kpc from t={t[k]:.3f} Gyr (merger)")


if __name__ == "__main__":
    sys.exit(main())
