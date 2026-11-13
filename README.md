# Galaxy collision explainer

An original explainer video, *"What happens if our universe collided with another one?"*,
built on an N-body engine written from scratch for it.

The galaxy-collision footage is computed, never hand-animated. Every frame is rendered from a
saved simulation snapshot written by the integrator. The renderer writes a
`frames_manifest.csv` that maps each video frame to its snapshot. A verification script
checks every exported clip against those snapshots.

> Scientific framing: an N-body gravity simulation models **galaxies**, not universes.
> The galaxy collision is the opening act. The video then turns to what physicists mean by
> "another universe" (bubble collisions in eternal inflation, and the searches for their
> imprint in the cosmic microwave background). Non-simulated animation is labelled
> "illustration" on screen.

## Status

| Phase | Content | State |
|---|---|---|
| 1 | N-body engine, tests, benchmark, 5k preview | **done (Checkpoint 1)** |
| 2 | Milky Way–Andromeda scenario, final-resolution run, renderer | in progress (Checkpoint 2) |
| 3 | Manim explainer, script, scratch narration | not started |
| 4 | Assembly, captions, LinkedIn deliverables | not started |

## Layout

```
nbody/        engine: units, direct + Barnes-Hut forces, KDK leapfrog, ICs, snapshot I/O, runner
scenarios/    parameter files (physics) and schedules/ (snapshot cadence for an edit)
render/       renderer (reads only snapshot files), camera, overlay, verification script, configs
benchmarks/   step-time benchmark
tests/        pytest suite
explainer/    Manim scenes            (Phase 3)
assembly/     ffmpeg assembly scripts (Phase 4)
output/       git-ignored: runs/, renders/, logs/ (snapshots and video never go in git)
```

## Setup

Python 3.13, ffmpeg 6.1.

```bash
python3 -m venv .venv
```

```bash
. .venv/bin/activate && pip install -r requirements.txt
```

## The engine (`nbody/`)

* **Units:** kpc, km/s, 1e10 Msun; G = 43007.1; time unit = 0.97779 Gyr (`nbody/units.py`).
* **Forces:**
  * Direct summation (`nbody/direct.py`) is the ground truth and is used in tests.
  * The Barnes-Hut octree (`nbody/tree.py`) is used for production. Particles are Morton-sorted,
    the tree is stored in pre-order with a threaded, stack-free walk, and single-child chains
    are collapsed.
  * Opening criterion: a node is accepted when *s/d < θ* (θ = 0.6 by default). *s* is the cell
    side and *d* the distance to the cell's centre of mass. As a safeguard, a cell is always
    opened if the particle lies inside it, enlarged by 20 %, as in GADGET-2.
  * Accepted cells contribute their monopole and, by default, their quadrupole moment. The
    quadrupole does not change which cells are opened. It cuts the median force error from
    0.4 % to 0.1 %, and the energy drift over a full collision from ~1 % to ~0.2 %.
  * Gravity uses Plummer softening.
* **Integrator:** kick-drift-kick leapfrog with a fixed timestep (`nbody/integrator.py`).
  Time is always `step × dt`, computed from the integer step.
* **Initial conditions** (`nbody/ics.py`):
  * Hernquist dark-matter halo and Hernquist bulge. Their velocities come from isotropic
    distribution functions, computed numerically with Eddington's formula in the total
    potential. The numerical DF agrees with the analytic Hernquist DF to better than 0.1 %.
  * Exponential sech² stellar disk. Its rotation comes from the midplane circular speed:
    halo and bulge enclosed mass plus the exact Freeman disk term; `vc_method:
    enclosed_mass` gives the pure spherical approximation. An asymmetric-drift correction is
    applied. Dispersions are set by Toomre *Q* = 1.5 at every radius (σ_R), epicyclic σ_φ, and
    isothermal-sheet σ_z.
  * The two galaxies are placed on a Kepler orbit, or on explicit relative position and
    velocity vectors, with arbitrary disk spin axes.
  * Everything is deterministic for a fixed seed.
