"""Same seed + same parameters -> identical snapshots.  Also: output cadence, thread
count and checkpoint-restart do not change the trajectory."""
import shutil

import numba
import numpy as np
import pytest

from conftest import load_yaml, write_params
from nbody.ics import make_initial_conditions
from nbody.io import read_snapshot
from nbody.run import run

N_STEPS = 120


def snapshots(run_dir):
    return {f.name: read_snapshot(f) for f in sorted((run_dir / "snapshots").glob("snap_*.npz"))}


def assert_identical(a, b, names=None):
    names = names or sorted(set(a) | set(b))
    assert names
    for n in names:
        for k in a[n]:
            assert np.array_equal(a[n][k], b[n][k]), (n, k)


@pytest.fixture(scope="module")
def setup(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("repro")
    p = load_yaml("test_collision_5k.yaml")
    p["output"]["render"] = {"every_myr": 10}
    p["output"]["checkpoint_every_myr"] = 60
    path = write_params(tmp, p)
    ref = run(path, out_root=tmp / "runs", n_steps_override=N_STEPS, name="ref", quiet=True)
    return tmp, p, path, ref


def test_same_seed_identical_snapshots(setup):
    tmp, p, path, ref = setup
    again = run(path, out_root=tmp / "runs", n_steps_override=N_STEPS, name="again", quiet=True)
    a, b = snapshots(ref), snapshots(again)
    assert len(a) == N_STEPS // 10 + 1
    assert_identical(a, b)


def test_dense_output_does_not_change_trajectory(setup):
    tmp, p, _, ref = setup
    q = dict(p)
    q["output"] = {"render": {"every_myr": 10, "windows": [{"start_gyr": 0.05, "end_gyr": 0.08,
                                                           "every_myr": 1}]},
                   "checkpoint_every_myr": 60}
    dense = run(write_params(tmp, q, "dense.yaml"), out_root=tmp / "runs",
                n_steps_override=N_STEPS, name="dense", quiet=True)
    a, b = snapshots(ref), snapshots(dense)
    assert len(b) > len(a)
    assert_identical(a, b, sorted(set(a) & set(b)))


def test_thread_count_does_not_change_result(setup):
    tmp, p, path, ref = setup
    old = numba.get_num_threads()
    numba.set_num_threads(1)
    try:
        one = run(path, out_root=tmp / "runs", n_steps_override=N_STEPS, name="one_thread", quiet=True)
    finally:
        numba.set_num_threads(old)
    assert_identical(snapshots(ref), snapshots(one))


def test_resume_from_checkpoint_is_bitwise(setup):
    tmp, p, path, ref = setup
    shutil.copytree(ref, tmp / "runs" / "resumed")
    d = tmp / "runs" / "resumed"
    # simulate a crash after the checkpoint at step 60
    for f in (d / "checkpoints").glob("ckpt_*.npz"):
        if int(f.stem.split("_")[1]) > 60:
            f.unlink()
    for f in (d / "snapshots").glob("snap_*.npz"):
        if int(f.stem.split("_")[1]) > 60:
            f.unlink()
    run(path, out_root=tmp / "runs", n_steps_override=N_STEPS, name="resumed", resume=True, quiet=True)
    assert_identical(snapshots(ref), snapshots(d))


def test_different_seed_differs():
    p = load_yaml("test_collision_5k.yaml")
    a = make_initial_conditions(p)
    p["seed"] = p["seed"] + 1
    b = make_initial_conditions(p)
    assert not np.array_equal(a["pos"], b["pos"])
