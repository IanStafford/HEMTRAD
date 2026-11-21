---
title: Drivers
tags: [tools, driver]
date: 2026-11-20
source: drivers/*.tcl, drivers/trim/, model/rfdevice*.tcl, sweeps/radIV.slurm, sweeps/fieldPlate.slurm, sweeps/eTempDebug.slurm, sweeps/pulsedIV_*.slurm, progress.md
---
# Drivers (Tcl decks that run a measurement, in `drivers/`)

**Which driver.** `drivers/radIV.tcl` runs all the radiation work since 2026-10-23 (pre/post-irradiation curves, the stress library, the strike studies). `drivers/seeIV.tcl` runs the single-event transient. `drivers/pulsedIV.tcl` is the Sep-Oct curve-tracer driver of the trap-map and late-onset studies. Levers of every driver are in [[levers]].

**Finding the model:** each driver sets `modelDir` (unless already set) to `.` if `GaN_modelfile_masterD` is in the current directory (a flat sweep task dir), else `model` if the current directory has a `model/` folder (running from the repo root), else `../model` relative to the driver. It then sources `$modelDir/GaN_modelfile_masterD` and `$modelDir/$deviceDeck`; the model file sources its siblings from `$modelDir` (default: its own folder). Run from the repo root: `flooxs drivers/radIV.tcl`. `drivers/render3d_build.tcl` is the exception: it sources `model/` directly, so it runs from the repo root only.

**Headless runs.** pulsedIV and trapPlot have GUI lines (`window`, `chart`; trapPlot also `plot1d`) that segfault without a display. The sweep templates strip the `window` and `chart` lines with `sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /'` (CLAUDE.md §3); trapPlot has no template and its `plot1d` line is not covered by that sed.

## `drivers/radIV.tcl` (radiation study, current)

Pre/post-irradiation characterisation. `radState pre` is the trap-free device; `radState post` adds the stress and the damage. All levers have `info exists` defaults; radIV sets its own trap and solver defaults and forces `trapEn` / `trapShape` ([[levers]], "Driver overrides").

**Stages:**
1. **Build.** Source the model file and `$deviceDeck`. With `stressLoad` or `stressResume` the structure is replaced by the saved state, the five contacts are re-issued and DevPsi/Qfn/Qfp start from zero ([[stress-library]]). Then `Initialize` and `device init`.
2. **Stress** (post with a damage lever; skipped with `stressSkip 1` or a loaded state). Gate ramp to `Vg_stress` in 0.5 V steps, then the drain in `stressStep` steps to `Vd_stress`, each step with bisection (`RETRY`). A ramp that stops early is accepted from `Vd_stressMin` up. Optional states at bias every `stressSaveEvery` volts; `stressOnly 1` stops here. The stress fields (Estress, EstressT, EstressNE, ElecStress) are stored, then the device ramps back to rest; `stressSave` writes the state there.
3. **Damage.** `DamageIn` builds TrapN from the damage laws and switches it in at rest in seven scale steps (0 to 1), one solve each ([[damage-model]]). With `damList` stages 3-4 repeat per entry, with the traps reset in between.
4. **Measure.** Id-Vg at `Vd_lin` from `Vg_hi` down to `Vg_lo` (CaptureTraps at every point). Id-Vd at `Vg_out` from 0 to `Vd_max` (hot-electron FillStep at every point, fill-only). Then one Id-Vd curve per `VgFam` entry, each from rest.

**Outputs** (prefix `tag`; radIV.slurm sets it to the params label):
- `<tag>_summary.txt`: surfCharge, the stress (Vd reached, peak lateral field), damage peaks and settings, a loaded state's settings line, `done`.
- `<tag>_IdVg.csv` (Vg, Id_dev, Id_ext mA/mm); `<tag>_IdVd.csv` (Vd, Id_dev, Id_ext, peak Te); `<tag>_IdVdG<Vg>.csv` per VgFam entry. Id_ext differs from Id_dev only with `Rgd`.
- `<tag>_cuts.txt`: Estress, EstressT, EstressNE, TrapN and IonAcceptor along y at x -0.04, -0.01, 0.001 and 0.016 µm (IonAcceptor at x ≥ 0 only). These are `print1d` cuts, resampled to at most 500 points on fine meshes ([[flooxs-gotchas]]).
- `<tag>_vdcuts.txt` (`vdCuts 1`), `<tag>_stressDiag.txt` (`stressDiag 1`), saved states (`stressSave`, `stressSaveEvery`).
- With `damList` the damage-dependent outputs (`_IdVg`, `_IdVd`, `_IdVdG`, `_cuts`, `_vdcuts`) carry `<tag>_<suffix>`; the summary, `_stressDiag` and saved states keep `<tag>`.

**Log markers** (stdout, the SLURM `.out`):
- `RETRY <contact> <from> -> <to> failed (depth <n>)`: one bisection, harmless on its own.
- `IDVG <tag> Vg=… Id=…` and `IDVD <tag> Vg=… Vd=… Id=… peakTe=…`: progress lines.
- `RAMP GAVE UP <contact> at <v>`, `IDVG GAVE UP at Vg=…`, `IDVD GAVE UP at Vd=…`: a curve or ramp stopped early.
- `DAMAGE solve failed at scale <s>`, `emitRest solve failed`.
- `RADIV DONE tag=<tag>` at the end (`(stress only)` with `stressOnly`). It also follows any GAVE UP during the measurements (`IDVD`, `IDVG`, `RAMP`) and a failed damList entry, so check for GAVE UP as well.
- A Tcl error ends the task without RADIV DONE. Among them: `stress gate ramp failed`, `stress drain ramp failed at <Vd>`, `stress drain ramp-down failed`, `stress gate ramp-down failed`, `damage`, the stressLoad / stressResume checks (Vd_stress, Vg_stress, deviceDeck, FP box) and `stressSkip with a damage law that needs the stress field`.
- The summary file adds `<tg> damage failed`, `<tg> measurement failed` and `reset solve failed` for damList runs. The per-driver check list is in [[sweep-pattern]].

**Template and params.** `sweeps/radIV.slurm`, one task per params line `label|lever=value;...`; `DRV=seeIV` (env) runs `drivers/seeIV.tcl` instead ([[sweep-pattern]]). `analysis/genRadStudy.py` writes many of the rad-era params files and `analysis/genRad3d.py` the 3D ones ([[analysis-scripts]]). Results: [[rad-model]], [[damage-region-map]], [[step-search-28v]], [[step-mechanism]], [[fp-contact-fix]].

## `drivers/seeIV.tcl` (single-event transient)

A heavy-ion strike on the trap-free deck at a DC bias; plan and results in [[see-plan]].
1. DC steady state at the strike bias: gate ramp to `Vg_bias`, drain ramp to `Vd_bias` in `Vd_rampStep` steps (with bisection).
2. Strike along a vertical track at `y = seeY0`. `seeMethod gen` (default) adds a Gaussian-in-time pair generation to both continuity equations through `seeGenExpr` (Continuity.tcl). `seeMethod qf` resets the quasi-Fermi levels at t = 0; it does not run, because FLOOXS's TR-BDF2 first step never converges from the reset state.
3. Transient to `seeTend` with log-growing steps; terminal fluxes every step.

Numerics: the trap model is on with an empty density (`trapEn 1`, `trapShape field`, TrapN ~1e-30), `occSafe 1`, `tranSign 1`, and DevPsi Abs/Rel.Error 0.1 as radIV has them. With `trapEn 0` the off-state drain ramp diverged above Vd ~8-10 V (job 48241815).

Outputs: `<tag>_see.csv` (t, then Qfn/Qfp/DevPsi flux per contact S D G FP B, A/µm), `<tag>_summary.txt`, `<tag>_cuts_<k>.txt` (Elec, Hole, DevPsi along y at x 0.016 / 0.5 µm at each `seeCutTimes`), `<tag>_map_<k>.vtk` plus `.txt` with the time at each `seeMapTimes` (current densities JnX/JnY/JnMag, JpX/JpY/JpMag, densities MapN/MapP), `<tag>_map_dc.vtk` with `seeMapDC 1`. Maps are drawn by `analysis/plot_seeMaps.py`.

Log: `RETRY`, `RAMP GAVE UP` (then a Tcl error), `SEEIV DONE tag=<tag>` at the end, `SEEIV INJECT-ONLY DONE` with `seeInjectOnly`. A transient that stops early writes `transient stopped: …` to the summary and still ends in SEEIV DONE. Params files: seeSmoke1, seeGen1, seeGen2, seeIso1, seeMap28 (run with `DRV=seeIV`). The seeMap28 DC snapshots showed the FP contact bug ([[fp-contact-fix]]).

## `drivers/pulsedIV.tcl` (Sep-Oct curve-tracer driver)

The curve-tracer model of the trap-map, late-onset and energy-balance studies. Sources `model/GaN_modelfile_masterD` and `$deviceDeck`, `Initialize`, ramps the gate to `Vg_meas` (traps at steady state, `CaptureTraps`), then sweeps Vd with `FillStep` at each point (fill-only, no emission). Each point is wrapped in [[retry-bisection]] with the [[te-ramp]] fallback. Writes `$ivCSV` (Vd, Id mA/mm, peak Te K) and, with `teProfile`, `<ivCSV root>_Te_Vd<Vd>.txt` ETemp cuts. Logs `PULSED`, `RETRY`, `TERAMP`, `ETEMP`, `PULSED GAVE UP`; there is no completion line, so check that the CSV reaches `Vd_max`. Trap defaults are the model file's, so sweeps always set [[run-F]]-style levers explicitly. Templates: `sweeps/pulsedIV_<study>.slurm` (positional params columns); the static-era ones are in `archive/static_mobility/`.

## `drivers/calibIdVg.tcl`

Trap-free transfer curve for [[calibration]] against `data/rfDeviceHFO2_Experimental.csv`. Ramps Vd to `Vd_cal` (10 V) at Vg 0 in 0.25 V steps, ramps the gate up to `Vg_max`, then sweeps it down to `Vg_min` in `Vg_step` and writes `calCSV` (Vg, Id mA/mm). `Rs_contact`/`Rd_contact` (Ω·mm) are solved by the SolveRc fixed-point iteration; `calHook` runs a Tcl script after the deck is sourced. Logs `CAL Vg=… Id=…` and `RC WARNING` when SolveRc does not converge. `deviceDeck`, `mobModel` as usual.

## `drivers/fieldPlate.tcl`

Trap-free HighK vs SiN field check (2026-10-16), a port of `archive/static_mobility/fieldPlateTest.tcl` with the field mobility. Vg ramps to -2 V, then Vd 0.5-20 V in 0.5 V steps with bisection. Levers: `deviceDeck`, `tag` (highk), `mobModel`, `eTemp`, `dampValue` 0.05, `retryDepth` 5, and `hotEb` 1.0 / `hotTau` 1e-14 for the local-field Te column only (`trapEn` forced 0). Writes `fp_<tag>.csv` (Vd, Id mA/mm, peak |∇Qfn| in the channel, its position, Te) and, at Vd 3 / 10 / 20 V, `cutE_<tag>_<Vd>.txt` and `cutPsi_<tag>_<Vd>.txt` along the 2DEG (x 0.016 µm). Logs `RETRY`, `FP Vd=…`, `FP GAVE UP at Vd=…`, `FP DONE tag=…`. Template `sweeps/fieldPlate.slurm` (task 0 HighK, task 1 SiN); job 46241088 gave `figures/fieldPlateFM_sweep.csv` and `figures/fieldPlateFM_cuts.csv`. It ran with the pre-2026-11-20 FP contact box ([[fp-contact-fix]]). Result: [[highk-vs-sin]].

## `drivers/render3d_build.tcl`

Builds the 3D SiN slice (`passMat Nitride`, `W3d` 1.0, `bot3d` 1.5, `yCoarse` 2.0, `zSpac0` 0.02, `zSpac1` 0.1) with one Gaussian ion track (σ 30 nm, 2e19 cm⁻³, at y 0.5 µm, z 0) as the data field `Track`, plus `LogDoping`, and writes `sin3d.vtk`. No solve: about 1 min and a 45 MB file. Prints `VTK WRITTEN`. The file is for `analysis/render3d.py` ([[3d-plan]]).

## Older drivers

- **`drivers/trapPlot.tcl`**: older dynamic-trap driver (Id-Vd plus trap profile dumps via `print1d`). It hard-codes `rfdevice.tcl` and `figures/trapOccupation2.csv` and uses the GUI.
- **`drivers/eTempDebug_tail.tcl`** (+ `sweeps/eTempDebug.slurm`): appended after `drivers/pulsedIV.tcl` with `Vd_max 0`; meant to attempt one bias step (`dbgVd`, 0.1 V) with Newton capped at 1 and 2 iterations and dump ETemp/Qfn/Elec/DevPsi/Δ peaks and cuts ([[energy-balance]]). The cap never took effect: FLOOXS reads `Math iterLimit` once, when it builds the solver at the first solve after `device init`, and the tail sets it later. So the dumps followed full solves, and the readings drawn from them are unverified (Ian, 2026-11-20; [[flooxs-gotchas]]).
- **`archive/static_mobility/stressFreeze.tcl`** (archived 2026-11-20): quiescent stress, `HotStress` at (VgQ, VdQ), `FreezeTraps`, measure Id-Vd at Vg -2. Static era; superseded by the stress stage of `drivers/radIV.tcl`.
- Archived drivers (`archive/static_mobility/`): `fieldpeak.tcl` (HighK εr bug; its "SiN" run was HighK), `fieldPlateTest.tcl`, `mobilityCompare.tcl`, `IV.tcl` (sources a missing `powerdevice.tcl`).
- A GaN starter copy (trap-free I-V focus, `quickIV.tcl`) lives in flooxs-pyplot `Test/SimpDev/GaNSuite` ([[repo-locations]]).

## `drivers/trim/` (TRIM inputs)

SRIM-2013 TRIM input files, run on the workstation with `bin/trim_run.sh <TRIM.IN> <out_dir>` ([[trim]]). `TRIM_HEMT_template.IN` holds the device stack (HfO2 / Si3N4 / AlGaN / GaN). `TRIM_HighK_Au2256.IN` and `TRIM_SiN_Au2256.IN` run Au ions at 2256 MeV, 200 ions; the `_test20` copies run 20 ions. `analysis/trimTrack.py` turns a full-cascade output into per-layer track parameters, and `analysis/genRad3d.py` reads them from `data/trim/<deck>_track.json` to build `damTube` lists ([[damage-model]]). Device-specific inputs are kept untracked.

## Device decks and model files

- **2D decks:** `model/rfdevice.tcl` (HighK passivation) and `model/rfdevice_SiN.tcl` ([[device-structure]]). Levers `meshY`, `bot2d`, `yCoarse`, `fpBoxOld` ([[levers]]).
- **3D deck:** `model/rfdevice3d.tcl`, the 2D cross-section extruded along the gate width over 0..W3d with reflecting side walls (2026-11-12). Levers `passMat`, `W3d`, `zSpac0`/`zSpac1`, `bot3d`, `yCoarse`, `init3d`, `mathDev3d`, `meshY`, `meshZ`, `fpBoxOld`; radIV uses it with `deviceDim 3` ([[3d-plan]]).
- **Model files:** `model/GaN_modelfile_masterD` (CRLF), `model/GaN.tcl`, `model/AlGaN.tcl`, `model/Insulator.tcl`, `model/Metal.tcl` (CRLF), `model/Continuity.tcl` (CRLF), `model/Poisson.tcl`, `model/ETemp.tcl`.
