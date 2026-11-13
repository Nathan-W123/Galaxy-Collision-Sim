"""Initial conditions for disk galaxies and two-galaxy encounters.

Galaxy model
------------
* Dark-matter halo: Hernquist (1990) sphere, truncated at ``r_max``.
* Bulge: Hernquist sphere, truncated at ``r_max``.
* Stellar disk: exponential in R, sech^2 in z:
      rho(R, z) = M_d / (4 pi h^2 z0) exp(-R/h) sech^2(z/z0)

Component ``mass`` is the mass actually realised by the particles (inside the
truncation radius); the analytic profile is normalised so that its mass inside the
truncation radius equals it.

Velocities
----------
* Halo and bulge: isotropic distribution functions from Eddington's formula, computed
  numerically for each component in the *total* spherically averaged potential (disk
  approximated by its spherically enclosed mass).  Speeds are sampled by inverse CDF.
  Speeds are capped so that every particle is bound in the truncated system.  The small
  random net momentum and rigid rotation left by finite sampling are removed.
* Disk: mean rotation from the midplane circular speed and asymmetric-drift
  correction; Gaussian dispersions with
      sigma_R = Q * 3.36 G Sigma / kappa          (Toomre Q, default 1.5, at every R)
      sigma_phi^2 = sigma_R^2 kappa^2 / (4 Omega^2) (epicyclic approximation)
      sigma_z^2 = pi G Sigma z0                     (isothermal sheet)
  The midplane circular speed uses the enclosed mass of the halo and bulge (exact for
  spheres).  For the disk's own contribution, ``vc_method`` selects
      "freeman"        - exact thin exponential disk (Freeman 1970), default
      "enclosed_mass"  - G M_disk(<R) / R, the spherical approximation; it
                         under-estimates the disk term by ~20 % near R = 2.2 h.
"""
import numpy as np
from scipy import special

from .io import PTYPE_BULGE, PTYPE_DISK, PTYPE_HALO
from .units import G as G_DEFAULT


# ----------------------------------------------------------------------- profiles
def hernquist_mass_frac(r, a):
    return r * r / (r + a) ** 2


def hernquist_rho(r, M, a):
    return M * a / (2.0 * np.pi * r * (r + a) ** 3)


def hernquist_drho_dr(r, M, a):
    return -hernquist_rho(r, M, a) * (1.0 / r + 3.0 / (r + a))


def disk_mass_frac(R, h):
    x = R / h
    return 1.0 - (1.0 + x) * np.exp(-x)


def hernquist_df_analytic(E, M, a, G):
    """Isotropic Hernquist (1990) distribution function f(E), E = relative energy."""
    vg = np.sqrt(G * M / a)
    q = np.sqrt(a * E / (G * M))
    pre = M / (8.0 * np.sqrt(2.0) * np.pi ** 3 * a ** 3 * vg ** 3)
    return pre * (1 - q * q) ** -2.5 * (3 * np.arcsin(q) + q * np.sqrt(1 - q * q)
                                         * (1 - 2 * q * q) * (8 * q ** 4 - 8 * q * q - 3))


class Component:
    def __init__(self, kind, cfg):
        self.kind = kind
        self.mass = float(cfg.get("mass", 0.0))
        self.n = int(cfg.get("n", 0))
        if kind in ("halo", "bulge"):
            self.a = float(cfg["scale_radius"])
            self.r_max = float(cfg["r_max"])
            self.frac_trunc = hernquist_mass_frac(self.r_max, self.a)
        else:
            self.h = float(cfg["scale_length"])
            self.z0 = float(cfg["scale_height"])
            self.R_max = float(cfg.get("r_max", 8.0 * self.h))
            self.z_max = float(cfg.get("z_max", 6.0 * self.z0))
            self.Q = float(cfg.get("toomre_q", 1.5))
            self.frac_trunc = disk_mass_frac(self.R_max, self.h) * np.tanh(self.z_max / self.z0)
        # analytic profile normalisation (mass of the untruncated profile)
        self.M_total = self.mass / self.frac_trunc if self.mass > 0 else 0.0