* **Output** (`nbody/io.py`, `nbody/schedule.py`):
  * Render snapshots hold float32 positions plus scalars: step, time, energy, momentum.
    They are written only at synchronised full steps, after the closing kick.
  * Per-particle type, galaxy and mass are stored once, in `static.npz`.
  * Full float64 checkpoints are written less often. Resuming from one is bitwise identical
    to an uninterrupted run.
  * Energy and momentum are logged every step in `energy.csv`.
  * Snapshot cadence is set per time window, and every output time must be an exact multiple
    of `dt`, or the run refuses to start.

## Reproduce

All outputs land in the git-ignored `output/` folder.

Run the tests (about 10 minutes; add `-m "not slow"` to skip the 25k disk test):

```bash
. .venv/bin/activate && python -m pytest -v
```

Run the benchmark (step time vs N, wall-time estimate for the final run):

```bash
. .venv/bin/activate && python benchmarks/bench_step.py
```

### Checkpoint-1 previews (test collision at 5,000 and 100,000 particles)

Workflow: coarse run -> find the interesting moments -> choose the time remap (playback
speed in Myr per frame vs. simulation time) -> deterministic rerun that writes exactly
the snapshots the edit needs. Slow motion comes from snapshot cadence, never from
interpolation; speed changes ramp gently because the remap is a staircase of
whole-step cadences.

Run 1, the coarse run (one snapshot every 10 Myr):

```bash
. .venv/bin/activate && python -m nbody.run scenarios/test_collision_5k.yaml --name test_collision_5k_coarse
```

Find the pericentre passages and the merger time:

```bash
. .venv/bin/activate && python -m nbody.analysis output/runs/test_collision_5k_coarse
```

Run 2, the rerun with the edit's time remap (same seed and physics):

```bash
. .venv/bin/activate && python -m nbody.run scenarios/test_collision_5k.yaml --schedule scenarios/schedules/preview_5k.yaml
```

Render from the snapshots, then verify the clip:

```bash
. .venv/bin/activate && python -m render.render render/configs/preview_5k.yaml
```

```bash
. .venv/bin/activate && python -m render.verify output/renders/preview_5k/preview_5k_collision.mp4 --rerender 4
```

The 100,000-particle version is the same, with `scenarios/preview_collision_100k.yaml`,
`scenarios/schedules/preview_100k.yaml` and `render/configs/preview_100k.yaml`. Each
100k run takes about 25 minutes on 4 cores; rendering takes about 6 minutes.

One command that regenerates the 100k preview footage from scratch:

```bash
. .venv/bin/activate && python -m nbody.run scenarios/preview_collision_100k.yaml --schedule scenarios/schedules/preview_100k.yaml && python -m render.render render/configs/preview_100k.yaml && python -m render.verify output/renders/preview_100k/preview_100k_collision.mp4 --rerender 4
```

### Phase 2: Milky Way – Andromeda

The scenario `scenarios/mw_m31_vdm2012.yaml` follows the canonical N-body model of van der
Marel et al. 2012 (Paper III). Every parameter, its source and every assumption are listed in
`sources.md`. The run uses 100,000 particles split 55 / 5 / 40 between dark matter, bulge and
disk, with equal particle masses per species in both galaxies. The softening is 0.2 kpc and
the timestep 1 Myr.

Run 1, the coarse run (10 Gyr, one snapshot every 20 Myr, about 80 minutes):

```bash
. .venv/bin/activate && python -m nbody.run scenarios/mw_m31_vdm2012.yaml --name mw_m31_vdm2012_coarse
```

Find the passages and the merger time (merger: centres within 5 kpc, the vdM2012 definition):

```bash
. .venv/bin/activate && python -m nbody.analysis output/runs/mw_m31_vdm2012_coarse --merge-kpc 5
```

