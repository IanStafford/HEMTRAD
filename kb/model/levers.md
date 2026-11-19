---
title: Levers
tags: [model, reference]
source: model/GaN_modelfile_masterD, drivers/pulsedIV.tcl, model/Metal.tcl
---
# Levers

Every lever has an `info exists` default, so a driver or array task sets it before sourcing the model file.

## Model (`model/GaN_modelfile_masterD`, `model/Metal.tcl`)
| Lever | Default | Meaning |
|---|---|---|
| `mobModel` | field | `field` (calibrated) or `static` (600) — [[mobility-models]] |
| `trapEn` | 0 (model file) / 1 (`drivers/pulsedIV.tcl`) | enable traps |
| `trapPeak` | 4e18 | peak density (cm⁻³) |
| `trapMeanX`, `trapMeanY` | 0.0, 0.20 | centre (µm; x 0 = AlGaN top, 0.015 = 2DEG; y gate drain edge = 0.125) |
| `trapSigma` | 0.025 | spatial σ (µm) |
| `trapSigmaY` | unset | lateral σ for an anisotropic Gaussian (then `trapSigma` is depth only) |
| `trapShape` | gauss | `gauss` or `cone` (proc `TrapConc_<name>`; add TRIM etc. the same way) |
| `coneLen`, `coneAngle`, `coneW0`, `coneEdge` | 0.1, 30, 0.01, 0.01 | cone geometry (apex at the trap centre, axis +x) |
| `trapLevel`, `trapWidth` | 0.68, 0.1 | depth below Ec, energy FWHM (eV) |
| `insTrapSign` | 0 | insulator trap charge — [[insulator-traps]] |
| `polCharge` | 7.0e12 | AlGaN/GaN polarization charge (cm⁻²), sets the 2DEG |
| `phiB` | 1.65 | gate/FP barrier vs Nitride Ec (eV); rigid Vth shift (`model/Metal.tcl`) |
| `surfCharge` | unset | fixed charge at the AlGaN/SiN surface (cm⁻²) |
| `hotEb`, `hotTau`, `hotMu`, `hotVsat` | 0.3, 1e-13, 600, 1.9e7 | [[hot-electron-capture]] |
| `eTemp`, `etTau`, `etMob`, `etStats`, `etThermo`, `etThermoJ`, `etThermoE`, `etFloor`, `etNeg`, `etDamp`, `etConv` | 0, 1e-12, low, 0, 0, 1, 1, 1e10, 0, 5.0, 0 (etStats/etThermo defaults 1 → 0 on 2026-10-13) | [[energy-balance]] |

## Driver (`drivers/pulsedIV.tcl`)
| Lever | Default | Meaning |
|---|---|---|
| `Vg_meas` | −2.0 | gate bias of the sweep (rest point) |
| `Vd_max`, `Vd_step` | 1.6, 0.1 | sweep |
| `fillIters`, `fillRelax` | 4, 0.5 | FillStep iterations and Te relaxation |
| `dampValue` | 0.10 | Newton damping (sweeps use 0.05) |
| `retryDepth`, `retrySubFill` | 5, 1 | [[retry-bisection]] |
| `teRamp`, `teRampW0`, `teRampMin`, `teRampTol`, `teRampMax` | 1, 0.1, 0.002, 0.01, 300 | [[te-ramp]] |
| `sweepIterLimit` (pulsedIV.tcl) | 300 (= deck `Math iterLimit`; set after Initialize, before `device init`, so it covers the gate ramp and the Vd sweep — see [[flooxs-gotchas]]). Tested 50/100 (job 45801978): 100 = no wall-time gain, 50 = 15-20% faster but changes post-collapse Id up to 9x (extra bisections change the trap-fill history); keep 300 | [[retry-bisection]] |
| `deviceDeck` | rfdevice.tcl | or `model/rfdevice_SiN.tcl` |
| `ivCSV` | figures/pulsedIV.csv | output (Vd, Id mA/mm, peak Te K); sweeps always set their own |
| `teProfile` | {} | Vd list for ETemp cut dumps ([[energy-balance]]) |

`drivers/pulsedIV.tcl`'s trap defaults are the model file's (0.68 eV / `hotEb` 0.3 / `hotTau` 1e-13), not [[run-F]]: sweeps always set the levers explicitly. `drivers/calibIdVg.tcl` levers: see [[drivers]].

