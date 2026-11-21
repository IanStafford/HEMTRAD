---
title: Insulator traps
tags: [model, results]
date: 2026-11-20
source: model/Poisson.tcl, model/GaN_modelfile_masterD, drivers/radIV.tcl
---
# Insulator trap charge (`insTrapSign`)

The parts of the trap density inside Nitride/HighK enter Poisson as **static charge** (`InsTrapCharge` in `model/Poisson.tcl`); no carriers or Qfn are solved there, so no Fermi or hot-electron filling.
- `insTrapSign` 0 (default): none; −1: fully filled (−q·N); +1: fixed positive (+q·N).
- It must be set before the model file is sourced (a task lever, not a `damList` entry).

**Static-era x–y map (`archive/static_mobility/RESULTS.md` §10j, jobs 44261474 + sign-0 companion 44274780):**
- **−1:** every blob from the nitride to 15 nm into the GaN is **off at rest** at every y — the filled nitride tail (2e13 cm⁻² at x = 0) exceeds the 2DEG density.
- **+1:** cancels the access-region hot-electron collapse (0.89–1.0 of trap-free at 3 V).
- **0:** the normal collapse returns between −2.5 and 40 nm depth, outside the gate.
- HighK charge (−1) 50 nm above the nitride switches the device off for y ≥ 1.5 µm but not under the T-gate/FP (metal screens it).

**Rad era: passivation damage from the stress field (`drivers/radIV.tcl`, 2026-10-24).** With field mobility, `damInsPeak` > 0 puts a fixed charge in the insulator layer `damInsXmin` ≤ x < 0 (default −0.05 µm, the 50 nm SiN under the HighK):
- density N = min(`damMax`, `damInsPeak`·(E/`damInsEref`)^`damInsM`) from the field at the stress bias (`damInsField` tot = |∇ψ| by default, or lat);
- `insTrapSign` is set to −1 (trapped electrons) automatically when `damInsPeak` > 0 and the sign isn't given;
- defaults `damInsEref` 1e6 V/cm, `damInsM` 2.
- **radIns (job 47458257, 14 tasks):** nitride charge 1e17 / 1e18 × m 2 / 4 at 1 MV/cm on both decks gave uniform losses, nearly identical in HighK and SiN. It doesn't separate the decks, so it was dropped ([[rad-model]]). These runs used the old FP contact box ([[fp-contact-fix]]).

**Key unknown:** the passivation **fill fraction** (could come from the measured Vth shift after irradiation). The static-era map above has not been repeated with field mobility; the rad era tested only the field-placed charge of radIns ([[current-status]]).

Related: [[trap-model]], [[damage-model]], [[static-era-lessons]].
