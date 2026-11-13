"""Barnes-Hut forces agree with direct summation."""
import numpy as np
import pytest

from nbody.direct import direct_accel
from nbody.ics import make_initial_conditions
from nbody.tree import Octree
from nbody.units import G

EPS = 0.2


@pytest.fixture(scope="module")
def merging_pair():
    """Two test galaxies 30 kpc apart (overlapping halos), 20k particles."""
    import copy
    from conftest import load_yaml
    p = copy.deepcopy(load_yaml("test_collision_5k.yaml"))
    for g in p["galaxies"]:
        m = copy.deepcopy(g["model"])
        m["halo"]["n"], m["bulge"]["n"], m["disk"]["n"] = 5000, 1000, 4000
        g["model"] = m
    p["orbit"]["separation_kpc"] = 30.0
    ics = make_initial_conditions(p)
    acc_d, pot_d = direct_accel(ics["pos"], ics["mass"], EPS, G)
    return ics["pos"], ics["mass"], acc_d, pot_d


def rel_err(acc, acc_ref):
    return np.linalg.norm(acc - acc_ref, axis=1) / np.linalg.norm(acc_ref, axis=1)


@pytest.mark.parametrize("quadrupole", [True, False])
def test_median_error_below_one_percent(merging_pair, quadrupole):
    pos, mass, acc_d, pot_d = merging_pair
    acc, pot = Octree(pos, mass, theta=0.6, quadrupole=quadrupole).accel(EPS, G)
    err = rel_err(acc, acc_d)
    print(f"quadrupole={quadrupole}: median {np.median(err):.2e}, 90% {np.percentile(err, 90):.2e}, "
          f"99% {np.percentile(err, 99):.2e}; potential median {np.median(np.abs(pot / pot_d - 1)):.1e}")
    assert np.median(err) < 0.01
    assert np.median(np.abs(pot / pot_d - 1)) < 1e-3


def test_error_decreases_with_theta(merging_pair):
    pos, mass, acc_d, _ = merging_pair
    med = [np.median(rel_err(Octree(pos, mass, theta=t).accel(EPS, G)[0], acc_d))
           for t in (0.3, 0.6, 0.9)]
    print("median errors at theta 0.3/0.6/0.9:", med)
    assert med[0] < med[1] < med[2]


def test_theta_zero_is_exact(merging_pair):
    """With theta -> 0 every node is opened: the tree reduces to direct summation."""
    pos, mass, acc_d, pot_d = merging_pair
    sub = slice(0, 3000)
    p, m = pos[sub], mass[sub]
    acc_t, pot_t = Octree(p, m, theta=1e-6).accel(EPS, G)
    acc_r, pot_r = direct_accel(p, m, EPS, G)
    assert np.max(rel_err(acc_t, acc_r)) < 1e-10


def test_walk_record_reproduces_production_force(merging_pair):
    """The Barnes-Hut visual is drawn from this record, so it must be the real walk."""
    pos, mass, _, _ = merging_pair
    tree = Octree(pos, mass, theta=0.6)
    acc, pot = tree.accel(EPS, G)
    for i in (0, 777, 12345, len(mass) - 1):
        status, a_i, p_i = tree.walk_record(i, EPS, G)
        assert np.array_equal(a_i, acc[i]) and p_i == pot[i]
        assert (status == 1).sum() > 0 and (status == 2).sum() > 0


def test_tree_structure(merging_pair):
    pos, mass, _, _ = merging_pair
    t = Octree(pos, mass, theta=0.6, leaf_size=8)
    nt = t.node_table()
    # every particle in exactly one leaf; leaves respect the bucket size
    leaves = nt["is_leaf"]
    assert nt["count"][leaves].sum() == len(mass)
    assert nt["count"][leaves].max() <= 8
    # root holds all the mass; children sit inside their parent's cube
    assert np.isclose(nt["mass"][0], mass.sum())
    par = nt["parent"][1:]
    d = np.abs(nt["center"][1:] - nt["center"][par]).max(axis=1)
    assert np.all(d + nt["half"][1:] <= nt["half"][par] * (1 + 1e-12))
    assert t.nn <= 2 * len(mass)
