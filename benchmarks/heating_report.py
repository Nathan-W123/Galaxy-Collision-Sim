"""Disk-heating comparison for isolated galaxy runs.

    python benchmarks/heating_report.py output/heating/heating_* [--approach-gyr 4.0]

For each run: disk thickness z_rms(t) (about the disk's own spin axis and centre),
the heating rate d<z^2>/dt from a linear fit, the projected thickness after the
approach phase, the halo-to-disk particle-mass ratio, and the energy drift.
"""
import argparse
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from nbody.io import PTYPE_DISK, PTYPE_HALO, read_json, read_snapshot, read_static  # noqa: E402


def thickness(pos, mass, disk, axis):
    c = (mass[disk, None] * pos[disk]).sum(0) / mass[disk].sum()
    x = pos[disk] - c
    z = x @ axis
    R = np.linalg.norm(x - z[:, None] * axis, axis=1)
    sel = (R > 2.0) & (R < 10.0)
    return float(np.sqrt(np.mean(z[sel] ** 2))), float(np.median(R))


def report(run_dir, approach_gyr):
    run_dir = Path(run_dir)
    meta = read_json(run_dir / "run_meta.json")
    st = read_static(run_dir / "static.npz")
    disk = st["ptype"] == PTYPE_DISK
    m_h = float(np.median(st["mass"][st["ptype"] == PTYPE_HALO]))
    m_d = float(np.median(st["mass"][disk]))
    axis = np.array([0.0, 0.0, 1.0])
    t, z, rh = [], [], []
    for f in sorted((run_dir / "snapshots").glob("snap_*.npz")):
        s = read_snapshot(f)
        zz, r = thickness(s["pos"].astype(float), st["mass"], disk, axis)
        t.append(float(s["time_gyr"]))
        z.append(zz)
        rh.append(r)
    t, z = np.array(t), np.array(z)
    rate = np.polyfit(t, z ** 2, 1)[0]
    z_proj = np.sqrt(z[0] ** 2 + rate * approach_gyr)
    log = np.genfromtxt(run_dir / "energy.csv", delimiter=",", names=True)
    dE = np.abs(log["energy"] - log["energy"][0]).max() / abs(log["energy"][0])
    return dict(name=meta["name"], N=meta["n_particles"], dt=meta["dt_myr"], eps=meta["softening_kpc"],
                m_halo=m_h * 1e10, ratio=m_h / m_d, z0=z[0], z_end=z[-1], t_end=t[-1], rate=rate,
                z_proj=z_proj, dE=dE, Rhalf0=rh[0], Rhalf1=rh[-1],
                wall_min=meta.get("wall_time_s", float("nan")) / 60)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--approach-gyr", type=float, default=4.0)
    a = ap.parse_args(argv)
    rows = [report(r, a.approach_gyr) for r in a.runs]
    print(f"| run | N | dt (Myr) | eps (kpc) | halo particle (Msun) | halo/disk mass | "
          f"z_rms t=0 | z_rms t={rows[0]['t_end']:.0f} Gyr | d<z^2>/dt (kpc^2/Gyr) | "
          f"z_rms after {a.approach_gyr:g} Gyr | max dE/E | wall (min) |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        print(f"| {r['name']} | {r['N']:,} | {r['dt']:g} | {r['eps']:g} | {r['m_halo']:.1e} | {r['ratio']:.1f} | "
              f"{r['z0']:.2f} | {r['z_end']:.2f} | {r['rate']:.3f} | {r['z_proj']:.2f} | {r['dE']:.1e} | "
              f"{r['wall_min']:.0f} |")


if __name__ == "__main__":
    main()