class GalaxyModel:
    def __init__(self, cfg, G=G_DEFAULT):
        self.G = float(G)
        self.halo = Component("halo", cfg["halo"])
        self.bulge = Component("bulge", cfg["bulge"]) if cfg.get("bulge") else None
        self.disk = Component("disk", cfg["disk"])
        self.vc_method = cfg.get("vc_method", "freeman")
        if self.vc_method not in ("freeman", "enclosed_mass"):
            raise ValueError(self.vc_method)

    # spherical quantities (disk approximated by its spherically enclosed mass)
    def spherical_components(self):
        out = [self.halo]
        if self.bulge is not None and self.bulge.mass > 0:
            out.append(self.bulge)
        return out

    def menc(self, r):
        m = np.zeros_like(r, dtype=float)
        for c in self.spherical_components():
            m += c.M_total * hernquist_mass_frac(r, c.a)
        m += self.disk.M_total * disk_mass_frac(r, self.disk.h)
        return m

    def psi(self, r):
        """Relative potential psi = -Phi of the untruncated, spherically averaged model."""
        G = self.G
        p = np.zeros_like(r, dtype=float)
        for c in self.spherical_components():
            p += G * c.M_total / (r + c.a)
        d = self.disk
        p += G * d.M_total * (-np.expm1(-r / d.h)) / r
        return p

    def truncation_offset(self):
        """Potential of the mass outside the truncation radii (seen as a constant inside)."""
        G = self.G
        C = 0.0
        for c in self.spherical_components():
            C += G * c.M_total * c.a / (c.r_max + c.a) ** 2
        d = self.disk
        C += G * d.M_total * np.exp(-d.R_max / d.h) / d.h
        return C

    # midplane disk kinematics
    def vc2_midplane(self, R):
        G = self.G
        v2 = np.zeros_like(R, dtype=float)
        for c in self.spherical_components():
            v2 += G * c.M_total * hernquist_mass_frac(R, c.a) / R
        d = self.disk
        if self.vc_method == "freeman":
            y = R / (2.0 * d.h)
            sigma0 = d.M_total / (2.0 * np.pi * d.h ** 2)
            bess = special.i0e(y) * special.k0e(y) - special.i1e(y) * special.k1e(y)
            v2 += 4.0 * np.pi * G * sigma0 * d.h * y * y * bess
        else:
            v2 += G * d.M_total * disk_mass_frac(R, d.h) / R
        return v2

    def disk_kinematics(self, R):
        """Return dict of v_c, kappa, Omega, Sigma, sigma_R, sigma_phi, sigma_z, vphi_mean on R."""
        G = self.G
        d = self.disk
        Rg = np.geomspace(1e-3 * d.h, 1.2 * d.R_max, 4000)
        vc2 = self.vc2_midplane(Rg)
        om2 = vc2 / Rg ** 2
        dom2 = np.gradient(om2, Rg)
        kap2 = Rg * dom2 + 4.0 * om2
        kap = np.sqrt(np.maximum(kap2, 1e-30))
        Sig = d.M_total / (2.0 * np.pi * d.h ** 2) * np.exp(-Rg / d.h)
        sR = d.Q * 3.36 * G * Sig / kap
        sR = np.minimum(sR, 0.7 * np.sqrt(vc2))  # sanity cap at very small R
        sz = np.sqrt(np.pi * G * Sig * d.z0)
        sphi2 = sR ** 2 * kap2 / (4.0 * om2)
        dln = np.gradient(np.log(Sig * sR ** 2), np.log(Rg))
        vphi2 = vc2 + sR ** 2 * (1.0 - kap2 / (4.0 * om2) + dln)
        vphi = np.sqrt(np.maximum(vphi2, 0.0))
        out = {}
        for name, arr in (("vc", np.sqrt(vc2)), ("kappa", kap), ("Omega", np.sqrt(om2)),
                          ("Sigma", Sig), ("sigma_R", sR), ("sigma_phi", np.sqrt(sphi2)),
                          ("sigma_z", sz), ("vphi_mean", vphi)):
            out[name] = np.interp(R, Rg, arr)
        out["Q"] = out["sigma_R"] * out["kappa"] / (3.36 * G * out["Sigma"])
        return out


