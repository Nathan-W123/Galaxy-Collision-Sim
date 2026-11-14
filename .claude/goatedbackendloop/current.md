# Current task
Status: building
Request: Phase 3 - explainer (Manim CE) per the brief; step 1 = fact-checked script for user approval (D-07), then scenes, scratch TTS, Checkpoint 3 low-quality full preview.
## Brief
- Outcome (step 1): script.md - narration ~105 s at ~150 wpm (~260 words) with timestamps, on-screen text, visual notes, and a source for every claim; user approves wording before any scene is built.
- Outcome (step 2): Manim scenes (4:5 1080x1350 first; 16:9 in Phase 4), scratch TTS (offline piper), composited low-quality preview with engine footage cut (not retimed) from the verified MW-M31 clip -> Checkpoint 3.
- Approach: research agent verifies claims (stars don't collide + analogy numbers, Barnes-Hut 1986, eternal inflation / bubble nucleation, Feeney et al. 2011 + Planck-era searches, future-wall claim, Planck map citation). Timing: per-line TTS durations -> timing.json -> scenes wait on it (no manim-voiceover dependency).
- Visual data from computation: Barnes-Hut scene from Octree.walk_record on a real snapshot; bubble scene from a toy nucleation model (de Sitter comoving radii, collisions from geometry), labelled "illustration (toy model)"; CMB = real Planck 2018 SMICA map + illustrative disk labelled "illustration".
- Tradeoff: real Planck map needs healpy + a large download; synthetic would be simpler but less honest/striking.
- Success: every on-screen claim traced to sources.md; user approves script; preview passes render.verify on each sim segment.
## Progress
- [ ] research (agent) -> sources.md additions
- [ ] toolchain: texlive, dvisvgm, manim 0.22.1, piper-tts + voice, healpy, Planck SMICA map
- [ ] script.md draft -> user approval
## Observations
## Handoff
