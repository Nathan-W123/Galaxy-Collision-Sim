"""Barnes-Hut octree (Barnes & Hut 1986) with Plummer softening.

Layout
------
Particles are sorted along a 63-bit Morton (Z-order) curve.  Every tree node owns a
contiguous range of the sorted particles.  Nodes are stored in depth-first pre-order,
so the first child of an internal node is ``node + 1`` and ``next[node]`` (the node
visited after the whole subtree has been skipped) is ``node + subtree_size``.  This gives
a stack-free ("threaded") tree walk.

Chains of single-child nodes are collapsed, so every internal node has at least two
children and the number of nodes is bounded by ``2 N``.

Opening criterion
-----------------
A node of side length ``s`` whose centre of mass is a distance ``d`` from the target
particle is accepted as a single pseudo-particle when

    s / d < theta

and the particle is not inside the node's cube enlarged by 20 % (the same safeguard as
GADGET-2, which protects against the pathological case of a centre of mass sitting
near the far side of a large cell).  Otherwise the node is opened.  Leaves that are
opened are summed particle-by-particle.

Multipoles
----------
An accepted node contributes its monopole (total mass at the centre of mass) plus, by
default, its traceless quadrupole moment Q_ij = sum m (3 x_i x_j - r^2 delta_ij)
(Hernquist 1987).  The quadrupole term does not change which nodes are opened; it
reduces the force error of each accepted node, which matters for energy conservation
at theta = 0.6.  ``quadrupole=False`` gives the classic monopole-only Barnes-Hut code.

Forces and potentials on all particles are independent computations, so results are
bitwise identical regardless of the number of threads or their scheduling.  The walk is
compiled with ``fastmath`` (FMA contraction, reassociation): this changes rounding
compared with strict IEEE evaluation, but the compiled code is fixed, so runs remain
bitwise reproducible on the same machine and software stack.
"""
import numpy as np
import numba
from numba import njit, prange

MAXLEV = 21  # 21 bits per dimension -> 63-bit Morton keys

# node data columns
(C_COMX, C_COMY, C_COMZ, C_MASS, C_CX, C_CY, C_CZ, C_HALF, C_ROPEN2, C_BOX,
 C_QXX, C_QYY, C_QZZ, C_QXY, C_QXZ, C_QYZ) = range(16)
NCOL = 16


@njit(cache=True, inline="always")
def _spread(x):
    x = x & 0x1FFFFF
    x = (x | (x << 32)) & 0x1F00000000FFFF
    x = (x | (x << 16)) & 0x1F0000FF0000FF
    x = (x | (x << 8)) & 0x100F00F00F00F00F
    x = (x | (x << 4)) & 0x10C30C30C30C30C3
    x = (x | (x << 2)) & 0x1249249249249249
    return x


@njit(parallel=True, cache=True)
def _morton(pos, corner, inv_cell, keys, ixyz):
    n = pos.shape[0]
    maxc = (1 << MAXLEV) - 1
    for i in prange(n):
        a = np.int64(np.floor((pos[i, 0] - corner[0]) * inv_cell))
        b = np.int64(np.floor((pos[i, 1] - corner[1]) * inv_cell))
        c = np.int64(np.floor((pos[i, 2] - corner[2]) * inv_cell))
        a = min(max(a, 0), maxc)
        b = min(max(b, 0), maxc)
        c = min(max(c, 0), maxc)
        ixyz[i, 0] = a
        ixyz[i, 1] = b
        ixyz[i, 2] = c
        keys[i] = _spread(a) | (_spread(b) << 1) | (_spread(c) << 2)


