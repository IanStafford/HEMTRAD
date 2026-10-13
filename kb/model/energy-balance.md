---
title: Electron energy balance
tags: [model, parked]
date: 2026-10-08
source: model/ETemp.tcl, model/Continuity.tcl, model/GaN_modelfile_masterD
---
# Electron energy balance — ETemp PDE

**Decision (Ian, 2026-10-13):** use the configuration that works — `eTemp 1` with the thermoelectric term off (`etThermo 0`). The thermo term stays parked (every fix tried failed; see below). Defaults are unchanged, so set `etThermo 0` explicitly in sweeps.

Ian's `ElecTemperature` proc (Sentaurus-style hydrodynamic energy equation with Qfn,Qfn heat source), implemented in `model/ETemp.tcl`:

1.5 k n dTe/dt − ∇·(1.5 k Te n μ ∇Qfn) − ∇·(1.5 k Te n μ k∇Te) − n μ |∇Qfn|² + 1.5 k n (Te − T)/τ = 0

**Switches** ([[levers]]): `eTemp` (0 = ETemp is a constant 300 K solution → old model byte-identical), `etTau` 1e-12, `etMob` low|field (mobility in heating/flux), `etStats` 1 (electron Vt and Nc at ETemp in `model/Continuity.tcl`), `etThermo` 1 (thermoelectric current term J = nμ∇EFn + nμkΔ∇Te, Δ = 2.5 F3/2(η)/F1/2(η) − η, FLOOXS `f12`/`f32` Blakemore-normalized; also carried into the convective flux and J·∇EFn heating), diagnostics `etThermoJ`/`etThermoE`, `etNeg` 0 (1 = `negative` ETemp), `etDamp` 5.0 (ETemp DampValue), `etConv` 0 (1 = consistent convective flux), `etFloor` 1e10 (density floor in the energy equation; Ian's original 1). Contacts S/D/B hold ETemp = 300 K. The solution is `damp`ed (DampValue 5). Trap capture uses max(ETemp, T) through `HotTeExpr`.

**What works:** without the thermo term it converges (~1 bisection retry per point). Statistics at T (`etStats 0`) match drift-diffusion exactly with peak ETemp ~3,900 K by 1.8 V. Statistics at ETemp **inflate trap-free Id by +17–48% at 2 V** (245 vs 168 mA/mm at τ 1 ps) — likely an artifact without the thermoelectric term. Trap runs collapse at 0.2–0.6 V (vs 2.3/3.5 V local model) but stop at the runaway (plain solve at the next Vd fails, so the [[te-ramp]] never starts). Figure `figures/eTemp_IdVd.png`.

**What fails:** every version with the thermo term stops at the first 0.1 V step, even with damping and the floor. Capped-iteration debug dumps (`sweeps/eTempDebug.slurm` + `drivers/eTempDebug_tail.tcl`) show the first Newton update driving ETemp to ~0.3 K (and up to 400–2,300 K) below the 2DEG in the access region; with ETemp in the statistics, Elec and the Fermi integrals then overflow. Learned on the way: the missing `damp` flag made DampValue a no-op; an `abs()` clamp kink made Newton cycle (use softplus); `(Elec+floor)·Δ` with Δ ~ −η in depletion makes a fake current (thermo terms use unfloored `Elec`).

**Found in the FLOOXS survey (2026-10-12):** ETemp is declared `!negative`. In FLOOXS, a node whose update would go negative gets old·e^(−h) (h ≤ ~10) **instead of** the damped step ([[flooxs-solver]]), so `damp` never limited the large downward first updates — that is exactly the 300 → 0.3 K (≈ 300·e^−7) seen in the debug dumps. **Tried 2026-10-12 (lever `etNeg`, jobs 45692147/45692148): worse.** With `negative damp`, ETemp goes below zero (−61 K after one iteration in the no-thermo debug run) and every run — thermo or not, trap-free or not — now fails at the **first equilibrium solve** (ETemp updates 150–500 K per iteration, RHS growing to 1e9, NaN, munmap crash); the old `!negative` multiplicative cut was what kept ETemp positive and the equilibrium solve stable. `etNeg` is back to 0 (default); the initial-guess fix (ETemp = Temp at the top of `Initialize`, needed for `negative`) stays. **Smaller damping, tried 2026-10-12 (lever `etDamp`, job 45696870, trap-free τ 1 ps, `etNeg 1`):** without the thermo term, `etDamp` 0.5 and 1.0 both reach 1 V with Id identical to the `!negative` run (143.06 mA/mm at 1 V, peak ETemp 837 K), just slower (36–64 min). With the thermo term it still fails: `etDamp 0.5` gives up at the first 0.1 V step, `etDamp 1.0` fails in the equilibrium solve (ETemp oscillating for 300 iterations). Damping does not rescue the thermoelectric term; `etNeg` stays 0 and `etDamp` 5.0 by default. **Consistent convective flux, tried 2026-10-13 (lever `etConv`, job 45711842):** convective energy flux = exactly 1.5 k Te × the continuity flux (field-dependent mobility, 1e2 floor, thermo part). Without the thermo term it converges to 1 V with Id 144.87 mA/mm (vs 143.06 old flux, 136.85 drift-diffusion) and peak ETemp 787 K. With the thermo term it is worse: it fails in the equilibrium solve (ETemp updates to 1e4 K, NaN) instead of at 0.1 V. `etConv` stays 0 by default.

**Remaining options (none tried):** τ continuation (τ as a data field), or use the thermo-free / `etStats 0` configuration for trap studies. Full log: `progress.md` "PARKED … electron energy balance"; dashboard Oct 7–8.

Related: [[hot-electron-capture]], [[flooxs-gotchas]].