Run 2, the rerun with the edit's time remap, then render and verify:

```bash
. .venv/bin/activate && python -m nbody.run scenarios/mw_m31_vdm2012.yaml --schedule scenarios/schedules/mw_m31.yaml
```

```bash
. .venv/bin/activate && python -m render.render render/configs/mw_m31.yaml
```

```bash
. .venv/bin/activate && python -m render.verify output/renders/mw_m31/mw_m31_collision.mp4 --rerender 4
```

One command that regenerates the collision footage from scratch:

```bash
. .venv/bin/activate && python -m nbody.run scenarios/mw_m31_vdm2012.yaml --schedule scenarios/schedules/mw_m31.yaml && python -m render.render render/configs/mw_m31.yaml && python -m render.verify output/renders/mw_m31/mw_m31_collision.mp4 --rerender 4
```

#### Prograde vs retrograde (low resolution)

Two identical 20,000-particle encounters that differ only in the disks' spin direction:

```bash
. .venv/bin/activate && for k in prograde retrograde; do python -m nbody.run scenarios/compare_$k.yaml --schedule scenarios/schedules/compare.yaml && python -m render.render render/configs/compare_$k.yaml && python -m render.verify output/renders/compare_$k/compare_$k.mp4; done
```

Stack the two verified panels; both use the same step sequence, so frames align:

```bash
ffmpeg -y -i output/renders/compare_prograde/compare_prograde.mp4 -i output/renders/compare_retrograde/compare_retrograde.mp4 -filter_complex "[0:v]pad=1080:676:0:0:color=0x1A1E28[a];[a][1:v]vstack=inputs=2,format=yuv420p[v]" -map "[v]" -c:v libx264 -preset slow -crf 14 -r 30 output/renders/compare/prograde_vs_retrograde.mp4
```

#### Disk-heating test

The particle split was chosen from this test. Its results are in `output/logs/heating_report.md`.

```bash
. .venv/bin/activate && for v in a_100k_default b_100k_halo_heavy c_200k_dt2 d_200k_halo_heavy; do python -m nbody.run scenarios/heating/$v.yaml --out output/heating; done && python benchmarks/heating_report.py output/heating/heating_*
```

## The renderer (`render/`)

The renderer reads only snapshot files. Each frame:

1. Takes the star particles (dark matter hidden).
2. Gives each particle a smoothing length from the distance to its k-th nearest
   neighbour. This is adaptive kernel density estimation, as used to visualise SPH
   simulations: dense disks stay sharp and sparse tidal debris goes soft.
3. Deposits each particle's light as a normalised Gaussian on a 2x supersampled canvas.
   Wide kernels go to coarser levels of an image pyramid.
4. Maps log surface density through a filmic tone curve. Colour comes from the galaxy of
   origin, with paler bulges.
5. Adds bloom from the highlights only, plus dithering against banding.

The camera follows monotone-cubic (PCHIP) curves, so it never stops and starts at
keyframes. The overlay layout (`render/overlay.py`) uses Inter with tabular figures, a
fixed-label scale bar and soft scrims behind the text. Every one of these settings is
presentation; particle positions are never altered or interpolated.

## Provenance

* Each run directory records the parameter-file and schedule-file SHA-256, the git commit
  (with `-dirty` if the tree was modified), the library versions and the initial energy.
* `frames_manifest.csv` has one row per video frame: `frame, snapshot_file, step, time_gyr,
  total_energy, sim_git_commit, param_sha256`.
* `frames_manifest.json` adds the render config and its hash.
* `render.verify` checks each clip against these records:
  * the frame count matches the manifest;
  * every snapshot exists and its own step, time and energy match the manifest;
  * every step was scheduled, and time equals step × dt exactly;
  * time never decreases;
  * energy drift stays within tolerance;
  * the provenance records agree;
  * optionally, re-rendered frames match the video (PSNR).
