---
title: Insulator traps
tags: [model, results]
---
# Insulator trap charge (`insTrapSign`)

The parts of the trap blob inside Nitride/HighK enter Poisson as **static charge** (`InsTrapCharge` in `Poisson.tcl`); no carriers or Qfn are solved there, so no Fermi or hot-electron filling.
- `insTrapSign` 0 (default): none; −1: fully filled (−q·N); +1: fixed positive (+q·N).

**Static-era x–y map (§10j, jobs 44261474 + sign-0 companion 44274780):**
- **−1:** every blob from the nitride to 15 nm into the GaN is **off at rest** at every y — the filled nitride tail (2e13 cm⁻² at x = 0) exceeds the 2DEG density.
- **+1:** cancels the access-region hot-electron collapse (0.89–1.0 of trap-free at 3 V).
- **0:** the normal collapse returns between −2.5 and 40 nm depth, outside the gate.
- HighK charge (−1) 50 nm above the nitride switches the device off for y ≥ 1.5 µm but not under the T-gate/FP (metal screens it).

**Key unknown:** the passivation **fill fraction** (could come from the measured Vth shift after irradiation). Only tested with static mobility; not yet repeated with field mobility ([[current-status]]).

Related: [[trap-model]], [[static-era-lessons]].
