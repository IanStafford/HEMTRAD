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
- Robust (insensitive to εr 6.3–35). The model has no dielectric fixed/interface charge or dynamic surface trapping — the usual way passivation affects real collapse.
- Old `fieldpeak.tcl` set HighK εr before sourcing the model file, which reset it, so its "SiN" run was HighK.
