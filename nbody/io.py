"""Snapshot / checkpoint I/O.

Run directory layout (all under the git-ignored ``output/``)::

    output/runs/<name>/
        run_meta.json            parameters, param-file sha256, git commit, E0, ...
        static.npz               per-particle data stored once: ptype, galaxy, mass
        snapshots/snap_0001234.npz   render snapshot: float32 positions + scalars
        checkpoints/ckpt_0001234.npz full float64 state (pos, vel) for restarts
        energy.csv               energy / momentum at every step
        progress.log             wall-clock progress

Render snapshots are written only at synchronised full steps (after the closing kick
of the KDK step), so position, time and energy refer to the same instant.
"""
import json
import os
import queue
import threading

import numpy as np

PTYPE_HALO, PTYPE_DISK, PTYPE_BULGE = 0, 1, 2
PTYPE_NAMES = {PTYPE_HALO: "halo", PTYPE_DISK: "disk", PTYPE_BULGE: "bulge"}


def snap_name(step):
    return f"snap_{step:07d}.npz"


def ckpt_name(step):
    return f"ckpt_{step:07d}.npz"


def _atomic_savez(path, compressed=True, **arrays):
    tmp = path + ".tmp.npz"
    if compressed:
        np.savez_compressed(tmp, **arrays)
    else:
        np.savez(tmp, **arrays)
    os.replace(tmp, path)


def write_static(path, ptype, galaxy, mass, galaxy_names):
    _atomic_savez(path, ptype=ptype.astype(np.uint8), galaxy=galaxy.astype(np.uint8),
                  mass=mass.astype(np.float64),
                  galaxy_names=np.array(galaxy_names, dtype="U32"))


def read_static(path):
    with np.load(path) as f:
        return {k: f[k] for k in f.files}


def render_snapshot_arrays(pos, step, time_internal, time_gyr, diag):
    return dict(
        pos=np.asarray(pos, dtype=np.float32),
        step=np.int64(step),
        time=np.float64(time_internal),
        time_gyr=np.float64(time_gyr),
        energy=np.float64(diag["energy"]),
        kinetic=np.float64(diag["kinetic"]),
        potential=np.float64(diag["potential"]),
        momentum=np.asarray(diag["momentum"], dtype=np.float64),
        angmom=np.asarray(diag["angmom"], dtype=np.float64),
    )


def read_snapshot(path):
    with np.load(path) as f:
        return {k: f[k] for k in f.files}


def read_snapshot_header(path):
    """Scalars only (cheap: does not decompress the positions)."""
    with np.load(path) as f:
        return {k: f[k] for k in f.files if k != "pos"}


def write_checkpoint(path, pos, vel, step, time_internal, diag):
    _atomic_savez(path, compressed=False, pos=pos, vel=vel, step=np.int64(step),
                  time=np.float64(time_internal), energy=np.float64(diag["energy"]))


def read_checkpoint(path):
    with np.load(path) as f:
        return {k: f[k] for k in f.files}


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True, default=_json_default)
    os.replace(tmp, path)


def read_json(path):
    with open(path) as fh:
        return json.load(fh)


def _json_default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


class AsyncWriter:
    """Writes snapshots on a background thread (zlib releases the GIL), so
    compression overlaps with force computation.  Bounded queue keeps memory flat."""

    def __init__(self, maxsize=8):
        self.q = queue.Queue(maxsize=maxsize)
        self.err = None
        self.t = threading.Thread(target=self._run, daemon=True)
        self.t.start()

    def _run(self):
        while True:
            item = self.q.get()
            if item is None:
                self.q.task_done()
                return
            path, arrays = item
            try:
                _atomic_savez(path, compressed=True, **arrays)
            except Exception as e:  # pragma: no cover
                self.err = e
            self.q.task_done()

    def submit(self, path, arrays):
        if self.err:
            raise self.err
        self.q.put((path, arrays))

    def close(self):
        self.q.put(None)
        self.t.join()
        if self.err:
            raise self.err
