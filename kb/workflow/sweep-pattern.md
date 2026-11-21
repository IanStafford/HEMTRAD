---
title: Sweep pattern
tags: [workflow, hpg]
---
# The standard sweep pattern

The binding rules are in `CLAUDE.md` §2: ask before `sbatch`/`scancel`, and check every task's logs before plotting. This note holds the recipe. Every HPG run since 2026-10-23 uses `sweeps/radIV.slurm`. The `pulsedIV_*` templates are records of the September-October curve-tracer era (last section).

## Params files and study names
- One file per study, `sweeps/params_<study>.txt`, one line per array task; task N reads line N+1. The committed file is the record of what the job ran.
- **Never edit or regenerate a params file after its job ran, and never reuse a study name.** A changed or repeated study gets a new name. What goes wrong otherwise: `params_radFine.txt` was overwritten on Nov 5 by a different study. "radFine Oct 24" (job 47562303) now exists only in git history, at commit 0fbf0ce (`git show 0fbf0ce:sweeps/params_radFine.txt`); the file on `main` is "radFine Nov 5" (job 49735196).
- Many rad-era params files are written by `analysis/genRadStudy.py` (and `analysis/genRad3d.py` for the 3D studies, [[analysis-scripts]]). Each run of a generator rewrites every file it owns. After running one, `git diff --stat sweeps/` must list only the new study's file.
- Commit and push the params file, then `git pull --ff-only` on HPG, before submitting. A file missing on HPG fails the job within seconds (radFine 47554718, Oct 24).

## radIV.slurm (all runs since 2026-10-23)
**Line format:** `label|lever=value;lever=value;...`. The label becomes the driver's `tag` and the prefix of every output file.

**Environment variables:** `RUN` (results folder, `<YYYYMMDD>_<study>`), `PARAMS` (file name in `sweeps/`), `DRV` (driver `drivers/$DRV.tcl`, default `radIV`; also `seeIV`, and `pulsedIV` for some pulsed runs such as radGauss 50128863), `REPO` (default the HPG checkout; set it to an HPG worktree to run a branch).

**Submit** from the repo root on HPG (recipe from the template header):
```bash
RUN=20261023_radCal1 PARAMS=params_radCal1.txt; mkdir -p results/$RUN
sbatch --array=0-7%8 --export=ALL,RUN=$RUN,PARAMS=$PARAMS \
       --output=results/$RUN/slurm_%A_%a.out --error=results/$RUN/slurm_%A_%a.err sweeps/radIV.slurm
```
- Run `mkdir -p results/$RUN` first. SLURM opens the `--output`/`--error` files before the script starts and does not create their folder.
- `--array=0-<lines-1>%N`: one task per line, throttled with `%N` (`squeue -A ee1` first).
- The template asks for `--qos=ee1-b`, 1 CPU, 4 GB and 24 h. Give `--mem`/`--time` on the command line for heavier runs (28 V stress jobs ask 8 GB and the 4-day limit, [[hpg-workflow]]). Add `DRV=seeIV` (or `REPO=...`) inside `--export=ALL,...`.

**What each task does** (`sweeps/radIV.slurm`):
1. Makes `results/$RUN/task_<id>/` and reads its line from `$REPO/sweeps/$PARAMS`.
2. Copies these model files flat from `$REPO/model/`: `GaN_modelfile_masterD`, `GaN.tcl`, `AlGaN.tcl`, `Insulator.tcl`, `Metal.tcl`, `Continuity.tcl`, `Poisson.tcl`, `ETemp.tcl`, `rfdevice.tcl`, `rfdevice_SiN.tcl`, `rfdevice3d.tcl`. Until 2026-11-21 `ETemp.tcl` was missing, so a radIV/seeIV line with `eTemp=1` stopped at `source ETemp.tcl`; `pulsedIV_eTemp.slurm` now also copies the SiN and 3D decks.
3. Writes `radIV_task.tcl` (the same name for every DRV): `set tag <label>`, then one `set <lever> <value>` per pair in line order, then `drivers/${DRV:-radIV}.tcl` with its `window` lines blanked and its `chart` lines commented out. It runs that with stock HPG FLOOXS ([[flooxs-builds]]). **Never edit the repo copy in place**: a per-run change goes on the params line.
4. Writes `params.json`: label, task_id, params file name and the pairs on the line, in order. It is not the full parameter set; the driver defaults fill in the rest ([[levers]]).

**Last value wins.** A lever set twice on one line takes the later value, because each pair is a plain Tcl `set`. Generated lines often repeat a lever: the first line of `params_radEB1.txt` sets `hotEb=0.5` and later `hotEb=1.0`, and `params_stressLib.txt` sets `meshY` twice. `params.json` then repeats the key too. Read the effective setting from the last occurrence.

**Read at task start.** The params line, the model files and the driver are read from `$REPO` when each task starts, not when the array is submitted. A push plus a `git pull` on HPG reaches every task that has not started yet. Pull model or driver changes only when no queued task should run the old code, or run the new code from a worktree via `REPO`.