# ------------------------------------------------------------------- Eddington
class EddingtonDF:
    """Numerical isotropic DF of one Hernquist component in the model's total potential."""

    def __init__(self, model, comp, n_r=4000, n_e=2000, n_quad=256):
        G = model.G
        r_lo = 1e-5 * min(model.halo.a, model.disk.h,
                          *(c.a for c in model.spherical_components()))
        r_hi = 1e3 * max(c.r_max for c in model.spherical_components())
        r = np.geomspace(r_lo, r_hi, n_r)
        psi = model.psi(r)
        dpsi_dr = -G * model.menc(r) / r ** 2
        g = hernquist_drho_dr(r, comp.M_total, comp.a) / dpsi_dr      # d rho / d psi > 0
        psi_inc = psi[::-1]
        lpsi = np.log(psi_inc)
        lg = np.log(g[::-1])
        self.psi_min = psi_inc[0]
        self.psi_max = psi_inc[-1]

        def g_of(p):
            out = np.zeros_like(p)
            ok = p > self.psi_min
            out[ok] = np.exp(np.interp(np.log(p[ok]), lpsi, lg))
            return out

        # log-spaced in E at low energy and in (psi_max - E) near the most bound end
        lo = np.geomspace(self.psi_min * 1.0001, 0.5 * self.psi_max, n_e // 2)
        hi = self.psi_max - np.geomspace(1e-7 * self.psi_max, 0.5 * self.psi_max, n_e // 2)
        E = np.unique(np.concatenate([lo, hi]))
        s, w = np.polynomial.legendre.leggauss(n_quad)
        s = 0.5 * (s + 1.0)
        w = 0.5 * w
        # F(E) = int_0^E g(psi) dpsi / sqrt(E - psi);  psi = E (1 - s^2)
        P = E[:, None] * (1.0 - s[None, :] ** 2)
        F = 2.0 * np.sqrt(E) * (g_of(P.ravel()).reshape(P.shape) @ w)
        f = np.gradient(F, E) / (np.sqrt(8.0) * np.pi ** 2)
        f = np.maximum(f, 0.0)
        self.E = E
        self.f = f
        self.lE = np.log(E)
        self.lf = np.log(np.maximum(f, 1e-300))
        self.fmax_cum = np.maximum.accumulate(f)

    def __call__(self, E):
        E = np.asarray(E, dtype=float)
        out = np.exp(np.interp(np.log(np.clip(E, self.E[0], self.E[-1])), self.lE, self.lf))
        return np.where(E <= 0, 0.0, out)

    def fmax_below(self, E):
        return np.interp(E, self.E, self.fmax_cum)


# ---------------------------------------------------------------------- sampling
def _random_unit_vectors(rng, n):
    v = rng.normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1)[:, None]


def sample_hernquist_positions(rng, comp):
    n = comp.n
    u = rng.random(n) * comp.frac_trunc          # enclosed-mass fraction within r_max
    su = np.sqrt(u)
    r = comp.a * su / (1.0 - su)
    return r[:, None] * _random_unit_vectors(rng, n), r


def sample_isotropic_velocities(rng, model, df, r, n_grid=320, chunk=20000):
    """Speeds from p(v) ~ v^2 f(psi - v^2/2) on [0, v_max] by inverse-CDF sampling on a
    per-particle grid (quadratically spaced, dense at low v where the distribution of a
    particle near the cusp centre is sharply peaked); isotropic directions.

    v_max = sqrt(2 (psi - C)) keeps every particle bound in the truncated system."""
    psi = model.psi(r)
    C = model.truncation_offset()
    vmax = np.sqrt(2.0 * np.maximum(psi - C, 0.0))
    s = np.linspace(0.0, 1.0, n_grid) ** 2
    u = rng.random(r.size)
    v = np.empty_like(r)
    for a in range(0, r.size, chunk):
        b = min(a + chunk, r.size)
        vg = vmax[a:b, None] * s[None, :]
        pdf = vg * vg * df(psi[a:b, None] - 0.5 * vg * vg)
        cdf = np.concatenate([np.zeros((b - a, 1)),
                              np.cumsum(0.5 * (pdf[:, 1:] + pdf[:, :-1]) * np.diff(vg, axis=1), axis=1)],
                             axis=1)
        cdf /= cdf[:, -1:]
        k = np.clip((cdf < u[a:b, None]).sum(axis=1) - 1, 0, n_grid - 2)
        rows = np.arange(b - a)
        c0 = cdf[rows, k]
        c1 = cdf[rows, k + 1]
        f = np.where(c1 > c0, (u[a:b] - c0) / np.where(c1 > c0, c1 - c0, 1.0), 0.0)
        v[a:b] = vg[rows, k] + f * (vg[rows, k + 1] - vg[rows, k])
    return v[:, None] * _random_unit_vectors(rng, r.size)


def sample_disk(rng, model):
    d = model.disk
    n = d.n
    R = np.empty(0)
    while R.size < n:
        x = rng.gamma(2.0, d.h, size=2 * (n - R.size) + 16)
        R = np.concatenate([R, x[x < d.R_max]])
    R = R[:n]
    z = np.empty(0)
    while z.size < n:
        x = d.z0 * np.arctanh(2.0 * rng.random(2 * (n - z.size) + 16) - 1.0)
        z = np.concatenate([z, x[np.abs(x) < d.z_max]])
    z = z[:n]
    ph = rng.random(n) * 2.0 * np.pi
    kin = model.disk_kinematics(R)
    vR = rng.normal(size=n) * kin["sigma_R"]
    vphi = kin["vphi_mean"] + rng.normal(size=n) * kin["sigma_phi"]
    vz = rng.normal(size=n) * kin["sigma_z"]
    c, s = np.cos(ph), np.sin(ph)
    pos = np.column_stack([R * c, R * s, z])
    vel = np.column_stack([vR * c - vphi * s, vR * s + vphi * c, vz])
    return pos, vel


def rotation_to(axis):
    """Rotation matrix taking +z to the unit vector ``axis`` (Rodrigues)."""
    a = np.asarray(axis, dtype=float)
    a = a / np.linalg.norm(a)
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(z, a)
    c = float(np.dot(z, a))
    if np.linalg.norm(v) < 1e-14:
        return np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))


