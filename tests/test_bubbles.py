"""The toy bubble model: wall growth, nucleation only in false vacuum, exact collision times."""
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from explainer.bubbles import BubbleUniverse


def make():
    return BubbleUniverse(8.0, 10.0, gamma=0.02, t_end=2.5, seed=3)


def test_bubbles_exist_and_later_ones_are_smaller():
    u = make()
    assert 10 < u.tn.size < 400
    r_inf = u.radius(1e9)
    assert np.all(np.diff(r_inf[np.argsort(u.tn)]) <= 1e-12)   # asymptotic size falls with t_n


def test_no_bubble_born_inside_another():
    u = make()
    for k in range(u.tn.size):
        older = u.tn < u.tn[k]
        d = np.linalg.norm(u.x[older] - u.x[k], axis=1)
        assert np.all(d >= u.radius(u.tn[k])[older] - 1e-12)


def test_collision_times_match_brute_force():
    u = make()
    assert len(u.collisions) > 3
    for i, j, tc, p in u.collisions[:20]:
        d = np.linalg.norm(u.x[i] - u.x[j])
        gap = lambda t: u.radius(t)[i] + u.radius(t)[j] - d
        assert abs(gap(tc)) < 1e-9
        assert gap(tc - 1e-6) < 0 < gap(tc + 1e-6)
        # contact point lies on both walls
        assert abs(np.linalg.norm(p - u.x[i]) - u.radius(tc)[i]) < 1e-9
        assert abs(np.linalg.norm(p - u.x[j]) - u.radius(tc)[j]) < 1e-9


def test_deterministic():
    a, b = make(), make()
    assert np.array_equal(a.x, b.x) and np.array_equal(a.tn, b.tn)
