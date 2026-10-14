---
title: Run F trap map with field mobility
tags: [results]
date: 2026-10-01
---
# Run F trap map with the calibrated field mobility

Job 44342967 (51 tasks, `sweeps/pulsedIV_trapMapF_field.slurm`), `results/20261001_trapMapF_field/`: 5 depths (0–15 nm) × 10 positions (−0.4 … 2.4 µm), Vd 0–3 V, Run F levers, `mobModel field`. No crashes; 3 source-side tasks gave up after their collapse. Figures `figures/trapMapF_field_tp4e+18_tl0.55.png`, `figures/mobCompare_F_{3d,compare}.png`.

| | static (archived 10f) | field |
|---|---|---|
| trap-free Id at 0.1 / 1 / 3 V | 10.0 / 90.1 / 146.9 | 17.6 / 136.9 / 177.2 mA/mm |
| regimes (of 50) | collapse 35, off 15 | collapse 31, off 19 |
| onset | 0.2–0.5 V, later away from the gate | 0.2 V almost everywhere |
| depth vs trap-free | 10^4.1–10^5.8 | 10^4.9–10^7.1 |
| at-rest Id / trap-free | 0.71–0.87 | 0.04–0.63 |

- **Earlier, deeper, more uniform collapse**; the static-era lateral onset trend nearly disappears (it reappears at weaker settings, [[position-maps]]).
- The 4 extra "off" devices (11–15 nm deep at y 0.285–0.5) sit at 0.04–0.05 of trap-free — borderline.
- Caveat: part of the larger ratios is the higher baseline (μ ~1160 vs 600); the low-Vd region isn't validated ([[calibration]]).
