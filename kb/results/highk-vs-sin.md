---
title: HighK vs SiN passivation
tags: [results]
date: 2026-10-01
---
# HighK vs SiN passivation

`model/rfdevice_SiN.tcl` replaces every HighK region (εr 35) by Nitride (εr 6.3). Static mobility.
- 2e18/0.75 grid (job 44294165): same regimes; trap-free SiN +1.5% at 3 V; only the source side (y −0.4) differs (HighK ~1.3–1.5× more suppression at 3 V, likely T-gate coupling through the high-εr layer).
- **Run F grid (job 44303974): identical** — 35 collapse / 15 off on both, onset identical at every position, depth within ±0.1–0.2 decades.
- **Why** (`archive/static_mobility/fieldPlateTest.tcl`, `archive/static_mobility/figures/fieldPlate.png`): at Vd ≤ 3 V the only hot spot is the gate drain edge (264 kV/cm at 3 V) under ~5 nm of nitride, which the HighK can't reach. HighK does flatten the T-gate-head/field-plate field, but only above ~5 V (at 20 V: 416 → 202 kV/cm). Seeing HighK in the collapse would need 10–20 V sweeps.
- **Rerun with the field-dependent mobility (2026-10-16, job 46241088, `drivers/fieldPlate.tcl`, `results/20261016_fieldPlate/`, `figures/fieldPlateFM_cuts.csv`/`_sweep.csv`, slide figure `figures/fieldSlide_highk.png` from `analysis/plot_strikeSlides.py`):** same picture. Gate-drain-edge peak along the 2DEG: 305 kV/cm at 3 V (static: 264), 484/486 at 10 V and 488/497 at 20 V HighK/SiN (≤2%). T-gate-head/field-plate peak: 183 → 117 kV/cm at 10 V (−36%), 403 → 193 at 20 V (−52%; static −51%). At 20 V the HighK spreads the field toward the drain: 8 → 138 kV/cm at y = 1 µm. At 3 V the curves overlap. Trap-free Id at 20 V: 193.6 (HighK) vs 197.5 mA/mm (SiN). 40/40 points per deck, no retries, ~7 min each.
- Robust (insensitive to εr 6.3–35). The model has no dielectric fixed/interface charge or dynamic surface trapping — the usual way passivation affects real collapse.
- Old `fieldpeak.tcl` set HighK εr before sourcing the model file, which reset it, so its "SiN" run was HighK.
- **With traps at Vg +1 V, Vd 0–10 V (2026-10-21, job 47062225, `sweeps/pulsedIV_deckVg1.slurm`, `results/20261021_deckVg1/`, `analysis/plot_deckVg1.py` → `figures/deckVg1_IdVd.png`):** the onsets are identical on both decks. The trap set is the sensitivity baseline (5e18, 0.30 eV, hotEb 1.0, hotTau 1e-14, local field).
  - **Trap-free Id at 10 V:** 802.2 (HighK) / 813.3 mA/mm (SiN). HighK equals the calibration value at Vg +1, Vd 10 (802.185), which confirms the new positive-Vg gate ramp.
  - **Trap at y 0.3:** −84% / −82% at 1.3 V, then recovers to ~9% of trap-free by 4–10 V (74 / 79 mA/mm at 10 V).
  - **Trap at y 1.0:** −100% at 1.5 V on both (122 / 126 → 0.05 mA/mm), floor ~1e-5. By 10 V HighK recovers to 0.24 mA/mm and SiN to 0.012.
  - **Trap at y 2.4:** −100% at 1.7 V on both, floor ~1e-6. At 10 V: 8e-4 (HighK) vs 1.4e-5 mA/mm (SiN).
  - So the passivation changes only the post-collapse recovery above ~4 V (SiN stays 20–60× lower). It does not change whether or where the collapse happens.
  - **The trap model cannot make SiN collapse while HighK does not.**
  - At Vg +1 the onset (1.3–1.7 V) comes earlier than at Vg −2 (2.3 V for y 1.0, [[trap-sensitivity]]): the current-driven ordering of [[gate-bias]].
  - All 8 tasks completed with no `GAVE UP`, in 28–66 min each.
