"""Run a simulation from a parameter file.

    python -m nbody.run scenarios/test_collision_5k.yaml [--schedule FILE] [--out output/runs]
                                                       [--resume] [--n-steps N] [--name NAME]

``--schedule`` replaces the parameter file's ``output`` section with an edit-specific
snapshot schedule (dense windows for slow motion).  The schedule never changes the
trajectory, so a coarse exploratory run and the dense rerun share the same physics file.

Writes render snapshots (float32 positions) on the configured windowed cadence, full
float64 checkpoints less often, and energy/momentum at every step.  ``--resume``
continues bitwise-identically from the newest checkpoint.
"""
import argparse
import hashlib
import platform
import shutil
import sys
import time
from pathlib import Path

import numba
import numpy as np
import yaml

from . import __version__
from .ics import make_initial_conditions
from .integrator import ForceSolver, diagnostics, leapfrog
from .io import (AsyncWriter, ckpt_name, read_checkpoint, read_json,
                 render_snapshot_arrays, snap_name, write_checkpoint, write_json,
                 write_static)
from .params import git_commit, load_params
from .schedule import build_checkpoint_steps, build_render_steps, to_steps
from .units import G as G_DEFAULT
from .units import TIME_UNIT_GYR, TIME_UNIT_MYR


def setup(params):
    sim = params["simulation"]
    G = float(params.get("units", {}).get("G", G_DEFAULT))
    dt_myr = float(sim["dt_myr"])
    n_steps = to_steps(float(sim["t_end_gyr"]) * 1e3, dt_myr, "t_end_gyr")
    dt = dt_myr / TIME_UNIT_MYR
    solver = ForceSolver(G, float(sim["softening_kpc"]), sim["solver"], float(sim["theta"]),
                         int(sim["leaf_size"]), bool(sim.get("quadrupole", True)))
    out = params["output"]
    render_steps = build_render_steps(out["render"], dt_myr, n_steps)
    ckpt_steps = build_checkpoint_steps(out["checkpoint_every_myr"], dt_myr, n_steps)
    return G, dt, dt_myr, n_steps, solver, render_steps, ckpt_steps


