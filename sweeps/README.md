# sweeps/: SLURM templates and params files

Every FLOOXS sweep on HPG is one SLURM array: a template here, plus (for most templates) a params file here with one line per array task. Task N reads line N+1. This page says which template takes which file, the rules that keep the files a true record, and an index of every file with the run directories and job IDs it produced. The submit recipe and the log check are in `kb/workflow/sweep-pattern.md`; the generators are in `kb/tools/analysis-scripts.md`.

## Template families

| Family | Files | Driver | Line format | Run dir and logs |
|---|---|---|---|---|
| Generic rad-era template (all runs since 2026-10-23) | `radIV.slurm` | `drivers/$DRV.tcl`: `DRV` unset = radIV, `DRV=seeIV`, `DRV=pulsedIV` | `label\|lever=value;lever=value;...`; each pair becomes `set lever value` ahead of the driver, in order, so the last value of a lever wins | `results/$RUN/task_<i>/`, logs `results/$RUN/slurm_<job>_<i>.{out,err}` (given on the `sbatch` line) |
| Generic energy-balance template (Oct 8 - Oct 16) | `pulsedIV_eTemp.slurm` | `drivers/pulsedIV.tcl` | 14 positional columns `tag\|eTemp\|etTau\|etMob\|etStats\|trapEn\|trapPeak\|trapLevel\|hotTau\|hotEb\|trapMeanY\|Vg\|Vd_max\|teProfile`, then an optional 15th, `extra`, of `lever value;...` settings; `etStats -` keeps the model default | `results/$RUN/<tag>/` (named by tag, not `task_<i>`), logs in `results/eTemp_logs/` |
| One-shot October templates (finished records) | `pulsedIV_<study>.slurm`, `fieldPlate.slurm` | `drivers/pulsedIV.tcl` (`fieldPlate.slurm`: `drivers/fieldPlate.tcl`) | each template's header gives its own columns | hard-coded in the template |

- **Environment.** `radIV.slurm` reads `RUN`, `PARAMS`, `DRV` and `REPO` from `--export`; `pulsedIV_eTemp.slurm` reads `RUN`, `PARAMS` and (since `7beac86`, 2026-10-15) `REPO`. `REPO` defaults to the HPG main checkout; point it at an HPG worktree (`.../HEMTRAD-wt/<branch>`) to run a branch. Until `e8342ee` (2026-11-04) `radIV.slurm` had `REPO` fixed to the `rad-model` worktree, which is why the Oct 23 - Nov 4 run dirs are there.
- **Read at task start.** Each task reads its params line, the model files and the driver from `$REPO` when it starts, not at submission.
- **Copied model files.** Both generic templates copy all of `model/` (including `ETemp.tcl` and the SiN and 3D decks) since `ee0ad3b` (2026-11-21). Before that, `radIV.slurm` did not copy `ETemp.tcl` (and copied `rfdevice3d.tcl` only from `f59ee0b`, 2026-11-12), and `pulsedIV_eTemp.slurm` did not copy `rfdevice_SiN.tcl` or `rfdevice3d.tcl`.
- **One-shot templates are records.** Each one hard-codes its params file and run dir and was used for one study in October. Do not reuse them; a new pulsed study goes through `radIV.slurm` with `DRV=pulsedIV` and `ivCSV=pulsedIV_<label>.csv` on the line.
- **Paths changed at the October reorganisation.** Every file marked `*` in the index was committed at the repo root and moved into `sweeps/` by `42ecf73` (2026-10-12), which also repointed the templates to `model/`, `drivers/` and `sweeps/`. The template that actually ran is `git show 42ecf73^:<file>` (for example `git show 42ecf73^:pulsedIV_onsetField1.slurm`).

## Rules

1. **Never edit or regenerate a params file after its job ran.** The committed file is the record of what the job ran. A changed rerun gets a new file and a new study name. Four params files break this rule (radFine, radExp1b, radStepDiag5, radNHsmoke; see Known mismatches). The worst is `params_radFine.txt`, which now holds a different study from the job that first used the name.
2. **Never reuse a study name**, neither for a params file nor for a run dir. Reruns of an unchanged file have gone into a new run dir name (`rad28fit` -> `rad28fitB`); log such a rerun in `progress.md` with its job ID and add it to the index.
3. **Generated files come from their generator.** The files marked genRadStudy or genRad3d in the index are written by `analysis/genRadStudy.py` and `analysis/genRad3d.py`. Add a new study as a new function and `STUDIES` entry in the generator, never by editing the output. Run `python3 analysis/genRadStudy.py --check` (and `analysis/genRad3d.py --check`) first: it writes nothing and lists the files that would be created or changed. A plain run writes only new or unchanged files and refuses to change a tracked one; `--force NAME` lets study NAME's file change, and is only for a file whose job has not run. These options came in clean-up stage 2 (`kb/workflow/cleanup-plan.md`); before that each generator rewrote every file it owns on every run. After writing, `git diff --stat sweeps/` must list only the new study's file.
4. **Commit and push the params file, then `git pull --ff-only` on HPG, before `sbatch`.** A file missing on HPG fails the job within seconds (radFine 47554718).
5. **Do not rename existing files**, even where the names mix schemes (`radFinal2`..`radFinal12`, `radStepA`..`radStepM3`, `meshChkLoad_m10`, `trapMapF_field`, `onsetField3Ramp` writing `onsetField3RetryRamp`). Scripts, KB notes and `progress.md` cite the current names; this index is the lookup instead.
6. **Keep this index current.** Add a row when a new file is committed, and fill in its run dir and job ID when it is submitted.

## Known mismatches

**One params file, several run dirs (reruns under other names):**

