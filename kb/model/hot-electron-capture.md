---
title: Hot-electron capture
tags: [model]
source: model/Poisson.tcl
---
# Hot-electron capture

Capture over a barrier `hotEb` at electron temperature Te; emission at the lattice T. Equivalent to lowering the trap level by **`hotEb·(1 − T/TeTrap)`** in the occupancy of the [[trap-model]].

**Local-field Te** (`HotTeExpr`, used by `UpdateTe`):
Te = T + (2/3) · `hotTau` · v(E) · E / (k/q), v(E) = `hotMu`·E / (1 + `hotMu`·E/`hotVsat`), with **E = |∇Qfn|** (the driving field, not |∇DevPsi|, so the polarization field doesn't heat electrons at equilibrium). `UpdateTe w` moves the data field `TeTrap` a fraction w toward the target (under-relaxed so the trap charge changes slowly per solve).

Levers ([[levers]]): `hotEb` (larger → earlier, deeper collapse; strongest depth lever), `hotTau` (larger → hotter → earlier; onset ∝ ~1/√hotTau in the static era), `hotMu`, `hotVsat` (Te only).

**Caveat:** the late-onset fits use `hotTau` 1e-14 s, well below physical GaN energy-relaxation times (0.1–1 ps); in the local model `hotTau` acts as a fit parameter absorbing non-local effects. The [[energy-balance]] removes that freedom (at τ = 1 ps it collapses much earlier).

Collapse mechanism in this model is **current-driven** (semi-ON hot-electron trapping), see [[gate-bias]].

Related: [[te-ramp]], [[run-F]]. Full derivation (capture barrier → level shift E_b(1 − T/Te), local-field Te from the energy balance, emission-time estimate) with references: https://claude.ai/artifact/4KLdks2Sd8t9zs8wb8wWJ9
