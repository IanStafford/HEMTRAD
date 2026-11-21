---
title: Electron energy balance
tags: [model]
date: 2026-10-08
source: model/ETemp.tcl, model/Continuity.tcl, model/GaN_modelfile_masterD
---
# Electron energy balance — ETemp PDE

> [!summary] Status (2026-11-20)
> - **Standard:** `eTemp 0`, the local-field model (Ian, since 2026-10-16).
> - **Option:** `eTemp 1` with `etStats 0` and `etThermo 0`, the working EB configuration, kept available. `HotTeExpr` then uses ETemp, and `hotTau`/`hotMu`/`hotVsat` are ignored.
> - **Parked:** the thermoelectric term (`etThermo 1`, which needs `etStats 1`); no version of it converged.

**Decisions, in order.**
- **2026-10-13 (Ian):** use the configuration that works, `eTemp 1` with the thermoelectric term off. `etStats 0` and `etThermo 0` became the defaults, and still are (`model/GaN_modelfile_masterD`). Electron statistics at the lattice Temp make Id drift-diffusion; ETemp drives the hot-electron trap capture through `HotTeExpr`.
- **2026-10-16 (Ian):** back to the local-field model (`eTemp 0`) as the standard, to save computation time. The energy balance stays available with `eTemp 1`.

With `eTemp 0` the model is unchanged (`etStats 0` is the original `Nc·f12(…/Vt)` expression). To reproduce the Oct 8–12 runs, set `etStats 1` (column in `params_eTemp*.txt`) and `etThermo 1` explicitly; their thermo tasks relied on the old default.

## Equation and switches

Ian's `ElecTemperature` proc (Sentaurus-style hydrodynamic energy equation with Qfn,Qfn heat source), implemented in `model/ETemp.tcl`:

1.5 k n dTe/dt − ∇·(1.5 k Te n μ ∇Qfn) − ∇·(1.5 k Te n μ k∇Te) − n μ |∇Qfn|² + 1.5 k n (Te − T)/τ = 0

