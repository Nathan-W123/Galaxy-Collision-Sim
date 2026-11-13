"""Two-body Kepler orbit: the measured period matches the analytic value within 0.1 %."""
import numpy as np
import pytest

from nbody.integrator import ForceSolver, leapfrog
from nbody.units import G


def kepler_period(method):
    m1, m2 = 10.0, 1.0                     # 1e11 and 1e10 Msun
    a, e = 20.0, 0.6                       # kpc
    M = m1 + m2
    T = 2 * np.pi * np.sqrt(a ** 3 / (G * M))
    rp = a * (1 - e)
    vp = np.sqrt(G * M * (1 + e) / rp)
    rel_x = np.array([rp, 0.0, 0.0])
    rel_v = np.array([0.0, vp, 0.0])
    pos = np.array([-m2 / M * rel_x, m1 / M * rel_x])
    vel = np.array([-m2 / M * rel_v, m1 / M * rel_v])
    mass = np.array([m1, m2])
    n_per_orbit = 2000
    dt = T / n_per_orbit
    n_orbits = 5
    solver = ForceSolver(G, 0.0, method=method)
    angles = []

    def on_step(step, p, v, acc, pot):
        r = p[1] - p[0]
        angles.append(np.arctan2(r[1], r[0]))

    leapfrog(pos, vel, mass, solver, dt, int((n_orbits + 0.5) * n_per_orbit), on_step=on_step)
    phase = np.unwrap(np.array(angles))
    t = np.arange(phase.size) * dt
    # times at which the orbit completes k full turns (linear root-finding on the
    # measured phase; this is analysis of the test, not part of any rendering)
    crossings = []
    for k in range(1, n_orbits + 1):
        target = 2 * np.pi * k
        i = np.searchsorted(phase, target)
        f = (target - phase[i - 1]) / (phase[i] - phase[i - 1])
        crossings.append(t[i - 1] + f * dt)
    periods = np.diff([0.0] + crossings)
    return periods, T


@pytest.mark.parametrize("method", ["direct", "tree"])
def test_kepler_period(method):
    periods, T = kepler_period(method)
    rel = np.abs(periods - T) / T
    print(f"{method}: analytic T = {T:.6f}, measured {periods}, max rel err {rel.max():.2e}")
    assert rel.max() < 1e-3
