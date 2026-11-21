---
title: Levers
tags: [model, reference]
date: 2026-11-20
source: model/GaN_modelfile_masterD, model/GaN.tcl, model/Metal.tcl, model/Continuity.tcl, model/Poisson.tcl, model/rfdevice.tcl, model/rfdevice_SiN.tcl, model/rfdevice3d.tcl, drivers/pulsedIV.tcl, drivers/radIV.tcl, drivers/seeIV.tcl, drivers/calibIdVg.tcl, drivers/fieldPlate.tcl, sweeps/params_*.txt
---
# Levers

A lever is a Tcl variable that a driver, a wrapper or a sweep task sets before the model file or the deck is sourced. Every lever has an `info exists` default or is optional (unset = old behaviour). The defaults below were read from the `info exists` lines of each file on 2026-11-20. In a `radIV.slurm` params line the last value of a repeated lever wins ([[sweep-pattern]]). Drivers are described in [[drivers]].

## Per-driver defaults

Each driver sets some levers before it sources the model file, so the same lever can have a different default per driver.

| Lever | Model file | pulsedIV | radIV | seeIV | fieldPlate | calibIdVg |
|---|---|---|---|---|---|---|
| `trapEn` | 0 | 1 | forced: `useTraps` | 1 | forced 0 | forced 0 |
| `trapShape` | gauss | gauss | forced: field | field | (traps off) | (traps off) |
| `trapLevel` | 0.68 | 0.68 | 0.30 | 0.68 (TrapN ~0) | (traps off) | (traps off) |
| `hotEb` | 0.3 | 0.3 | 1.0 | 0.3 | 1.0 (Te column only) | (traps off) |
| `hotTau` | 1e-13 | 1e-13 | 1e-14 | 1e-13 | 1e-14 (Te column only) | (traps off) |
| `dampValue` | not a lever | 0.10 | 0.05 | 0.05 | 0.05 | not set |
| `retryDepth` | not a lever | 5 | 6 | 6 | 5 | no retry |
| `occSafe` | off | off | off | 1 | off | off |
| `tranSign` | 0 | 0 | 0 | 1 | 0 | 0 |

## Model file (`model/GaN_modelfile_masterD`)

| Lever | Default | Meaning |
|---|---|---|
| `mobModel` | field | `field` (calibrated) or `static` (600); read in `model/GaN.tcl` ([[mobility-models]]) |
| `trapEn` | 0 | Enable the trap model (`IonizedAcceptor` in GaN and AlGaN; `InsTrapCharge` in Nitride and HighK when `insTrapSign` is not 0). Driver values above |
| `trapPeak` | 4e18 | Peak density (cm⁻³) |
| `trapMeanX`, `trapMeanY` | 0.0, 0.20 | Centre (µm; x 0 = AlGaN top, 0.015 = 2DEG; y gate drain edge = 0.125) |
| `trapSigma` | 0.025 | Spatial σ (µm) |
| `trapSigmaY` | unset | Lateral σ for an anisotropic Gaussian (then `trapSigma` is depth only) |
| `trapShape` | gauss | `gauss`, `cone` or `field` (proc `TrapConc_<name>`; add TRIM etc. the same way). `field` returns the data field `TrapN`, which `Initialize` sets to ~0 and radIV writes ([[damage-model]]) |
| `coneLen`, `coneAngle`, `coneW0`, `coneEdge` | 0.1, 30, 0.01, 0.01 | Cone geometry (apex at the trap centre, axis +x) |
| `trapLevel`, `trapWidth` | 0.68, 0.1 | Depth below Ec, energy FWHM (eV) |
| `insTrapSign` | 0 | Insulator trap charge: -1 = the trap density fully filled (-q·N), +1 = +q·N ([[insulator-traps]]) |
| `polCharge` | 7.0e12 | AlGaN/GaN polarization charge (cm⁻²), sets the 2DEG |
| `polWinFac`, `polWinYmin`, `polWinYmax` | unset | Interface polarization charge factor in a y window (µm); set all three (2026-11-04, radVth) |
| `surfCharge` | unset | Fixed charge at the AlGaN/SiN surface (cm⁻²) |
| `hotEb`, `hotTau`, `hotMu`, `hotVsat` | 0.3, 1e-13, 600, 1.9e7 | [[hot-electron-capture]] |
| `eTemp`, `etTau`, `etMob`, `etStats`, `etThermo`, `etThermoJ`, `etThermoE`, `etFloor`, `etNeg`, `etDamp`, `etConv` | 0, 1e-12, low, 0, 0, 1, 1, 1e10, 0, 5.0, 0 (etStats/etThermo defaults 1 → 0 on 2026-10-13) | [[energy-balance]] |