## Radiation studies (`drivers/radIV.tcl`, 2026-11-04; all default off)
| Lever | Default | Meaning |
|---|---|---|
| `damSites` | {} | Uniform acceptor sites `{ymin ymax xmin xmax N}` (µm, cm⁻³), any number ([[damage-region-map]]) |
| `stressSkip` | 0 | Skip the stress solve when no damage law uses the stress field |
| `emitFrac` (`Poisson.tcl`) | unset | Crude emission: fraction of the charge released before each capture. Live occupancy still sets the floor. 1 = no memory |
| `emitRest` | 0 | Fraction of the captured charge released at rest before each Id–Vd curve |
| `noRampBack` | 0 | Stop after the last curve, with no ramp back to rest. Ignored when `VgFam` or `damList` is set |
| `meshY` (`rfdevice*.tcl`) | unset | Local mesh refinement, `{y spacing y spacing ...}` in µm. Lines needn't be in order. FLOOXS grades the spacing only between neighbouring lines, so a deck line inside a patch keeps its own spacing: rightFP (y 0.725, 20 nm) and DrainT (0.485, 10 nm) break any patch around them (the library's '5 nm at 0.8' is 15 nm). Cancel them with helper lines just beside them (e.g. 0.72/0.73 at 5 nm); a meshY line exactly on a deck line makes zero-area faces and FLOOXS aborts |
| `VgFam` | {} | Extra Id–Vd curves at these Vg, in order, to `<tag>_IdVdG<Vg>.csv` |
| `mobDamFac`, `mobDamYmin/Ymax/Xmax` | unset | Low-field mobility factor in a window, GaN (`model/GaN.tcl`) |
| `polWinFac`, `polWinYmin/Ymax` | unset | Interface polarization charge factor in a y window |

- **stressSave / stressLoad** (radIV, 2026-11-14, default ""): `stressSave=<file>` writes the whole structure after the off-state stress and the ramp back to rest (`struct outfile`), plus `<file>.txt` with the stress settings. `stressLoad=<file>` builds the deck, replaces the structure with the file, re-issues the 2D contact biases, skips the stress and places damage as usual. The mesh comes from the file, so mesh levers of the loading run are ignored; Vg_stress, Vd_stress and deviceDeck are checked against `<file>.txt`. 2D only. Local check: identical Id-Vd to all digits ([[flooxs-commands]]). HPG check radStressIO (2026-11-15): load run identical to the save run (Id-Vd, Vth, gm, peakN) in 1 h 14 min against 9 h 07 min. A strike variant loaded from a stress saved without refinement round the strike differs near the ~2 V drop (399 vs 426 mA/mm at 2.3 V), so save the stress on a mesh already refined at every strike position.

- **Stress library** (radIV, 2026-11-15, all off by default): `stressSaveEvery` (V) saves the state at bias at every multiple of it during the stress ramp, with the stress fields computed, to `<stressSaveDir>/<stressSavePrefix>_Vd<Vd>.str.gz` plus a `.str.txt` settings file (`Vd_stress` = that Vd). `stressLoad` accepts these files (damage placed from that Vd; set the loading run's `Vd_stress` to match). `stressResume=<file>` continues a ramp from a saved state. `stressOnly 1` stops after the ramp (no ramp-down, damage or curves); a stalled ramp saves its last converged point. Library: `/blue/ee1/ianstafford/stress/<deck>_Vg-10/` (stressLib, 1 V steps to 84 V). Local check: resume and load reproduce the uninterrupted run exactly. The library mesh has 93,080 points (179 x 520; meshY with 5 nm patches at the strike sites) and the files are about 13.7 MB gzipped. Every round A-I task runs on this mesh (stressLoad keeps the file's mesh); its actual spacing is in [[step-search-28v]].

- **gaussFieldM** (radIV, 2026-11-18, default 0): multiplies the damGauss strike damage by (field/damEref)^m from the stored stress field (the damField field), capped at damMax. A strike then leaves dense damage only where the field was high during the biased irradiation. Local check on the 28 V states: a 3e18 strike at y 0.5 um with m = 4 peaks at 9.4e18 in SiN and 5.2e17 in HighK (SiN's field under the T-gate overhang is 2.1x HighK's).
- **damGaussF / gaussFieldMF** (radIV, 2026-11-18, default {} / 4.0): a second Gaussian strike list {y x sigma N} that is always field-scaled, N × (E/damEref)^gaussFieldMF capped at damMax, added alongside an unscaled damGauss list (gaussFieldM 0), so one run can mix field-scaled strikes near the gate with plain strikes further out. Local check on the 28 V SiN library state: the damGaussF strike reproduces round I's damGauss + gaussFieldM 4 peak exactly (1.400982e18).
- **vdCuts** (radIV, 2026-11-19, default 0): at every Id-Vd point appends cuts along y to `<tag>_vdcuts.txt`: IonAcceptor, Elec, lateral field Ey and TeTrap 1 nm below the AlGaN/GaN interface (x 0.016 um), plus IonAcceptor and TeTrap mid-barrier (x 0.008, labels `*_x0.008`). Read with `analysis/vdcuts.py`. The GaN-side damage is fully filled at rest and stays constant through the sweep; the barrier damage is ~1% filled at rest and is the part that can fill with hot electrons.
