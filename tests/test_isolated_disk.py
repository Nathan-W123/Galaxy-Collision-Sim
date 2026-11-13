"""An isolated 5,000-particle galaxy evolved for 2 Gyr stays a stable, rotating disk.

At N = 5,000 the disk is heated by two-body encounters with the (9x heavier) halo
particles, so it thickens (measured heating rate d<z^2>/dt ~ 2.3 kpc^2/Gyr at 5k and
~0.4 kpc^2/Gyr at 25k, i.e. proportional to the halo particle mass), and shot-noise torques
from the halo make its spin axis random-walk by several degrees.  Both are resolution
effects that shrink with N.  The test checks that the disk neither blows up nor
collapses: it stays centrally concentrated, flattened, rotation-dominated, bound, with a
roughly fixed spin axis, and energy is conserved.
"""
import numpy as np
import pytest

from conftest import REPO
from nbody.io import read_static
from nbody.run import run


def disk_metrics(pos, vel, mass, disk):
    c = (mass[disk, None] * pos[disk]).sum(0) / mass[disk].sum()
    vc = (mass[disk, None] * vel[disk]).sum(0) / mass[disk].sum()
    x = pos[disk] - c
    v = vel[disk] - vc
    L = np.cross(x, v).sum(0)
    zhat = L / np.linalg.norm(L)
    z = x @ zhat
    Rv = x - z[:, None] * zhat
    R = np.linalg.norm(Rv, axis=1)
    eR = Rv / R[:, None]
    ephi = np.cross(zhat, eR)
    vR = np.einsum("ij,ij->i", v, eR)
    vphi = np.einsum("ij,ij->i", v, ephi)
    vz = v @ zhat
    sel = R < 2 * np.median(R)
    # rotation vs 1D-averaged random motion, inside two half-mass radii
    sigma1d = np.sqrt((np.var(vR[sel]) + np.var(vphi[sel]) + np.var(vz[sel])) / 3.0)
    r3 = np.linalg.norm(x, axis=1)
    return dict(R_half=np.median(R), R90=np.percentile(R, 90), z_rms=np.sqrt(np.mean(z ** 2)),
                spin=zhat, v_over_sigma=np.mean(vphi[sel]) / sigma1d,
                bound_frac=np.mean(r3 < 50.0))


# limits: (R_half ratio range, max z_rms / R_half, min V/sigma_1D, max spin tilt in deg)
CASES = {
    # 5k: heavy halo particles (1.4e8 Msun, 9x a disk particle) heat the disk by two-body
    # encounters; "no blow-up" = still a centrally concentrated, flattened,
    # rotation-dominated disk whose spin axis stays put to within noise.
    "test_isolated_disk.yaml": ((0.8, 1.35), 0.5, 1.0, 15.0),
    # 25k: 4.6x lighter halo particles -> ~5x lower heating rate; tighter limits.
    "test_isolated_disk_25k.yaml": ((0.9, 1.2), 0.3, 2.0, 10.0),
}


@pytest.mark.parametrize("scenario", [
    "test_isolated_disk.yaml",
    pytest.param("test_isolated_disk_25k.yaml", marks=pytest.mark.slow),
])
def test_isolated_disk_stays_a_disk(tmp_path, scenario):
    from nbody.io import read_checkpoint
    run_dir = run(REPO / "scenarios" / scenario, out_root=tmp_path, quiet=True)
    st = read_static(run_dir / "static.npz")
    disk = st["ptype"] == 1
    ck = sorted((run_dir / "checkpoints").glob("ckpt_*.npz"))
    first = read_checkpoint(ck[0])
    last = read_checkpoint(ck[-1])
    assert int(first["step"]) == 0 and int(last["step"]) == 2000      # 2 Gyr at dt = 1 Myr
    m0 = disk_metrics(first["pos"], first["vel"], st["mass"], disk)
    m1 = disk_metrics(last["pos"], last["vel"], st["mass"], disk)
    fmt = lambda m: ", ".join(f"{k}={np.round(v, 3)}" for k, v in m.items())
    print(f"\n{scenario} N={st['mass'].size}\n  t=0 Gyr: {fmt(m0)}\n  t=2 Gyr: {fmt(m1)}")
    (lo, hi), zmax, vsmin, tilt_max = CASES[scenario]
    tilt = np.degrees(np.arccos(np.clip(np.dot(m0["spin"], m1["spin"]), -1, 1)))
    print(f"  spin-axis tilt after 2 Gyr: {tilt:.1f} deg")
    assert lo < m1["R_half"] / m0["R_half"] < hi              # no expansion / collapse
    assert m1["R90"] / m0["R90"] < 1.4
    assert m1["z_rms"] / m1["R_half"] < zmax                  # still flattened
    assert m1["v_over_sigma"] > vsmin                         # still rotation dominated
    assert tilt < tilt_max
    assert m1["bound_frac"] > 0.99                            # nothing flung out
    log = np.genfromtxt(run_dir / "energy.csv", delimiter=",", names=True)
    drift = np.abs(log["energy"] - log["energy"][0]) / abs(log["energy"][0])
    print(f"  max |dE/E| = {drift.max():.2e}")
    assert drift.max() < 0.01
