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
