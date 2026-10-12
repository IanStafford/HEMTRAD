---
title: Electron energy balance (parked)
tags: [model, parked]
date: 2026-10-08
source: model/ETemp.tcl, model/Continuity.tcl, model/GaN_modelfile_masterD
---
# Electron energy balance — ETemp PDE (**parked 2026-10-08**)

Ian's `ElecTemperature` proc (Sentaurus-style hydrodynamic energy equation with Qfn,Qfn heat source), implemented in `model/ETemp.tcl`:

1.5 k n dTe/dt − ∇·(1.5 k Te n μ ∇Qfn) − ∇·(1.5 k Te n μ k∇Te) − n μ |∇Qfn|² + 1.5 k n (Te − T)/τ = 0

**Switches** ([[levers]]): `eTemp` (0 = ETemp is a constant 300 K solution → old model byte-identical), `etTau` 1e-12, `etMob` low|field (mobility in heating/flux), `etStats` 1 (electron Vt and Nc at ETemp in `model/Continuity.tcl`), `etThermo` 1 (thermoelectric current term J = nμ∇EFn + nμkΔ∇Te, Δ = 2.5 F3/2(η)/F1/2(η) − η, FLOOXS `f12`/`f32` Blakemore-normalized; also carried into the convective flux and J·∇EFn heating), diagnostics `etThermoJ`/`etThermoE`, `etFloor` 1e10 (density floor in the energy equation; Ian's original 1). Contacts S/D/B hold ETemp = 300 K. The solution is `damp`ed (DampValue 5). Trap capture uses max(ETemp, T) through `HotTeExpr`.

**What works:** without the thermo term it converges (~1 bisection retry per point). Statistics at T (`etStats 0`) match drift-diffusion exactly with peak ETemp ~3,900 K by 1.8 V. Statistics at ETemp **inflate trap-free Id by +17–48% at 2 V** (245 vs 168 mA/mm at τ 1 ps) — likely an artifact without the thermoelectric term. Trap runs collapse at 0.2–0.6 V (vs 2.3/3.5 V local model) but stop at the runaway (plain solve at the next Vd fails, so the [[te-ramp]] never starts). Figure `figures/eTemp_IdVd.png`.

**What fails:** every version with the thermo term stops at the first 0.1 V step, even with damping and the floor. Capped-iteration debug dumps (`sweeps/eTempDebug.slurm` + `drivers/eTempDebug_tail.tcl`) show the first Newton update driving ETemp to ~0.3 K (and up to 400–2,300 K) below the 2DEG in the access region; with ETemp in the statistics, Elec and the Fermi integrals then overflow. Learned on the way: the missing `damp` flag made DampValue a no-op; an `abs()` clamp kink made Newton cycle (use softplus); `(Elec+floor)·Δ` with Δ ~ −η in depletion makes a fake current (thermo terms use unfloored `Elec`).

**Found in the FLOOXS survey (2026-10-12):** ETemp is declared `!negative`. In FLOOXS, a node whose update would go negative gets old·e^(−h) (h ≤ ~10) **instead of** the damped step ([[flooxs-solver]]), so `damp` never limited the large downward first updates — that is exactly the 300 → 0.3 K (≈ 300·e^−7) seen in the debug dumps. Cheap thing to try first: declare ETemp `negative damp` (or keep `!negative` but give it a smaller first step), so damping applies in both directions; it is a solver setting, not physics.

**Next step (proposed, not approved):** make the convective energy flux exactly 1.5 k Te × the continuity flux (same mobility and the same 1e2 floor as `ElecContinuity`) so a uniform Te has zero divergence; rerun the debug pair before any sweep. Alternatives: τ continuation (τ as a data field), or use the thermo-free / `etStats 0` configuration for trap studies. Full log: `progress.md` "PARKED … electron energy balance"; dashboard Oct 7–8.

Related: [[hot-electron-capture]], [[flooxs-gotchas]].
