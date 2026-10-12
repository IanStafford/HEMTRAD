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
| `eTemp`, `etTau`, `etMob`, `etStats`, `etThermo`, `etThermoJ`, `etThermoE`, `etFloor` | 0, 1e-12, low, 1, 1, 1, 1, 1e10 | [[energy-balance]] |

## Driver (`drivers/pulsedIV.tcl`)
| Lever | Default | Meaning |
|---|---|---|
| `Vg_meas` | −2.0 | gate bias of the sweep (rest point) |
| `Vd_max`, `Vd_step` | 1.6, 0.1 | sweep |
| `fillIters`, `fillRelax` | 4, 0.5 | FillStep iterations and Te relaxation |
| `dampValue` | 0.10 | Newton damping (sweeps use 0.05) |
| `retryDepth`, `retrySubFill` | 5, 1 | [[retry-bisection]] |
| `teRamp`, `teRampW0`, `teRampMin`, `teRampTol`, `teRampMax` | 1, 0.1, 0.002, 0.01, 300 | [[te-ramp]] |
| `deviceDeck` | rfdevice.tcl | or `model/rfdevice_SiN.tcl` |
| `ivCSV` | figures/pulsedIV.csv | output (Vd, Id mA/mm, peak Te K); sweeps always set their own |
| `teProfile` | {} | Vd list for ETemp cut dumps ([[energy-balance]]) |

`drivers/pulsedIV.tcl`'s trap defaults are the model file's (0.68 eV / `hotEb` 0.3 / `hotTau` 1e-13), not [[run-F]]: sweeps always set the levers explicitly. `drivers/calibIdVg.tcl` levers: see [[drivers]].