@njit(cache=True)
def _build(keys, ixyz, leaf_size, corner, cell,
           nstart, nend, nlevel, nparent, nleaf, ncen):
    """Top-down build in depth-first pre-order. Returns number of nodes or -1."""
    n = keys.shape[0]
    max_nodes = nstart.shape[0]
    stack = np.empty((2048, 4), np.int64)
    cs = np.empty(8, np.int64)
    ce = np.empty(8, np.int64)
    stack[0, 0] = 0
    stack[0, 1] = n
    stack[0, 2] = 0
    stack[0, 3] = -1
    top = 1
    nn = 0
    while top > 0:
        top -= 1
        s = stack[top, 0]
        e = stack[top, 1]
        lev = stack[top, 2]
        par = stack[top, 3]
        # collapse chains of single-child nodes
        while lev < MAXLEV and e - s > leaf_size:
            sh = 3 * (MAXLEV - (lev + 1))
            if (keys[s] >> sh) == (keys[e - 1] >> sh):
                lev += 1
            else:
                break
        if nn >= max_nodes:
            return -1
        node = nn
        nn += 1
        nstart[node] = s
        nend[node] = e
        nlevel[node] = lev
        nparent[node] = par
        shc = MAXLEV - lev
        side_cells = np.int64(1) << shc
        for k in range(3):
            base = (ixyz[s, k] >> shc) << shc
            ncen[node, k] = corner[k] + (base + 0.5 * side_cells) * cell
        if e - s > leaf_size and lev < MAXLEV:
            nleaf[node] = 0
            sh = 3 * (MAXLEV - (lev + 1))
            cnt = 0
            j = s
            while j < e:
                pre = keys[j] >> sh
                lo = j + 1
                hi = e
                while lo < hi:
                    mid = (lo + hi) >> 1
                    if (keys[mid] >> sh) <= pre:
                        lo = mid + 1
                    else:
                        hi = mid
                cs[cnt] = j
                ce[cnt] = lo
                cnt += 1
                j = lo
            for c in range(cnt - 1, -1, -1):
                stack[top, 0] = cs[c]
                stack[top, 1] = ce[c]
                stack[top, 2] = lev + 1
                stack[top, 3] = node
                top += 1
        else:
            nleaf[node] = 1
    return nn


@njit(cache=True)
def _finish(nn, nparent, nleaf, nstart, nend, nlevel, ncen, pos_s, mass_s,
            root_half, theta, nnext, ndata):
    size = np.ones(nn, np.int64)
    for i in range(nn - 1, 0, -1):
        size[nparent[i]] += size[i]
    for i in range(nn):
        nnext[i] = i + size[i]
    msum = np.zeros(nn)
    mx = np.zeros((nn, 3))
    for i in range(nn - 1, -1, -1):
        if nleaf[i] == 1:
            m = 0.0
            sx = 0.0
            sy = 0.0
            sz = 0.0
            for j in range(nstart[i], nend[i]):
                mj = mass_s[j]
                m += mj
                sx += mj * pos_s[j, 0]
                sy += mj * pos_s[j, 1]
                sz += mj * pos_s[j, 2]
            msum[i] += m
            mx[i, 0] += sx
            mx[i, 1] += sy
            mx[i, 2] += sz
        p = nparent[i]
        if p >= 0:
            msum[p] += msum[i]
            mx[p, 0] += mx[i, 0]
            mx[p, 1] += mx[i, 1]
            mx[p, 2] += mx[i, 2]
    inv_t2 = 1.0 / (theta * theta)
    for i in range(nn):
        half = root_half / (2.0 ** nlevel[i])
        if msum[i] > 0.0:
            for k in range(3):
                ndata[i, k] = mx[i, k] / msum[i]
        else:
            for k in range(3):
                ndata[i, k] = ncen[i, k]
        ndata[i, C_MASS] = msum[i]
        ndata[i, C_CX] = ncen[i, 0]
        ndata[i, C_CY] = ncen[i, 1]
        ndata[i, C_CZ] = ncen[i, 2]
        ndata[i, C_HALF] = half
        ndata[i, C_ROPEN2] = 4.0 * half * half * inv_t2   # open if d^2 <= (s/theta)^2
        ndata[i, C_BOX] = 1.2 * half                       # open if inside enlarged cube
    # traceless quadrupole about each node's centre of mass (parallel-axis theorem upward)
    q = np.zeros((nn, 6))
    for i in range(nn - 1, -1, -1):
        X = ndata[i, 0]
        Y = ndata[i, 1]
        Z = ndata[i, 2]
        if nleaf[i] == 1:
            for j in range(nstart[i], nend[i]):
                mj = mass_s[j]
                dx = pos_s[j, 0] - X
                dy = pos_s[j, 1] - Y
                dz = pos_s[j, 2] - Z
                r2 = dx * dx + dy * dy + dz * dz
                q[i, 0] += mj * (3 * dx * dx - r2)
                q[i, 1] += mj * (3 * dy * dy - r2)
                q[i, 2] += mj * (3 * dz * dz - r2)
                q[i, 3] += mj * 3 * dx * dy
                q[i, 4] += mj * 3 * dx * dz
                q[i, 5] += mj * 3 * dy * dz
        p = nparent[i]
        if p >= 0:
            mi = ndata[i, C_MASS]
            dx = X - ndata[p, 0]
            dy = Y - ndata[p, 1]
            dz = Z - ndata[p, 2]
            r2 = dx * dx + dy * dy + dz * dz
            q[p, 0] += q[i, 0] + mi * (3 * dx * dx - r2)
            q[p, 1] += q[i, 1] + mi * (3 * dy * dy - r2)
            q[p, 2] += q[i, 2] + mi * (3 * dz * dz - r2)
            q[p, 3] += q[i, 3] + mi * 3 * dx * dy
            q[p, 4] += q[i, 4] + mi * 3 * dx * dz
            q[p, 5] += q[i, 5] + mi * 3 * dy * dz
    for i in range(nn):
        for k in range(6):
            ndata[i, C_QXX + k] = q[i, k]