## Material and equation files (`GaN.tcl`, `Metal.tcl`, `Continuity.tcl`, `Poisson.tcl`)

| Lever | File | Default | Meaning |
|---|---|---|---|
| `mobMumax` | GaN.tcl | unset = 1907 | `mumax` of the field mobility (cm²/Vs). Field mobility only |
| `mobNref` | GaN.tcl | unset = 1e17 | `Nref` of the field mobility (cm⁻³) |
| `mobVsat` | GaN.tcl | unset = 3.3e7 - 3.0e6·(T/300) | Saturation velocity of the Heller high-field term (cm/s) |
| `mobDamFac` | GaN.tcl | unset | Low-field mobility factor inside the window `mobDamYmin`/`mobDamYmax`/`mobDamXmax`, through the data field `MobDam` that radIV sets (radRon, [[ron-increase]]) |
| `phiB` | Metal.tcl | 1.65 | Gate/FP barrier vs Nitride Ec (eV); rigid Vth shift |
| `pGaN` | Metal.tcl | 0 | 1 = treat the gate as an ohmic pGaN contact; `phiB` then enters only the initial guess (`InitMetal`). No params file sets it |
| `tranSign` | Continuity.tcl | unset = 0 | Sign of the transport term. 0 = old form; 1 = FLOOXS's own form, needed for transients. DC solutions are unchanged; contact fluxes change sign |
| `srhTau` | Continuity.tcl | unset = off | SRH recombination R = np/(τ(n+p)) in both continuity equations (s). Ian OK 2026-10-29 for the single-event transient; seeGen1 and seeSmoke1 used 1e-9 |
| `seeGenExpr` | Continuity.tcl | unset = off | Pair generation term (cm⁻³ s⁻¹). Built by seeIV from its `see*` levers; not set by hand |
| `carFloor` | Continuity.tcl | unset = off | Additive floor on Elec and Hole (cm⁻³), a floating-point guard for fully depleted regions (Ian approved 2026-10-29). stressFloor1 used 1e-100 and 1e-30 |
| `occSafe` | Poisson.tcl | unset = off | 1 = trap occupancy written as w·e⁻ᵃ/(e⁻ᵃ + g), the same function without the exp overflow. Needed for a stress above Vd ~17.7 V (jobs 48125435-48161617), so every study that reaches the 28 V stress sets it; seeIV default 1 |
| `emitFrac` | Poisson.tcl | unset | Crude emission: fraction of the charge released before each capture. Live occupancy still sets the floor. 1 = no memory (radEmit) |

## Device decks (`model/rfdevice.tcl`, `rfdevice_SiN.tcl`, `rfdevice3d.tcl`)

| Lever | Decks | Default | Meaning |
|---|---|---|---|
| `deviceDeck` | (driver lever) | rfdevice.tcl in every driver | Deck file name inside `modelDir`: `rfdevice.tcl` (HighK), `rfdevice_SiN.tcl` or `rfdevice3d.tcl` (3D, with radIV `deviceDim 3`). Give the bare file name: drivers source `[file join $modelDir $deviceDeck]`, so `model/rfdevice_SiN.tcl` would resolve to `model/model/…` |
| `meshY` | all three | unset | Local mesh refinement, `{y spacing y spacing ...}` in µm. Lines needn't be in order. FLOOXS grades the spacing only between neighbouring lines, so a deck line inside a patch keeps its own spacing: rightFP (y 0.725, 20 nm) and DrainT (0.485, 10 nm) break any patch around them (the library's '5 nm at 0.8' is 15 nm). Cancel them with helper lines just beside them (e.g. 0.72/0.73 at 5 nm); a meshY line exactly on a deck line makes zero-area faces and FLOOXS aborts ([[stress-library]], [[mesh]]) |
| `bot2d` | 2D | unset = 7.5 | Buffer depth (µm), for 3D comparisons (2026-11-12; rad3dRod, rad3dSolve) |
| `yCoarse` | 2D and 3D | 1.0 | Factor on the 0.05 µm spacing of the outer y lines (source end and the drain-gate line) |
| `fpBoxOld` | all three | 0 = fixed | The FP contact box (2026-11-20). The pre-fix box also covered the drain half of the T-gate head, which held part of the gate metal at the FP potential ([[fp-contact-fix]]). 0 builds a box matching the FP metal; 1 rebuilds the old box, only to reproduce pre-2026-11-20 runs. The new default changes behaviour on purpose (Ian: fix the bug). radIV writes `fpBox=fixed|old` into every saved stress state's settings file, and stressLoad / stressResume refuse a state whose box differs from the run's fpBoxOld (no entry = old) |
| `passMat` | 3D | HighK | Passivation above the gate nitride: `HighK` or `Nitride` ([[3d-plan]]) |
| `W3d` | 3D | 0.5 | Slice width along the gate width (µm); with `deviceDim 3` radIV divides the contact current by it |
| `zSpac0`, `zSpac1` | 3D | 0.02, 0.1 | z spacing at the track wall z = 0 and at z = W3d (µm) |
| `bot3d` | 3D | 7.5 | Buffer depth (µm) |
| `init3d` | 3D | "quad nogas" | Options of `init` (bricks, no gas region) |
| `mathDev3d` | 3D | "col umf none scale" | 3D device solver options; UMFPACK fails above ~50k points |
| `meshZ` | 3D | unset | Extra z lines, `{z spacing ...}` (µm) |

