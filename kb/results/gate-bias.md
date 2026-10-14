---
title: Gate bias — current-driven collapse
tags: [results, physics]
date: 2026-10-03
---
# Curve tracer at Vg = −1 and 0 V

Job 44573629 (`sweeps/pulsedIV_curveTracer.slurm`, `analysis/plot_curveTracer.py` → `figures/Vg_-1V/`, `figures/Vg_0V/`; Vg −2 stays the default in `figures/`). Vd 0–4 V.

| Device | Vg −2 | Vg −1 | Vg 0 |
|---|---|---|---|
| late-onset set, y 1.0 µm | 2.3 V | 1.6 V | 1.5 V |
| late-onset set, y 2.4 µm | 3.5 V | 1.8 V | 1.8 V |
| Run F | 0.2 V | 0.2 V | 0.2 V |

- **Less negative gate → earlier and deeper collapse** (floor 1e-5 to 1e-4 vs 2e-3 mA/mm); y 2.4 decays instead of creeping.
- **Why:** the collapse starts at about the **same current** (165–205 mA/mm) at every Vg. At −2 V the gate caps the current near that level, so it creeps up to it by 2.2–3.4 V; at −1/0 V the current passes it by ~1.6 V (trap-free 407/513 mA/mm at 4 V vs 184).
- The **peak** field is lower at higher Vg (trap-free peak Te 703 K at −2 vs 335 K at −1 at 3 V), but these traps sit in the access region, where the local field scales with current. Likely mechanism (inferred, not yet checked with a field dump): ~85% of traps are filled at rest, locally depleting the channel; current through that spot makes a field spike ∝ current → heating → more capture → runaway. Uniform access-region heating would be <1 K.
- So the model's collapse is **semi-ON hot-electron trapping** (cf. Meneghini et al.). A **field-driven** mechanism would move the onset later with higher Vg — a discriminating measurement ([[field-driven-trapping]]).
