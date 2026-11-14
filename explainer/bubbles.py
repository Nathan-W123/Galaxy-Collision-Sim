"""Toy model of bubble nucleation in an inflating false vacuum (illustration only).

This is NOT a cosmological calculation (no general relativity, no field dynamics, no wall
energetics).  It is a geometric toy that captures the qualitative picture used in the
explainer, and the video labels it "illustration (toy model)":

* Space inflates with scale factor a(t) = exp(H t)  (units H = c = 1 by default).
* Bubbles nucleate at random comoving positions at a constant rate per unit *physical*
  area per unit time, Gamma, i.e. Gamma a(t)^2 per unit comoving area, but only in the
  still-inflating false vacuum (a candidate point inside an existing bubble is rejected).
* Each bubble wall moves outward at a fixed physical speed v, so its comoving radius is

      r(t) = (v / H) (exp(-H t_n) - exp(-H t)),     t >= t_n,

  which tends to (v/H) exp(-H t_n): bubbles born later stay smaller in comoving terms.
* Two bubbles collide when their walls first touch, |x_i - x_j| = r_i(t) + r_j(t), which
  has the closed-form solution

      exp(-H t_c) = (exp(-H t_i) + exp(-H t_j) - H d / v) / 2,

  valid if the right-hand side is positive and t_c >= max(t_i, t_j).

Everything shown in the bubble scene (which circles exist, how big they are at each
moment, when and where they collide) is computed from these formulas -- no keyframes.
"""
import numpy as np


class BubbleUniverse:
    def __init__(self, width, height, gamma, t_end, v=1.0, H=1.0, seed=7, max_bubbles=400):
        self.W, self.H_box = float(width), float(height)
        self.gamma, self.t_end, self.v, self.H = float(gamma), float(t_end), float(v), float(H)
        self.rng = np.random.default_rng(seed)
        self.x = np.zeros((0, 2))
        self.tn = np.zeros(0)
        self._nucleate(max_bubbles)
        self.collisions = self._collisions()

    # ---------------------------------------------------------------- geometry
    def radius(self, t):
        """Comoving radii of all bubbles at time t (0 for bubbles not yet born)."""
        H, v = self.H, self.v
        r = (v / H) * (np.exp(-H * self.tn) - np.exp(-H * t))
        return np.where(t >= self.tn, r, 0.0)

    def inside_any(self, p, t):
        if self.tn.size == 0:
            return False
        r = self.radius(t)
        d = np.linalg.norm(self.x - p, axis=1)
        return bool(np.any((self.tn <= t) & (d < r)))

    # ---------------------------------------------------------------- nucleation
    def _nucleate(self, max_bubbles):
        """Thinning of a non-homogeneous Poisson process with rate Gamma a(t)^2 per comoving
        area; candidates falling inside existing bubbles are rejected (true vacuum)."""
        area = self.W * self.H_box
        lam_max = self.gamma * np.exp(2 * self.H * self.t_end) * area
        t = 0.0
        xs, ts = [], []
        while True:
            t += self.rng.exponential(1.0 / lam_max)
            if t > self.t_end or len(ts) >= max_bubbles:
                break
            p = self.rng.random(2) * [self.W, self.H_box]
            accept_rate = np.exp(2 * self.H * t) / np.exp(2 * self.H * self.t_end)
            if self.rng.random() > accept_rate:
                continue
            self.x = np.array(xs) if xs else np.zeros((0, 2))
            self.tn = np.array(ts)
            if self.inside_any(p, t):
                continue
            xs.append(p)
            ts.append(t)
        self.x = np.array(xs) if xs else np.zeros((0, 2))
        self.tn = np.array(ts)

    # ---------------------------------------------------------------- collisions
    def _collisions(self):
        """All wall-wall first contacts (i, j, t_c, contact point), sorted by time."""
        H, v = self.H, self.v
        out = []
        n = self.tn.size
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(self.x[i] - self.x[j])
                rhs = 0.5 * (np.exp(-H * self.tn[i]) + np.exp(-H * self.tn[j]) - H * d / v)
                if rhs <= 0:
                    continue
                tc = -np.log(rhs) / H
                if tc < max(self.tn[i], self.tn[j]) or tc > self.t_end:
                    continue
                ri = (v / H) * (np.exp(-H * self.tn[i]) - rhs)
                p = self.x[i] + (self.x[j] - self.x[i]) * (ri / d)
                out.append((i, j, tc, p))
        out.sort(key=lambda c: c[2])
        return out

    def state(self, t):
        """Everything needed to draw time t: centres, radii, alive mask, collisions so far."""
        r = self.radius(t)
        alive = self.tn <= t
        hits = [c for c in self.collisions if c[2] <= t]
        return self.x, r, alive, hits
