---
title: Position maps
tags: [results]
date: 2026-10-03
---
# Position maps: how trap position sets the onset

**Late-onset set map** (job 44441813 + Te-ramp rescue 44452289, `sweeps/pulsedIV_posMapLate.slurm`, `results/20261002_posMapLate/`): 0.30 eV / 5e18 / `hotTau` 1e-14 / `hotEb` 1.0 at depth {0, 3.75, 7.5, 11.25, 15} nm × y {−0.4 … 2.4} µm, Vd 0–3 V. After the rescue: deep 33, medium 10, shallow 15, off 5, stalled 2.
- Surface traps: deep onset **1.6 → 2.1 → 2.3 → 2.5 → 2.8 → 3.0 V** at y 0.285 / 0.725 / 1.0 / 1.25 / 1.5 / 1.75 µm. Traps nearer the 2DEG reach farther out (7.5 nm: 1.5 → 2.4 V, and 2.8 V at y 2.4).
- Source side and y ≥ 2.0 near the surface: shallow. y = 0.125: medium at 0.2 V; y = 0: off at rest. 50/65 positions cut >10× by 3 V.
- Figures `figures/posMapLate_{grid,onset}.png`, `figures/posMapLate.gif`.
- Onset view (2026-10-14, Ian's idea): `figures/posMapLate_onset3d.png` / `.gif` (`analysis/plot_posOnset.py`): 45/65 positions collapse (deep, medium or stalled) by 3.0 V, earliest 0.2 V (gate region), latest 3.0 V; the ridge falls away from the gate toward the drain. All six sets: `figures/posMap_onset3d_sets.png`, per-set `figures/posMap_<set>_onset3d.{png,gif}`. Collapsing positions by 3.0 V (of 65): 0.30/4e18 7, 0.25/6e18 36, 0.30/5e18 45, 0.30/6e18 47, 0.40/5e18 50, 0.55/4e18 50. Threshold sets (0.30/5e18, 0.25/6e18) give a ridge at the gate (0.2 V) sloping to 3.0 V; 0.30/6e18 slopes only to 1.9 V; 0.40/5e18 is a plateau at 0.7–1.2 V; 0.55/4e18 a 0.3–2.5 V plateau with isolated late pits.

**Five more level/concentration sets** (job 44573468, `sweeps/pulsedIV_posMapLM.slurm`, `results/20261003_posMap_<set>/`, same grid and hot-electron levers):

| Set | Deep (of 65) | Surface onset (near gate → farthest collapsing) |
|---|---|---|
| 0.30 eV / 4e18 | 0 (7 medium) | no deep collapse — too little charge |
| 0.30 / 5e18 (above) | 33 | 1.6 → 3.0 V |
| 0.30 / 6e18 | 43 | 1.2 → 1.9 V, even at y 2.0–2.4 |
| 0.25 / 6e18 | 29 | 1.8 → 3.0 V; the front hits the 3 V limit beyond y 1.0 |
| 0.40 / 5e18 | 50 | 0.8–1.2 V everywhere outside the gate |
| 0.55 / 4e18 | 42 | 0.4–0.5 V almost everywhere |

**Lesson:** deeper level or more charge → earlier, more uniform collapse; the outward-spreading front exists only near the charge threshold (0.25–0.30 eV, 5–6e18). Figures `figures/posMap_<set>_{grid,onset}.png`, `.gif`.

Talk figures by zone and across the six sets: `figures/posSlide_{lateral,sets}.png` (`analysis/plot_posSlides.py`). Under the field plate (y 0.285–0.5) the collapse starts at 1.4–1.7 V but the Id drop at 3 V is only 5–80×, vs up to 1e8 beyond it (cause not checked).

Earlier static-era position findings: [[static-era-lessons]].