def run(param_path, out_root="output/runs", resume=False, n_steps_override=None, name=None,
        quiet=False, write_snapshots=True, schedule_path=None):
    params, phash = load_params(param_path)
    shash = None
    if schedule_path is not None:
        raw = Path(schedule_path).read_bytes()
        shash = hashlib.sha256(raw).hexdigest()
        params["output"] = yaml.safe_load(raw)
        params["output"].setdefault("checkpoint_every_myr", 500.0)
    if name:
        params["name"] = name
    G, dt, dt_myr, n_steps, solver, render_steps, ckpt_steps = setup(params)
    if n_steps_override is not None:
        n_steps = int(n_steps_override)
        render_steps = render_steps[render_steps <= n_steps]
        ckpt_steps = np.union1d(ckpt_steps[ckpt_steps <= n_steps], [n_steps])
    run_dir = Path(out_root) / params["name"]
    snap_dir = run_dir / "snapshots"
    ckpt_dir = run_dir / "checkpoints"

    t_setup = time.time()
    start_step = 0
    if resume and ckpt_dir.exists() and any(ckpt_dir.iterdir()):
        meta = read_json(run_dir / "run_meta.json")
        if meta["param_sha256"] != phash or meta.get("schedule_sha256") != shash:
            raise SystemExit("parameter or schedule file changed since the run started; refusing to resume")
        last = sorted(ckpt_dir.glob("ckpt_*.npz"))[-1]
        ck = read_checkpoint(str(last))
        from .io import read_static
        st = read_static(str(run_dir / "static.npz"))
        pos, vel, mass = ck["pos"].copy(), ck["vel"].copy(), st["mass"]
        start_step = int(ck["step"])
        E0 = meta["E0"]
        # truncate the energy log to the restart step
        lines = (run_dir / "energy.csv").read_text().splitlines()
        keep = [lines[0]] + [l for l in lines[1:] if int(l.split(",")[0]) < start_step]
        (run_dir / "energy.csv").write_text("\n".join(keep) + "\n")
        meta["resumed_from_step"] = meta.get("resumed_from_step", []) + [start_step]
        write_json(str(run_dir / "run_meta.json"), meta)
    else:
        if run_dir.exists():
            shutil.rmtree(run_dir)
        snap_dir.mkdir(parents=True)
        ckpt_dir.mkdir(parents=True)
        ics = make_initial_conditions(params, G)
        pos, vel, mass = ics["pos"], ics["vel"], ics["mass"]
        write_static(str(run_dir / "static.npz"), ics["ptype"], ics["galaxy"], mass,
                     ics["galaxy_names"])
        shutil.copy(param_path, run_dir / "params.yaml")
        if schedule_path is not None:
            shutil.copy(schedule_path, run_dir / "schedule.yaml")
        meta = {
            "name": params["name"],
            "param_file": str(param_path),
            "param_sha256": phash,
            "schedule_file": str(schedule_path) if schedule_path else None,
            "schedule_sha256": shash,
            "git_commit": git_commit(),
            "engine_version": __version__,
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "numba": numba.__version__,
            "platform": platform.platform(),
            "threads": numba.get_num_threads(),
            "seed": params["seed"],
            "n_particles": int(mass.size),
            "n_by_type": {str(t): int((ics["ptype"] == t).sum()) for t in (0, 1, 2)},
            "G": G,
            "dt_internal": dt,
            "dt_myr": dt_myr,
            "time_unit_gyr": TIME_UNIT_GYR,
            "n_steps": n_steps,
            "softening_kpc": solver.eps,
            "solver": solver.method,
            "theta": solver.theta,
            "leaf_size": solver.leaf_size,
            "quadrupole": solver.quadrupole,
            "render_steps": render_steps.tolist(),
            "checkpoint_steps": ckpt_steps.tolist(),
            "galaxy_names": ics["galaxy_names"],
            "galaxy_masses": [float(mass[ics["galaxy"] == g].sum())
                              for g in range(len(ics["galaxy_names"]))],
        }
        if "relative_position" in ics:
            meta["initial_relative_position_kpc"] = ics["relative_position"]
            meta["initial_relative_velocity_kms"] = ics["relative_velocity"]
        E0 = None
        (run_dir / "energy.csv").write_text(
            "step,time_gyr,energy,kinetic,potential,px,py,pz,Lx,Ly,Lz,wall_s\n")
        write_json(str(run_dir / "run_meta.json"), meta)

    render_set = set(int(s) for s in render_steps)
    ckpt_set = set(int(s) for s in ckpt_steps)
    writer = AsyncWriter()
    elog = open(run_dir / "energy.csv", "a")
    plog = open(run_dir / "progress.log", "a")
    t0 = time.time()
    state = {"E0": E0, "last_report": t0}

    def on_step(step, pos, vel, acc, pot):
        d = diagnostics(pos, vel, mass, pot)
        if state["E0"] is None:
            state["E0"] = d["energy"]
            meta["E0"] = d["energy"]
            write_json(str(run_dir / "run_meta.json"), meta)
        tgyr = step * dt * TIME_UNIT_GYR
        now = time.time()
        p, L = d["momentum"], d["angmom"]
        elog.write(f"{step},{tgyr:.9f},{d['energy']:.12e},{d['kinetic']:.12e},"
                   f"{d['potential']:.12e},{p[0]:.6e},{p[1]:.6e},{p[2]:.6e},"
                   f"{L[0]:.6e},{L[1]:.6e},{L[2]:.6e},{now - t0:.3f}\n")
        if write_snapshots and step in render_set:
            writer.submit(str(snap_dir / snap_name(step)),
                          render_snapshot_arrays(pos, step, step * dt, tgyr, d))
        if step in ckpt_set:
            write_checkpoint(str(ckpt_dir / ckpt_name(step)), pos, vel, step, step * dt, d)
            elog.flush()
        if now - state["last_report"] > 30 or step == n_steps:
            done = step - start_step
            rate = (now - t0) / max(done, 1)
            eta = rate * (n_steps - step)
            dE = (d["energy"] - state["E0"]) / abs(state["E0"])
            msg = (f"step {step}/{n_steps} t={tgyr:.3f} Gyr  {rate:.3f} s/step  "
                   f"ETA {eta / 60:.1f} min  dE/E={dE:+.2e}")
            plog.write(time.strftime("%H:%M:%S ") + msg + "\n")
            plog.flush()
            if not quiet:
                print(msg, flush=True)
            state["last_report"] = now

    leapfrog(pos, vel, mass, solver, dt, n_steps, start_step=start_step, on_step=on_step)
    writer.close()
    elog.close()
    plog.close()
    meta = read_json(str(run_dir / "run_meta.json"))
    meta["wall_time_s"] = meta.get("wall_time_s", 0.0) + (time.time() - t_setup)
    meta["completed"] = True
    write_json(str(run_dir / "run_meta.json"), meta)
    return run_dir


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("params")
    ap.add_argument("--schedule", default=None, help="snapshot schedule file (replaces `output`)")
    ap.add_argument("--out", default="output/runs")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--n-steps", type=int, default=None, help="stop early (testing)")
    ap.add_argument("--name", default=None, help="override run name")
    ap.add_argument("--threads", type=int, default=None)
    a = ap.parse_args(argv)
    if a.threads:
        numba.set_num_threads(a.threads)
    run(a.params, a.out, a.resume, a.n_steps, a.name, schedule_path=a.schedule)


if __name__ == "__main__":
    main()
