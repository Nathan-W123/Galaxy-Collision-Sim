"""Initial-condition sanity checks (not part of the five required tests)."""
import numpy as np

from conftest import load_yaml
from nbody.ics import EddingtonDF, GalaxyModel, hernquist_df_analytic, hernquist_mass_frac, make_initial_conditions
from nbody.units import G


def test_eddington_matches_analytic_hernquist():
    a = 20.0
    cfg = {"halo": {"mass": 50.0 * hernquist_mass_frac(1e6, a), "scale_radius": a, "r_max": 1e6, "n": 1},
           "disk": {"mass": 0.0, "scale_length": 3.0, "scale_height": 0.3, "n": 0}}
    m = GalaxyModel(cfg, G)
    df = EddingtonDF(m, m.halo)
    E = m.psi(np.geomspace(0.05 * a, 50 * a, 30))
    ratio = df(E) / hernquist_df_analytic(E, m.halo.M_total, a, G)
    assert np.max(np.abs(ratio - 1)) < 2e-3


def test_disk_toomre_q_and_masses():
    p = load_yaml("test_collision_5k.yaml")
    model = GalaxyModel(p["galaxies"][0]["model"], G)
    R = np.linspace(1.0, 20.0, 40)
    k = model.disk_kinematics(R)
    assert np.allclose(k["Q"][R > 2.0], 1.5, rtol=1e-4)
    ics = make_initial_conditions(p)
    for g in (0, 1):
        sel = ics["galaxy"] == g
        assert np.isclose(ics["mass"][sel].sum(), 55.0)
    # centre-of-mass frame
    assert np.allclose((ics["mass"][:, None] * ics["pos"]).sum(0), 0, atol=1e-9)
    assert np.allclose((ics["mass"][:, None] * ics["vel"]).sum(0), 0, atol=1e-9)


def test_disk_rotates_about_spin_axis():
    p = load_yaml("test_collision_5k.yaml")
    ics = make_initial_conditions(p)
    for g, axis in ((0, np.array([0, 0, 1.0])), (1, None)):
        sel = (ics["galaxy"] == g) & (ics["ptype"] == 1)
        x = ics["pos"][sel] - ics["pos"][sel].mean(0)
        v = ics["vel"][sel] - ics["vel"][sel].mean(0)
        L = np.cross(x, v).sum(0)
        L /= np.linalg.norm(L)
        if axis is None:
            th, ph = np.radians(45.0), np.radians(30.0)
            axis = np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])
        assert np.dot(L, axis) > 0.999


def test_halo_velocities_match_jeans_equation():
    """Sampled isotropic dispersion matches sigma^2 = (1/rho) int_r^inf rho G M(<r')/r'^2 dr'."""
    from nbody.ics import hernquist_rho, sample_hernquist_positions, sample_isotropic_velocities
    cfg = {"halo": {"mass": 50.0, "scale_radius": 20.0, "r_max": 300.0, "n": 60000},
           "bulge": {"mass": 1.0, "scale_radius": 0.6, "r_max": 10.0, "n": 0},
           "disk": {"mass": 4.0, "scale_length": 3.0, "scale_height": 0.3, "n": 0}}
    m = GalaxyModel(cfg, G)
    df = EddingtonDF(m, m.halo)
    rng = np.random.default_rng(1)
    _, r = sample_hernquist_positions(rng, m.halo)
    v = sample_isotropic_velocities(rng, m, df, r)
    rg = np.geomspace(1e-3, 3e4, 20000)
    rho = hernquist_rho(rg, m.halo.M_total, 20.0)
    g = G * m.menc(rg) / rg ** 2
    for lo, hi in [(1, 3), (5, 10), (10, 20), (30, 60), (80, 150)]:
        sel = (r > lo) & (r < hi)
        rc = np.sqrt(lo * hi)
        msk = rg >= rc
        s2 = np.trapezoid(rho[msk] * g[msk], rg[msk]) / np.interp(rc, rg, rho)
        s1 = np.sqrt(np.sum(v[sel] ** 2, axis=1).mean() / 3)
        assert abs(s1 / np.sqrt(s2) - 1) < 0.03


def test_particle_budget_gives_equal_particle_masses():
    from nbody.ics import allocate_particles
    p = load_yaml("test_collision_5k.yaml")
    p["galaxies"][1]["model"] = {**p["galaxies"][1]["model"],
                                 "halo": {**p["galaxies"][1]["model"]["halo"], "mass": 75.0}}
    p["particles"] = {"total": 10000, "split": {"halo": 0.6, "bulge": 0.05, "disk": 0.35}}
    q = allocate_particles(p)
    nh = [g["model"]["halo"]["n"] for g in q["galaxies"]]
    assert sum(nh) == 6000 and nh == [2400, 3600]
    ics = make_initial_conditions(p)
    for t in (0, 1, 2):
        assert np.ptp(ics["mass"][ics["ptype"] == t]) < 1e-12 * ics["mass"][ics["ptype"] == t].max()
    assert ics["mass"].size == 10000