## `drivers/pulsedIV.tcl` (Sep-Oct curve-tracer driver)

| Lever | Default | Meaning |
|---|---|---|
| `Vg_meas` | -2.0 | Gate bias of the sweep (rest point) |
| `Vd_max`, `Vd_step` | 1.6, 0.1 | Sweep |
| `fillIters`, `fillRelax` | 4, 0.5 | FillStep iterations and Te relaxation |
| `dampValue` | 0.10 | Newton damping (sweeps use 0.05) |
| `retryDepth`, `retrySubFill` | 5, 1 | [[retry-bisection]] |
| `teRamp`, `teRampW0`, `teRampMin`, `teRampTol`, `teRampMax` | 1, 0.1, 0.002, 0.01, 300 | [[te-ramp]] |
| `sweepIterLimit` | 300 | Newton iteration limit (= deck `Math iterLimit`). It is set after Initialize and before `device init`, so it covers the gate ramp and the Vd sweep ([[flooxs-gotchas]]). Tested 50/100 (job 45801978): 100 = no wall-time gain; 50 = 15-20% faster but changes post-collapse Id up to 9x (extra bisections change the trap-fill history). Keep 300 ([[retry-bisection]]) |
| `deviceDeck` | rfdevice.tcl | See the deck table |
| `ivCSV` | figures/pulsedIV.csv | Output (Vd, Id mA/mm, peak Te K); sweeps always set their own |
| `teProfile` | {} | Vd list for ETemp cut dumps ([[energy-balance]]) |
| `trapEn` and the trap set | 1; trapPeak 4e18, trapMeanX 0.0, trapMeanY 0.20, trapSigma 0.025, trapLevel 0.68, trapWidth 0.1, hotEb 0.3, hotTau 1e-13 | pulsedIV turns the traps on and repeats the model file's trap defaults |

`drivers/pulsedIV.tcl`'s trap defaults are the model file's (0.68 eV / `hotEb` 0.3 / `hotTau` 1e-13), not [[run-F]]: sweeps always set the levers explicitly.

## `drivers/radIV.tcl` (radiation study, all work since 2026-10-23)

**Driver overrides.** Before it sources the model file, radIV sets its own defaults: `trapLevel` 0.30, `trapWidth` 0.1, `hotEb` 1.0 and `hotTau` 1e-14 (the late-onset set, [[late-onset-search]]), `fillIters` 4, `fillRelax` 0.5, `dampValue` 0.05, `retryDepth` 6, and measurement and stress defaults `Vd_max` 10, `Vd_step` 0.25, `Vg_out` +1, `Vg_stress` -10 and `Vd_stress` 28. It overwrites `trapEn` (= `useTraps`: `radState post` with any damage lever set; `damGaussF` counts since 2026-11-20) and `trapShape` (`field`) unconditionally, so a params value for those two is ignored.