| Params file | Run dirs and jobs | What changed between runs |
|---|---|---|
| `params_eTemp2.txt` | `20261008_eTemp2` 45189280; `20261008_eTemp3` 45193421; `20261008_eTemp4` 45197486; `20261008_eTemp6` 45209165; `20261008_eTemp7` 45210604; `20261012_eTemp8` 45691970 (crashed at setup), 45692148 | model and solver code only; the file is unchanged. eTemp3, eTemp4, eTemp6 and eTemp7 were stopped part-way (`progress.md` 2026-10-08) |
| `params_iterLimit.txt` | `20261013_iterLimit_invalid` 45791746; `20261013_iterLimit2` 45801978 | `drivers/pulsedIV.tcl` only: the first run set `Math iterLimit` after the solver was built, so the limit never applied (`kb/numerics/flooxs-gotchas.md`); its dir was renamed on HPG |
| `params_onsetField2.txt` | `20261002_onsetField2_cancelled` 44363616; `20261002_onsetField2` 44433016 | nothing: cancelled (Ian), then resubmitted unchanged |
| `params_seeSmoke1.txt` | rm: `20261029_seeSmoke1` 48227316; rm: `20261029_seeSmoke2` 48241815; rm: `20261102_seeSmoke3` 48965450 | `drivers/seeIV.tcl` only (tolerances, then radIV's stress numerics) |
| `params_radNHsmoke.txt` | rm: `20261026_radNHsmoke` 47860677; rm: `20261026_radNHsmoke2` 47861047 | the file: see the next table |
| `params_radExp1b.txt` | `20261111_radExp1b` 50847918 (cancelled); `20261111_radExp1c` 50892179 | the file: see the next table |
| `params_rad28fit.txt` | `20261112_rad28fit` 51040272; `20261113_rad28fitB` 51196550, 51249769 | nothing: tasks 1-3 rerun with a 48 h limit, because the originals hit 24 h in the stress ramp; 51249769 replaced task 3 after a conda failure |
| `params_radStepDiag5.txt` | `20261119_radStepDiag5` 52017613 (cancelled); `20261119_radStepDiag5b` 52018703 | the file and radIV's `vdCuts`: see the next table |
| `params_gateInj.txt` (branch) | gi: `20261015_gateInj_failed` 46040981; gi: `20261015_gateInj` 46042673 | `model/Poisson.tcl` on the branch (`e97c1fe`, an expression fix); the file is unchanged. The first job failed at once |

**Run dirs named differently from their params file:** `params_onsetField3Ramp.txt` -> `20261002_onsetField3RetryRamp`; `params_posMapLateRamp.txt` -> `20261002_posMapLateRetryRamp` (both names are hard-coded in their templates, and the analysis scripts pick up any `<run>Retry*` folder); `params_posMapLM.txt` -> `20261003_posMap_tl0.25_tp6e18`, `20261003_posMap_tl0.30_tp4e18`, `20261003_posMap_tl0.30_tp6e18`, `20261003_posMap_tl0.40_tp5e18`, `20261003_posMap_tl0.55_tp4e18`, with the SLURM logs in `20261003_posMapLM_logs`.

**Params files edited after their first commit** (the first four after a job had run):

| File | First job ran | Later version | Where the old version is |
|---|---|---|---|
| `params_radFine.txt` | Oct 24 radFine, job 47562303 (after 47554718 failed: file not yet on HPG), hand-written, commit `0fbf0ce` | Nov 5: replaced by a different study (`5c8412b`, genRadStudy), job 49735196 into `20261105_radFine` | `git show 0fbf0ce:sweeps/params_radFine.txt` (Ian, 2026-11-20: stays in git history). Cite either study with its job ID |
| `params_radExp1b.txt` | job 50847918 ran `0e38272` (occSafe let the stress run past 17 V; cancelled) | `6d7fff7` adds `Vd_stress=17.0` to both lines; run as radExp1c 50892179 | `git show 0e38272:sweeps/params_radExp1b.txt` |
| `params_radStepDiag5.txt` | job 52017613 ran the 4-line `8857f66` (cancelled after 1 h) | `f2edae8` adds a fifth line (library-mesh A_N1); run as radStepDiag5b 52018703 | `git show 8857f66:sweeps/params_radStepDiag5.txt` |
| `params_radNHsmoke.txt` | job 47860677 ran the 2-line `860d71d` (failed at once) | `78acfe7` adds `stressNoHolesX=0.1` to both lines and a third line; run as radNHsmoke2 47861047 | `git show 860d71d:sweeps/params_radNHsmoke.txt` |
| `params_radFinal12.txt` | never run as its own job | `6d7fff7` (same day) adds `Vd_stress=17.0` to its two biased lines; `params_radHV.txt` is derived from it | `git show 06af71b:sweeps/params_radFinal12.txt` |
| `params_radVth.txt`, `params_radMap1.txt` | 49570570 / 49570571; the submission was logged at 16:16 on Nov 4 (`74d4644`) | `9619606` at 16:15 the same day is the last edit, so the committed files are taken to be what ran | `git show e8342ee:sweeps/params_radVth.txt` |

**Generated files for a driver other than radIV:** `params_radGauss.txt` and `params_radGauss2.txt` are pulsedIV.tcl lines (run with `DRV=pulsedIV`), and `params_seeMap28.txt` is for seeIV. Before the stage-2 rewrite, the `analysis/genRadStudy.py` docstring named only seeMap28 as an exception, and its list of the files it writes left out `params_fpFixEB1p.txt` (it writes 61 files, the list had 60).

**Run dirs with no params file in `sweeps/`:**
- September and early October static-mobility runs (`20260924_lateOnset`, `20260925_lateOnsetB`, `20260925_lateOnsetC`, `20260925_lateOnsetD`, `20260925_lateOnsetE`, `20260925_lateOnsetF`, `20260925_lateOnsetG`, `20260925_lateOnsetH`, `20260925_lateOnsetI`, `20260925_trapPlacement`, `20260926_trapConcLevel`, `20260926_trapConcLevelRetry`, `20260926_trapMap`, `20260926_trapMapRetry`, `20260927_trapCone`, `20260927_trapConeCollapse`, `20260927_trapMapSets`, `20260927_trapMapSetsRetry`, `20260928_critBand`, `20261001_trapDeep`, `20261001_trapSiN`, `20261001_trapSiN_F`, `20261001_trapXYMap`, `20261001_trapXYMap0`): their params files are in `archive/static_mobility/` (README there).
- `20261016_fieldPlate`: `fieldPlate.slurm` takes no params file (its two decks are hard-coded).
- `eTemp_logs` (main, `field-capture` and `gate-injection` checkouts) and `20261003_posMapLM_logs`: SLURM logs only.
- `20261002_onsetField2_cancelled`, `20261013_iterLimit_invalid`, gi: `20261015_gateInj_failed`: renamed outputs of the cancelled, invalid or failed first runs listed above.
- `20261119_radEth1` (job 52000451, 14 tasks, first label `T_sin_pow`) in the HPG checkout labelled `dam-threshold`: no params file on any branch in this clone and no `progress.md` entry. Unrecorded; ask before using it.

## Archived

Moved to `archive/energy_balance/` in clean-up stage 4 with `drivers/eTempDebug_tail.tcl`:

| Was | Now | Run dir | Jobs | KB note |
|---|---|---|---|---|
| `sweeps/eTempDebug.slurm` | `archive/energy_balance/eTempDebug.slurm` | `20261008_eTempDebug/<tag>/` (hard-coded, so every rerun wrote into the same tag folders), logs `eTemp_logs/dbg_*` | Oct 8: 45207320 (panicked on a cut on a mesh line), 45208486, 45209164, 45210603; Oct 12: 45691969 (crashed at setup), 45692147 | energy-balance (its readings of these dumps are unverified) |
| `sweeps/params_eTempDebug.txt` | `archive/energy_balance/params_eTempDebug.txt` | as above | as above | energy-balance |

## Index

One row per file in `sweeps/` (and per params file that exists only on an `explore/*` branch), in order of first use.

- **Template, driver:** `radIV.slurm` alone means `DRV` unset (drivers/radIV.tcl). "own template" means the one-shot `pulsedIV_<study>.slurm` of the same name.
- **Run dirs** are under `results/` of the HPG main checkout (`/home/ianstafford/blue/ee1/ianstafford/HEMTRAD`; rsynced copies under `results/` on the workstation), except: `rm:` the `HEMTRAD-wt/rad-model` worktree, `fc:` `HEMTRAD-wt/field-capture`, `gi:` `HEMTRAD-wt/gate-injection`. "(states on /blue)" means the saved stress states are in the stress library (`kb/workflow/stress-library.md`).
- **Job IDs** are from `progress.md` and the HPG run directories. "job matched by content" means `progress.md` gives the job but not the file name; the match is by what the lines contain.
- **First commit:** short hash and date (2026) of the commit that added the file; `*` = added at the repo root and moved here by `42ecf73`.
- **Generated by:** `genRadStudy` = `analysis/genRadStudy.py`, `genRad3d` = `analysis/genRad3d.py`, `hand` = written by hand.
- **KB note:** a note name under `kb/` (`kb/index.md` lists them).
- **Status** (as of 2026-11-21): done (ran and was read; tasks that stopped early are in `progress.md` and the KB note), cancelled, superseded (replaced by the study named), repurposed (the file now holds a different study), never run, running, pending, branch-only. Every radIV or seeIV run before 2026-11-20 used the old FP contact box (`kb/results/fp-contact-fix.md`); the `fpFix*` studies redo key cases with the fixed box.

| File | Template, driver | Run dir(s) | Job ID(s) | First commit | Generated by | KB note | Status |
|---|---|---|---|---|---|---|---|
| `pulsedIV_trapMapF_field.slurm` | one-shot, pulsedIV.tcl | `20261001_trapMapF_field` | 44342967 | `515d9b5`* 10-01 | hand | field-mobility-trap-map | done |
| `params_trapMapF_field.txt` | own template | `20261001_trapMapF_field` | 44342967 | `515d9b5`* 10-01 | hand | field-mobility-trap-map | done |
| `pulsedIV_onsetField1.slurm` | one-shot, pulsedIV.tcl | `20261002_onsetField1` | 44359813 | `fb4847c`* 10-01 | hand | late-onset-search | done; header comment fixed after the run (`2ae6ca7`) |
| `params_onsetField1.txt` | own template | `20261002_onsetField1` | 44359813 | `fb4847c`* 10-01 | hand | late-onset-search | done |
| `pulsedIV_onsetField2.slurm` | one-shot, pulsedIV.tcl | `20261002_onsetField2`, `20261002_onsetField2_cancelled` | 44363616, 44433016 | `4ba9a16`* 10-01 | hand | late-onset-search | done; header comment fixed after the run (`2ae6ca7`) |
| `params_onsetField2.txt` | own template | `20261002_onsetField2`, `20261002_onsetField2_cancelled` | 44363616, 44433016 | `4ba9a16`* 10-01 | hand | late-onset-search | done; first job cancelled (Ian), resubmitted unchanged |
| `pulsedIV_onsetField3.slurm` | one-shot, pulsedIV.tcl | `20261002_onsetField3` | 44435511 | `9df8927`* 10-02 | hand | late-onset-search | done |
| `params_onsetField3.txt` | own template | `20261002_onsetField3` | 44435511 | `9df8927`* 10-02 | hand | late-onset-search | done |
| `pulsedIV_onsetField4.slurm` | one-shot, pulsedIV.tcl | `20261002_onsetField4` | 44440027 | `2d187c1`* 10-02 | hand | late-onset-search | cancelled (Ian) with 44 of 61 tasks done; not analysed |
| `params_onsetField4.txt` | own template | `20261002_onsetField4` | 44440027 | `2d187c1`* 10-02 | hand | late-onset-search | cancelled (Ian) with 44 of 61 tasks done; not analysed |
| `pulsedIV_posMapLate.slurm` | one-shot, pulsedIV.tcl | `20261002_posMapLate` | 44441813 | `2912623`* 10-02 | hand | position-maps | done |
| `params_posMapLate.txt` | own template | `20261002_posMapLate` | 44441813 | `2912623`* 10-02 | hand | position-maps | done |
| `pulsedIV_onsetField3Retry.slurm` | one-shot, pulsedIV.tcl | `20261002_onsetField3Retry` | 44443669 | `7b82876`* 10-02 | hand | late-onset-search | superseded by onsetField3Ramp (no stall resolved) |
| `params_onsetField3Retry.txt` | own template | `20261002_onsetField3Retry` | 44443669 | `7b82876`* 10-02 | hand | late-onset-search | superseded by onsetField3Ramp (no stall resolved) |
| `pulsedIV_onsetField3Ramp.slurm` | one-shot, pulsedIV.tcl | `20261002_onsetField3RetryRamp` | 44452288 | `875dc41`* 10-02 | hand | te-ramp | done; run dir name differs from the file name |
| `params_onsetField3Ramp.txt` | own template | `20261002_onsetField3RetryRamp` | 44452288 | `875dc41`* 10-02 | hand | te-ramp | done; run dir name differs from the file name |
| `pulsedIV_posMapLateRamp.slurm` | one-shot, pulsedIV.tcl | `20261002_posMapLateRetryRamp` | 44452289 | `875dc41`* 10-02 | hand | te-ramp | done; run dir name differs from the file name |
| `params_posMapLateRamp.txt` | own template | `20261002_posMapLateRetryRamp` | 44452289 | `875dc41`* 10-02 | hand | te-ramp | done; run dir name differs from the file name |
| `pulsedIV_posMapLM.slurm` | one-shot, pulsedIV.tcl | five `20261003_posMap_<set>`, logs in `20261003_posMapLM_logs` | 44573468 | `40cfadb`* 10-03 | hand | position-maps | done; one run dir per set (see below) |
| `params_posMapLM.txt` | own template | five `20261003_posMap_<set>`, logs in `20261003_posMapLM_logs` | 44573468 | `40cfadb`* 10-03 | hand | position-maps | done; one run dir per set (see below) |
| `pulsedIV_curveTracer.slurm` | one-shot, pulsedIV.tcl | `20261003_curveTracer` | 44573629 | `0715efb`* 10-03 | hand | gate-bias | done; task dirs are `Vg<Vg>_<devTag>/` |
| `params_curveTracer.txt` | own template | `20261003_curveTracer` | 44573629 | `0715efb`* 10-03 | hand | gate-bias | done |
| `pulsedIV_eTemp.slurm` | generic, pulsedIV.tcl | every row with template `pulsedIV_eTemp.slurm`; logs in `eTemp_logs` | - | `ab4ca9a`* 10-08 | hand | energy-balance | kept (generic; last used 10-16) |
| `params_eTemp0.txt` | `pulsedIV_eTemp.slurm` | `20261008_eTemp0` | 45185690 | `ab4ca9a`* 10-08 | hand | energy-balance | done (smoke test; job matched to the file by its content) |
| `params_eTemp1.txt` | `pulsedIV_eTemp.slurm` | `20261008_eTemp1` | 45186466 | `6cf4dc0`* 10-08 | hand | energy-balance | cancelled (Ian) with 6 of 13 tasks done; read |
| `params_eTemp2.txt` | `pulsedIV_eTemp.slurm` | `20261008_eTemp2`, `_eTemp3`, `_eTemp4`, `_eTemp6`, `_eTemp7`, `20261012_eTemp8` | 45189280, 45193421, 45197486, 45209165, 45210604, 45691970, 45692148 | `84fc8b1`* 10-08 | hand | energy-balance | done; rerun five times under other run names (see below) |
| `params_eTemp5.txt` | `pulsedIV_eTemp.slurm` | `20261008_eTemp5` | 45202242 | `b2cc0a3`* 10-08 | hand | energy-balance | done |
| `params_eTemp9.txt` | `pulsedIV_eTemp.slurm` | `20261012_eTemp9` | 45696870 | `fcd635c` 10-12 | hand | energy-balance | done |
| `params_eTemp10.txt` | `pulsedIV_eTemp.slurm` | `20261012_eTemp10` | 45711842 | `f410856` 10-12 | hand | energy-balance | done |
| `params_reorgCheck.txt` | `pulsedIV_eTemp.slurm` | `20261012_reorgCheck` | 45683803 | `529328c` 10-12 | hand | progress.md 10-12 | done (check of the repo reorganisation) |
| `params_eTempStdCheck.txt` | `pulsedIV_eTemp.slurm` | `20261013_eTempStdCheck` | 45766865 | `c8173f5` 10-13 | hand | energy-balance | done |
| `params_eTempStd1.txt` | `pulsedIV_eTemp.slurm` | `20261013_eTempStd1` | 45768739 | `c8173f5` 10-13 | hand | energy-balance | done |
| `params_iterLimit.txt` | `pulsedIV_eTemp.slurm` | `20261013_iterLimit_invalid`, `20261013_iterLimit2` | 45791746, 45801978 | `ee3c1fa` 10-13 | hand | flooxs-gotchas | done as iterLimit2; the first run was invalid (see below) |
| `params_vgEB.txt` | `pulsedIV_eTemp.slurm` | `20261015_vgEB` | 46040979 | `1875439` 10-15 | hand | vg-dependence | done |
| `params_vgEBgate.txt` | `pulsedIV_eTemp.slurm` | `20261015_vgEBgate` | 46052606 | `d50496d` 10-15 | hand | vg-dependence | done |
| `params_fieldCap.txt` | `pulsedIV_eTemp.slurm` (branch) | fc: `20261015_fieldCap` | 46040980 | `bd57c76` 10-15 | hand | vg-dependence | branch-only (`explore/field-capture`; same file on `explore/gate-injection`) |
| `params_fieldCapFN.txt` | `pulsedIV_eTemp.slurm` (branch) | fc: `20261015_fieldCapFN` | 46046442 | `afcfce6` 10-15 | hand | vg-dependence | branch-only (`explore/field-capture`) |
| `params_virtGate.txt` | `pulsedIV_eTemp.slurm` (branch) | fc: `20261015_virtGate` | 46052532 | `cb622dc` 10-15 | hand | vg-dependence | branch-only (`explore/field-capture`) |
| `params_virtGate2.txt` | `pulsedIV_eTemp.slurm` (branch) | fc: `20261015_virtGate2` | 46054851 | `f153ef7` 10-15 | hand | vg-dependence | branch-only (`explore/field-capture`); job matched by content |
| `params_virtGate3.txt` | `pulsedIV_eTemp.slurm` (branch) | fc: `20261015_virtGate3` | 46057777 | `9296121` 10-15 | hand | vg-dependence | branch-only (`explore/field-capture`) |
| `params_virtGate4.txt` | `pulsedIV_eTemp.slurm` (branch) | fc: `20261015_virtGate4` | 46106674 | `6d1bcfa` 10-15 | hand | vg-dependence | branch-only (`explore/field-capture`) |
| `params_virtGate5.txt` | `pulsedIV_eTemp.slurm` (branch) | fc: `20261016_virtGate5` | 46209709 | `e6b7bf7` 10-16 | hand | vg-dependence | branch-only (`explore/field-capture`) |
| `params_virtGate6.txt` | `pulsedIV_eTemp.slurm` (branch) | fc: `20261016_virtGate6` | 46224198 | `7b31532` 10-16 | hand | vg-dependence | branch-only (`explore/field-capture`) |
| `params_gateInj.txt` | `pulsedIV_eTemp.slurm` (branch) | gi: `20261015_gateInj`, `20261015_gateInj_failed` | 46040981, 46042673 | `7e99eb1` 10-15 | hand | vg-dependence | branch-only (`explore/gate-injection`); first job failed at once |
| `params_gateInjFN.txt` | `pulsedIV_eTemp.slurm` (branch) | gi: `20261015_gateInjFN` | 46046389 | `bba1cb0` 10-15 | hand | vg-dependence | branch-only (`explore/gate-injection`) |
| `params_gateInjFN2.txt` | `pulsedIV_eTemp.slurm` (branch) | gi: `20261015_gateInjFN2` | 46048098 | `c6cdd35` 10-15 | hand | vg-dependence | branch-only (`explore/gate-injection`); job matched by content (gate-edge field probe) |
| `fieldPlate.slurm` | one-shot, fieldPlate.tcl (no params file) | `20261016_fieldPlate` | 46241088 | `4640da1` 10-16 | hand | highk-vs-sin | done |
| `pulsedIV_sensitivity.slurm` | one-shot, pulsedIV.tcl | `20261017_sensitivity` | 46462234 | `c3d9403` 10-17 | hand | trap-sensitivity | done |
| `params_sensitivity.txt` | own template | `20261017_sensitivity` | 46462234 | `c3d9403` 10-17 | hand | trap-sensitivity | done |
| `pulsedIV_deckVg1.slurm` | one-shot, pulsedIV.tcl | `20261021_deckVg1` | 47062225 | `f4f091f` 10-21 | hand | highk-vs-sin | done |
| `params_deckVg1.txt` | own template | `20261021_deckVg1` | 47062225 | `f4f091f` 10-21 | hand | highk-vs-sin | done |
| `radIV.slurm` | generic; DRV picks the driver | every row with template `radIV.slurm` | - | `bf4cd84` 10-23 | hand | sweep-pattern | in use (generic) |
| `params_radCal1.txt` | `radIV.slurm` | rm: `20261023_radCal1` | 47311016 | `bf4cd84` 10-23 | hand | calibration | done |
| `params_radCal2.txt` | `radIV.slurm` | rm: `20261023_radCal2` | 47324103 | `fea974c` 10-23 | hand | calibration | done |
| `params_radCal3.txt` | `radIV.slurm` | rm: `20261023_radCal3` | 47327599 | `a779243` 10-23 | hand | calibration | done |
| `params_radDam1.txt` | `radIV.slurm` | rm: `20261023_radDam1` | 47327524 | `009fd64` 10-23 | hand | rad-model | done |
| `params_radDam2.txt` | `radIV.slurm` | rm: `20261023_radDam2` | 47356193 | `25562d8` 10-23 | hand | rad-model | done |
| `params_radIns.txt` | `radIV.slurm` | rm: `20261024_radIns` | 47458257 | `3fa478d` 10-24 | hand | insulator-traps | done |
| `params_radWin.txt` | `radIV.slurm` | rm: `20261024_radWin` | 47458256 | `3fa478d` 10-24 | hand | rad-model | done |
| `params_radPost.txt` | `radIV.slurm` | rm: `20261024_radPost` | 47523721 | `41ec394` 10-24 | hand | rad-model | done |
| `params_radFine.txt` | `radIV.slurm` | rm: `20261024_radFine` (Oct 24); `20261105_radFine` (Nov 5) | 47554718, 47562303 (Oct 24); 49735196 (Nov 5) | `0fbf0ce` 10-24 | hand (Oct 24); genRadStudy (Nov 5) | rad-model, damage-region-map | repurposed: two studies under one name (see below) |
| `params_radFit1.txt` | `radIV.slurm` | rm: `20261025_radFit1` | 47593908 | `c65eda8` 10-25 | hand | rad-model | done |
| `params_radFit2.txt` | `radIV.slurm` | rm: `20261025_radFit2` | 47606666 | `ab6655e` 10-25 | hand | rad-model | done |
| `params_radNEsmoke.txt` | `radIV.slurm` | rm: `20261025_radNEsmoke` | 47625503 | `2050fe7` 10-25 | hand | rad-model | done (smoke test) |
| `params_radNE1.txt` | `radIV.slurm` | rm: `20261025_radNE1` | 47628955 | `1374fad` 10-25 | hand | rad-model | done |
| `params_radNE2.txt` | `radIV.slurm` | rm: `20261025_radNE2` | 47662463 | `532d7cf` 10-25 | hand | rad-model | done |
| `params_radFinal.txt` | `radIV.slurm` | rm: `20261025_radFinal` | 47693156 | `bf0abd9` 10-25 | hand | rad-model | done |
| `params_radPhys1.txt` | `radIV.slurm` | rm: `20261025_radPhys1` | 47725314 | `1c9a41c` 10-25 | hand | rad-model | done |
| `params_radFinal2.txt` | `radIV.slurm` | rm: `20261025_radFinal2` | 47752290 | `94c589e` 10-25 | hand | rad-model | done |
| `params_radFinal3.txt` | `radIV.slurm` | rm: `20261026_radFinal3` | 47773690 | `8675788` 10-26 | hand | rad-model | done |
| `params_radFinal4.txt` | `radIV.slurm` | rm: `20261026_radFinal4` | 47797775 | `6e44932` 10-26 | hand | rad-model | done |
| `params_radFinal5.txt` | `radIV.slurm` | rm: `20261026_radFinal5` | 47806744 | `d3c1da5` 10-26 | hand | rad-model | done |
| `params_radFinal6.txt` | `radIV.slurm` | rm: `20261026_radFinal6` | 47829928 | `c85aa34` 10-26 | hand | rad-model | done |
| `params_radFinal7.txt` | `radIV.slurm` | rm: `20261026_radFinal7` | 47852523 | `88a1ed4` 10-26 | hand | rad-model | done |
| `params_radNHsmoke.txt` | `radIV.slurm` | rm: `20261026_radNHsmoke`, `20261026_radNHsmoke2` | 47860677, 47861047 | `860d71d` 10-26 | hand | rad-model | done as radNHsmoke2; edited after the first job (see below) |
| `params_radQDsmoke.txt` | `radIV.slurm` | rm: `20261026_radQDsmoke` | 47875456 | `dcbf974` 10-26 | hand | rad-model | done (its stressQfnDamp lever had no effect, flooxs-gotchas) |
| `params_radFinal8.txt` | `radIV.slurm` | rm: `20261026_radFinal8` | 47887339 | `29ec6e6` 10-26 | hand | rad-model | done |
| `params_radFinal9.txt` | `radIV.slurm` | rm: `20261027_radFinal9` | 47908735 | `f47857a` 10-27 | hand | rad-model | done |
| `params_radFinal10.txt` | `radIV.slurm` | rm: `20261027_radFinal10` | 47943462 | `7a377d0` 10-27 | hand | rad-model | done |
| `params_radFinal11.txt` | `radIV.slurm` | rm: `20261027_radFinal11` | 47959281 | `3eef67f` 10-27 | hand | rad-model | done |
| `params_stressDiag1.txt` | `radIV.slurm` | rm: `20261028_stressDiag1` | 48125435 | `6997d69` 10-28 | hand | rad-model | done |
| `params_stressAbs1.txt` | `radIV.slurm` | rm: `20261028_stressAbs1` | 48141047 | `9b983f3` 10-28 | hand | rad-model | done (its stressQfnAbs lever had no effect, flooxs-gotchas) |
| `params_stressAbs2.txt` | `radIV.slurm` | rm: `20261028_stressAbs2` | 48141104 | `dbd063d` 10-28 | hand | rad-model | done |
| `params_stressDiag2.txt` | `radIV.slurm` | rm: `20261028_stressDiag2` | 48147357 | `9f8def7` 10-28 | hand | rad-model | done |
| `params_stressDiag3.txt` | `radIV.slurm` | rm: `20261029_stressDiag3` | 48159016 | `7b8df74` 10-28 | hand | rad-model | done |
| `params_stressFloor1.txt` | `radIV.slurm` | rm: `20261029_stressFloor1` | 48161617 | `6594e48` 10-29 | hand | rad-model | done |
| `params_stressClamp1.txt` | `radIV.slurm` | rm: `20261029_stressClamp1` | 48174580 | `fcb7f6a` 10-29 | hand | rad-model | cancelled (Ian OK): too slow |
| `params_stressSafe1.txt` | `radIV.slurm` | rm: `20261029_stressSafe1` | 48182110 | `e7227cd` 10-29 | hand | rad-model | done (occSafe reaches 28 V) |
| `params_rad28a.txt` | `radIV.slurm` | rm: `20261029_rad28a` | 48206375 | `639faae` 10-29 | hand | rad-model | done |
| `params_seeSmoke1.txt` | `radIV.slurm`, DRV=seeIV | rm: `20261029_seeSmoke1`, `20261029_seeSmoke2`, `20261102_seeSmoke3` | 48227316, 48241815, 48965450 | `f9818a6` 10-29 | hand | see-plan | three runs of one file, seeIV fixed in between (see below) |
| `params_seeIso1.txt` | `radIV.slurm`, DRV=seeIV | rm: `20261102_seeIso1` | 48965552 | `a205c9e` 11-02 | hand | see-plan | cancelled (Ian OK) |
| `params_seeGen1.txt` | `radIV.slurm`, DRV=seeIV | rm: `20261102_seeGen1` | 49135298 | `9bd997f` 11-02 | hand | see-plan | done |
| `params_seeGen2.txt` | `radIV.slurm`, DRV=seeIV | rm: `20261104_seeGen2` | 49511531 | `9621b78` 11-04 | hand | see-plan | done |
| `params_radChk.txt` | `radIV.slurm` | `20261104_radChk` | 49552956 | `e8342ee` 11-04 | genRadStudy | rad-model | done |
| `params_radVth.txt` | `radIV.slurm` | `20261104_radVth` | 49570570 | `e8342ee` 11-04 | genRadStudy | rad-model | done; last edit `9619606` came one minute before the submission was logged |
| `params_radMap1.txt` | `radIV.slurm` | `20261104_radMap1` | 49570571 | `e8342ee` 11-04 | genRadStudy | damage-region-map | done; last edit `9619606` came one minute before the submission was logged |
| `params_radMesh.txt` | `radIV.slurm` | `20261104_radMesh` | 49606872 | `b9f0ace` 11-04 | genRadStudy | damage-region-map | done |
| `params_radFam.txt` | `radIV.slurm` | `20261104_radFam` | 49606874 | `b9f0ace` 11-04 | genRadStudy | damage-region-map | done |
| `params_radStress.txt` | `radIV.slurm` | `20261104_radStress` | 49606875 | `b9f0ace` 11-04 | genRadStudy | ron-increase | done |
| `params_radVth2.txt` | `radIV.slurm` | `20261104_radVth2` | 49606876 | `b9f0ace` 11-04 | genRadStudy | rad-model | done |
| `params_radRon.txt` | `radIV.slurm` | `20261104_radRon` | 49606877 | `b9f0ace` 11-04 | genRadStudy | ron-increase | done |
| `params_radVth3.txt` | `radIV.slurm` | `20261104_radVth3` | 49614033 | `6072eb7` 11-04 | genRadStudy | rad-model | done |
| `params_radMulti.txt` | `radIV.slurm` | `20261105_radMulti` | 49735488 | `fc01d3a` 11-05 | genRadStudy | damage-region-map | done (8 of 61 tasks ran out of memory, not rerun) |
| `params_radEmit.txt` | `radIV.slurm` | `20261105_radEmit` | 49834170 | `06f08b4` 11-05 | genRadStudy | damage-region-map | done (15 tasks); the 6 emitRest tasks were cancelled after a driver bug |
| `params_radEmit2.txt` | `radIV.slurm` | `20261105_radEmit2` | 49853997 | `b6b74c5` 11-05 | genRadStudy | damage-region-map | done |
| `params_radEmit3.txt` | `radIV.slurm` | `20261107_radEmit3` | 50128200 | `eaa9b22` 11-07 | genRadStudy | damage-region-map | done |
| `params_radChk2.txt` | `radIV.slurm` | `20261107_radChk2` | 50128862 | `3e1ffc3` 11-07 | genRadStudy | damage-region-map | done |
| `params_radGauss.txt` | `radIV.slurm`, DRV=pulsedIV | `20261107_radGauss` | 50128863 | `3e1ffc3` 11-07 | genRadStudy | damage-region-map | done |
| `params_radMap2.txt` | `radIV.slurm` | `20261107_radMap2` | 50128864 | `3e1ffc3` 11-07 | genRadStudy | damage-region-map | done |
| `params_radGauss2.txt` | `radIV.slurm`, DRV=pulsedIV | `20261107_radGauss2` | 50148046 | `02c4dfd` 11-07 | genRadStudy | damage-region-map | done |
| `params_radEB1.txt` | `radIV.slurm` | `20261109_radEB1` | 50411481 | `25a3a2c` 11-09 | genRadStudy | rad-model | done |
| `params_radEB2.txt` | `radIV.slurm` | `20261109_radEB2` | 50470082 | `7d5de2f` 11-09 | genRadStudy | rad-model | done |
| `params_radFinal12.txt` | `radIV.slurm` | - | - | `06af71b` 11-11 | genRadStudy | rad-model | never run as its own job (radChk and radEB1 had run its lines); edited `6d7fff7`; feeds radHV |
| `params_radExp1.txt` | `radIV.slurm` | `20261111_radExp1` | 50831893 | `4ada678` 11-11 | genRadStudy | rad-model | done |
| `params_radExp1b.txt` | `radIV.slurm` | `20261111_radExp1b`, `20261111_radExp1c` | 50847918, 50892179 | `0e38272` 11-11 | genRadStudy | rad-model | done as radExp1c; edited after the first job (see below) |
| `params_radExp2.txt` | `radIV.slurm` | `20261112_radExp2` | 51020993 | `13a867d` 11-12 | genRadStudy | rad-model | done |
| `params_radExp3.txt` | `radIV.slurm` | `20261112_radExp3` | 51021670 | `47063a0` 11-12 | genRadStudy | rad-model | done |
| `params_radHV.txt` | `radIV.slurm` | `20261112_radHV` | 51027334 | `b04cc46` 11-12 | genRadStudy | rad-model | done |
| `params_radStrike2.txt` | `radIV.slurm` | `20261112_radStrike2` | 51027921 | `6210e3b` 11-12 | genRadStudy | rad-model | done |
| `params_rad28fit.txt` | `radIV.slurm` | `20261112_rad28fit`, `20261113_rad28fitB` | 51040272; 51196550, 51249769 | `fba1ffe` 11-12 | genRadStudy | rad-model | done; tasks 1-3 rerun as rad28fitB (see below) |
| `params_rad3dBuild.txt` | `radIV.slurm` | `20261112_rad3dBuild` | 51045898 | `f59ee0b` 11-12 | genRad3d | 3d-plan | done |
| `params_rad3dSolve.txt` | `radIV.slurm` | `20261112_rad3dSolve` | 51052220 | `232fa56` 11-12 | genRad3d | 3d-plan | done |
| `params_rad3dTrack1.txt` | `radIV.slurm` | `20261112_rad3dTrack1` | 51061333, 51061334 | `1e50c44` 11-12 | genRad3d | 3d-plan | done (the UMFPACK task ran out of memory; the three track sweeps gave up early) |
| `params_radStrikeN.txt` | `radIV.slurm` | `20261113_radStrikeN` | 51174895 | `6b3c8d5` 11-13 | genRadStudy | rad-model | done |
| `params_radStressIO.txt` | `radIV.slurm` | `20261114_radStressIO` | 51380388, 51380389 | `d9b03a3` 11-14 | genRadStudy | stress-library | done |
| `params_rad28strike.txt` | `radIV.slurm` | `20261115_rad28strike` | 51454301, 51454302, 51454303 | `37fe807` 11-15 | genRadStudy | stress-library | superseded by rad28strikeL: the save tasks hit 48 h, all three jobs cancelled |
| `params_stressLib.txt` | `radIV.slurm` | `20261115_stressLib` (states on /blue) | 51459840 | `9dc97a6` 11-15 | genRadStudy | stress-library | done (HighK); SiN continued by stressLibResume |
| `params_rad28strikeL.txt` | `radIV.slurm` | `20261117_rad28strikeL` | 51762900, 51763582 | `175d35a` 11-16 | genRadStudy | step-search-28v | done; the first job failed at once (driver fix `a308148`) |
| `params_rad3dRod.txt` | `radIV.slurm` | `20261117_rad3dRod` | 51784348, 51784349, 51784350 | `6ee73d8` 11-17 | genRad3d | 3d-plan | 2D reference tasks 3, 6, 7 ran; 3D tasks 0-2 cancelled (3D field wrong, 3d-plan); 3D tasks 4-5 never submitted |
| `params_radStepA.txt` | `radIV.slurm` | `20261117_radStepA` | 51784676 | `b54ea98` 11-17 | genRadStudy | step-search-28v | done |
| `params_radStepB.txt` | `radIV.slurm` | `20261117_radStepB` | 51799601 | `6a6e14f` 11-17 | genRadStudy | step-search-28v | done |
| `params_radStepC.txt` | `radIV.slurm` | `20261117_radStepC` | 51799741, 51799742 | `26f8ab7` 11-17 | genRadStudy | step-search-28v | done |
| `params_radStepD.txt` | `radIV.slurm` | `20261117_radStepD` | 51801163 | `1c00ba9` 11-17 | genRadStudy | step-search-28v | done |
| `params_radStepE.txt` | `radIV.slurm` | `20261117_radStepE` | 51801897, 51801898 | `51a0136` 11-17 | genRadStudy | step-search-28v | done |
| `params_radStepF.txt` | `radIV.slurm` | `20261117_radStepF` | 51811467, 51811468 | `8078203` 11-17 | genRadStudy | step-search-28v | done |
| `params_radStepG.txt` | `radIV.slurm` | `20261117_radStepG` | 51823696 | `5a9428a` 11-17 | genRadStudy | step-search-28v | done |
| `params_radStepH.txt` | `radIV.slurm` | `20261118_radStepH` | 51871249 | `27e94a5` 11-18 | genRadStudy | step-search-28v | done |
| `params_radStepI.txt` | `radIV.slurm` | `20261118_radStepI` | 51878761 | `349a5d3` 11-18 | genRadStudy | step-search-28v | done |
| `params_meshChkStress.txt` | `radIV.slurm` | `20261118_meshChkStress` | 51883722 | `43396a7` 11-18 | genRadStudy | step-search-28v | done |
| `params_radStepJ.txt` | `radIV.slurm` | `20261118_radStepJ` | 51922589 | `f26f0e7` 11-18 | genRadStudy | step-search-28v | done |
| `params_meshChkLoad_m10.txt` | `radIV.slurm` | `20261118_meshChkLoad_m10` | 51939191 | `17977a2` 11-18 | genRadStudy | step-search-28v | done |
| `params_meshChkLoad_m5fix.txt` | `radIV.slurm` | `20261118_meshChkLoad_m5fix` | 51939192 | `17977a2` 11-18 | genRadStudy | step-search-28v | done |
| `params_radStepK.txt` | `radIV.slurm` | `20261118_radStepK` | 51939558 | `e99e44d` 11-18 | genRadStudy | step-search-28v | done |
| `params_seeMap28.txt` | `radIV.slurm`, DRV=seeIV | `20261118_seeMap28` | 51945449 | `233a6f1` 11-18 | genRadStudy | see-plan | done |
| `params_stressLibResume.txt` | `radIV.slurm` | `20261119_stressLibResume` (states on /blue) | 51998839 | `287e7a7` 11-19 | genRadStudy | stress-library | done (SiN library to 84 V) |
| `params_radStepDiag.txt` | `radIV.slurm` | `20261119_radStepDiag` | 51998840 | `287e7a7` 11-19 | genRadStudy | step-mechanism | done |
| `params_radStepDiag5.txt` | `radIV.slurm` | `20261119_radStepDiag5`, `20261119_radStepDiag5b` | 52017613, 52018703 | `8857f66` 11-19 | genRadStudy | step-mechanism | done as radStepDiag5b; edited after the first job (see below) |
| `params_radStepM.txt` | `radIV.slurm` | `20261119_radStepM` | 52044406 | `23c1936` 11-19 | genRadStudy | step-search-28v | done |
| `params_meshChkStress2p5.txt` | `radIV.slurm` | `20261119_meshChkStress2p5` | 52044407 | `23c1936` 11-19 | genRadStudy | step-search-28v | cancelled at Vd 20 (old FP contact box) |
| `params_radStepM2.txt` | `radIV.slurm` | `20261120_radStepM2` | 52072550 | `294c57a` 11-19 | genRadStudy | step-search-28v | done |
| `params_radStepM3.txt` | `radIV.slurm` | - | - | `56dd4c9` 11-20 | genRadStudy | step-search-28v | never run: the stress it loads (meshChkStress2p5) was cancelled |
| `params_fpFixStress.txt` | `radIV.slurm` | `20261120_fpFixStress` (states on /blue) | 52134552 | `591715e` 11-20 | genRadStudy | fp-contact-fix | done (28 V, both decks) |
| `params_fpFixPre.txt` | `radIV.slurm` | `20261120_fpFixPre` | 52134553 | `591715e` 11-20 | genRadStudy | fp-contact-fix | done |
| `params_fpFixEB1.txt` | `radIV.slurm` | `20261120_fpFixEB1` | 52134554 | `591715e` 11-20 | genRadStudy | fp-contact-fix | done |
| `params_fpFixLoad.txt` | `radIV.slurm` | - | - | `591715e` 11-20 | genRadStudy | fp-contact-fix | never run; replaced by fpFixScale28 (Nov 21) |
| `params_fpFixMesh.txt` | `radIV.slurm` | `20261120_fpFixMesh` (states on /blue) | 52135538 | `bd4430f` 11-20 | genRadStudy | stress-library | done (m5fix and m2p5 at 28 V) |
| `params_fpFixEB1p.txt` | `radIV.slurm` | `20261120_fpFixEB1p` | 52140899 | `50eb28f` 11-20 | genRadStudy | fp-contact-fix | done |
| `params_fpFixScaleEB1.txt` | `radIV.slurm` | `20261121_fpFixScaleEB1` | 52223190 | `9025b73` 11-21 | genRadStudy (written first by a one-off snippet, identical) | fp-contact-fix | done (scale 1.5e18) |
| `params_fpFixScale28.txt` | `radIV.slurm` | `20261122_fpFixScale28` | 52354341 (HighK), 52385669 (SiN) | `9025b73` 11-21 | genRadStudy (written first by a one-off snippet, identical) | fp-contact-fix | done |
| `params_fxRadHV.txt` | `radIV.slurm` | `20261122_fxRadHV` | 52357001 | `a16dd0a` 11-22 | genRadStudy | fp-contact-fix | done (4 of 6 gave up before 28 V) |
| `params_fxRadStrike2.txt` | `radIV.slurm` | `20261122_fxRadStrike2` | 52357002 | `a16dd0a` 11-22 | genRadStudy | fp-contact-fix | done |
| `params_fxRadStrikeN.txt` | `radIV.slurm` | `20261122_fxRadStrikeN` | 52357003 | `a16dd0a` 11-22 | genRadStudy | fp-contact-fix | done |
| `params_fxSeeMap28.txt` | `radIV.slurm`, DRV=seeIV | `20261122_fxSeeMap28` | 52357004 | `a16dd0a` 11-22 | genRadStudy | fp-contact-fix | done (maps not plotted yet) |
| `params_fxMeshStressM10.txt` | `radIV.slurm` | `20261122_fxMeshStressM10` (states on /blue) | 52357005 | `a16dd0a` 11-22 | genRadStudy | fp-contact-fix | done (m10 28 V state saved) |
| `params_fpFixScale28b.txt` | `radIV.slurm` | `20261124_fpFixScale28b` | 52585664 | `efe9bcf` 11-24 | genRadStudy | fp-contact-fix | running |
