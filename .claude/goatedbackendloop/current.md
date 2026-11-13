# Current task
Status: done
Request: Make the 100k collision render crisp and clear (user: "still very fuzzy i cant see great"), then implement the Phase 2 fix (disk heating) and continue Phase 2.
## Brief
- Outcome: simulation frames where structure (spiral arms, bridges, tails, cores) reads sharply at 1080x1350.
- Diagnosis: (1) every particle drawn as a 2-4 px soft kernel -> continuous fog, nothing sharp; (2) low black point (6e5 Msun/kpc^2) shows faint outer disk as haze; (3) bloom adds halo; (4) physics: disks thicken by two-body heating, remnant is genuinely smooth.
- Approach: hybrid star rendering. Layer 1: every star particle as a crisp ~1 px point (star-field texture, gives the eye detail). Layer 2: the adaptive-kernel diffuse light at reduced weight (body, continuity). Raise black point, cut bloom to a tight core glow, mild local-contrast ("clarity"). Presentation only; positions untouched.
- Tradeoff: crisp points show particle graininess (honest about N=100k); smooth light hides it but looks soft.
- Success: user picks a still variant; full clip re-rendered in that look passes render.verify; fine structure visible at 100% zoom.
- Then Phase 2: isolated MW model at final N for 4 Gyr -> choose disk-heating fix (particle allocation / DM softening / dt) -> sources + params -> MW-M31 run.
## Progress
- [x] point layer + clarity in renderer
- [x] still comparison (3 variants, 2 moments) shown to user, pick -> B (D-04)
- [x] re-render 100k clip in look B; render.verify ALL PASS (min re-render PSNR 41.4 dB); consecutive frames coherent (no twinkle)
- [ ] Phase 2
## Observations
- 2026-11-13 user rejected two clips on look; switching to stills-first (L-01)
- 2026-11-13 stills comparison -> user picked B in one round, no re-render wasted (L-01 helped)
- 2026-11-13 fine point detail raises H.264 bitrate (20 s clip = 36 MB at crf 14); fine for masters, revisit for LinkedIn export
## Handoff