def spin_axis_from_cfg(cfg):
    if "spin" in cfg:
        return np.asarray(cfg["spin"], dtype=float)
    if "spin_angles" in cfg:
        th = np.radians(float(cfg["spin_angles"]["theta_deg"]))
        ph = np.radians(float(cfg["spin_angles"]["phi_deg"]))
        return np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])
    return np.array([0.0, 0.0, 1.0])


def remove_net_rotation(pos, vel, mass):
    """Remove the spurious net momentum and rigid rotation that finite sampling gives an
    isotropic, non-rotating component: v -> v - <v> - omega x x with omega = I^-1 L.

    With N ~ 1e3-1e4 halo particles the random net angular momentum is comparable to the
    disk's, and a live halo spinning about a random axis slowly tilts the disk.  The
    correction is tiny per particle (< 1 km/s here)."""
    m = mass[:, None]
    vel = vel - (m * vel).sum(0) / mass.sum()
    x = pos - (m * pos).sum(0) / mass.sum()
    L = (m * np.cross(x, vel)).sum(0)
    r2 = np.einsum("ij,ij->i", x, x)
    I = (mass * r2).sum() * np.eye(3) - np.einsum("i,ij,ik->jk", mass, x, x)
    omega = np.linalg.solve(I, L)
    return vel - np.cross(omega, x)


def make_galaxy(cfg, rng, G=G_DEFAULT):
    """Particles of one galaxy, centred on its own centre of mass, at rest."""
    model = GalaxyModel(cfg, G)
    pos_l, vel_l, m_l, t_l = [], [], [], []
    for comp, ptype in ((model.halo, PTYPE_HALO), (model.bulge, PTYPE_BULGE)):
        if comp is None or comp.n == 0 or comp.mass == 0:
            continue
        df = EddingtonDF(model, comp)
        p, r = sample_hernquist_positions(rng, comp)
        v = sample_isotropic_velocities(rng, model, df, r)
        v = remove_net_rotation(p, v, np.full(comp.n, comp.mass / comp.n))
        pos_l.append(p)
        vel_l.append(v)
        m_l.append(np.full(comp.n, comp.mass / comp.n))
        t_l.append(np.full(comp.n, ptype, np.uint8))
    if model.disk.n > 0:
        p, v = sample_disk(rng, model)
        R = rotation_to(spin_axis_from_cfg(cfg))
        pos_l.append(p @ R.T)
        vel_l.append(v @ R.T)
        m_l.append(np.full(model.disk.n, model.disk.mass / model.disk.n))
        t_l.append(np.full(model.disk.n, PTYPE_DISK, np.uint8))
    pos = np.vstack(pos_l)
    vel = np.vstack(vel_l)
    mass = np.concatenate(m_l)
    ptype = np.concatenate(t_l)
    mt = mass.sum()
    pos -= (mass[:, None] * pos).sum(0) / mt
    vel -= (mass[:, None] * vel).sum(0) / mt
    return pos, vel, mass, ptype, model


