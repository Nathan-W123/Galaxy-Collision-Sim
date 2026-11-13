"""Output schedule: which integer steps write render snapshots / checkpoints.

All times are converted to integer step indices, and conversion fails loudly unless
the requested time is an exact multiple of the timestep.  Snapshot times are therefore
always ``step * dt`` exactly: nothing is ever written between steps and nothing is
interpolated.

Render cadence is configured either per time window ("dense output"), e.g.

    render:
      every_myr: 10            # default cadence
      windows:                 # finer cadence in [start, end)
        - {start_gyr: 3.6, end_gyr: 4.2, every_myr: 1}

or as a time remap for an edit: playback speed in Myr per frame as a function of
simulation time, interpolated geometrically between keys, e.g.

    render:
      speed_myr_per_frame:     # [sim time (Gyr), Myr per frame]
        - [0.00, 6]
        - [0.18, 2]            # ramp into slow motion
        - [0.40, 2]
        - [0.55, 12]           # ramp back out

Each frame advances by round(speed / dt) >= 1 whole steps, so a smooth ramp becomes a
staircase of small speed changes, and every frame is still one saved snapshot.
"""
import numpy as np

_TOL = 1e-9


def to_steps(value_myr, dt_myr, what="time"):
    """Convert a duration/time in Myr to an exact integer number of steps."""
    k = value_myr / dt_myr
    ki = int(round(k))
    if abs(k - ki) > _TOL * max(1.0, abs(k)):
        raise ValueError(f"{what}={value_myr} Myr is not an integer multiple of dt={dt_myr} Myr")
    return ki


def build_remap_steps(keys, dt_myr, n_steps):
    """Steps for a speed curve ``[[t_gyr, myr_per_frame], ...]`` (geometric interpolation)."""
    keys = sorted((float(t) * 1e3, float(v)) for t, v in keys)
    if any(v <= 0 for _, v in keys):
        raise ValueError("speed_myr_per_frame must be positive")
    tk = np.array([k[0] for k in keys])
    lv = np.log([k[1] for k in keys])
    steps = [0]
    s = 0
    while s < n_steps:
        sp = float(np.exp(np.interp(s * dt_myr, tk, lv)))
        s = min(s + max(1, int(round(sp / dt_myr))), n_steps)
        steps.append(s)
    return np.array(steps, dtype=np.int64)


def build_render_steps(render_cfg, dt_myr, n_steps):
    """Sorted unique array of steps at which render snapshots are written."""
    if "speed_myr_per_frame" in render_cfg:
        return build_remap_steps(render_cfg["speed_myr_per_frame"], dt_myr, n_steps)
    every = to_steps(float(render_cfg.get("every_myr", 10.0)), dt_myr, "render.every_myr")
    if every <= 0:
        raise ValueError("render.every_myr must be positive")
    windows = []
    for w in render_cfg.get("windows", []) or []:
        s = to_steps(float(w["start_gyr"]) * 1e3, dt_myr, "window.start_gyr")
        e = to_steps(float(w["end_gyr"]) * 1e3, dt_myr, "window.end_gyr")
        k = to_steps(float(w["every_myr"]), dt_myr, "window.every_myr")
        if not (0 <= s < e) or k <= 0:
            raise ValueError(f"bad window {w}")
        windows.append((s, e, k))
    windows.sort()
    for (s0, e0, _), (s1, e1, _) in zip(windows, windows[1:]):
        if s1 < e0:
            raise ValueError("render windows overlap")
    all_steps = np.arange(n_steps + 1, dtype=np.int64)
    in_window = np.zeros(n_steps + 1, bool)
    keep = np.zeros(n_steps + 1, bool)
    for s, e, k in windows:
        sel = (all_steps >= s) & (all_steps < e)
        in_window |= sel
        keep |= sel & ((all_steps - s) % k == 0)
    keep |= (~in_window) & (all_steps % every == 0)
    keep[0] = True
    keep[n_steps] = True
    return all_steps[keep]


def build_checkpoint_steps(every_myr, dt_myr, n_steps):
    k = to_steps(float(every_myr), dt_myr, "checkpoint_every_myr")
    steps = set(range(0, n_steps + 1, k))
    steps.add(n_steps)
    return np.array(sorted(steps), dtype=np.int64)
