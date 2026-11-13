import numpy as np
import pytest

from nbody.schedule import build_checkpoint_steps, build_render_steps, to_steps


def test_to_steps_exact_and_rejects_off_grid():
    assert to_steps(10.0, 0.5) == 20
    assert to_steps(3600.0, 1.0) == 3600
    with pytest.raises(ValueError):
        to_steps(10.25, 0.5)


def test_windowed_cadence():
    cfg = {"every_myr": 10, "windows": [{"start_gyr": 1.0, "end_gyr": 1.1, "every_myr": 1}]}
    s = build_render_steps(cfg, 0.5, 4000)          # dt = 0.5 Myr, 2 Gyr
    assert s[0] == 0 and s[-1] == 4000
    inside = s[(s >= 2000) & (s < 2200)]
    assert np.all(np.diff(inside) == 2)              # every 1 Myr = 2 steps
    outside = s[s < 2000]
    assert np.all(np.diff(outside) == 20)            # every 10 Myr = 20 steps
    assert np.all(np.diff(s) > 0)


def test_overlapping_windows_rejected():
    cfg = {"every_myr": 10, "windows": [{"start_gyr": 1.0, "end_gyr": 1.5, "every_myr": 1},
                                        {"start_gyr": 1.4, "end_gyr": 1.6, "every_myr": 2}]}
    with pytest.raises(ValueError):
        build_render_steps(cfg, 1.0, 3000)


def test_checkpoints():
    assert list(build_checkpoint_steps(500, 1.0, 1200)) == [0, 500, 1000, 1200]