**Rad baseline block.** radIV keeps the model file's calibration defaults (polCharge 7.0e12, phiB 1.65, the GaN.tcl mobility; [[calibration]]). Every radIV params line from radDam2 on therefore starts with the rad pre-irradiation calibration `polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100` ([[rad-model]]; radCal1-3 searched for it, and radDam1 used mobVsat 2.0e7 without mobMumax), and post lines usually add `surfCharge=-4.0e11`. A radIV run without the block mixes the rad-era trap defaults with the older calibration.

**Run and solver**

| Lever | Default | Meaning |
|---|---|---|
| `radState` | pre | `pre` = trap-free device; `post` = stress, damage, then the same measurements |
| `tag` | = radState | Output prefix (radIV.slurm sets it to the params label) |
| `mobModel`, `eTemp` | field, 0 | As in the model file |
| `deviceDim` | 2 | 3 with `deviceDeck=rfdevice3d.tcl`: the contact current is divided by `W3d` ([[3d-plan]]) |
| `qfnAbs` | unset (model 1e-2) | Qfn Abs.Error (V) in GaN/AlGaN for the whole run. Set before the solver is built; with 1e-2 the off-state stress cannot converge above Vd ~17 V (job 48125435). stressAbs2, stressClamp1, stressDiag2/3, stressFloor1 and stressSafe1 used 1.0 (stressAbs2 also 0.1) |

**Measurements**

| Lever | Default | Meaning |
|---|---|---|
| `Vd_lin`, `Vg_hi`, `Vg_lo`, `Vg_step` | 0.1, 1.0, -4.0, 0.05 | Id-Vg at Vd_lin, Vg_hi down to Vg_lo |
| `Vg_out`, `Vd_max`, `Vd_step` | 1.0, 10.0, 0.25 | Id-Vd at Vg_out, Vd 0 to Vd_max |
| `doIdVg`, `doIdVd` | 1, 1 | 0 skips that curve |
| `VgFam` | {} | Extra Id-Vd curves at these Vg, in order, to `<tag>_IdVdG<Vg>.csv` |
| `noRampBack` | 0 | Stop after the last curve, with no ramp back to rest. Ignored when `VgFam` or `damList` is set |
| `emitRest` | 0 | Fraction of the captured charge released at rest before each Id-Vd curve |
| `vdCuts` | 0 | 1: at every Id-Vd point appends cuts along y to `<tag>_vdcuts.txt`: IonAcceptor, Elec, lateral field Ey and TeTrap 1 nm below the AlGaN/GaN interface (x 0.016 µm), plus IonAcceptor and TeTrap mid-barrier (x 0.008, labels `*_x0.008`); 2026-11-19. Read with `analysis/vdcuts.py`. On the library states the GaN-side damage was fully filled at rest and stayed constant through the sweep, and the barrier damage was ~1% filled at rest and is the part that can fill with hot electrons ([[step-mechanism]]; pre-fix; being rerun, [[fp-contact-fix]]) |
| `Rgd` | 0 | Lumped gate-drain leakage (Ω·mm), Id_ext = Id_dev + (Vd - Vg)/Rgd; post-processing only. No committed params file sets it |

**Stress** (details and the saved-state library: [[stress-library]])

| Lever | Default | Meaning |
|---|---|---|
| `Vg_stress`, `Vd_stress` | -10.0, 28.0 | Irradiation (stress) bias |
| `stressStep` | 1.0 | Drain step of the stress ramp (V), bisected on failure; targets are its multiples, then Vd_stress |
| `Vd_stressMin` | 12.0 | A ramp that stops early is accepted if it reached at least this Vd (without occSafe the ramp stops near 17.7 V, which gave the Nov 11 model its 17.66 V stress) |
| `stressSkip` | 0 | 1: no stress solve, for damage that doesn't use the stress field (damSites, surfCharge, a uniform dam2/dam3 site); the stress fields are then ~0. It stops with an error when a law needs the field (damPeak, a field-scaled dam2 or damIns site, damList); since 2026-11-20 the check also covers field-scaled `damGauss`, `damGaussF` and field-scaled tracks |
| `stressNoHoles`, `stressNoHolesX` | 0, 0.1 | 1: solve the stress without holes above x = stressNoHolesX (µm; Qfp frozen at +50 V there), restored at rest (Ian, 2026-10-26). radNHsmoke, stressDiag2 |
| `stressDiag`, `stressDiagStep` | 0, 0.25 | 1: after the ramp stops, try one more drain step and write fields and Newton changes along cuts to `<tag>_stressDiag.txt` |
| `stressSave`, `stressLoad` | "", "" | Save the state after the stress and the ramp back to rest; load a saved state and skip the stress (2026-11-14) |
| `stressSaveEvery`, `stressSaveDir`, `stressSavePrefix` | 0 (off), ".", "" (= tag) | Save the state at bias at every multiple of stressSaveEvery (V) during the ramp (2026-11-15) |
| `stressResume`, `stressOnly` | "", 0 | Continue a ramp from a state saved at bias; stop after the ramp |

