"""Kick-drift-kick leapfrog with a fixed global timestep."""
import numpy as np

from .direct import direct_accel
from .tree import Octree


class ForceSolver:
    """Gravity solver: 'tree' (Barnes-Hut, production) or 'direct' (ground truth)."""

    def __init__(self, G, softening, method="tree", theta=0.6, leaf_size=8, quadrupole=True):
        if method not in ("tree", "direct"):
            raise ValueError(method)
        self.G = float(G)
        self.eps = float(softening)
        self.method = method
        self.theta = float(theta)
        self.leaf_size = int(leaf_size)
        self.quadrupole = bool(quadrupole)

    def __call__(self, pos, mass):
        if self.method == "direct":
            return direct_accel(pos, mass, self.eps, self.G)
        return Octree(pos, mass, self.theta, self.leaf_size, self.quadrupole).accel(self.eps, self.G)


def diagnostics(pos, vel, mass, pot):
    """Energy, momentum and angular momentum at a synchronised step."""
    kin = 0.5 * float(np.sum(mass * np.einsum("ij,ij->i", vel, vel)))
    potential = 0.5 * float(np.sum(mass * pot))
    mom = (mass[:, None] * vel).sum(axis=0)
    L = (mass[:, None] * np.cross(pos, vel)).sum(axis=0)
    return {"energy": kin + potential, "kinetic": kin, "potential": potential,
            "momentum": mom, "angmom": L}


def leapfrog(pos, vel, mass, solver, dt, n_steps, start_step=0, on_step=None):
    """Integrate in place from ``start_step`` to ``n_steps``.

    One step (KDK):  v += a dt/2 ;  x += v dt ;  a = a(x) ;  v += a dt/2
    ``on_step(step, pos, vel, acc, pot)`` is called at every *synchronised* full step
    (after the closing kick), including ``start_step`` itself.  Time is ``step * dt``,
    computed from the integer step, never accumulated.
    """
    acc, pot = solver(pos, mass)
    if on_step is not None:
        on_step(start_step, pos, vel, acc, pot)
    half = 0.5 * dt
    for step in range(start_step + 1, n_steps + 1):
        vel += half * acc
        pos += dt * vel
        acc, pot = solver(pos, mass)
        vel += half * acc
        if on_step is not None:
            on_step(step, pos, vel, acc, pot)
    return pos, vel