**Outputs** in `task_<id>/` (prefix = label, or `<label>_<entry>` per `damList` entry):
- radIV: `_summary.txt`, `_IdVg.csv`, `_IdVd.csv`, `_IdVdG<Vg>.csv` (`VgFam`), `_cuts.txt`, `_vdcuts.txt` (`vdCuts`), `_stressDiag.txt` (`stressDiag`). `stressSave=<file>` writes `<file>` plus `<file>.txt`. `stressSaveEvery`/`stressOnly` write states at bias to `stressSaveDir` (default `.`) as `<stressSavePrefix>_Vd<Vd>.str.gz` (prefix defaults to the tag) plus a `.str.txt` settings file ([[stress-library]]).
- seeIV: `_summary.txt`, `_see.csv`, `_cuts_<k>.txt` (`seeCutTimes`), `_map_<k>.vtk` and `_map_dc.vtk` (`seeMapTimes`, `seeMapDC`).
- pulsedIV through radIV.slurm: set `ivCSV=pulsedIV_<label>.csv` on the line. The default `figures/pulsedIV.csv` has no folder in a task directory.
- SLURM logs: `results/$RUN/slurm_<job>_<task>.out` / `.err`.

## After the array: check every task's logs
Use `grep`/`tail`, not `cat`. Report failures before plotting.

**All drivers** (`.out`/`.err`): `munmap` / `FLPS_panic` ([[munmap-crash]]), OOM (`oom-kill`, signal 9), `DUE TO TIME`, `CANCELLED`, missing output CSVs, core files (delete them, 1-2 GB each).

**Per driver:**

| Driver | Failure markers | Completion line |
|---|---|---|
| pulsedIV (`pulsedIV_*` templates, or radIV.slurm with `DRV=pulsedIV`) | `.out`: `PULSED GAVE UP at Vd=` | none; check that the CSV reaches `Vd_max` |
| radIV | `.out`: `IDVD GAVE UP at Vd=`, `IDVG GAVE UP at Vg=`, `RAMP GAVE UP`, `DAMAGE solve failed`, `emitRest solve failed`. `.err`: any Tcl error, e.g. `stress drain ramp failed at`, `stress gate ramp failed`, `stressLoad: ...`, `stressResume: ...`, `state has the ... FP contact box` ([[fp-contact-fix]]). `_summary.txt`: any `failed` line (`<tg> damage failed`, `<tg> measurement failed`, `reset solve failed`) | `RADIV DONE tag=<label>`, or `RADIV DONE tag=<label> (stress only)` |
| seeIV | `.out`: `RAMP GAVE UP`. `.err`: Tcl errors `gate ramp`, `drain ramp`. `_summary.txt`: `gate ramp failed`, `drain ramp failed`, `transient stopped: ...` | `SEEIV DONE tag=<label>`, or `SEEIV INJECT-ONLY DONE tag=<label>`; the summary should say `transient done to <seeTend>` |

- **Ignore** `RETRY <c> <a> -> <b> failed (depth n)` lines. They are normal bisection steps ([[retry-bisection]]).
- **The completion line is necessary but not sufficient.** radIV still prints `RADIV DONE` after `IDVD GAVE UP` (the curve stops early) and after a `damage failed` entry. seeIV still prints `SEEIV DONE` after `transient stopped`.
- **Stress Vd.** radIV accepts a stress ramp that stops anywhere at or above `Vd_stressMin` (12 V). In runs that solve the stress, check that `field taken at Vd=` in `_summary.txt` equals `Vd_stress`. In `stressOnly` runs, check `last converged Vd=`. In `stressLoad` runs, check that `stress loaded from` names the intended state file.

**Then** `rsync -a --exclude='core*' hpg:/home/ianstafford/blue/ee1/ianstafford/HEMTRAD/results/<run>/ results/<run>/` and analyse and plot on the workstation.

## Oct-era templates (pulsedIV)
Used with `drivers/pulsedIV.tcl` until `radIV.tcl` arrived on Oct 23. Each `pulsedIV_<study>.slurm` (and `fieldPlate.slurm`, `eTempDebug.slurm`) hard-codes its run folder and its params file (`fieldPlate.slurm` hard-codes its two decks instead): it is a finished record of one study. `pulsedIV_eTemp.slurm` is the one generic template (`PARAMS`, `RUN`, `REPO` from the environment; an optional `extra` column of `lever value;...` settings). Static-era templates are in `archive/static_mobility/`.

1. Commit the driver, template and params file on the workstation; `git push`. On HPG: `git pull --ff-only`, then `sbatch sweeps/<template>.slurm` from the repo root. The `#SBATCH --output=results/...` paths are relative to the submit directory.
2. Params lines are pipe-delimited columns, one line per task.
3. Each task copies the model files flat into its own folder under `results/<YYYYMMDD>_<tag>/`, prepends `set <lever> <value>` lines, strips the GUI lines, and runs there. Only `pulsedIV_eTemp.slurm` and `eTempDebug.slurm` copy `ETemp.tcl`. The driver finds the flat model files in its own directory (`modelDir` lookup, [[drivers]]). **Never edit the repo copy in place.**
4. Per-task CSVs `pulsedIV_<tag>.csv` (never the shared `figures/pulsedIV.csv`) and a `params.json`.
5. Format floats in names (`printf '%.2e'`).
6. Log check and rsync as above.

Rescue and retry runs go into `<run>Retry*/` folders. `analysis/analyze_onset.py` and `analysis/plot_posVd.py` read every `<run>Retry*` and keep the run that got furthest ([[analysis-scripts]]).

Related: [[hpg-workflow]], [[git-conventions]], [[stress-library]], [[drivers]].
