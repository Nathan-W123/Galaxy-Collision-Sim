# Decisions
### D-01 · Quadrupole moments in the Barnes-Hut tree (2026-11-13)
- Decision: accepted nodes contribute monopole + quadrupole; opening criterion stays s/d < theta = 0.6.
- Why: monopole at theta 0.6 gave 0.97 % energy drift over the 3 Gyr collision (limit 1 %); quadrupole gives ~0.2 %.
- Alternatives considered: theta 0.35-0.5 (1.7x+ cost), monopole only.
- Source: recommended at Checkpoint 1; user did not object
- Revisit if: step time becomes the bottleneck for the final run.
### D-02 · Disk circular speed uses the exact Freeman disk term (2026-11-13)
- Decision: vc_method freeman by default; enclosed_mass available.
- Why: pure enclosed-mass approximation under-rotates the disk by ~20 % near 2.2 h.
- Alternatives considered: spherical enclosed-mass (spec wording).
- Source: recommended at Checkpoint 1; user did not object
- Revisit if: user wants strict spec wording.
### D-03 · Preview at final resolution (100k) is the look reference (2026-11-13)
- Decision: judge footage quality on 100k-particle runs; 5k stays the test size.
- Why: 5k cannot look like a galaxy with any renderer (blobs vs blur).
- Source: assumption, user implicitly accepted by reviewing the 100k clip
- Revisit if: user wants 5k previews polished.
### D-04 · Footage look: hybrid crisp stars + smooth light ("B") (2026-11-13)
- Decision: every star particle drawn as a ~1 px point (sigma 0.6 px, gain 1.3, weight 0.9) over the adaptive-kernel light at 0.75 weight; black point 2e6 Msun/kpc^2; clarity 0.6 @ 8 px; tight, weak bloom.
- Why: the smooth-only look read as fuzzy (user, twice); B is crisp while faint tails/bridges stay continuous.
- Alternatives considered: A smooth only (rejected as fuzzy), C star field (faint tails dissolve into dots).
- Source: stated by user (picked B from full-res stills)
- Revisit if: graininess or twinkle shows in motion.
### D-05 · MW-M31 initial conditions: vdM2012 Paper III canonical (2026-11-13)
- Decision: final run uses the Paper III canonical N-body setup and M31 velocity (72.6, -69.7, 50.9) km/s; no Gaia-velocity clip.
- Why: only fully specified source with disks; full collision + merger within 10 Gyr; 5k check reproduced the published timeline (first pericentre 3.72 vs 3.87 Gyr).
- Alternatives considered: vdM2019 Gaia velocity (wide flyby, merger only begins at 10 Gyr); running both.
- Source: stated by user ("2012 only")
- Revisit if: the script needs to show the near-miss future; Sawala 2025's ~50 % odds must be stated on screen/script regardless.
### D-06 · Particle split 55 / 5 / 40 (halo / bulge / disk) of 100k (2026-11-13)
- Decision: `particles: {total: 100000, split: {halo: 0.55, bulge: 0.05, disk: 0.40}}`; equal particle mass per species across both galaxies.
- Why: heating test showed allocation is a weak lever (bars dominate thickening); keeps 45k star particles for the crisp look; 200k@dt=2 fails energy.
- Alternatives considered: 50/10/40, 70/5/25, 200k at dt = 2 Myr.
- Source: recommended and approved
- Revisit if: disks look too thick at the encounter.
### D-07 · Script approval stop before building scenes (2026-11-14)
- Decision: write and fact-check script.md, stop for the user's approval, then build Manim scenes.
- Why: text is cheap to change before animation, expensive after (cf. L-01).
- Alternatives considered: straight to the Checkpoint 3 preview.
- Source: stated by user
- Revisit if: -
### D-08 · CMB scene uses the real Planck 2018 map (2026-11-14)
- Decision: Planck 2018 SMICA CMB map (public, via IRSA) in Mollweide; the bubble-collision disk drawn on top and labelled "illustration".
- Why: real data is more honest and striking; only the disk is illustrative.
- Alternatives considered: synthetic Gaussian sky (whole scene "illustration").
- Source: stated by user
- Revisit if: download/licence problems.