@njit(cache=True, inline="always", fastmath=True)
def _node_term(ndata, node, dx, dy, dz, r2, eps2, quad):
    """Field of an accepted node at offset (dx, dy, dz) = com - x_target.

    Returns (ax, ay, az, phi) without the factor G."""
    inv = 1.0 / np.sqrt(r2 + eps2)
    inv2 = inv * inv
    inv3 = inv * inv2
    m = ndata[node, C_MASS]
    ax = m * inv3 * dx
    ay = m * inv3 * dy
    az = m * inv3 * dz
    p = -m * inv
    if quad:
        qx = ndata[node, C_QXX] * dx + ndata[node, C_QXY] * dy + ndata[node, C_QXZ] * dz
        qy = ndata[node, C_QXY] * dx + ndata[node, C_QYY] * dy + ndata[node, C_QYZ] * dz
        qz = ndata[node, C_QXZ] * dx + ndata[node, C_QYZ] * dy + ndata[node, C_QZZ] * dz
        rqr = dx * qx + dy * qy + dz * qz
        inv5 = inv3 * inv2
        inv7 = inv5 * inv2
        c = 2.5 * rqr * inv7
        ax += -inv5 * qx + c * dx
        ay += -inv5 * qy + c * dy
        az += -inv5 * qz + c * dz
        p -= 0.5 * rqr * inv5
    return ax, ay, az, p


@njit(parallel=True, cache=True, fastmath=True)
def _walk(pos_s, mass_s, nn, nnext, nleaf, nstart, nend, ndata, eps2, G, quad, acc, pot, nint):
    n = pos_s.shape[0]
    for i in prange(n):
        xi = pos_s[i, 0]
        yi = pos_s[i, 1]
        zi = pos_s[i, 2]
        ax = 0.0
        ay = 0.0
        az = 0.0
        p = 0.0
        cnt = 0
        node = 0
        while node < nn:
            dx = ndata[node, C_COMX] - xi
            dy = ndata[node, C_COMY] - yi
            dz = ndata[node, C_COMZ] - zi
            r2 = dx * dx + dy * dy + dz * dz
            b = ndata[node, C_BOX]
            inside = (abs(ndata[node, C_CX] - xi) < b and
                      abs(ndata[node, C_CY] - yi) < b and
                      abs(ndata[node, C_CZ] - zi) < b)
            if (not inside) and r2 > ndata[node, C_ROPEN2]:
                tx, ty, tz, tp = _node_term(ndata, node, dx, dy, dz, r2, eps2, quad)
                ax += tx
                ay += ty
                az += tz
                p += tp
                cnt += 1
                node = nnext[node]
            elif nleaf[node] == 1:
                for j in range(nstart[node], nend[node]):
                    if j == i:
                        continue
                    ex = pos_s[j, 0] - xi
                    ey = pos_s[j, 1] - yi
                    ez = pos_s[j, 2] - zi
                    inv = 1.0 / np.sqrt(ex * ex + ey * ey + ez * ez + eps2)
                    mj = mass_s[j]
                    mi3 = mj * inv * inv * inv
                    ax += mi3 * ex
                    ay += mi3 * ey
                    az += mi3 * ez
                    p -= mj * inv
                    cnt += 1
                node = nnext[node]
            else:
                node += 1
        acc[i, 0] = G * ax
        acc[i, 1] = G * ay
        acc[i, 2] = G * az
        pot[i] = G * p
        nint[i] = cnt


