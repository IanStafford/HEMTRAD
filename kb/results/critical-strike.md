---
title: Critical-strike probability
tags: [results]
date: 2026-09-28
---
# Critical-strike probability at 1e7 ions/cm²

`archive/static_mobility/critical_strike.py` → `figures/criticalStrike*`. Gate width 200 µm. A **critical strike** = a Gaussian blob (σ 40 nm) that cuts Id to ≤1/10 of trap-free at any Vd ≤ 3 V. Critical band Δy from the static 10f maps + band-edge refinement (job 43542730). Poisson hits: λ = Φ·Δy·W, P(≥1) = 1 − e^−λ, Φ = 0.1 µm⁻².

| setting | Δy (µm) | λ | P(≥1) | Φ for 50% |
|---|---|---|---|---|
| 2e18/0.55 | 0.30 (gate) | 6.0 | 0.9975 | 1.2e6 cm⁻² |
| 2e18/0.75 | 0.47 | 9.4 | 0.99992 | 7.4e5 |
| 4e18/0.35 | 2.67 | 53 | ≈1 | 1.3e5 |
| 4e18/0.55, 8e18/0.35 | 3.01 | 60 | ≈1 | 1.15e5 |

**Big caveat — 2D vs 3D:** 2D makes each blob span the whole width. A real cascade is ~0.16 µm wide along the width; current flows around it → only ~0.5–4.8% of the width damaged (a few-% Id loss). Device-level collapse would need overlapping cascades (Φ ≳ 4e9 cm⁻²). Whether the runaway ignites around a 0.16 µm patch needs a 3D run ([[current-status]]).