# --------------------------------------------------------------------- the orbit
def relative_orbit(orbit_cfg, M_total, G=G_DEFAULT):
    """Relative position and velocity of galaxy B with respect to galaxy A."""
    kind = orbit_cfg.get("type", "kepler")
    if kind == "vectors":
        return (np.asarray(orbit_cfg["relative_position_kpc"], float),
                np.asarray(orbit_cfg["relative_velocity_kms"], float))
    if kind == "radial_tangential":
        r0 = float(orbit_cfg["separation_kpc"])
        return (np.array([r0, 0.0, 0.0]),
                np.array([float(orbit_cfg["v_radial_kms"]), float(orbit_cfg["v_tangential_kms"]), 0.0]))
    if kind == "kepler":
        r0 = float(orbit_cfg["separation_kpc"])
        rp = float(orbit_cfg["pericenter_kpc"])
        e = float(orbit_cfg.get("eccentricity", 1.0))
        p = rp * (1.0 + e)
        cosnu = (p / r0 - 1.0) / e
        if not -1.0 <= cosnu <= 1.0:
            raise ValueError("separation not reachable on this orbit")
        nu = -np.arccos(cosnu)                       # before pericentre: approaching
        h = np.sqrt(G * M_total / p)
        vr = h * e * np.sin(nu)
        vt = h * (1.0 + e * np.cos(nu))
        rhat = np.array([np.cos(nu), np.sin(nu), 0.0])
        that = np.array([-np.sin(nu), np.cos(nu), 0.0])
        return r0 * rhat, vr * rhat + vt * that
    raise ValueError(kind)


def make_initial_conditions(params, G=G_DEFAULT):
    """Build every particle of the scenario.  Deterministic for a given seed.

    Returns dict with pos, vel, mass, ptype, galaxy, galaxy_names, models.
    """
    seed = int(params["seed"])
    gals = params["galaxies"]
    ss = np.random.SeedSequence(seed)
    rngs = [np.random.default_rng(s) for s in ss.spawn(len(gals))]
    parts = [make_galaxy(g["model"] | {k: g[k] for k in ("spin", "spin_angles") if k in g},
                         rng, G) for g, rng in zip(gals, rngs)]
    names = [g["name"] for g in gals]
    if len(parts) == 1:
        pos, vel, mass, ptype, model = parts[0]
        galaxy = np.zeros(mass.size, np.uint8)
        offset = params.get("galaxies")[0].get("position_kpc")
        if offset is not None:
            pos = pos + np.asarray(offset, float)
        return dict(pos=pos, vel=vel, mass=mass, ptype=ptype, galaxy=galaxy,
                    galaxy_names=names, models=[model])
    if len(parts) != 2:
        raise ValueError("one or two galaxies supported")
    (pA, vA, mA, tA, modA), (pB, vB, mB, tB, modB) = parts
    MA, MB = mA.sum(), mB.sum()
    rel_x, rel_v = relative_orbit(params["orbit"], MA + MB, G)
    M = MA + MB
    pos = np.vstack([pA - (MB / M) * rel_x, pB + (MA / M) * rel_x])
    vel = np.vstack([vA - (MB / M) * rel_v, vB + (MA / M) * rel_v])
    mass = np.concatenate([mA, mB])
    ptype = np.concatenate([tA, tB])
    galaxy = np.concatenate([np.zeros(mA.size, np.uint8), np.ones(mB.size, np.uint8)])
    return dict(pos=pos, vel=vel, mass=mass, ptype=ptype, galaxy=galaxy,
                galaxy_names=names, models=[modA, modB],
                relative_position=rel_x, relative_velocity=rel_v)