@njit(cache=True, fastmath=True)
def _walk_record(i, pos_s, mass_s, nn, nnext, nleaf, nstart, nend, ndata, eps2, G, quad):
    """Same walk as `_walk` for one target, recording every decision.

    status[node]: 0 = never reached, 1 = accepted as monopole,
                  2 = opened leaf (summed directly), 3 = opened internal node.
    """
    status = np.zeros(nn, np.int8)
    xi = pos_s[i, 0]
    yi = pos_s[i, 1]
    zi = pos_s[i, 2]
    ax = 0.0
    ay = 0.0
    az = 0.0
    p = 0.0
    node = 0
    while node < nn:
        dx = ndata[node, C_COMX] - xi
        dy = ndata[node, C_COMY] - yi
        dz = ndata[node, C_COMZ] - zi
        r2 = dx * dx + dy * dy + dz * dz
        b = ndata[node, C_BOX]
        inside = (abs(ndata[node, C_CX] - xi) < b and
                  abs(ndata[node, C_CY] - yi) < b and
                  abs(ndata[node, C_CZ] - zi) < b)
        if (not inside) and r2 > ndata[node, C_ROPEN2]:
            tx, ty, tz, tp = _node_term(ndata, node, dx, dy, dz, r2, eps2, quad)
            ax += tx
            ay += ty
            az += tz
            p += tp
            status[node] = 1
            node = nnext[node]
        elif nleaf[node] == 1:
            for j in range(nstart[node], nend[node]):
                if j == i:
                    continue
                ex = pos_s[j, 0] - xi
                ey = pos_s[j, 1] - yi
                ez = pos_s[j, 2] - zi
                inv = 1.0 / np.sqrt(ex * ex + ey * ey + ez * ez + eps2)
                mj = mass_s[j]
                mi3 = mj * inv * inv * inv
                ax += mi3 * ex
                ay += mi3 * ey
                az += mi3 * ez
                p -= mj * inv
            status[node] = 2
            node = nnext[node]
        else:
            status[node] = 3
            node += 1
    out = np.empty(4)
    out[0] = G * ax
    out[1] = G * ay
    out[2] = G * az
    out[3] = G * p
    return status, out