- **stressSave / stressLoad history.** Local check: identical Id-Vd to all digits ([[flooxs-commands]]). HPG check radStressIO (2026-11-15): the load run was identical to the save run (Id-Vd, Vth, gm, peakN) in 1 h 14 min against 9 h 07 min. A strike variant loaded from a stress saved without refinement round the strike differs near the ~2 V drop (399 vs 426 mA/mm at 2.3 V), so save the stress on a mesh already refined at every strike position.
- **Stress library history.** The 2026-11-15 library (`/blue/ee1/ianstafford/stress/<deck>_Vg-10/`, 1 V steps to 84 V) has the old FP box. Its mesh has 93,080 points (179 x 520; meshY with 5 nm patches at the strike sites), each state is about 13.7 MB gzipped. Rounds A-K, rad28strikeL and radStepDiag loaded its states (28 V; round E also 24 and 30 V); radStepM / M2 loaded the mesh-check states. A fixed-box library is being built. Both are described in [[stress-library]]; the actual spacing is in [[step-search-28v]].

**Damage** (formulas and the studies that used each law: [[damage-model]])

| Lever | Default | Meaning |
|---|---|---|
| `damPeak`, `damEref`, `damM`, `damMax` | 0.0, 1.0e6, 2.0, 1.0e19 | Field damage N = min(damMax, damPeak·(F/damEref)^damM) (cm⁻³, V/cm) |
| `damXmax`, `damYmin`, `damYmax` | 0.05, -1.0e3, 1.0e3 | Its window: x 0 to damXmax (µm below the AlGaN top), y window (also used by damIns*) |
| `damField` | lat | Stress field F: `lat` = lateral, `tot` = total, `ne` = normalised n·E |
| `damNexp`, `damNref` | 0.0, 1.0e17 | First site also times (ElecStress/damNref)^damNexp; 0 = field only |
| `dam2Peak`, `dam2M`, `dam2Ymin`, `dam2Ymax` | 0.0, 0.0, 0.65, 1.0 | Second field site, own y window |
| `dam2Field`, `dam2Eref`, `dam2Xmax` | "", "", "" | "" = damField, damEref, damXmax |
| `dam3Peak`, `dam3Ymin`, `dam3Ymax` | 0.0, 1.0, 1.6 | Uniform site in a y window |
| `damInsPeak`, `damInsEref`, `damInsM`, `damInsXmin`, `damInsField` | 0.0, 1.0e6, 2.0, -0.05, tot | Fixed charge in the insulator (damInsXmin ≤ x < 0) |
| `insTrapSign` (radIV) | -1 when damInsPeak > 0 and unset | Sign of that charge; must be a task lever, not a damList entry |
| `damSites` | {} | Uniform acceptor sites `{ymin ymax xmin xmax N}` (µm, cm⁻³), any number ([[damage-region-map]]) |
| `damGauss`, `gaussFieldM` | {}, 0.0 | Gaussian strikes `{y x sigma N}`; gaussFieldM m ≠ 0 scales them by (F/damEref)^m, capped at damMax |
| `damGaussF`, `gaussFieldMF` | {}, 4.0 | A second strike list that is always field-scaled |
| `damTube`, `damRod`, `trackFieldM` | {}, {}, 0.0 | 3D ion tracks along the depth / along the gate width; trackFieldM scales damTube only |
| `damList` | {} | Several damage settings after one stress solve, `{{suffix {lever value ...}} ...}` |
| `mobDamYmin`, `mobDamYmax`, `mobDamXmax` | -1.0e3, 1.0e3, 0.05 | Window of `mobDamFac` (radIV defaults; µm) |

