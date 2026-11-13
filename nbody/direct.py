"""Direct-summation gravity with Plummer softening (ground truth, O(N^2))."""
import numpy as np
from numba import njit, prange


@njit(parallel=True, cache=True)
def _direct_kernel(pos, mass, eps2, G, acc, pot):
    n = pos.shape[0]
    for i in prange(n):
        xi = pos[i, 0]
        yi = pos[i, 1]
        zi = pos[i, 2]
        ax = 0.0
        ay = 0.0
        az = 0.0
        p = 0.0
        for j in range(n):
            if j == i:
                continue
            dx = pos[j, 0] - xi
            dy = pos[j, 1] - yi
            dz = pos[j, 2] - zi
            r2 = dx * dx + dy * dy + dz * dz + eps2
            inv = 1.0 / np.sqrt(r2)
            mi3 = mass[j] * inv * inv * inv
            ax += mi3 * dx
            ay += mi3 * dy
            az += mi3 * dz
            p -= mass[j] * inv
        acc[i, 0] = G * ax
        acc[i, 1] = G * ay
        acc[i, 2] = G * az
        pot[i] = G * p


def direct_accel(pos, mass, eps, G):
    """Accelerations and potentials of all particles by direct summation.

    a_i = G sum_j m_j (x_j - x_i) / (|x_j - x_i|^2 + eps^2)^{3/2}
    phi_i = -G sum_j m_j / sqrt(|x_j - x_i|^2 + eps^2)      (j != i)
    """
    pos = np.ascontiguousarray(pos, dtype=np.float64)
    mass = np.ascontiguousarray(mass, dtype=np.float64)
    acc = np.empty_like(pos)
    pot = np.empty(pos.shape[0])
    _direct_kernel(pos, mass, float(eps) ** 2, float(G), acc, pot)
    return acc, pot


@njit(parallel=True, cache=True)
def _direct_targets_kernel(tpos, pos, mass, eps2, G, acc, pot):
    """Field of all source particles at arbitrary target points (no self-skip)."""
    nt = tpos.shape[0]
    n = pos.shape[0]
    for i in prange(nt):
        ax = 0.0
        ay = 0.0
        az = 0.0
        p = 0.0
        for j in range(n):
            dx = pos[j, 0] - tpos[i, 0]
            dy = pos[j, 1] - tpos[i, 1]
            dz = pos[j, 2] - tpos[i, 2]
            r2 = dx * dx + dy * dy + dz * dz + eps2
            if r2 == 0.0:
                continue
            inv = 1.0 / np.sqrt(r2)
            mi3 = mass[j] * inv * inv * inv
            ax += mi3 * dx
            ay += mi3 * dy
            az += mi3 * dz
            p -= mass[j] * inv
        acc[i, 0] = G * ax
        acc[i, 1] = G * ay
        acc[i, 2] = G * az
        pot[i] = G * p


def direct_field(targets, pos, mass, eps, G):
    targets = np.ascontiguousarray(targets, dtype=np.float64)
    acc = np.empty_like(targets)
    pot = np.empty(targets.shape[0])
    _direct_targets_kernel(targets, np.ascontiguousarray(pos, dtype=np.float64),
                           np.ascontiguousarray(mass, dtype=np.float64),
                           float(eps) ** 2, float(G), acc, pot)
    return acc, pot
