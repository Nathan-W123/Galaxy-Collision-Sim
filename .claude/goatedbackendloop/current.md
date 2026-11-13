# Current task
Status: done
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
- [x] coarse run (82 min, dE 0.53 %): pericentre 3.72 Gyr / 25 kpc, apocentre 4.36 / 137, 2nd passage 5.22, merged 5.56 Gyr
- [x] prograde vs retrograde: both panels verified, stacked composite sent
- [x] remap scenarios/schedules/mw_m31.yaml (1161 frames, 38.7 s); camera from measured separation; framing checked on coarse stills
- [x] dense rerun (commit 6be176a): 1161 snapshots, bitwise identical to coarse at 102 shared steps, dE 0.53 %
- [x] render look B (black point 5e6); scale-bar crossfade defect found on contact sheet and fixed (sequential fade); render.verify ALL PASS (min PSNR 41.5 dB)
- [x] README Phase 2 commands; pytest 31 passed
## Observations
- 2026-11-13 heating hypothesis (halo particle noise dominates) only partly right: 2.8x lighter halo particles -> 1.4x lower rate; bars dominate. Testing before committing to 200k saved a 2+ h run that would have failed energy.
- 2026-11-13 framing stills on the coarse run caught clipped tails (3.9 Gyr) and a frame-filling remnant (5.6 Gyr) before the 80-min dense run was rendered
## Handoff