class Octree:
    """Barnes-Hut octree built from a particle set.

    Parameters
    ----------
    pos : (N, 3) float64 positions
    mass : (N,) float64 masses
    theta : opening angle (default 0.6)
    leaf_size : maximum particles per leaf (default 8)
    quadrupole : include node quadrupole moments (default True)
    """

    def __init__(self, pos, mass, theta=0.6, leaf_size=8, quadrupole=True):
        pos = np.ascontiguousarray(pos, dtype=np.float64)
        mass = np.ascontiguousarray(mass, dtype=np.float64)
        n = pos.shape[0]
        self.n = n
        self.theta = float(theta)
        self.leaf_size = int(leaf_size)
        self.quadrupole = bool(quadrupole)
        lo = pos.min(axis=0)
        hi = pos.max(axis=0)
        center = 0.5 * (lo + hi)
        half = 0.5 * float(np.max(hi - lo))
        half = half * (1.0 + 1e-6) + 1e-12
        self.root_center = center
        self.root_half = half
        corner = center - half
        cell = 2.0 * half / (1 << MAXLEV)
        keys = np.empty(n, np.int64)
        ixyz = np.empty((n, 3), np.int64)
        _morton(pos, corner, 1.0 / cell, keys, ixyz)
        order = np.argsort(keys, kind="stable")
        self.order = order
        keys_s = keys[order]
        ixyz_s = ixyz[order]
        self.pos_s = np.ascontiguousarray(pos[order])
        self.mass_s = np.ascontiguousarray(mass[order])

        max_nodes = 2 * n + 16
        nstart = np.empty(max_nodes, np.int64)
        nend = np.empty(max_nodes, np.int64)
        nlevel = np.empty(max_nodes, np.int64)
        nparent = np.empty(max_nodes, np.int64)
        nleaf = np.empty(max_nodes, np.int8)
        ncen = np.empty((max_nodes, 3))
        nn = _build(keys_s, ixyz_s, self.leaf_size, corner, cell,
                    nstart, nend, nlevel, nparent, nleaf, ncen)
        if nn < 0:
            raise RuntimeError("octree node buffer overflow")
        self.nn = nn
        self.nstart = nstart[:nn].copy()
        self.nend = nend[:nn].copy()
        self.nlevel = nlevel[:nn].copy()
        self.nparent = nparent[:nn].copy()
        self.nleaf = nleaf[:nn].copy()
        ncen = ncen[:nn].copy()
        self.nnext = np.empty(nn, np.int64)
        self.ndata = np.empty((nn, NCOL))
        _finish(nn, self.nparent, self.nleaf, self.nstart, self.nend, self.nlevel, ncen,
                self.pos_s, self.mass_s, half, self.theta, self.nnext, self.ndata)

    # ------------------------------------------------------------------ forces
    def accel(self, eps, G, return_counts=False):
        """Accelerations and potentials for all particles, in the original order."""
        n = self.n
        acc_s = np.empty((n, 3))
        pot_s = np.empty(n)
        nint = np.empty(n, np.int64)
        _walk(self.pos_s, self.mass_s, self.nn, self.nnext, self.nleaf, self.nstart,
              self.nend, self.ndata, float(eps) ** 2, float(G), self.quadrupole,
              acc_s, pot_s, nint)
        acc = np.empty_like(acc_s)
        pot = np.empty_like(pot_s)
        acc[self.order] = acc_s
        pot[self.order] = pot_s
        if return_counts:
            cnt = np.empty_like(nint)
            cnt[self.order] = nint
            return acc, pot, cnt
        return acc, pot

    def walk_record(self, particle_index, eps, G):
        """Record the walk for one particle (index in the *original* ordering).

        Returns (status, acc, pot) where status[node] is 0 unvisited, 1 accepted,
        2 opened leaf, 3 opened internal node.  Used for the Barnes-Hut visual; tests
        check that it reproduces the production force exactly.
        """
        inv = np.empty(self.n, np.int64)
        inv[self.order] = np.arange(self.n)
        i_s = int(inv[particle_index])
        status, out = _walk_record(i_s, self.pos_s, self.mass_s, self.nn, self.nnext,
                                   self.nleaf, self.nstart, self.nend, self.ndata,
                                   float(eps) ** 2, float(G), self.quadrupole)
        return status, out[:3].copy(), float(out[3])

    # ------------------------------------------------------------ inspection
    def node_table(self):
        """Geometry of every node, for visualisation."""
        return {
            "center": self.ndata[:, C_CX:C_CZ + 1].copy(),
            "half": self.ndata[:, C_HALF].copy(),
            "com": self.ndata[:, C_COMX:C_COMZ + 1].copy(),
            "mass": self.ndata[:, C_MASS].copy(),
            "level": self.nlevel.copy(),
            "is_leaf": self.nleaf.astype(bool),
            "parent": self.nparent.copy(),
            "count": (self.nend - self.nstart).copy(),
            "start": self.nstart.copy(),
            "end": self.nend.copy(),
        }


def tree_accel(pos, mass, eps, G, theta=0.6, leaf_size=8, quadrupole=True):
    t = Octree(pos, mass, theta=theta, leaf_size=leaf_size, quadrupole=quadrupole)
    return t.accel(eps, G)