**Switches** ([[levers]]): `eTemp` (0 = ETemp is a constant 300 K solution → old model byte-identical), `etTau` 1e-12, `etMob` low|field (mobility in heating/flux), `etStats` 0 (1 = electron Vt and Nc at ETemp in `model/Continuity.tcl`), `etThermo` 0 (1 = thermoelectric current term J = nμ∇EFn + nμkΔ∇Te, Δ = 2.5 F3/2(η)/F1/2(η) − η, FLOOXS `f12`/`f32` Blakemore-normalized; also carried into the convective flux and J·∇EFn heating), diagnostics `etThermoJ`/`etThermoE`, `etNeg` 0 (1 = `negative` ETemp), `etDamp` 5.0 (ETemp DampValue), `etConv` 0 (1 = consistent convective flux), `etFloor` 1e10 (density floor in the energy equation; Ian's original 1). Contacts S/D/B hold ETemp = 300 K. The solution is `damp`ed (DampValue 5). Trap capture uses max(ETemp, T) through `HotTeExpr`.

## Without the thermo term

**What works:** without the thermo term it converges (~1 bisection retry per point). Statistics at T (`etStats 0`) match drift-diffusion exactly with peak ETemp ~3,900 K by 1.8 V. Statistics at ETemp **inflate trap-free Id by +17–48% at 2 V** (245 vs 168 mA/mm at τ 1 ps), likely an artifact without the thermoelectric term. Trap runs collapse at 0.2–0.6 V (vs 2.3/3.5 V local model) but stop at the runaway (plain solve at the next Vd fails, so the [[te-ramp]] never starts). Figure `figures/eTemp_IdVd.png`.

**Trap study, working EB configuration (2026-10-13, job 45768739, `figures/eTempStd_IdVd.png`):** the eTemp1 trap set rerun with etStats 0 / etThermo 0, Vd 0–4 V.
- Unlike Oct 8, the runs get past the collapse (6/7 to 4 V; Run F timed out at 2.2 V).
- The late set (5e18, 0.30 eV) collapses at **0.4 / 0.5 / 0.7 V for τ 1 / 0.3 / 0.1 ps**, independent of position (local-field model: 2.3 V at y 1.0, 3.5 V at y 2.4).
- At y 1.0 µm the drop is 1e5–1e7× to the noise floor. At **y 2.4 µm it is 60–4000× to a 0.01–0.1 mA/mm plateau that creeps up (τ 0.1 ps: 0.02 → 0.07 mA/mm by 1.7 V)**, the measured collapse-then-creep shape at about the measured onset ([[project-goal]]). A second drop to ~1e-7 follows at 2.5–2.7 V.
- Cost: ~1.9 s per Newton iteration and up to 300-iteration failed solves (`sweepIterLimit`, [[retry-bisection]]). Lowering the Newton limit does not help (job 45801978: limit 100 no faster; limit 50 15-20% faster but post-collapse Id changes up to 9x because the extra bisections change the trap-fill history), so the limit stays 300; end sweeps at 1.5-2 V instead.
- Post-collapse Id is step-history dependent: compare curves only at the same Vd step and limit.

## Thermoelectric term (parked)

**What fails:** every version with the thermo term stops at the first 0.1 V step, even with damping and the floor. Debug dumps (`eTempDebug.slurm` + `eTempDebug_tail.tcl`, in `archive/energy_balance/` since 2026-11-21, README there with the job list) after the 0 → 0.1 V step show ETemp near 0.3 K (and up to 400–2,300 K) below the 2DEG in the access region; with ETemp in the statistics, Elec and the Fermi integrals then overflow. Learned on the way: the missing `damp` flag made DampValue a no-op; an `abs()` clamp kink made Newton cycle (use softplus); `(Elec+floor)·Δ` with Δ ~ −η in depletion makes a fake current (thermo terms use unfloored `Elec`).

**The debug dumps are not 1- or 2-iteration snapshots (unverified reading, 2026-11-20).** The tail was meant to cap Newton at 1 and then 2 iterations. It sets `Math iterLimit` after the solver is built, so the cap never took effect ([[flooxs-gotchas]]). The dumps followed full (possibly failed) solves under the deck's `iterLimit` 300. So every reading below and in progress.md that ties a value to "the first Newton update" or "one iteration" (debug jobs 45208486, 45209164, 45210603 and 45692147) is unverified. Rechecking it, with `iterLimit` set before `device init`, is Ian's call if the thermo term is ever resumed.

**Found in the FLOOXS survey (2026-10-12):** ETemp is declared `!negative`. In FLOOXS, a node whose update would go negative gets old·e^(−h) (h ≤ ~10) **instead of** the damped step ([[flooxs-solver]]), so `damp` never limits large downward updates. That fits the 300 → 0.3 K (≈ 300·e^−7) in the debug dumps, but since those were not first-update states, the match is unverified.

**Tried (2026-10-12/13):**
- **`etNeg 1` (2026-10-12, jobs 45692147/45692148): worse.** With `negative damp`, ETemp goes below zero (min −61 K in the no-thermo debug run, reported as "after one iteration", unverified as above). Every run, thermo or not, trap-free or not, now fails at the **first equilibrium solve** (ETemp updates 150–500 K per iteration, RHS growing to 1e9, NaN, munmap crash). The old `!negative` multiplicative cut was what kept ETemp positive and the equilibrium solve stable. `etNeg` is back to 0 (default); the initial-guess fix (ETemp = Temp at the top of `Initialize`, needed for `negative`) stays.
- **Smaller damping, `etDamp` (2026-10-12, job 45696870, τ 1 ps, `etNeg 1`).** Without the thermo term, `etDamp` 0.5 and 1.0 both reach 1 V with Id identical to the `!negative` run (143.06 mA/mm at 1 V, peak ETemp 837 K), just slower (36–64 min). With the thermo term it still fails: `etDamp 0.5` gives up at the first 0.1 V step, and `etDamp 1.0` fails in the equilibrium solve (ETemp oscillating for 300 iterations). Damping does not rescue the thermoelectric term; `etNeg` stays 0 and `etDamp` 5.0 by default.
- **Consistent convective flux, `etConv` (2026-10-13, job 45711842).** The convective energy flux is exactly 1.5 k Te × the continuity flux (field-dependent mobility, 1e2 floor, thermo part). Without the thermo term it converges to 1 V with Id 144.87 mA/mm (vs 143.06 old flux, 136.85 drift-diffusion) and peak ETemp 787 K. With the thermo term it is worse: it fails in the equilibrium solve (ETemp updates to 1e4 K, NaN) instead of at 0.1 V. `etConv` stays 0 by default.

**Remaining option (not tried):** τ continuation (τ as a data field). The other option on the list, the thermo-free `etStats 0` configuration for trap studies, became the working EB configuration on 2026-10-13. Full log: `progress.md` "PARKED … electron energy balance"; dashboard Oct 7–8.

Related: [[hot-electron-capture]], [[flooxs-gotchas]].
