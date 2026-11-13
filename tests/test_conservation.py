"""Full 5k-particle collision (approach, two passages, merger; 3 Gyr) with the
production Barnes-Hut solver: energy drift < 1 %, momentum conserved."""
import numpy as np
import pytest

from conftest import load_yaml, write_params
from nbody.integrator import ForceSolver, diagnostics, leapfrog
from nbody.io import read_snapshot, read_static
from nbody.run import run
from nbody.units import G


@pytest.fixture(scope="module")
def collision_run(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("collision")
    p = load_yaml("test_collision_5k.yaml")
    p["output"]["render"] = {"every_myr": 100}
    run_dir = run(write_params(tmp, p), out_root=tmp / "runs", quiet=True)
    log = np.genfromtxt(run_dir / "energy.csv", delimiter=",", names=True)
    st = read_static(run_dir / "static.npz")
    return run_dir, log, st


def test_energy_drift_below_one_percent(collision_run):
    _, log, _ = collision_run
    E0 = log["energy"][0]
    drift = np.abs(log["energy"] - E0) / abs(E0)
    print(f"steps {len(log) - 1}, t_end {log['time_gyr'][-1]:.2f} Gyr, max |dE/E| {drift.max():.2e}, "
          f"final {drift[-1]:.2e}")
    assert drift.max() < 0.01


def test_momentum_conserved(collision_run):
    _, log, st = collision_run
    P = np.column_stack([log["px"], log["py"], log["pz"]])
    M = st["mass"].sum()
    dv_com = np.linalg.norm(P - P[0], axis=1) / M          # drift of the centre-of-mass velocity
    # natural scale: total |momentum| of the particles, sum m |v|, ~ M * 250 km/s here
    print(f"max centre-of-mass velocity drift {dv_com.max():.3f} km/s")
    assert dv_com.max() < 0.5          # km/s, vs. ~300 km/s encounter velocity


def test_angular_momentum_conserved(collision_run):
    _, log, _ = collision_run
    L = np.column_stack([log["Lx"], log["Ly"], log["Lz"]])
    dL = np.linalg.norm(L - L[0], axis=1) / np.linalg.norm(L[0])
    print(f"max |dL|/|L0| {dL.max():.2e}")
    assert dL.max() < 0.01


def test_the_run_is_a_full_collision(collision_run):
    """The two galaxies' centres (bulge centres of mass) end up merged."""
    run_dir, log, st = collision_run
    snaps = sorted((run_dir / "snapshots").glob("snap_*.npz"))
    bulge = st["ptype"] == 2
    sep = []
    for f in snaps:
        pos = read_snapshot(f)["pos"].astype(float)
        c = [np.median(pos[bulge & (st["galaxy"] == g)], axis=0) for g in (0, 1)]
        sep.append(np.linalg.norm(c[1] - c[0]))
    sep = np.array(sep)
    print("separations (kpc):", np.round(sep, 1))
    assert sep[0] > 90 and sep.min() < 20 and sep[-1] < 3


def test_direct_summation_conserves_momentum_exactly():
    rng = np.random.default_rng(3)
    n = 1500
    pos = rng.normal(size=(n, 3)) * 5
    vel = rng.normal(size=(n, 3)) * 50
    mass = rng.uniform(0.5, 1.5, n) * 1e-3
    vel -= (mass[:, None] * vel).sum(0) / mass.sum()
    solver = ForceSolver(G, 0.1, "direct")
    p0 = (mass[:, None] * vel).sum(0)
    scale = (mass * np.linalg.norm(vel, axis=1)).sum()
    leapfrog(pos, vel, mass, solver, 1e-4, 50)
    p1 = (mass[:, None] * vel).sum(0)
    assert np.linalg.norm(p1 - p0) / scale < 1e-12
