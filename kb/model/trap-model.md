---
title: Trap model
tags: [model]
source: model/Poisson.tcl, model/GaN_modelfile_masterD
---
# Trap model (`model/Poisson.tcl`)

**`IonizedAcceptor Mat Ntrap Etrap Efwhm {g 2}`** — acceptor traps, **neutral when empty, −q when filled**. `IonAcceptor = Ntrap · f`, f = Fermi–Dirac occupancy of a level at `Econd − Etrap` (degeneracy g = 2), with a Gaussian energy spread (FWHM `trapWidth`) via 3-point Gauss–Hermite. Poisson uses `− IonAcceptor`. Spatial density from `TrapConc_<trapShape>` (Gaussian or cone; [[levers]]).

**Sign bug (fixed in 760b388):** the old `NeutralAcceptor` put *empty* traps in Poisson as negative charge, so trapping fed on itself and Newton diverged into NaN at Vd ≈ 1.5 V. The abrupt collapse in `radPlot.csv`/`radPlot1.csv` came from this bug, so only their onset and depth are targets, not the decay to 1e-9 after the collapse.

**Hot-electron capture:** the trap level is lowered by `hotEb·(1 − T/TeTrap)` — see [[hot-electron-capture]].

**Trap memory** (data fields made in `Initialize`: `TrapFrozen`, `FrozenFlag`, `TeTrap`):
- When not frozen, charge = `max(TrapFrozen, live)`, written `0.5*(a+b+abs(a-b))`.
- `CaptureTraps` — store the present charge in `TrapFrozen`: traps fill but never empty (fill-only sweep; deep traps emit on s–100 s scales, slower than a pulsed sweep).
- `FreezeTraps` — hold the charge fixed via `FrozenFlag`.
- `ThawTraps` — back to live Fermi occupancy with cold electrons.
- `HotStress` — iterate Te ↔ device solve at fixed bias; `FillStep` — the same with capture after each solve (4 × w 0.5 per Vd point).

The data fields are initialised with a tiny spatial variation because constant fields are folded into the equations at `device init` ([[flooxs-gotchas]]).

**Rule (CLAUDE.md):** don't change the trap physics to get convergence; propose physics changes to Ian first.

Regimes found ([[static-era-lessons]], [[position-maps]]): deep levels / high density fill at rest and switch the device **off** (a threshold shift); the hot-electron **collapse** lives in a band of moderate density and shallow-to-mid levels.

Related: [[insulator-traps]], [[retry-bisection]], [[te-ramp]].
