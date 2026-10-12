---
title: Drivers
tags: [tools, driver]
---
# Drivers (Tcl decks that run a measurement, in `drivers/`)

**Finding the model:** each driver sets `modelDir` (unless already set) to `.` if `GaN_modelfile_masterD` is in the current directory (a flat sweep task dir), else `model` if the current directory has a `model/` folder (running from the repo root), else `../model` relative to the driver. It then sources `$modelDir/GaN_modelfile_masterD` and `$modelDir/$deviceDeck`; the model file sources its siblings from `$modelDir` (default: its own folder). Run from the repo root: `flooxs drivers/pulsedIV.tcl`.

- **`drivers/pulsedIV.tcl`** — curve-tracer model, the main tool. Sources `model/GaN_modelfile_masterD` and `$deviceDeck`, `Initialize`, ramps the gate to `Vg_meas` (traps at steady state, `CaptureTraps`), then sweeps Vd with `FillStep` at each point (fill-only, no emission). Each point is wrapped in [[retry-bisection]] with the [[te-ramp]] fallback. Writes `$ivCSV` (Vd, Id mA/mm, peak Te K); logs `PULSED`, `RETRY`, `TERAMP`, `ETEMP`, `PULSED GAVE UP`. Levers in [[levers]]. Trap defaults are the model file's, so sweeps always set [[run-F]]-style levers explicitly.
- **`drivers/calibIdVg.tcl`** — trap-free transfer curve for [[calibration]]: Vd ramp to `Vd_cal` (10 V), Vg +1 → −4 V; `Rs_contact`/`Rd_contact` (Ω·mm, SolveRc iteration), `calCSV`, `deviceDeck`, `mobModel`.
- **`drivers/stressFreeze.tcl`** — quiescent stress: `HotStress` at (VgQ, VdQ), `FreezeTraps`, measure Id–Vd at Vg −2. Static era: (−2, 10) gave a 46% drop plus knee walkout; (−4, 20) NaN at Vd ≈ 17.5 V. Not rerun with field mobility; it's the proposed off-state pre-stress test in [[field-driven-trapping]].
- **`drivers/trapPlot.tcl`** — older dynamic-trap driver (Id–Vd plus trap profile dumps via `print1d`).
- **`drivers/eTempDebug_tail.tcl`** (+ `sweeps/eTempDebug.slurm`) — appended after `drivers/pulsedIV.tcl` with `Vd_max 0`: attempts one bias step with Newton capped at 1 and 2 iterations and dumps ETemp/Qfn/Elec/DevPsi/Δ peaks and cuts ([[energy-balance]]).
- Device decks: `model/rfdevice.tcl`, `model/rfdevice_SiN.tcl` ([[device-structure]]). Model files: `model/GaN_modelfile_masterD` (CRLF), `model/GaN.tcl`, `model/AlGaN.tcl`, `model/Insulator.tcl`, `model/Metal.tcl` (CRLF), `model/Continuity.tcl` (CRLF), `model/Poisson.tcl`, `model/ETemp.tcl`.
- Archived drivers (`archive/static_mobility/`): `fieldpeak.tcl` (HighK εr bug — its "SiN" run was HighK), `fieldPlateTest.tcl`, `mobilityCompare.tcl`, `IV.tcl` (sources a missing `powerdevice.tcl`).
- A GaN starter copy (trap-free I–V focus, `quickIV.tcl`) lives in flooxs-pyplot `Test/SimpDev/GaNSuite` ([[repo-locations]]).
