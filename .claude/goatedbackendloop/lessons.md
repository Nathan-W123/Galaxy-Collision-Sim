# Project lessons (galaxy-collision explainer)
### P-01 · The MW/M31 disk models are bar-unstable; thickening is mostly physics
- Observation: ELK X = 0.74 (MW) and 0.79 (M31) for the vdM2012 III models; bars (A2 up to 0.3) form within ~1 Gyr and thicken the inner disks at any N.
- Evidence: 2026-11-13 heating test (output/logs/heating_report.md)
- Adjustment: do not chase disk thickness with particle count; handle crispness in the renderer and framing.
- Scope: project
- Status: provisional
- Outcomes:
### P-02 · dt = 2 Myr is too coarse at 0.15-0.2 kpc softening
- Observation: isolated disk drifted 0.8-1.1 % energy in 2 Gyr at dt = 2 Myr (vs 0.07 % at 1 Myr).
- Evidence: 2026-11-13 heating runs c, d
- Adjustment: keep dt = 1 Myr for production; 100k x 10 Gyr = ~80 min on 4 cores.
- Scope: project
- Status: validated (MW-M31 production run: 0.53 % over 10 Gyr at dt = 1 Myr)
- Outcomes: +2026-11-13
