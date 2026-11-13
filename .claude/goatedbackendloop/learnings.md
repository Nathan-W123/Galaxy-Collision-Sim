# goatedbackendloop learning reference
Sessions: 0 · Last consolidated: never
## Stated preferences
- Visual output must be crisp and clearly readable; soft/fuzzy footage is rejected ("still very fuzzy i cant see great") · scope: all projects · stated 2026-11-13
## Workflow lessons
### L-01 · Show stills and get a pick before rendering visual deliverables
- Observation: two full preview renders were rejected on look ("bad, vibe coded", then "still very fuzzy") after I tuned the look myself from contact sheets.
- Evidence: 2026-11-13 · two rejected clips, each costing a full sim + render cycle
- Adjustment: for any visual deliverable, render 2-3 labelled still variants of the same frame at full resolution, show them, and get the user's pick before rendering the full clip.
- Scope: workflow
- Status: provisional
- Outcomes: +2026-11-13 helped (user picked B from stills in one round) · +2026-11-13 helped (framing stills on the coarse run caught clipped tails and a frame-filling remnant before the final render)
### L-02 · Run the cheapest discriminating experiment before an expensive commitment
- Observation: before a 2+ h production run, short tests (four 2-Gyr isolated-disk runs; two 5k 10-Gyr orbit checks) overturned the working hypothesis (more particles fixes thickening) and ruled out the 200k option on energy.
- Evidence: 2026-11-13 · 200k @ dt 2 Myr drifted 0.8-1.1 % in 2 Gyr; heating rate fell only 1.4x for 2.8x lighter halo particles (bars dominate)
- Adjustment: when a choice commits hours of compute, first run a minutes-scale test that can falsify the plan, and show the user its numbers with the decision.
- Scope: workflow
- Status: provisional
- Outcomes: +2026-11-13 helped
### L-03 · Review rendered output as a contact sheet before delivering
- Observation: a scale-bar crossfade produced overlapping labels that only showed up when viewing frames across the clip.
- Evidence: 2026-11-13 · garbled "200/50 kpc" label at 2.70 and 3.46 Gyr caught on the 12-frame sheet, fixed before delivery
- Adjustment: extract a 10-12 frame contact sheet spanning every scene transition and inspect it before sending any clip.
- Scope: workflow
- Status: provisional
- Outcomes: +2026-11-13 helped
## Retired
## Changelog
- 2026-11-13 · created; added L-01
- 2026-11-13 · L-01 +1 outcome; added L-02, L-03