- **gaussFieldM** (2026-11-18): local check on the 28 V states. A 3e18 strike at y 0.5 µm with m = 4 peaks at 9.4e18 in SiN and 5.2e17 in HighK, because SiN's field under the T-gate overhang is 2.1x HighK's (pre-fix; being rerun, [[fp-contact-fix]]).
- **damGaussF / gaussFieldMF** (2026-11-18): lets one run mix field-scaled strikes near the gate with plain strikes further out. Local check on the 28 V SiN library state: the damGaussF strike reproduces round I's damGauss + gaussFieldM 4 peak exactly (1.400982e18).

## `drivers/seeIV.tcl` (single-event transient, [[see-plan]])

| Lever | Default | Meaning |
|---|---|---|
| `tag`, `deviceDeck`, `mobModel`, `eTemp` | see, rfdevice.tcl, field, 0 | Run setup |
| `dampValue`, `retryDepth` | 0.05, 6 | As in radIV |
| `Vg_bias`, `Vd_bias`, `Vd_rampStep` | -10.0, 28.0, 1.0 | DC bias of the strike; drain ramp step (V) |
| `seeStrike` | 1 | 0 = the same transient without injection (control) |
| `seeMethod` | gen | `gen` = Gaussian-in-time pair generation; `qf` = quasi-Fermi reset at t = 0 (does not run: no first time step converges) |
| `seeY0`, `seeSigma`, `seeWeff`, `seePairs` | 1.0, 0.05, 1.0, 4.3e10 | Strike position (µm), track σ (µm), effective width of the 2D slab (µm), pairs/cm along the track |
| `seeXmin`, `seeXmax` | 0.0 (0.0155 for qf), 1.4 | Depth range of the track (µm) |
| `seeGenTau` | 1.0e-12 | Width of the generation pulse (s); centred at 3·seeGenTau |
| `seeTinit`, `seeTend`, `seeUserStep` | 1.0e-15, 1.0e-9, 0.0 | Transient first step, end time, step cap (0 = none) |
| `seeCutTimes` | {1e-13 1e-12 ... 1e-7} | Times of the `<tag>_cuts_<k>.txt` cuts |
| `seeMapTimes`, `seeMapDC` | {}, 0 | Times of the `<tag>_map_<k>.vtk` maps; 1 = also a map of the DC state |
| `seeInjectOnly` | unset | 1 = stop after the qf injection checks |
| `trapEn`, `trapShape`, `occSafe`, `tranSign` | 1, field, 1, 1 | Numerics: trap model on with an empty density, overflow-safe occupancy, transient sign of the transport term |
| `qfnAbs` | unset | As in radIV |

## `drivers/calibIdVg.tcl` ([[calibration]])

| Lever | Default | Meaning |
|---|---|---|
| `deviceDeck`, `mobModel` | rfdevice.tcl, field | Run setup; `trapEn` is forced to 0 |
| `calCSV` | figures/calib_IdVg.csv | Output (Vg, Id mA/mm) |
| `Vd_cal` | 10.0 | Drain bias of the transfer curve (V) |
| `Vg_max`, `Vg_min`, `Vg_step` | 1.0, -4.0, 0.1 | Gate sweep, Vg_max down to Vg_min |
| `Rs_contact`, `Rd_contact` | 0.0, 0.0 | Lumped contact resistances (Ω·mm), SolveRc fixed-point iteration |
| `calHook` | unset | Tcl script evaluated after the deck is sourced, e.g. `pdbSetDouble` calls |

## Legacy and no-effect levers

- `occClamp` (Poisson.tcl, 2026-10-29): capped the occupancy exponent via abs(); replaced by `occSafe` (commit e7227cd) and no longer read. Used by `params_stressClamp1.txt`.
- `stressQfnAbs`, `stressQfnDamp` (radIV, defaults 1.0e-2 and 0.1): still read, but they change pdb values mid-run, which FLOOXS ignores (it reads them only when the solver is built). No effect; use `qfnAbs`. Used by `params_stressAbs1.txt` and `params_radQDsmoke.txt`.
- The pulsedIV-era params files (`params_curveTracer`, `params_sensitivity`, `params_eTemp*`, `params_onsetField*`, `params_posMap*`, `params_trapMapF_field`, `params_deckVg1`, `params_iterLimit`, `params_vgEB*` ...) are positional columns, mapped to levers by a `sweeps/pulsedIV_*.slurm` template, not by name. The eTemp-format files (`params_eTemp*`, `params_iterLimit`, `params_vgEB*`, `params_reorgCheck`) share `pulsedIV_eTemp.slurm` (`PARAMS=`); `params_eTempDebug` goes with `eTempDebug.slurm`.
