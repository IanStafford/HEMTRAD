---
title: Analysis scripts
tags: [tools, analysis]
date: 2026-11-20
source: module docstrings and code of every tracked analysis/*.py (git ls-files analysis, 58 scripts), dashboard/webfig.py and dashboard/build_cleanup_page.py; generator rerun in a clean git archive copy (2026-11-20); survey findings AN-KB-1, KBC-12, LAY-3, AN-KB-2, AN-4 ([[cleanup-plan]])
---
# Analysis and plotting scripts

**How to run.** From the repo root, after rsyncing the results: `python3 analysis/<script>.py <args>`. The Usage columns below give only the arguments. Shared helpers live in `analysis/common.py` (stage 3a of [[cleanup-plan]], 2026-11-21): CSV readers and column constants (`read_csv`, `read_glob`, `IDVD`, `IDVG`, `PULSED`), the task index `label_index`, the drop finders `drop_episodes` / `drop_values` with `DROP_MIN_TABLE = 8` and `DROP_MIN_FIG = 10`, the collapse classifier `classify_collapse` (see [[collapse-classification]]), the reference-curve registry `REF` (pre-fix curves, each with its job ID), the rad metrics `vth_gm` / `ron_step`, the measured-data guard, and the plot palettes. `radMetrics.py` is a re-export shim kept for `radFit.py` and `plot_radFinal.py`. Scripts import by module name (`common`, `plot_meshSeries`, `plot_radStepSeries`, `vdcuts`); that works because Python puts `analysis/` on the path when it runs a script there (not under `python3 -I`).

**Python.** The system `python3` (numpy, matplotlib; Pillow for `make_gif.py` and `webfig.py`) runs everything except `render3d.py`, `render3d_slice.py` and `plot_seeMaps.py`. Those three need `~/venvs/render/bin/python` (pyvista, vtk).

**Scope.** 47 tracked scripts in `analysis/` plus 2 in `dashboard/`, one row each, and the 11 scripts archived on 2026-11-21 ("Archived scripts" at the end). Every script has a module docstring. All but `analyze_trapMapSets.py` and the two imported modules (`radMetrics`, `vdcuts`) give their usage there. When you add a script, give it a docstring and add its row here. Static-era scripts are in `archive/static_mobility/` (`analyze_trap{ConcLevel,Cone,Deep,Map,SiN,XYMap}.py`, `critical_strike.py`, `plot_fieldPlate.py`, `plot_trapPlacement.py`, and since 2026-11-21 `analyze_mobCompare.py`).

## Conventions

**CSV columns.**
- radIV writes `<label>_IdVd.csv` as (Vd, Id_dev, Id_ext, peak Te) and `<label>_IdVg.csv` as (Vg, Id_dev, Id_ext), in V and mA/mm. pulsedIV writes (Vd, Id, peak Te).
- The rad metrics read their currents from Id_ext (column 2): `radMetrics.ron_step`, `radCompare`, `radMap`, `radFit`, `plot_radFinal`, `plot_radMechanism`. Their Vth and gm (`vth_gm`) use Id_dev (column 1), and so do the step, strike and cut scripts.
- The two columns are equal while the lumped leakage `Rgd` is 0. That is radIV's default (`Rgd 0.0`), and no params file sets it.

**Two drop rules.** They gave different counts on 3 of the 66 mesh-series curves checked on 2026-11-20 (survey AN-1).
- *Table rule, 8 mA/mm* (`common.drop_values(v, i, DROP_MIN_TABLE, "hyst")`). An episode starts when Id falls more than 1 mA/mm in one step and continues while each step falls more than 0.5 mA/mm. It counts if the total fall is at least 8 mA/mm. Used by `plot_meshSeries`, `plot_pocketVolts`, `plot_vdcutsDrops` and `vdcutsDropTable`. The drop counts in the [[step-search-28v]] and [[step-mechanism]] tables use this rule.
- *Figure rule, 10 mA/mm* (`common.drop_values(v, i, DROP_MIN_FIG, "any")`, which `plot_radStep.drops` wraps). It takes any run of strictly falling Id and keeps it if the total fall is at least `min_drop`. The default is 10 mA/mm in `plot_radStep`. `plot_radStepSeries` (and through it the arrows of `plot_meshDeliverable`), `testRegister` and the archived `plot_radStepHighlights` call it with 10.

**Three meanings of `onset_Vd`.** Five committed metrics CSVs have an `onset_Vd` column. Don't compare onsets across these scripts.
- `analyze_onset.py` (`figures/onsetField{1,2,3}_metrics.csv`): the Vd after the first single step whose loss reaches the device's class threshold (> 95% deep, ≥ 50% medium, the largest step for shallow). Stalled runs get the last Vd + 0.1 V, and off-at-rest devices get NaN ([[collapse-classification]]).
- `analyze_trapMapSets.py` (`figures/trapMapF_field_metrics.csv`): the first Vd after the Id peak where Id < peak / 10.
- `archive/static_mobility/analyze_mobCompare.py` (`figures/mobCompare_F_metrics.csv`): the first Vd where Id < running maximum / 10.
- The last two are static-era metrics from before the class rule of 2026-10-01. The committed CSVs keep the column name `onset_Vd` for all three.
- `plot_sensitivity.py` writes the class-rule onset under the column name `onset` (`figures/sensitivity_metrics.csv`). Its stalled onset is the last Vd + Vd_step, and its shallow onset is NaN.

**Copies of the collapse-class rule.** `analyze_onset`, `plot_posVd`, `plot_posOnset`, `plot_posSlides` and `plot_sensitivity` each implement the rule. `plot_strikeSlides` has no stalled class. `plot_vgOnset` (deep or medium only), the archived `plot_eTemp` (deep only) and `plot_eTempStd` use simpler rules on purpose.

**Measured data (public repo).**
- `radCompare.py` (since 2026-11-20) and `plot_radFinal.py` overlay measured curves only when given `--targets`.
- `radFit.py` always reads the targets, because it fits to them. Its default path is `~/HEMTRAD/data/rad_y2/targets.csv`.
- `radCompare.py` reads the measured pre-irradiation scalars from `pre_scalars.csv` beside the targets file.
- All three call `radMetrics.guard_private_output()`, which refuses to write a figure with measured data under `figures/` or `dashboard/`.
- The targets and scalars stay in `data/rad_y2/`, which is gitignored.

**Reference curves.** Many rad-era scripts hard-code the pre-irradiation curves `results/20261104_radMap1/task_*/{sin,hk}_ref_IdVd.csv` and the Nov 11 model `results/20261109_radEB1/task_*/sin_b_eb1_IdVd.csv`. Both are pre-fix and being rerun (fpFixPre 52134553, fpFixEB1 52134554; [[fp-contact-fix]]).

**Plot style.** The October trap-map and position-map figures (`analyze_onset`, `analyze_trapMapSets`, the archived `analyze_mobCompare`, `plot_posVd`, `plot_posOnset`) share one style. It uses a recessive grid and axes, a one-hue sequential blue ramp (`SEQ`) for magnitude, text in ink colours and legends off the data. Later scripts use their own palettes: viridis in `radCurves` and `radPlacementFig`, jet in `plot_seeMaps`, matplotlib's default cycle in `radCompare` and `radFit`, and 0-3 strike ramps in the step scripts (orange for SiN, blue for HighK).

## Curve-tracer era (pulsedIV.tcl, Sep-Oct)

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `analyze_onset.py`: collapse class and onset per device | `<run_dir> <tag> [rows cols xpar ypar]` (default trapLevel, hotEb, hotTau, trapPeak) | `<run_dir>` and `<run_dir>Retry*`, `task_*/pulsedIV_*.csv` + `params.json`; keeps each device's furthest run | `figures/<tag>.png`, `figures/<tag>_metrics.csv` | [[collapse-classification]], [[late-onset-search]] |
| `analyze_trapMapSets.py`: 3D depth and suppression surfaces over (depth, y) | `[run tag]` (default `results/20261001_trapMapF_field`, `trapMapF_field`) | a trap map with a trap-free task | `figures/<tag>_metrics.csv`, `<tag>_tp<peak>_tl<level>.png`, `<tag>_overview_{depth,suppression}.png` | [[field-mobility-trap-map]] |
| `plot_posVd.py`: per-Vd 3D suppression surfaces with a shared z scale; stalled points as orange × | `<run_dir> <tag> [Vd list]` (default 0.3, 0.6 ... 3.0) | a position map (trapMeanX x trapMeanY) | `figures/<tag>_grid.png`, `figures/<tag>_frames/Vd_<v>.png`, `figures/<tag>_onset.png` | [[position-maps]] |
| `plot_posOnset.py`: 3D onset surface, earliest collapse highest | `<run_dir> <tag>` | a position map | `figures/<tag>_onset3d.png`, `figures/<tag>_onset3d_frames/` | [[position-maps]] |
| `make_gif.py`: GIF from `Vd_*.png` frames, shared palette, last frame held | `<frames_dir> <out.gif> [ms_per_frame [hold_last_ms]]` (default 350, 2000) | frames of `plot_posVd` or `plot_posOnset` | `out.gif` | [[position-maps]] |
| `plot_lateIdVd.py`: latest deep collapses vs trap-free | none | `results/20261002_onsetField3` | `figures/lateOnset_IdVd.png` | [[late-onset-search]] |
| `plot_curveTracer.py`: Id-Vd at other Vg, one folder per Vg | `[run_dir]` (default `results/20261003_curveTracer`, job 44573629) | the run, plus reference curves from onsetField1 and onsetField3 | `figures/Vg_<Vg>V/curveTracer_Vg<Vg>V.png` and copies of the CSVs | [[gate-bias]] |
| `plot_sensitivity.py`: one-at-a-time trap-lever sensitivity | `[run_dir]` (default `results/20261017_sensitivity`) | a `sweeps/pulsedIV_sensitivity.slurm` run | `figures/sensitivity_metrics.csv`, `sensitivity.png`, `sensitivity_IdVd.png` | [[trap-sensitivity]] |
| `plot_vgOnset.py`: collapse onset vs gate bias | `<out.png> "<title>" label=csv ...` | pulsedIV CSVs | `out.png`; prints the onset per curve | [[vg-dependence]] |
| `plot_deckVg1.py`: HighK vs SiN Id-Vd at Vg +1 per trap position | `[run_dir]` (default `results/20261021_deckVg1`, job 47062225) | a `sweeps/pulsedIV_deckVg1.slurm` run | `figures/deckVg1_IdVd.png` | [[highk-vs-sin]] |

GIF recipe: `python3 analysis/plot_posVd.py <run> <tag>_gif $(python3 -c "print(','.join(f'{0.1*k:.1f}' for k in range(1,31)))")`, then `python3 analysis/make_gif.py figures/<tag>_gif_frames figures/<tag>.gif`.

Frame folders: the six `figures/posMap*_frames/` folders of `plot_posVd` (60 PNGs) are committed. The `plot_posOnset` frames (`*_onset3d_frames/`) and the GIF-recipe frames (`figures/<tag>_gif_frames/`) are not committed; since 2026-11-21 both patterns are gitignored at any depth under `figures/` (`figures/README.md`). Stage figures by explicit path all the same.

## Calibration and energy balance

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `calib_score.py`: rigid gate shift dv that minimises the rms % error over Vg -2.6..+1 V | `[--phiB 1.65] label=sim.csv ...` | `figures/calib_IdVg_*.csv` (written by `drivers/calibIdVg.tcl`) and `data/rfDeviceHFO2_Experimental.csv` | prints a dv / phiB / rms table; writes no files | [[calibration]] |
| `plot_calib.py`: transfer-curve calibration plot | `<out.png> label=sim.csv ...` | as calib_score | `out.png` (Id-Vg linear and log, % error, gm) | [[calibration]] |
| `plot_eTempStd.py`: trap study with eTemp 1, etStats 0, etThermo 0 | `[run_dir]` (default `results/20261013_eTempStd1`, job 45768739) | the run, `results/20261008_eTemp1`, onsetField1 and onsetField3 | `figures/eTempStd_IdVd.png` | [[energy-balance]] |

The model standard has been `eTemp 0` since 2026-10-16 ([[energy-balance]]).

## Rad model (radIV.tcl)

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `radMetrics.py`: shared helpers | imported | - | `vth_gm` (linear extrapolation at max gm), `ron_step` (Ron from the slope for 0 < Vd ≤ 0.5 V, largest neighbour drop), `guard_private_output`, `load_pre_scalars` | [[rad-model]] |
| `radCompare.py`: per task Vth, gm, Id at Vg -2.6 / -2.0 / -1.4 (Vd 0.1), Id at Vg +1 at 1 / 2 / 4 / 6 / 10 V, Ron, largest step, Ioff | `<run_or_task_dir>... [--targets t.csv] [--plot out.png] [--ref LABEL]` | radIV task dirs (`params.json`, `*_IdVg.csv`, `*_IdVd.csv`) | table on stdout (`--ref` adds post/pre ratios); optional 3-panel plot | [[rad-model]] |
| `radFit.py`: fits lumped drain-access elements (series R, offset V0) to post/pre ratios | `<pre_task> <post_task>:<curve> ... [--targets t.csv] [--plot out.png]` | radIV tasks and the untracked measured targets | best (V0, R) and the rms of the log ratios over Vd 0.5-10 V | [[rad-model]] |
| `radMap.py`: damage-region map from uniform-site runs (`damSites`) | `<run_dir>... --csv out.csv [--plot out.png] [--xlabel TEXT]` | each deck's `*_ref` task is the reference | CSV per task (Vth, gm, Ron, Id at 1 / 4 / 10 V, largest step, give-up Vd); e.g. `figures/rad/radMap1.png` | [[damage-region-map]] |
| `radCurves.py`: Id-Vd of a position map, one panel per deck | `<run_dir> <out.png>` | radMap1-style labels | e.g. `figures/rad/radMap1_curves.png` | [[damage-region-map]] |
| `radMeshFig.py`: damaged sections on the standard and fine meshes | `<radMap1_dir> <radMesh_dir> <out.png>` | radMap1, radMesh | `figures/rad/radMesh_curves.png` | [[damage-region-map]] |
| `radPlacementFig.py`: strike placement on a fine mesh | `<out.png> <title> <run> <pattern with {d} and {y}> y1 y2 ...` | the run, plus fixed radFine and radMesh extras | `figures/rad/placement_{w0.1,4e18,8e18}.png` | [[damage-region-map]] |
| `radPartialWidth.py`: partial-width estimate, parallel columns, no solver | none | radMap1 `hk_ref`; radMesh `hk_y1.50_m05` and `hk_w0.1_m05` | prints only | [[damage-region-map]] |
| `plot_radFinal.py`: consolidated pre/post model, 3 panels | `[run_dir] [--pre pre_run_dir] [--targets t.csv] [--out fig.png] [--damPeak 5e18\|""]` (default `results/20261025_radFinal`, job 47693156) | radFinal-style labels `pre_`, `nb_`, `b_` + `{highk,sin}` | default `figures/radFinal_model.png` | [[rad-model]] |
| `plot_radMechanism.py`: model-only mechanism figures | none | radFinal8, radFinal11, radFinal | `figures/radMech_damage.png`, `figures/radMech_SiN_IdVd.png` | [[rad-model]] |
| `plot_radStrikeN.py`: 0-3 strikes on the 17 V stress model | `<run dir> <out dir>` | `task_*/{sin,hk}_N{0..3}_IdVd.csv` (and `_IdVg.csv`) | `<out dir>/{sin,hk}_IdVd.png`, `summary.png`, `metrics.json` (committed in `figures/rad/strikeN/`) | [[rad-model]] |
| `plot_rad28strike.py`: 0-3 strikes on the 28 V stress library | `<run dir> <P> <out.png>` | rad28strikeL (51763582) | `figures/rad/strike28/strike28_<P>.png` | [[rad-model]], [[stress-library]] |

## Step search and mesh checks (28 V stress)

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `plot_radStep.py`: every Id-Vd of a run, one panel per group, drops listed | `<run dir> <out.png> [min_drop mA/mm] [group regex]` | labels like `A_p1.5e+18_n5e+18_N3` (the panel is the label without `_N<k>`) | `out.png`, `<out>_drops.json` | [[step-search-28v]] |
| `plot_radStepSeries.py`: matched 0-3 strike series, SiN and HighK | `<out prefix> [key ...]` | hard-coded radStep runs (keys of `SERIES`) | `<prefix>_<key>.png`, `<prefix>_all.png`, with keys also `<prefix>_deliverable.png` (committed as `figures/rad/step28/series_*.png`) | [[step-search-28v]] |
| `plot_radStepFS.py`: field-scaled strike series and a what-if width estimate | `[out prefix] [f]` (default `figures/rad/step28/fieldscaled`, 0.25) | radStepC, radStepI | `<prefix>_series.png`, `<prefix>_segments.png` | [[step-search-28v]] |
| `plot_radStepH.py`: round H, SiN and HighK side by side | `[out.png]` (default `figures/rad/step28/fieldstrike_H.png`) | radStepC, radStepH | `out.png` | [[step-search-28v]] |
| `plot_meshSeries.py`: 0-3 strike series, one column per mesh; prints every drop | `[out.png] [set key ...]` (default `figures/rad/step28/mesh_series.png`) | radStep A-F, meshChkLoad_m10 and m5fix, radStepM, radStepM2, radStepM3 (never submitted, so the 2.5 nm column is empty) | `out.png`; drop table on stdout | [[step-search-28v]] |
| `plot_meshDeliverable.py`: the mesh-checked deliverable, drops marked by arrows | `<out.png> <key> [<key> ...]` (e.g. `lev30_n8 lev40_n7`) | keys of `plot_meshSeries.SETS` | `figures/rad/step28/mesh_deliverable.png` | [[step-search-28v]] |
| `plot_meshChkSteps.py`: the first mesh check of the strike steps; superseded by plot_meshSeries | `[out.png]` (default `figures/rad/step28/meshchk_steps.png`) | radStep runs, meshChkLoad_m10 51939191, meshChkLoad_m5fix 51939192 | `out.png` | [[step-search-28v]] |
| `testRegister.py`: register of the stepped-collapse tests | `<out.json> [--no-hpg]` | `sweeps/params_<run>.txt`, synced `results/<dir>/task_*/`, and sacct over `ssh -o BatchMode=yes hpg` unless `--no-hpg`; rounds S, A-H and 3D are hard-coded in `ROUNDS` | JSON for the `tests` dataset of the Stepped-Collapse Test Register dashboard | [[step-search-28v]] |

## Cuts from vdCuts runs (radIV `vdCuts 1`)

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `vdcuts.py`: reader | imported: `load(path) -> {Vd: {label: (y, value)}}` | `<label>_vdcuts.txt`: cuts along y at x 0.016 µm (1 nm below the AlGaN/GaN interface) of IonAcceptor, Elec, Ey and TeTrap, plus IonAcceptor and TeTrap at x 0.008 µm (labels `*_x0.008`) | - | [[step-mechanism]] |
| `vdcutsDropTable.py`: what switches at each drop | `<task dir> [<task dir> ...]` | vdCuts task dirs | table on stdout | [[step-mechanism]] |
| `plot_vdcutsDrops.py`: channel profiles before and after each drop | `<task dir> <out.png> [title]` | a vdCuts task dir | e.g. `figures/rad/step28/diag/lib_*.png` | [[step-mechanism]] |
| `plot_pocketVolts.py`: voltage across each damaged spot vs Vd | `<out.png> <title>=<task dir> ...` (the title's leading digit is the strike count) | vdCuts task dirs | e.g. `figures/rad/step28/diag/pocket_volts.png` | [[step-mechanism]] |

## 3D, TRIM and SEE

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `trimTrack.py`: per-ion track parameters per layer | `<trim_out_dir> <HighK\|SiN> <out.json>` | `COLLISON.txt` of a full-cascade TRIM run (`bin/trim_run.sh`) | `data/trim/<deck>_track.json` | [[trim]], [[3d-plan]] |
| `render3d.py`: 3D slice render (render venv) | `<file.vtu> <out prefix> [track field] [iso cm^-3]` | `struct vtk=` output of `drivers/render3d_build.tcl` | `<prefix>_overview.png`, `<prefix>_track.png` (committed as `figures/rad3d/sin3d_track_{overview,closeup}.png`) | [[3d-plan]] |
| `render3d_slice.py`: damaged 3D slice render (render venv) | `<file.vtu> <out.png> [ymin ymax um] [label]` | a radIV `damRod` slice with LogElec and LogTrap fields | e.g. `figures/rad3d/half3d_render.png` | [[3d-plan]] |
| `plot_seeMaps.py`: current-density maps of a strike transient (render venv) | `<out.png> <row label>=<prefix> ... [--carrier p\|n] [--y ymin ymax] [--x xmin xmax] [--clim lo hi] [--strike y0] [--ncol k]` | `drivers/seeIV.tcl` snapshots (`seeMapTimes`, `seeMapDC`) | e.g. `figures/see/map28_{hole,elec}J.png`, `poc_{hole,elec}J.png` | [[see-plan]] |

## Params generators (they write sweeps/params_*.txt)

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `genRadStudy.py`: the Nov rad studies, the stress library, the step rounds, the mesh checks, seeMap28 and the fpFix sets | `[--check] [--force <name>] [--show <study or params name> [label]]` | constants and builders in `analysis/radparams.py`; one function per study, registered in `STUDIES` | 63 params files (listed below) | [[sweep-pattern]], [[step-search-28v]], [[fp-contact-fix]] |
| `radparams.py`: constants and line builders for the generators (calibration prefix, damage blocks, deck table, mesh patches, Gaussian strikes, the 28 V load paths, the emit / check / show machinery) | imported | - | - | [[sweep-pattern]] |
| `genRad3d.py`: the 3D slice studies | `[--check] [--force <name>]` | `data/trim/SiN_track.json` (the `damTube` columns of rad3dTrack1) | `params_rad3d{Build,Solve,Track1,Rod}.txt` | [[3d-plan]] |

- **The generated files are the HPG record.** A rerun of both generators in a clean `git archive HEAD` copy reproduces every committed file byte for byte (63 of 63 and 4 of 4 on 2026-11-21, after the library refactor).
- **genRadStudy.py writes:** fpFixEB1, fpFixEB1p, fpFixLoad (never run; superseded by fpFixScale28), fpFixScale28, fpFixScaleEB1, fpFixMesh, fpFixPre, fpFixStress, meshChkLoad_m10, meshChkLoad_m5fix, meshChkStress, meshChkStress2p5, rad28fit, rad28strike, rad28strikeL, radChk, radChk2, radEB1, radEB2, radEmit, radEmit2, radEmit3, radExp1, radExp1b, radExp2, radExp3, radFam, radFinal12, radFine, radGauss, radGauss2, radHV, radMap1, radMap2, radMesh, radMulti, radRon, radStepA to radStepK (11 files), radStepDiag, radStepDiag5, radStepM, radStepM2, radStepM3, radStress, radStressIO, radStrike2, radStrikeN, radVth, radVth2, radVth3, seeMap28, stressLib and stressLibResume.
- **Overwrite rail (2026-11-21).** Both generators write a file only when it is new or unchanged. If a tracked params file would change (for example after an edit to a shared constant in `radparams.py`), they print the diff and refuse unless `--force <name>` is given. Run `--check` first; it writes nothing. `--show` prints a study's effective levers (last value wins) against its base set. Add a new study as a new function and `Study(...)` entry; never edit the rows of a study whose job ran (rules in `sweeps/README.md`). Don't rename the scripts.
- **Format.** Each line of a generated file is `label|lever=value;lever=value;...` (read by `sweeps/radIV.slurm`). The pulsedIV-era files use positional columns instead. When a lever repeats on one line, the last value wins. Damage sites are `{ymin ymax xmin xmax N}` (µm along the channel, µm below the AlGaN top, cm⁻³). Gaussian strikes are `{y x sigma N}`.
- **radFine names two studies.** `params_radFine.txt` now holds radFine Nov 5 (job 49735196). The radFine Oct 24 params (job 47562303) are only in git history: `git show 0fbf0ce:sweeps/params_radFine.txt`.
- **Hand-written params files** are the other 67 of the 132 tracked in `sweeps/` (counted 2026-11-21; `params_eTempDebug.txt` moved to `archive/energy_balance/` that day). They are the Sep-Oct curve-tracer files (curveTracer, deckVg1, eTemp*, eTempStd*, iterLimit, onsetField*, posMap*, reorgCheck, sensitivity, trapMapF_field, vgEB*) and rad28a, radCal1-3, radDam1-2, radFinal and radFinal2-11, radFit1-2, radIns, radNE1-2, radNEsmoke, radNHsmoke, radPhys1, radPost, radQDsmoke, radWin, seeGen1-2, seeIso1, seeSmoke1 and the stress* checks.

## Talk and dashboard-day figures

Each makes fixed figures from hard-coded results paths. Nine more one-off day-figure scripts moved to `archive/analysis_dayfigs/` on 2026-11-21 (stage 4 of [[cleanup-plan]]); their rows are under "Archived scripts" below.

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `plot_headline.py`: talk headline, the late set at y 2.4 µm against the measured collapse window | `[run_dir]` (default `results/20261013_eTempStd1`); `HEADLINE_FONT_DIR` for Source Sans 3 | eTempStd1 (job 45768739), onsetField3RetryRamp | `figures/eTempStd_headline.png` | [[energy-balance]] |
| `plot_posSlides.py`: trap-placement talk figures | none; `HEADLINE_FONT_DIR` | the six position maps | `figures/posSlide_lateral.png`, `posSlide_sets.png` | [[position-maps]] |
| `plot_strikeSlides.py`: the Oct 16 two-slide deck | none; `HEADLINE_FONT_DIR` | `results/20261002_posMapLate`, `figures/fieldPlateFM_cuts.csv` (job 46241088; no script in `analysis/` makes it) | `figures/strikeSlide_IV.png`, `strikeSlide_placement.png`, `fieldSlide_highk.png` | [[highk-vs-sin]] |
| `plot_radFinalEB.py` | `<out.png>` | radMap1, radEB1 | `figures/rad/radFinalEB_IdVd.png` | [[rad-model]] |

## Archived scripts (2026-11-21)

Moved out of `analysis/` in stage 4 of [[cleanup-plan]], with only their usage lines edited. Run them from the repo root as `python3 archive/<folder>/<script>.py <args>`. Each folder's README says why it was archived and which runs and jobs it belongs to; `archive/analysis_dayfigs/README.md` also gives each figure's dashboard day. The archived `plot_radStepHighlights.py` still imports `plot_radStep.drops` from `analysis/`, through its own `sys.path.insert(0, "analysis")`.

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `archive/static_mobility/analyze_mobCompare.py`: static vs field Run F maps, each against its own trap-free device | `[trapPeak trapLevel field_run tag]` (default 4e18, 0.55, `results/20261001_trapMapF_field`, `mobCompare_F`) | static map `results/archive_static_mobility/20260927_trapMapSets{,Retry}` | `figures/<tag>_metrics.csv`, `<tag>_3d.png`, `<tag>_compare.png` | [[field-mobility-trap-map]] |
| `archive/energy_balance/plot_eTemp.py`: energy-balance runs vs the local-field model; ETemp profiles | `[run_dir]` (default `results/20261008_eTemp1`, the etStats-1 run) | the run, plus onsetField1 and onsetField3 | `figures/eTemp_IdVd.png`, `figures/eTemp_profiles.png` | [[energy-balance]] |
| `archive/analysis_dayfigs/plot_gaussFine.py` | `<out.png>` | deckVg1, radGauss | `figures/rad/gaussFine_decks.png` | [[damage-region-map]] |
| `archive/analysis_dayfigs/plot_radExp1.py` | `<out.png>` | radMap1, radEB1, radExp1, radExp1c | `figures/rad/radExp1.png` | [[rad-model]] |
| `archive/analysis_dayfigs/radEBFig.py` | `<out.png>` | radMap1, radChk2, radFine (Nov 5), radEB1, radEB2 | `figures/rad/hotEb_final.png` | [[rad-model]] |
| `archive/analysis_dayfigs/radGaussFig.py` | `<out.png>` | radGauss, deckVg1 | `figures/rad/gauss_mesh.png` | [[damage-region-map]] |
| `archive/analysis_dayfigs/radFineFig.py` | `<out.png>`; needs `FINAL_REF` in the environment (path to a CSV of the standard-mesh final SiN curve) | radFine (Nov 5), radMulti, radMesh, radFam, radMap1 | `figures/rad/radFine.png` | [[damage-region-map]] |
| `archive/analysis_dayfigs/plot_nov12.py` | `<out dir>` | radHV, radStrike2 | `<out dir>/radHV_28V.png`, `radStrike2_pos.png` | [[rad-model]] |
| `archive/analysis_dayfigs/plot_rad28fit.py` | `<out.png>` | rad28fit, radExp3, rad28fitB, radMap1 | `figures/rad/step28/rad28fit.png` | [[rad-model]] |
| `archive/analysis_dayfigs/plot_rad3dFix.py` | `<out.png>` | `data/rad3d_fangs` (FANGS model output), `results/20261112_rad3dSolve/task_6` | `figures/rad3d/rad3d_fix.png` | [[3d-plan]] |
| `archive/analysis_dayfigs/plot_radStepHighlights.py` | `<out.png> [best]` | radStep runs, radMap1, radEB1 | `figures/rad/step28/step_highlights.png`; with `best`, `step_best3.png` | [[step-search-28v]] |

## Dashboard helpers

| Script | Usage | Inputs | Outputs | KB note |
|---|---|---|---|---|
| `dashboard/webfig.py`: web-sized copies of figures | `python3 dashboard/webfig.py figures/a.png ...` | figures | `dashboard/fig/<name>.jpg` (max 1600 px wide, JPEG q86, `+` dropped from names; GIFs copied unchanged) | [[dashboard]] |
| `dashboard/build_cleanup_page.py`: the clean-up plan page | `python3 dashboard/build_cleanup_page.py` | `kb/workflow/cleanup-plan.md` | `dashboard/cleanup-plan.html` | [[cleanup-plan]] |
