# Current task
Status: building
Request: Phase 2 with the disk-heating fix ("implement the fix to phase 2"), in the crisp look B.
## Brief
- Outcome: Checkpoint 2 - MW-M31 raw collision clip from the final run, frames_manifest.csv, verify output; sources.md; parameter file; low-res prograde vs retrograde comparison.
- Approach: vdM2012 Paper III canonical N-body setup (only fully specified source with disks); equal per-species particle masses via `particles` budget; coarse 10 Gyr run -> events -> remap -> dense rerun -> render (look B) -> verify.
- Tradeoff: the 2012 velocity gives a full merger in 10 Gyr; the 2019 Gaia velocity gives a wide flyby with the merger only starting at 10 Gyr. Sawala 2025: ~50 % odds either way.
- Success: published timeline reproduced at full resolution; render.verify ALL PASS; energy drift < 1 %.
## Progress
- [x] literature verified (scratchpad/phase2_sources.md -> sources.md)
- [x] heating test (output/logs/heating_report.md): 200k@dt2 fails energy (0.8-1.1 %); halo-heavy split -25 % heating rate; most thickening is bar/spiral dynamics (models bar-unstable, ELK X 0.74-0.88; A2 up to 0.3)
- [x] 5k orbit checks: A first pericentre 3.72 Gyr / 24 kpc (pub. 3.87 / 31), merged ~5.6 Gyr (pub. 5.86); B 4.34 Gyr / 116 kpc (pub. ~4.5 / ~130), merger starts ~10 Gyr
- [x] user: orbit = vdM2012 only (D-05); split 55/5/40 (D-06)
- [x] sources.md (parameter mapping, assumptions, full verification notes)
- [~] coarse run mw_m31_vdm2012_coarse (100k, 10 Gyr, every 20 Myr) - started at commit 3a70b7a, ETA ~80 min
- [~] prograde vs retrograde runs (20k, 1.6 Gyr, shared remap) - running
- [ ] events -> remap (approach ~8 s for the hook, slow first passage + coalescence) -> dense rerun (~80 min) -> render look B -> verify
- [ ] comparison panels render + verify + vstack composite
- [ ] README Phase 2 commands, Checkpoint 2 report
## Observations
- 2026-11-13 heating hypothesis (halo particle noise dominates) only partly right: 2.8x lighter halo particles -> 1.4x lower rate; bars dominate. Testing before committing to 200k saved a 2+ h run that would have failed energy.
## Handoff
