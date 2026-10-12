---
title: FLOOXS parameter database (pdb)
tags: [flooxs, reference]
source: ~/flooxs/Params, src/param.tcl, Params/pdb
---
# FLOOXS parameter database (pdb)

A hierarchical key store: `<Material|Interface|Contact|Math> [<Solution>] <Parameter>`. Defaults live in `~/flooxs/Params/<Material>/…`; decks override them.

- **Set:** `pdbSetDouble GaN DevPsi RelEps 8.9`, `pdbSetString GaN Qfn Equation "<expr>"`, `pdbSetBoolean D Qfn Fixed 1`. A "double" can hold an **expression string**: `pdbSetDouble GaN Elec Nc (2.3e18*sqrt(Temp*Temp*Temp/2.7e7))`.
- **Get:** `pdbGetDouble`, `pdbDelayDouble`, `pdbGetString`, `pdbGet` return the stored text (not evaluated). `pdbDelayDouble` is the idiom for **inlining a stored expression** into another expression string: `"[pdbDelayDouble $Mat Elec mob] * (Elec+1e2) * grad(Qfn)"`. `pdbGetDouble` in `[expr …]` works only for plain numbers.
- **Keys the HEMTRAD model uses** (`model/`): per material `DevPsi RelEps`, `Affinity`, `Eg`, `Elec Ec/Nc/mob/lowfldmob/mumin/…`, `Hole Ev/Nv/mob`, `<Sol> Equation`, `<Sol> DampValue`, `Abs.Error`, `Rel.Error`; per interface `AlGaN_GaN DevPsi Equation` (polarization charge), `AlGaN_Nitride DevPsi Equation` (surface charge); per contact (S, D, B, G, FP) `<Sol> Fixed`, `Flux`, `Flux.Scale`, `Equation` (e.g. `"Qfn+S"` pins Qfn to the contact voltage); `Math iterLimit` etc.
- **Contact equations** replace the node equations (Dirichlet when `Fixed 1`); the contact's voltage appears as the variable named after the contact (`S`, `D`, `G`) in the equation string.
