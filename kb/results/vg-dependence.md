---
title: Gate-bias dependence of the onset (Oct 15 exploration)
tags: [results, physics, open]
date: 2026-10-15
---
# Onset vs Vg: measured later at more positive Vg

**Measured (reported to Ian 2026-10-15, new data pending):** the collapse comes **later** as Vg becomes more positive. The hot-electron model predicts the opposite ([[gate-bias]]), the discriminating signature listed in [[field-driven-trapping]].

## A. Can the present model explain it?
- **Access-region traps, energy balance (job 46040979):** late set at y 2.4 µm, τ 1 ps collapses at **0.3–0.4 V at Vg −2, −1 and 0** (`figures/vgOnset_EB.png`); τ 0.1 ps: 0.7 V at −2, 0.6 V at −1. Same as the local-field result: current-driven, no later onset at higher Vg.
- **Why:** trap-free Te at Vd 0.4 V (τ 1 ps) is 304 / 306 / 307 K at y 2.4 µm for Vg −2/−1/0, with no Vg dependence, but **346 / 314 / 309 K at the gate drain edge** (y 0.14 µm). Only traps at the gate edge would see less heating at higher Vg.
- **Gate-edge traps with the energy balance** (y 0.2 / 0.3 µm, 4e18 / 5e18, job 46052606): running; very slow (still at Vd 0.2 V after 20 min).

## B. Field-driven models (exploratory worktrees, not in main)
Branches `explore/field-capture` and `explore/gate-injection` (workstation `~/HEMTRAD-wt/`, HPG `…/ianstafford/HEMTRAD-wt/`). New levers, default off (`capMode hot`): `capMode field|gate`, `capField lat|tot|qfn`, `capForm pf|fn`, `capBeta`, `capF0`, `capFth`, `injLen`; plus a `fieldProfile` dump in `drivers/pulsedIV.tcl`. The field lowers the capture barrier, entered as an equivalent TeTrap so `IonizedAcceptor`, `FillStep` and the Te ramp are unchanged. pf = capBeta·√F (Poole–Frenkel), fn = kT·capF0·(1/capFth − 1/F) ≥ 0 (tunnelling rate ∝ exp(−F0/F)).
- **Gate-edge field** (peak |∂ψ/∂y| near the AlGaN top at y ≈ 0.14 µm, trap-free): 2.9e5 / 1.2e5 / 4e4 V/cm at rest for Vg −2/−1/0; +~6e3 V/cm per 0.1 V of Vd at −2 and −1. Mid-barrier: 1.35e5 / 5.8e4 / 1.6e4.
- **Poole–Frenkel (√F), local field or gate injection** (jobs 46040980, 46042673): either nothing to 2 V or traps full at rest (Id 1e-8 / 1e-4 / 1 mA/mm at Vg −2/−1/0 from Vd = 0). √F is too soft to make a ~10% field rise switch the traps.
- **Gate injection, FN** (supply set by the gate-edge field, decaying along the surface with injLen; jobs 46046389, 46048098): right Vg ordering, but **no sharp collapse**. Charge at y 1 µm does not raise the gate-edge field, so there is no runaway.
- **Virtual gate = surface trap sheet + FN local lateral-field capture** (σx 5 nm, σy 0.8 µm at y 1.2 µm, 0.15 eV, peak 2e19 ≈ 1.2e13 cm⁻², capF0 2e7, capFth 1.4e5, hotEb 2.0; jobs 46052532, 46054851; `figures/vgOnset_virtGate.png`): **Vg −2: 21 → 5.3 → 0.0019 → 7e-9 mA/mm at Vd 0.2–0.6 V (onset 0.5 V); Vg −1.5: 0.5 V; Vg −1, −0.5, 0: no collapse to 1.8–4 V.** Filled traps extend the depletion and push the field peak outward: the feedback that a sharp collapse needs. capFth 1.6e5: onset 0.8 V at −2, none at −1.5 to 1.9 V. Peak 1e19: no collapse. Level 0.0 eV: onset 0.5 V.
- **Misfits:** the onset shift is switch-like (≤ −1.5 V collapses, ≥ −1 V does not) because the gate-edge field drops steeply with Vg; Id before the collapse is already ~40% low at Vg −2; the post-collapse current sits at the 1e-8 noise floor (no creep, far deeper than the measured ~1000×). Softer capF0 (5e6, 1e7, capFth 1.2e5, Vg −2 … 0) running as job 46057777.

## Reading
Only a mechanism that sees **Vd − Vg** (the gate-edge field) gives the measured trend, and it needs positive feedback to collapse sharply; a trap sheet along the surface supplies both. This is the classic "virtual gate" (Vetury et al., IEEE TED 2001). The hot-electron energy balance explains the measured onset voltage only for access-region traps, which are current-driven.

Open: gradual vs switch-like shift (needs the new data: onset at each Vg); creep and depth of the collapse; whether gate-edge hot-electron traps (A) give the trend without new physics.
