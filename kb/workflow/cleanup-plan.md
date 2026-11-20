---
title: Clean-up plan and KB audit (2026-11-20)
tags: [workflow, plan, cleanup]
date: 2026-11-20
source: survey workflow wf_fb7accb6-e0e (seven readers, each finding re-checked by an independent verifier); progress.md 2026-11-20
---
# Clean-up plan and KB audit (2026-11-20)

Published page: https://claude.ai/artifact/QTDF84jNysUWQcsTfsswKp (rebuild with `python3 dashboard/build_cleanup_page.py`, then republish `dashboard/cleanup-plan.html`).

**How this was made.** Seven readers each surveyed one slice of the repo: drivers, model, `analysis/genRadStudy.py`, the other analysis scripts, sweeps / bin / layout, the KB results notes, and the rest of the KB. A separate skeptic then re-checked every finding against the files. Of 156 findings, 155 survived (115 confirmed, 40 confirmed with corrections) and 1 was refuted. IDs (DRV-, MOD-, GEN-, AN-, LAY-, KB-R-, KBC-) refer to the appendix. **Nothing has been changed yet.** Every step below is behaviour-preserving unless it says otherwise, and each code stage has an acceptance test.

**Baseline facts the plan relies on:**
- `genRadStudy.py` run on a clean `git archive` copy reproduces all 55 params files it writes byte-for-byte.
- The three CRLF model files are fully CRLF.
- No wikilink in the KB is broken.

## 1. Decisions for Ian (before any clean-up)

1. **DONE 2026-11-20 (Ian: fix it). FP contact covers the drain half of the T-gate head (MOD-1, confirmed locally).** Fixed in all three decks (lever `fpBoxOld`, default 0 = fixed). The 2.5 nm stress (old box) was cancelled; the stress library, the pre-irradiation curves and the Nov 11 model are being rerun ([[fp-contact-fix]]).
   - The FP contact box in all three decks reaches into the head metal (`rfdevice.tcl:88`, `rfdevice_SiN.tcl:91`, `rfdevice3d.tcl:103`).
   - At the 28 V stress the head's drain corner sits at −0.5 to −0.6 V against the FP instead of −10 V. Numbers and the check are in `progress.md` (2026-11-20 afternoon).
   - It probably changes the stress field and damage in every rad-era result. Fixing it is a physics change: fix and redo the library and key results, or keep it as a documented caveat?
   - Stage 3d can go ahead after the fix tests.
2. **Measured numbers in tracked files of the public repo (AN-2, KB-R-14, LAY-7 / DRV-18).**
   - `analysis/radCompare.py` hard-codes three measured pre-irradiation values. By default it overlays the measured curves on any output path when the local targets file exists.
   - `kb/results/rad-model.md` has a "Measured" column (:61), and its :129 and :266 give or imply a measured onset.
   - Is `radPlot1` measured or simulated? It is cited in `static-era-lessons.md:10`.
   - The untracked `drivers/trim/TRIM_NCY2_SiN_Au2256.IN` names the measured device.
   - Proposal: qualitative wording in tracked files, numbers moved to the untracked measured notes, and a `.gitignore` rule for `*NCY2*`. These lines have been in public history since October, so a further history purge is a separate yes/no.
3. **useTraps / stressSkip guards (DRV-7).**
   - A run with only `damGaussF` strikes (damPeak 0, no damGauss) gets `trapEn 0`, and the strikes are silently ignored.
   - The stressSkip check misses the field-scaled strike levers.
   - Fixing either changes behaviour, though only for configurations no committed params file uses.
4. **energy-balance "first Newton update" readings (DRV-11, KBC-9).** The eTempDebug dumps were never capped at one or two iterations, because `iterLimit` is read once at solver build. The energy-balance note's reading of them is unverified. Record that as a caveat, or recheck if the thermo term is ever resumed?
5. **Archive or keep:**
   - `drivers/stressFreeze.tcl`: still named as the tool for the open off-state pre-stress test (DRV-15).
   - The untracked `bin/hpg_sbatch.sh`: obsolete for radIV.slurm, so delete it or rewrite it (LAY-6).
6. **Restore the October radFine record (GEN-2, KB-GEN-1, KB-R-13).** `params_radFine.txt` was overwritten on Nov 5 by a different study. Write `git show 0fbf0ce:sweeps/params_radFine.txt` to `archive/radFine_2026-10-24/` with a README (job 47562303).

## 2. Stage 1: docs, KB and comments (no behaviour change)

The main theme is an **era gap**. Most orientation docs were written in the pulsedIV curve-tracer era (Sep 23 – Oct 16) and never brought forward to radIV.tcl / radIV.slurm / the stress library, which all work since Oct 23 uses. Several gaps can cause a wrong or wasted run.

**2a. Orientation docs (do first):**
- **High: the log check misses radIV failures.** The mandatory post-array log check (CLAUDE.md §2, `kb/workflow/sweep-pattern.md` step 7) names only `PULSED GAVE UP`. radIV / seeIV failures print `IDVD GAVE UP`, `IDVG GAVE UP`, `RAMP GAVE UP`, `DAMAGE solve failed` and `<tg> measurement failed`; normal runs end with `RADIV DONE` / `SEEIV DONE` (KBC-1).
  - Add a per-driver marker table to sweep-pattern, and have §2 point to it.
- **sweep-pattern rewrite: the radIV.slurm recipe** (KBC-5, LAY-4, KB-GEN-2):
  - the `label|k=v;…` format;
  - `RUN`, `PARAMS`, `DRV` and `REPO`, with `mkdir -p results/$RUN` first;
  - the last value wins;
  - the params file is read at task start;
  - ETemp.tcl is not copied into task directories.
- **README layout table** (LAY-1), **drivers.md** (DRV-1, KBC-11) and **index.md**:
  - radIV.tcl is the main driver; pulsedIV.tcl is the Sep–Oct curve-tracer driver;
  - add entries for seeIV, fieldPlate, render3d_build, rfdevice3d and drivers/trim/.
- **CLAUDE.md:**
  - §7 KB map: it omits all 12 rad-era notes. Replace the per-note list with a pointer to `kb/index.md` plus the entry notes (LAY-11, KB-R-20, KBC-15).
  - §4 data rule: "commit `data/`" conflicts with the measured-data rule in `.gitignore`. Add the public-repo rule and "stage by explicit path" (KBC-4).
  - §6: add a 3D brick-gradient bullet (KBC-3) and a "pdb solver parameters are read once at solver build" bullet (KBC-9).
- **levers.md:** restructure into one table per source file (model, GaN/Metal/Continuity/Poisson, decks, pulsedIV, radIV, seeIV, rfdevice3d).
  - Record radIV's own defaults (trapLevel 0.30, hotEb 1.0, hotTau 1e-14, dampValue 0.05, retryDepth 6, Vd_max 10, Vd_step 0.25, Vg_out +1, Vd_stress 28) and its overrides of trapEn / trapShape.
  - About 31 levers used in current params files are undocumented (KBC-2, DRV-10, KB-GEN-3, MOD-10).
  - Fix the `deviceDeck` example path (DRV-22).
- **analysis-scripts.md:** it lists 13 of 58 scripts. Regenerate from the docstrings, grouped by study, and add the generators genRadStudy.py, genRad3d.py and testRegister.py (AN-KB-1, KBC-12, LAY-3).
- **Other notes:**
  - project-goal: add the rad-model goal (KBC-16).
  - glossary: rad-era terms such as library / m10 / m5fix / m2p5, pocket, row A, band b and HPD (KBC-21).
  - repo-locations: the `/blue` stress library and HEMTRAD-FANGS (KBC-6).
  - hpg-workflow: the current reconnect script (KBC-7).
  - dashboard.md: the third tracked page and the branch wording (LAY-15, KBC-25).
- **New atomic notes:**
  - `kb/model/damage-model.md`: the damage laws, which field each uses, and which runs used them.
  - `kb/workflow/stress-library.md`: save, load, resume, mesh caveat.
  - A radIV driver note (KBC-13).

**2b. KB conflicts and stale notes:** see §6. The biggest are current-status (KB-R-1, -2, -6), rad-model (KB-R-4), see-plan (KB-R-3, -15) and the radFine name (KB-GEN-1).

**2c. Code comments only:**
- radIV:
  - a header that maps the stages and lists all outputs (DRV-8);
  - the `dam2*` and `damYmin` comments, which describe old roles (DRV-2);
  - comments detached from their levers (DRV-3; move comments only, not code, in this stage).
- Model files:
  - `Metal.tcl` comments say AlGaN Ec, but the code uses Nitride Ec (MOD-2);
  - the "25 nm AlGaN" comment next to `Al_Thick 0.015` (MOD-5);
  - GaN.tcl's unused Farahmand high-field keys, to be marked "reference only" (MOD-7);
  - masterD's stale `CLAUDE.md 10m` reference and the hotMu claim (MOD-8);
  - ETemp.tcl's k/q constant, which needs a comment (MOD-9).
- Analysis and drivers:
  - references to CLAUDE.md §10.x sections that no longer exist, to be repointed to KB notes (AN-11, LAY-10, KBC-28);
  - seeIV's qf-route comments (DRV-14);
  - fieldPlate.tcl's reference to a missing `plot_fieldPlate.py` (AN-9, DRV-21);
  - the genRadStudy docstring (GEN-10).
- CRLF files must be edited from Python with `newline=''`; check with `file` afterwards.

## 3. Stage 2: safety rails (small, behaviour-preserving)

- **Generators:**
  - `genRadStudy.py --check` diffs against the committed files.
  - It refuses to overwrite a tracked params file whose content would change unless `--force <name>` is given (GEN-2).
  - `--show <study> [task]` prints the effective lever set. about 420 of the ~790 generated lines repeat a lever with conflicting values; the last one wins, which hides the real settings (GEN-3).
  - Hard-code the three radMulti orders (GEN-9).
  - The same treatment for `genRad3d.py` (AN-18).
- **`sweeps/README.md`:**
  - the template families;
  - an index of params file → template / DRV → run dir(s) → job IDs → commit → KB note → branch (LAY-2, LAY-3, LAY-19);
  - the rules "never edit or regenerate a params file after its job ran" and "never reuse a study name".
- **Templates:** `radIV.slurm` and `pulsedIV_eTemp.slurm` copy all of `model/`. ETemp.tcl is missing today, so an `eTemp 1` radIV run would fail on HPG (LAY-5, DRV-23).
- **radIV dead lines:** delete the two no-op `pdbSetDouble` lines for `stressQfnDamp` / `stressQfnAbs` (`radIV.tcl:355`, `:379`). Keep their `info exists` defaults so the two old params files still parse (DRV-4). Acceptance: a short local stress before and after, with `cmp` on the outputs.
- **Analysis thresholds:** name them `DROP_MIN_FIG = 10` and `DROP_MIN_TABLE = 8`, and say in the KB which one each count uses (AN-1). The two drop finders give different counts on 3 of 66 curves.
- **Measured-data guard:** after decision 2, `guard_private_output()` refuses to write measured overlays under `figures/` or `dashboard/` (AN-2).

## 4. Stage 3: refactors, each with a regression test

| Order | What | Findings | Acceptance test |
|---|---|---|---|
| a | `analysis/common.py`: CSV readers and column constants, label index, one drop finder with both modes, collapse classifier, REF registry for the reference curves (pre-irradiation, Nov 11, onsetField3, Run F), style palettes; `radMetrics.py` becomes a re-export shim | AN-1, -3, -5, -6, -7, -14, -15, -20 | Rerun every script that used the moved helpers on the same inputs; printed tables and CSVs identical; figures checked by eye |
| b | `genRadStudy.py` → `analysis/radparams.py` (constants and builders, no side effects) + one function per study + a study registry (params file, run dirs, job IDs, driver, status); derived studies read their parents' rows in memory; rename the "FINAL*" base sets by source and date | GEN-1, -4 to -8, -11 to -13 | `git archive HEAD` copy, run, `diff -rq sweeps/`: no difference in all 55 generated files |
| c | `radIV.tcl` in stage order: header; lever block grouped by stage, with a "legacy, kept for old params files" group (DRV-9); model and deck; stress (split the 115-line if/elseif); DamageIn with small procs for the cap, field scaling, Gaussian sum and solve-or-restore; measurement | DRV-3, -5, -6, -9, -13 | Local before/after `cmp` of `_summary.txt`, `_IdVd.csv` and `_cuts.txt` for (1) a pre run, (2) a short stress + damage + Id-Vd, (3) stressLoad + damGauss + damGaussF + vdCuts. Lever defaults stay before `source GaN_modelfile_masterD`; no line may start with `window` (radIV.slurm blanks those) |
| d | **After the fix tests (decision 1 done).** Decks: a `passMat` lever folds `rfdevice_SiN.tcl` into `rfdevice.tcl` (they differ in 3 region lines); a coordinate table and named literals (`FP2` is an offset, not a length; the gate-insulator 0.005); a shared contacts block; keep `rfdevice3d.tcl` in sync | MOD-3, -4, -6, -14, -17 | Commit before the change; HighK and SiN pre Id-Vg / Id-Vd byte-identical locally; `file` check on the CRLF files |
| e | Deferred: one retry/bisection helper shared by the drivers. There are four variants today. radIV.slurm copies only the driver into the task directory, so this needs a template change | DRV-12 | Document the four variants in retry-bisection.md now |

## 5. Stage 4: moves to archive/ (README per folder; update references in the same commit)

- **drivers:**
  - `trapPlot.tcl` and `figures/radPlot*.csv` → `archive/static_mobility/` (LAY-9);
  - `eTempDebug_tail.tcl` with its slurm and params files, and the two `test20` TRIM inputs (DRV-17);
  - `stressFreeze.tcl` only after decision 5.
- **analysis:**
  - the one-off day-figure scripts (plot_gaussFine, plot_radExp1, radEBFig, radGaussFig, radFineFig, plot_nov12, plot_rad28fit, plot_rad3dFix, plot_radStepHighlights) → `archive/analysis_dayfigs/`, with a script → figure → dashboard day → job table (AN-8);
  - analyze_mobCompare and plot_eTemp to the static / etstats archive.
- **figures and notebook:** `figures.ipynb` → `archive/static_mobility/` (LAY-14), and `figures/README.md` stating the per-study folder rule and the frames policy (LAY-12, AN-17).
- **Do not rename params files**, even where the naming schemes are mixed (LAY-16). Old scripts, KB notes and progress.md cite them. The sweeps index (stage 2) does the job instead (LAY-21).
- **Local clutter:** `vdc_sin.log`, the log of a failed local run (LAY-8).

## 6. KB issues and conflicts

| Note(s) | Issue | Which is right / fix | ID |
|---|---|---|---|
| current-status | "Key results" still describes the Oct 27 model (17 V, two steps near 4.5 / 5.8 V, jobs 47887339 / 47959281). Energy-balance paragraph says eTemp 1 is standard. Several lines say runs are still going or decisions are pending when they are done. | The 28 V model in step-search-28v and rad-model, and eTemp 0 (standard since Oct 16). Rebuild as Now / Current answers / Parked, with history in progress.md. | KB-R-1, -2, -6 |
| rad-model | Several inconsistent "final" states: refit "running" but done Nov 15; 17 V vs 17.66 V; hotEb 0.5 vs 1.0; "unchanged" vs the Nov 11 change; "branch" wording | Restructure into Current model / Superseded / History | KB-R-4, DRV-24, KB-GEN-4 |
| rad-model, static-era-lessons | Measured numbers or offsets in a public note | Decision 2 | KB-R-14 |
| see-plan | Presents the quasi-Fermi route as the method, but it failed: the TR-BDF2 first step never converges. TR-BDF2 and tranSign are not documented anywhere. Decisions not marked as taken. seeMap28 missing. | Generation pulse (`seeMethod gen`, `tranSign 1`). Add a "Method as run" section and put the TR-BDF2 / tranSign facts in gotchas. | KB-R-3, -15 |
| rad-model, damage-region-map, current-status | "radFine" names two studies: Oct 24 (47562303) and Nov 5 (49735196) | Cite with the job ID; restore the Oct params (decision 6) | KB-GEN-1, KB-R-13 |
| step-search-28v | Not in date or importance order. Case labels are never defined. The Nov 18 audit's "15 nm at y 0.8" disagrees with the true-node 9.5–17.2 nm. Reproduction command misses the output argument. Rounds S and K and the 28 V refit are missing. | Current-answer box at the top; label legend table; true-node spacings; full command | KB-R-5, -7 to -10, -17 |
| damage-region-map | The opening summary contradicts the note's own later correction: Gaussian traps at hotEb 1.0 do collapse, converged at 2.5 nm | Summarise both outcomes | KB-R-11 |
| highk-vs-sin, index | "The trap model cannot make SiN collapse while HighK does not" reads as contradicting the rad result | Qualify: with hand-placed traps; the deck difference comes from the stress field | KB-R-12 |
| rad-literature-steps | The test plan does not say which tests have been run | Add an outcome column | KB-R-16 |
| energy-balance, drivers, gotchas, flooxs-solver, flooxs-commands | Muddled "standard" mode. iterLimit described as a live setting. eTempDebug dumps read as capped iterations. | eTemp 0 is standard; pdb solver parameters are read once at solver build; the dumps' readings are unverified | KBC-8, -9, DRV-11 |
| calibration, mobility-models | Only the Oct 1 HfO2 calibration. The rad baseline (polCharge 1e13, phiB 2.94, mob* levers, 2026-10-23) is missing. | Add a rad-baseline section | KBC-10 |
| device-structure, Metal.tcl | FP "0.42 µm thick" (it spans 0.27 µm). Passivation stack described wrongly. Metal comments contradict the code. | Correct from the deck coordinates | MOD-11, MOD-2 |
| mesh | Stale next to step-search-28v (spacings, meshY recipe, size rules) | Rewrite as current facts, including the print1d resampling caveat | KBC-14 |
| levers | Called "every knob" but about 31 current levers are missing; radIV defaults are not recorded | Stage 2a | KBC-2, DRV-10, KB-GEN-3 |
| flooxs-gotchas | Missing: the 3D brick-gradient bug; `struct infile` clears contacts; the high-bias Initialize overflow; others | Add bullets with links | KBC-3, -19 |
| CLAUDE.md §4, git-conventions, README | "Commit data/" vs the measured-data rule | Public-repo rule | KBC-4 |
| repo-locations, hpg-workflow | The /blue stress library is missing. The reconnect description is out of date. | Update from the scripts | KBC-6, -7 |
| trim, insulator-traps, model-caveats | Stale: the real ion still called "pending"; field-mobility retest; rad-era caveats missing | Update | DRV-16, KBC-17, -22, -23 |
| munmap-crash vs energy-balance | "Zero munmap crashes since Sep 27" vs one on Oct 12 (45692147 / 8) | energy-balance is right | KBC-20 |
| critical-strike; munmap-crash and two others | Broken figure path (the file now lives in archive/static_mobility/figures/). `flooxs-crashfix.patch` is cited but does not exist. | Fix the path; say where the patch lives or that it is lost | KB-R-18, KBC-18 |
| 3d-plan | A plan that has grown into a dated results log | Split into plan / results | KBC-27 |
| several | Small in-note staleness (a job "running" that has a result; frontmatter keys; index dates) | Polish | KB-R-19, -21, -22, KBC-24, -26 |

## 7. Suggested order

1. Decisions 1–6 (Ian).
2. Stage 1 (docs and KB): a day or two of edits, no risk. 2a first, because sweep-pattern / CLAUDE.md §2 can cause missed failures.
3. Stage 2 (rails): the `genRadStudy --check` / no-overwrite rule and the sweeps index first.
4. Stage 3 a → b → c, one per commit, each with its acceptance test logged in progress.md. Then d, after decision 1.
5. Stage 4 moves, one folder per commit.

The low-priority polish items are in the appendix (severity "low").

## Refuted

AN-16 claimed that eleven scripts crash on a fresh clone because they write to figures/ folders that don't exist. Every such folder holds tracked files, so it exists in any clone.

Related: [[current-status]], [[levers]], [[sweep-pattern]], [[analysis-scripts]], [[rad-model]], [[step-search-28v]], [[step-mechanism]], [[flooxs-gotchas]].

## Appendix: all verified findings

Severity: H high, M medium, L low. Effort: S/M/L. Verdict: ✓ confirmed, ~ confirmed with corrections (the corrected wording is in the survey output). The full text of every finding and verdict is in the workflow journal (wf_fb7accb6-e0e).


### Drivers (25)

| ID | Sev | Eff | ✓ | Finding | Files |
|---|---|---|---|---|---|
| DRV-1 | H | S | ✓ | The orientation docs omit the drivers the current work runs on. | `kb/tools/drivers.md:9, README.md:12 (+4)` |
| DRV-11 | H | S | ~ | Correct drivers.md:13, energy-balance.md:19 and energy-balance.md:21. | `drivers/eTempDebug_tail.tcl:1, drivers/eTempDebug_tail.tcl:39 (+3)` |
| DRV-2 | H | S | ✓ | Two radIV lever comments describe roles the levers no longer have in the final model. | `drivers/radIV.tcl:71, drivers/radIV.tcl:86 (+1)` |
| DRV-10 | M | M | ✓ | levers.md documents only a few radIV levers and none of seeIV's, and it never records that radIV uses its own trap and solver defaults. | `kb/model/levers.md:44, kb/model/levers.md:28 (+3)` |
| DRV-12 | M | M | ✓ | There are four separate retry-bisection implementations with small semantic differences, and retry-bisection.md describes only pulsedIV's. | `drivers/pulsedIV.tcl:104, drivers/radIV.tcl:242 (+4)` |
| DRV-14 | M | S | ~ | For the tolerance comment (seeIV.tcl:90-93): do not reword it to 'also needed when trapEn 0'. | `drivers/seeIV.tcl:1, drivers/seeIV.tcl:40 (+4)` |
| DRV-15 | M | S | ~ | Archive trapPlot.tcl to archive/static_mobility/ and list it in that folder's README. | `drivers/stressFreeze.tcl:15, drivers/stressFreeze.tcl:23 (+4)` |
| DRV-16 | M | S | ✓ | trim.md is stale on three points. It describes only the 10 MeV / 20-ion template and calls the real ion 'pending (2026-10-21)', although the production model-deck inputs (Au 2256 MeV, 200 ions, full cascades) ran on Nov 12. | `kb/tools/trim.md, drivers/trim/TRIM_HighK_Au2256.IN (+2)` |
| DRV-3 | M | S | ~ | Risk: behaviour-preserving only if every lever default stays ahead of `source GaN_modelfile_masterD` (radIV.tcl:195). | `drivers/radIV.tcl:89, drivers/radIV.tcl:100 (+4)` |
| DRV-4 | M | S | ✓ | stressQfnDamp and stressQfnAbs do nothing: they set pdb values mid-run, and FLOOXS reads those only when it builds the solver. | `drivers/radIV.tcl:52, drivers/radIV.tcl:59 (+3)` |
| DRV-5 | M | L | ✓ | radIV.tcl's layout follows the order in which features were added, not the order it runs in. | `drivers/radIV.tcl:27, drivers/radIV.tcl:149 (+2)` |
| DRV-6 | M | M | ✓ | DamageIn and the stress-file code repeat themselves. | `drivers/radIV.tcl:438, drivers/radIV.tcl:441 (+7)` |
| DRV-7 | M | S | ✓ | Two guards have fallen behind the newer damage levers. | `drivers/radIV.tcl:188, drivers/radIV.tcl:317` |
| DRV-8 | M | S | ✓ | radIV's header describes the Oct 23-25 driver. | `drivers/radIV.tcl:1, drivers/radIV.tcl:2 (+2)` |
| DRV-9 | M | S | ~ | Evidence corrections for the legacy-group annotations: damIns* is used by radIns, radFam, radRon, radVth and radVth2 (Oct 24 - Nov 4). | `drivers/radIV.tcl:51, drivers/radIV.tcl:56 (+7)` |
| DRV-13 | L | S | ~ | Within radIV.tcl, the 2D DamageIn cut (543) is the only print1d without a catch. | `drivers/radIV.tcl:392, drivers/radIV.tcl:535 (+6)` |
| DRV-17 | L | S | ✓ | The two test20 TRIM inputs are smoke-test copies of the production inputs, differ only in the ion count, and are referenced nowhere. | `drivers/trim/TRIM_HighK_Au2256_test20.IN, drivers/trim/TRIM_SiN_Au2256_test20.IN (+1)` |
| DRV-18 | L | S | ✓ | drivers/trim/ contains an untracked CRLF TRIM input, next to the tracked ones, that describes the measured device's layer stack. | `drivers/trim/TRIM_NCY2_SiN_Au2256.IN, vdc_sin.log` |
| DRV-19 | L | S | ✓ | render3d_build.tcl hard-codes `set modelDir model` and `source model/...` instead of the shared modelDir lookup, sets the 3D deck levers without `info exists`, and writes a 45 MB sin3d.vtk into the current directory, normally the  | `drivers/render3d_build.tcl:3, drivers/render3d_build.tcl:15 (+3)` |
| DRV-20 | L | S | ✓ | The drivers use different lever names for the same concept, and different defaults for shared levers. | `drivers/pulsedIV.tcl:35, drivers/radIV.tcl:39 (+4)` |
| DRV-21 | L | S | ~ | Header: 'The field-mobility run (job 46241088) was collected into figures/fieldPlateFM_sweep.csv and figures/fieldPlateFM_cuts.csv (the conversion is not in a tracked script). | `drivers/fieldPlate.tcl:8, kb/results/highk-vs-sin.md:12` |
| DRV-22 | L | S | ✓ | levers.md gives the alternative deviceDeck value as `model/rfdevice_SiN.tcl`. | `kb/model/levers.md:39, kb/model/levers.md:55 (+1)` |
| DRV-23 | L | S | ✓ | radIV and seeIV expose an eTemp lever, but radIV.slurm doesn't copy ETemp.tcl into the task directory, and the model file sources ETemp.tcl when eTemp is 1. | `drivers/radIV.tcl:31, sweeps/radIV.slurm:38 (+1)` |
| DRV-24 | L | S | ✓ | rad-model.md and see-plan.md still call radIV, seeIV and the mob* levers branch-only, although they were merged to main on 2026-11-04. | `kb/results/rad-model.md:7, kb/results/rad-model.md:20 (+2)` |
| DRV-25 | L | S | ✓ | Small polish items in pulsedIV and calibIdVg. | `drivers/pulsedIV.tcl:72, drivers/pulsedIV.tcl:157 (+3)` |

### Model (21)

| ID | Sev | Eff | ✓ | Finding | Files |
|---|---|---|---|---|---|
| MOD-1 | H | S | ✓ | The FP contact box does not match the FP metal region and reaches into the T-gate head. | `model/rfdevice.tcl:88, model/rfdevice_SiN.tcl:91 (+4)` |
| MOD-2 | H | S | ✓ | Comments in Metal.tcl contradict the code. | `model/Metal.tcl:1-3, model/Metal.tcl:50-53 (+3)` |
| MOD-10 | M | S | ~ | Add a 'Model numerics and SEE hooks' table to levers.md with tranSign (default 0 in Continuity.tcl, 1 in seeIV.tcl), srhTau, carFloor, occSafe, pGaN, mobMumax, mobNref and mobVsat. | `kb/model/levers.md:9-26, model/Metal.tcl:46 (+5)` |
| MOD-11 | M | S | ✓ | device-structure.md misdescribes the deck in two places. | `kb/device/device-structure.md:14, kb/device/device-structure.md:19 (+2)` |
| MOD-3 | M | S | ✓ | rfdevice_SiN.tcl is a 125-line copy of rfdevice.tcl. | `model/rfdevice_SiN.tcl, model/rfdevice.tcl:66-71 (+1)` |
| MOD-4 | M | M | ~ | Low-cost option, as proposed: add 'keep in sync with rfdevice.tcl' comments in both decks, and change rfdevice3d.tcl:11 to 'bot3d buffer depth (um); | `model/rfdevice3d.tcl:36-124, model/rfdevice.tcl:13-119 (+1)` |
| MOD-5 | M | S | ✓ | A stale structure comment says the AlGaN is 25 nm thick, six lines below `set Al_Thick 0.015 ;# 15nm AlGaN thickness`. | `model/rfdevice.tcl:31, model/rfdevice_SiN.tcl:34 (+1)` |
| MOD-6 | M | S | ✓ | The geometry variables do not mean what their names say, and several mesh coordinates are unnamed numbers. | `model/rfdevice.tcl:13-24, model/rfdevice.tcl:40-59 (+3)` |
| MOD-7 | M | S | ✓ | GaN.tcl sets the full Farahmand high-field parameter set (hfalpha, n1, n2, Ecmob) and a GaN vsat, but the GaN field model uses Heller saturation with vs = mobVsat or 3.3e7-3e6*T/300. | `model/GaN.tcl:36-41, model/GaN.tcl:43-44 (+1)` |
| MOD-8 | M | S | ✓ | There are stale cross-references and claims. | `model/GaN_modelfile_masterD:19, model/GaN_modelfile_masterD:82 (+3)` |
| MOD-9 | M | S | ~ | For legibility, add a comment at ETemp.tcl:17: 'local k/q = 8.625e-5 eV/K, differs by 0.09% from masterD kev = 8.617e-5; | `model/ETemp.tcl:17, model/ETemp.tcl:53 (+3)` |
| MOD-12 | L | S | ✓ | Insulator.tcl has dead and unclear parts. | `model/Insulator.tcl:1-5, model/Insulator.tcl:21 (+3)` |
| MOD-13 | L | S | ✓ | InitMetal ('#now Metal' in Initialize) only writes a data field, MetalDevPsi, seeded from the AlGaN affinity + phiB. | `model/Metal.tcl:46-47, model/Metal.tcl:72-75 (+2)` |
| MOD-14 | L | S | ✓ | The doping block's names and numbers are unclear. | `model/rfdevice.tcl:103-117, model/rfdevice3d.tcl:117-123 (+1)` |
| MOD-15 | L | S | ✓ | Poisson.tcl is mostly not about Poisson. Lines 1-20 are Poisson/InsPoisson; | `model/Poisson.tcl:22-158, README.md:11` |
| MOD-16 | L | S | ✓ | The Farahmand low-field mobility (Tn, N with IonAcceptor, seg1/seg2/Nr/a, lowfldmob) is the same block in GaN.tcl and AlGaN.tcl apart from the material name. | `model/GaN.tcl:48-58, model/AlGaN.tcl:51-60` |
| MOD-17 | L | S | ✓ | The five contact bias/current lines (G current=(Hole_Nitride-Elec_Nitride), B/D/S current=(Hole_GaN-Elec_GaN), FP) exist in four copies: three decks plus the stressLoad re-issue in radIV.tcl. | `model/rfdevice.tcl:97-101, model/rfdevice_SiN.tcl:100-104 (+2)` |
| MOD-18 | L | S | ✓ | Small clarity gaps in the shared code. The physical constants have no units (k J/K, q C, eps0 F/cm, kev V/K), and two are unused: hbar, and egan = 7.88e-13 = 8.9*eps0 F/cm. | `model/GaN_modelfile_masterD:9-16, model/Continuity.tcl:24 (+3)` |
| MOD-19 | L | S | ~ | Make one whitespace-only commit. Dedent the file-level blocks in GaN.tcl (lines 3-75) and in Insulator.tcl (Oxide :35-46, HighK :49-57) to column 0, replace the tabs in GaN.tcl:3-5, and strip trailing whitespace outside quoted str | `model/GaN.tcl:3-75, model/rfdevice.tcl (+4)` |
| MOD-20 | L | S | ✓ | The line-ending state is currently correct and consistent: the three required files are 100% CRLF in both the index and the worktree (masterD 213/213, Metal 81/81, Continuity 94/94; | `model/GaN_modelfile_masterD, model/Metal.tcl (+2)` |
| MOD-21 | L | S | ~ | Add rfdevice3d.tcl (3D slice, [[3d-plan]]) to README.md:11. | `README.md:11, model/rfdevice.tcl:1-11 (+1)` |

### genRadStudy.py (17)

| ID | Sev | Eff | ✓ | Finding | Files |
|---|---|---|---|---|---|
| GEN-2 | H | S | ✓ | Nothing stops the generator from replacing a committed params file that is already the record of a job, and this has already happened. | `analysis/genRadStudy.py:144, analysis/genRadStudy.py:177 (+1)` |
| GEN-3 | H | M | ✓ | Lines are built as 'old base + overrides', and radIV.slurm turns each lever into a `set k v` line in order, so the last value wins. | `analysis/genRadStudy.py:237, analysis/genRadStudy.py:314 (+4)` |
| KB-GEN-1 | H | S | ~ | Severity medium. The KB uses 'radFine' for two studies: Oct 24 (job 47562303, 8 tasks, m4 damPeak 4-7.5e18, surfCharge -1.2e12; | `kb/results/rad-model.md:41, kb/results/rad-model.md:76 (+3)` |
| GEN-1 | M | L | ~ | Same description and proposal, but the generator writes 55 committed params files (788 lines), not 57; | `analysis/genRadStudy.py` |
| GEN-10 | M | S | ✓ | The module docstring is out of date. It describes 'the 2026-11 damage-region and Vth studies', but the script also writes the stress library (stressLib, stressLibResume, meshChkStress, meshChkStress2p5), the SEE maps and rounds A- | `analysis/genRadStudy.py:1, analysis/genRadStudy.py:723 (+2)` |
| GEN-11 | M | M | ~ | Keep a study registry (name -> params file, RUN dir(s), job IDs with task ranges, driver radIV/seeIV, mem/time, status done/cancelled/superseded/composite, purpose) in a module with no side effects on import. | `sweeps/params_radExp1b.txt, sweeps/params_radStepDiag5.txt (+3)` |
| GEN-4 | M | S | ✓ | Several base sets are named as if they were 'the final' model, but each belongs to a different date. | `analysis/genRadStudy.py:172, analysis/genRadStudy.py:237 (+6)` |
| GEN-5 | M | S | ✓ | Shared lever strings are copied as literals instead of being defined once. | `analysis/genRadStudy.py:7, analysis/genRadStudy.py:33 (+6)` |
| GEN-6 | M | M | ~ | As described, except: g2() generalises gcase() only when a mesh is given. | `analysis/genRadStudy.py:19, analysis/genRadStudy.py:70 (+11)` |
| GEN-7 | M | M | ✓ | Derived studies get their data by re-reading files the script wrote earlier in the same run (8 reads). | `analysis/genRadStudy.py:300, analysis/genRadStudy.py:369 (+6)` |
| GEN-9 | M | S | ✓ | The radMulti random strike sets come from `random.Random(seed).sample(POOL, 5)`. | `analysis/genRadStudy.py:196, sweeps/params_radMulti.txt` |
| KB-GEN-2 | M | S | ~ | As described, with the evidence fixed to radIV.slurm:34 (`LINE=$(sed -n ... | `kb/tools/analysis-scripts.md, kb/workflow/sweep-pattern.md:9 (+3)` |
| KB-GEN-3 | M | M | ~ | kb/model/levers.md has no entry for 31 of the 86 lever names the generated params use, including the core radIV levers (radState, damPeak, damM, damYmin/damYmax, damXmax, dam2*, dam3Peak, occSafe, doIdVg, Vg_out, stressStep, mobMu | `kb/model/levers.md:45` |
| GEN-12 | L | S | ✓ | Label conventions are mixed. The deck tag is 'hk' in write()/writex() but 'highk' in the nb_ labels of radChk, radEB1 and radExp3. | `analysis/genRadStudy.py:37, analysis/genRadStudy.py:287 (+4)` |
| GEN-13 | L | S | ✓ | Small dead or confusing code. The M05 lambda is never used. | `analysis/genRadStudy.py:148, analysis/genRadStudy.py:436 (+2)` |
| GEN-8 | L | S | ✓ | The assertions are weak and the counts are maintained by hand. | `analysis/genRadStudy.py:783, analysis/genRadStudy.py:701 (+2)` |
| KB-GEN-4 | L | S | ✓ | rad-model.md still describes the radIV work as living on a branch. | `kb/results/rad-model.md:5, kb/results/rad-model.md:7 (+2)` |

### Analysis scripts (21)

| ID | Sev | Eff | ✓ | Finding | Files |
|---|---|---|---|---|---|
| AN-1 | H | M | ✓ | Five scripts define a function named drops(), with two incompatible definitions. | `analysis/plot_radStep.py:26, analysis/plot_meshSeries.py:50 (+8)` |
| AN-2 | H | S | ✓ | radCompare loads the measured targets file from the default path whenever that file exists on the workstation. | `analysis/radCompare.py:29, analysis/radCompare.py:70 (+6)` |
| AN-10 | M | S | ~ | radFineFig.py:27 reads its 'standard mesh' curve from the undocumented FINAL_REF environment variable. | `analysis/radFineFig.py:2, analysis/radFineFig.py:27` |
| AN-11 | M | S | ✓ | Several docstrings point to things that no longer exist or no longer match the code. | `analysis/analyze_onset.py:3, analysis/analyze_onset.py:9 (+7)` |
| AN-20 | M | L | ✓ | Shared code currently lives in random leaf scripts. | `analysis/radMetrics.py, analysis/plot_radStep.py (+2)` |
| AN-3 | M | M | ✓ | The 2026-10-01 collapse-classification rule is re-implemented at least seven times, and the copies have drifted. | `analysis/analyze_onset.py:35, analysis/analyze_onset.py:75 (+10)` |
| AN-4 | M | S | ✓ | Three committed metrics CSVs have a column named onset_Vd, and it means three different things. | `analysis/analyze_trapMapSets.py:80, analysis/analyze_mobCompare.py:68 (+4)` |
| AN-5 | M | M | ✓ | The tolerant CSV reader idiom `np.array([[float(v) for v in l.split(',') if v.strip()] for l in open(f) if l.strip()])` is copied into 23 scripts (24 sites; | `analysis/plot_meshSeries.py:45, analysis/plot_radStepSeries.py:65 (+8)` |
| AN-6 | M | S | ~ | Seven scripts build a label -> data map from task_*/params.json: plot_meshSeries, plot_meshChkSteps, plot_radStepFS, plot_radStepH, plot_radStep, plot_radFinal and plot_deckVg1 (plus radFineFig and radMap). | `analysis/plot_meshSeries.py:30, analysis/plot_meshChkSteps.py:16 (+6)` |
| AN-7 | M | M | ✓ | The same reference curves are hard-coded again and again as results/<date>_<run> paths, some with task numbers. | `analysis/plot_lateIdVd.py:8, analysis/plot_curveTracer.py:20 (+6)` |
| AN-8 | M | M | ~ | Move the hard-coded, single-figure scripts (plot_gaussFine, plot_radExp1, radEBFig, radGaussFig, radFineFig, plot_nov12, plot_rad28fit, plot_rad3dFix, plot_radStepHighlights) to archive/analysis_dayfigs/ with the README table. | `analysis/plot_meshChkSteps.py, analysis/analyze_mobCompare.py (+12)` |
| AN-9 | M | S | ✓ | plot_strikeSlides reads figures/fieldPlateFM_cuts.csv, which comes from the field-mobility rerun (job 46241088). | `analysis/plot_strikeSlides.py:176, drivers/fieldPlate.tcl:8 (+1)` |
| AN-KB-1 | M | M | ✓ | kb/tools/analysis-scripts.md documents 13 of the 57 analysis scripts plus webfig. | `kb/tools/analysis-scripts.md:7, README.md:15` |
| AN-12 | L | M | ✓ | There is no common command-line convention. | `analysis/plot_radStep.py:4, analysis/radPlacementFig.py:2 (+5)` |
| AN-13 | L | S | ✓ | testRegister feeds the 'Stepped-Collapse Test Register' dashboard. | `analysis/testRegister.py:20, analysis/testRegister.py:52 (+1)` |
| AN-14 | L | S | ✓ | Style constants are copied rather than shared. | `analysis/analyze_onset.py:28, analysis/plot_posVd.py:27 (+7)` |
| AN-15 | L | S | ✓ | Nine scripts add to sys.path by hand: seven with the cwd-relative "analysis", two with os.path.dirname(__file__). | `analysis/plot_eTempStd.py:17, analysis/plot_meshDeliverable.py:11 (+7)` |
| AN-17 | L | S | ~ | .gitignore protects only *_onset3d_frames/. | `.gitignore:11, analysis/plot_posVd.py:132 (+1)` |
| AN-18 | L | S | ✓ | genRad3d.py rewrites all four of its sweeps/params_*.txt files (rad3dBuild, rad3dSolve, rad3dTrack1, rad3dRod) every time it runs. | `analysis/genRad3d.py:10, analysis/genRad3d.py:44 (+1)` |
| AN-19 | L | S | ✓ | These are generic tools that take a run directory, yet their titles hard-code run-specific facts ('σ 40 nm', 'Vg = −2 V', 'field mobility'). | `analysis/plot_posVd.py:120, analysis/plot_posOnset.py:133 (+1)` |
| AN-KB-2 | L | S | ✓ | Several rows in the existing note are wrong. | `kb/tools/analysis-scripts.md:18, kb/tools/analysis-scripts.md:24 (+3)` |

### Sweeps, bin, layout (21)

| ID | Sev | Eff | ✓ | Finding | Files |
|---|---|---|---|---|---|
| LAY-1 | H | S | ✓ | README.md has not changed since 2026-10-13 (git log 503f5ab), so it predates the whole rad era. | `README.md:11, README.md:12 (+5)` |
| LAY-2 | H | M | ✓ | The params files are treated as the record of what each HPG job ran, but nothing maps a params file to its run directories, job IDs or git commit. | `sweeps/params_radFine.txt, sweeps/params_radExp1b.txt (+5)` |
| LAY-10 | M | S | ~ | Repoint as follows: 10.0 -> kb/results/collapse-classification.md; | `sweeps/pulsedIV_onsetField3Ramp.slurm:4, sweeps/pulsedIV_onsetField3Retry.slurm:3 (+11)` |
| LAY-11 | M | S | ✓ | The CLAUDE.md §7 KB map, which every session reads, leaves out 12 of the 54 tracked KB notes. | `CLAUDE.md:93, CLAUDE.md:98` |
| LAY-21 | M | M | ~ | Same target layout and order with these fixes. | `sweeps/, figures/ (+3)` |
| LAY-3 | M | S | ✓ | About 45 of the rad-era params files are generated, not hand-written. | `analysis/genRadStudy.py:1, analysis/genRadStudy.py:19 (+1)` |
| LAY-4 | M | S | ✓ | The sweep-pattern note describes October practice. | `kb/workflow/sweep-pattern.md:8, kb/workflow/sweep-pattern.md:9 (+2)` |
| LAY-5 | M | S | ✓ | The model files copied into task directories differ from template to template. | `sweeps/radIV.slurm:38, sweeps/pulsedIV_eTemp.slurm:38 (+2)` |
| LAY-6 | M | S | ✓ | The untracked bin/hpg_sbatch.sh (2026-10-21, not executable, referenced nowhere) is obsolete for the current workflow. | `bin/hpg_sbatch.sh` |
| LAY-7 | M | S | ✓ | drivers/trim/TRIM_NCY2_SiN_Au2256.IN is untracked (2026-10-21) next to five tracked TRIM inputs. | `drivers/trim/TRIM_NCY2_SiN_Au2256.IN, .gitignore:13` |
| LAY-9 | M | S | ~ | Move drivers/trapPlot.tcl to archive/static_mobility/ and figures/radPlot{,1,2}.csv to archive/static_mobility/figures/. | `drivers/trapPlot.tcl:60, figures/radPlot.csv (+3)` |
| LAY-12 | L | M | ~ | Add figures/README.md: the root holds frozen October field-era outputs; | `figures/, figures/posMapLate_frames (+4)` |
| LAY-13 | L | S | ✓ | The README and repo-locations describe data/ as 'measured inputs', but data/ also holds model outputs: data/rad3d_fangs/ (its own README says 'Model output only') and TRIM-derived tracks in data/trim/*.json. | `README.md:16, kb/workflow/repo-locations.md:14 (+3)` |
| LAY-14 | L | S | ~ | Move figures.ipynb to archive/static_mobility/figures.ipynb and update its 5 referencing files (README.md, kb/index.md, kb/tools/notebook.md, kb/workflow/repo-locations.md, archive/static_mobility/README.md). | `figures.ipynb` |
| LAY-15 | L | S | ✓ | Three dashboard pages are tracked, but kb/workflow/dashboard.md documents only two. | `kb/workflow/dashboard.md:9, dashboard/rad-week.html (+2)` |
| LAY-16 | L | S | ✓ | Params names use several schemes at once. | `sweeps/params_onsetField3Ramp.txt, sweeps/params_onsetField3Retry.txt (+4)` |
| LAY-17 | L | S | ~ | Optional, low value. Add .gitattributes with `model/GaN_modelfile_masterD -text`, `model/Metal.tcl -text` and `model/Continuity.tcl -text` to document the intent and block renormalisation (behaviour-preserving; | `model/GaN_modelfile_masterD, model/Metal.tcl (+1)` |
| LAY-18 | L | S | ✓ | All three archive subfolders have a README, which is good. | `README.md:20, archive/fangs-hpg-tests/README.md (+1)` |
| LAY-19 | L | S | ~ | Add a branch column to the sweeps index for the 11 branch-only params files (fieldCap on both branches; | `sweeps/` |
| LAY-20 | L | S | ✓ | progress.md is 277 KB, 2,257 lines and 129 '##' headings in one chronological file: about 43 KB for September, 140 KB for October and 92 KB for November. | `progress.md` |
| LAY-8 | L | S | ✓ | Local clutter. vdc_sin.log at the repo root is the log of a failed FLOOXS run (Nov 19; | `vdc_sin.log, .gitignore (+2)` |

### KB results notes (22)

| ID | Sev | Eff | ✓ | Finding | Files |
|---|---|---|---|---|---|
| KB-R-1 | H | S | ✓ | The current-status 'Key results' bullet for the pre/post-irradiation model still describes the Oct 27 model as current. | `kb/current-status.md:24, kb/results/rad-model.md:9 (+4)` |
| KB-R-14 | H | S | ~ | Tracked notes in the public repo may contain measured-device numbers (locations only): rad-model.md:61 (the Measured column), :266 (second clause, a measured onset voltage) and :129 (a model-vs-measured offset that reveals the mea | `kb/results/rad-model.md:61, kb/results/rad-model.md:266 (+4)` |
| KB-R-2 | H | S | ~ | current-status.md:36 gives the 2026-10-13 decision ('standard = eTemp 1 ...') without the 2026-10-16 reversal to eTemp 0, which line 10 and GaN_modelfile_masterD:38 record. | `kb/current-status.md:36, kb/current-status.md:10 (+2)` |
| KB-R-3 | H | S | ✓ | see-plan presents quasi-Fermi injection as the strike method, and index.md repeats it. | `kb/results/see-plan.md:8, kb/results/see-plan.md:16 (+2)` |
| KB-R-4 | H | M | ~ | rad-model.md has stale or contradictory 'current' statements: :9 (refit 'being' done; | `kb/results/rad-model.md:2, kb/results/rad-model.md:9 (+7)` |
| KB-R-6 | H | M | ✓ | Apart from KB-R-1 and KB-R-2, current-status.md has many dated paragraphs that are stale or contradict each other: - Line 14 calls the 2.5 nm check 'a decision for Ian', but it was submitted (52044407) and Ian said to keep it runn | `kb/current-status.md:14, kb/current-status.md:16 (+7)` |
| KB-R-10 | M | M | ✓ | The strike-step notes rely on case labels that are never defined in one place: - In C_p1.5_N0, A_p1.5e+18_n6e+18_N1, B_n6e18_N2, A_N3, E_lev0.4_N2, C_n8e18_N2, lev30_n8 and lev40_n7, the leading letter is the HPG round, not the se | `kb/results/step-mechanism.md:45, kb/results/step-mechanism.md:14 (+3)` |
| KB-R-11 | M | M | ✓ | The opening summary of damage-region-map says the radMap1 steps were mesh artifacts and that a dense site acts as a current limit. | `kb/results/damage-region-map.md:8, kb/results/damage-region-map.md:79 (+8)` |
| KB-R-12 | M | S | ✓ | highk-vs-sin states without qualification that 'the trap model cannot make SiN collapse while HighK does not', and index.md summarises the note as 'passivation dielectric does not matter at ≤3 V'. | `kb/results/highk-vs-sin.md:21, kb/index.md:67 (+3)` |
| KB-R-13 | M | S | ✓ | The run name 'radFine' refers to two different jobs: 47562303 (Oct 24, the m4 damage scale, rad-model:41/76) and 49735196 (Nov 5, the fine-mesh current limit; | `kb/results/rad-model.md:76, kb/results/rad-model.md:235 (+4)` |
| KB-R-15 | M | S | ✓ | Beyond KB-R-3, see-plan is stale in several places: - It is still titled and tagged as a plan, though most of it is results. | `kb/results/see-plan.md:2, kb/results/see-plan.md:37 (+3)` |
| KB-R-16 | M | S | ✓ | The 'What our model could test' and 'Runs that distinguish them' sections (written Nov 17) read as an open plan, but most of the tests have since been run and none is marked: - knock-out (radStepD: other steps moved only slightly); | `kb/results/rad-literature-steps.md:165, kb/results/rad-literature-steps.md:191 (+2)` |
| KB-R-20 | M | S | ✓ | The KB map in CLAUDE.md §7, which agents read first, leaves out the notes most used now: rad-model, step-search-28v, step-mechanism, damage-region-map, ron-increase, see-plan, rad-literature, rad-literature-steps, trap-sensitivity | `CLAUDE.md:7` |
| KB-R-5 | M | M | ~ | Results missing from the owning notes: rad28fitB 51196550/51249769 (SiN 2e18-4e18 at 28 V), round S rad28strikeL 51763582 (every SiN strike count collapses, HighK never does), round K radStepK 51939558 (hybrid fails, HighK thresho | `kb/results/rad-model.md, kb/results/step-search-28v.md:2 (+4)` |
| KB-R-7 | M | S | ✓ | Mesh facts in step-search-28v come from the Nov 18 audit and estimates that later results superseded: - The library spacing at the y 0.8 strike is given as '15 nm' (lines 55, 71). | `kb/results/step-search-28v.md:49, kb/results/step-search-28v.md:55 (+5)` |
| KB-R-8 | M | M | ✓ | step-search-28v is ordered neither by date nor by importance. | `kb/results/step-search-28v.md:2, kb/results/step-search-28v.md:4 (+3)` |
| KB-R-9 | M | S | ✓ | The reproduction command for the headline figure leaves out the script's required first argument, the output path. | `kb/results/step-search-28v.md:53, analysis/plot_meshDeliverable.py:4 (+1)` |
| KB-R-17 | L | S | ~ | step-search-28v.md:16 gives an interpretation ('Strikes interact') with no job ID. | `kb/results/step-search-28v.md:16, progress.md:2136` |
| KB-R-18 | L | S | ~ | critical-strike.md:8 points to a nonexistent `figures/criticalStrike*`; | `kb/results/critical-strike.md:8, kb/results/critical-strike.md:17` |
| KB-R-19 | L | S | ✓ | index.md has small problems: - Its frontmatter says 'updated: 2026-10-12'. | `kb/index.md:4, kb/index.md:51 (+3)` |
| KB-R-21 | L | S | ✓ | Smaller in-note staleness in the older notes: - vg-dependence:21 says job 46057777 is 'running', but :49 reports its result. | `kb/results/vg-dependence.md:21, kb/results/flooxs-pyplot-regression.md:28 (+3)` |
| KB-R-22 | L | S | ~ | Three notes use frontmatter keys outside CLAUDE.md §9's 'title, tags, optional date/source': index.md and current-status.md ('updated:') and static-era-lessons.md ('period:'). | `kb/index.md:4, kb/current-status.md:4 (+2)` |

### KB other notes, CLAUDE.md, README (28)

| ID | Sev | Eff | ✓ | Finding | Files |
|---|---|---|---|---|---|
| KBC-1 | H | S | ~ | Proposal: add a per-driver check table to sweep-pattern step 7. | `CLAUDE.md:48, kb/workflow/sweep-pattern.md:13 (+7)` |
| KBC-2 | H | M | ✓ | index.md advertises levers.md as 'every model/driver knob and its default', but the note is incomplete and partly misleading for the drivers in use now. | `kb/model/levers.md:8, kb/model/levers.md:43 (+10)` |
| KBC-3 | H | S | ✓ | Stock FLOOXS computes gradients wrongly on 3D brick meshes: the x and z components are scaled by (hx/hz)^±1, and only y is exact. | `kb/model/3d-plan.md:116, kb/flooxs/flooxs-builds.md:12 (+6)` |
| KBC-4 | H | S | ✓ | CLAUDE.md §4 and git-conventions tell agents to commit `data/`, and README calls data/ 'measured inputs'. | `CLAUDE.md:63, kb/workflow/git-conventions.md:8 (+3)` |
| KBC-5 | H | M | ✓ | CLAUDE.md §2 says to follow 'the standard sweep pattern' exactly, but the note describes only the pulsedIV templates. | `kb/workflow/sweep-pattern.md:9, kb/workflow/sweep-pattern.md:10 (+6)` |
| KBC-10 | M | S | ✓ | The device notes describe one calibration: the Oct 1 HfO2 transfer curve at Vds 10 V, 'no parameters changed', polCharge 7e12, phiB 1.65, GaN mumax 1907. | `kb/device/calibration.md:12, kb/device/calibration.md:27 (+5)` |
| KBC-11 | M | S | ✓ | drivers.md still calls pulsedIV 'the main tool'. | `kb/tools/drivers.md:9, kb/tools/drivers.md:14 (+6)` |
| KBC-12 | M | M | ~ | analysis-scripts.md lists 13 of the 58 tracked analysis scripts (plus dashboard/webfig.py), none from the rad era. | `kb/tools/analysis-scripts.md:7, kb/tools/analysis-scripts.md:25 (+4)` |
| KBC-13 | M | M | ✓ | The physics and machinery behind every current result have no atomic notes. | `kb/model/trap-model.md:8, kb/model/levers.md:58 (+6)` |
| KBC-14 | M | S | ~ | mesh.md is stale next to step-search-28v. | `kb/device/mesh.md:8, kb/device/mesh.md:16 (+5)` |
| KBC-15 | M | S | ✓ | CLAUDE.md §7's KB map omits 12 tracked notes, which is every rad-era note: model/3d-plan.md, tools/trim.md, and results/ damage-region-map, rad-literature, rad-literature-steps, rad-model, ron-increase, see-plan, step-mechanism, s | `CLAUDE.md:93, CLAUDE.md:97 (+4)` |
| KBC-16 | M | S | ✓ | project-goal.md is the first 'Start here' note. | `kb/project-goal.md:13, CLAUDE.md:5 (+2)` |
| KBC-17 | M | S | ✓ | trim.md still calls the ion line a placeholder, with the real ion 'pending (2026-10-21)', and its 'Use in the model' section proposes a TRIM TrapConc proc after a mesh refinement. | `kb/tools/trim.md:33, kb/tools/trim.md:39 (+4)` |
| KBC-19 | M | M | ✓ | Several FLOOXS behaviours that cost jobs are recorded only in code comments or results notes, not in flooxs-gotchas: `struct infile` clears the contact setup, so the contact lines must be re-issued; | `kb/numerics/flooxs-gotchas.md:23, kb/flooxs/flooxs-expressions.md:13 (+5)` |
| KBC-21 | M | S | ✓ | The glossary stops at the field era. It has no entries for terms used across many notes: FANGS / flooxs-pyplot / HEMTRAD-FANGS (5 notes), HPD (4), strike (15), pocket (4), stress library, library mesh, m10/m5fix/m2p5, pre/nb/biase | `kb/glossary.md, sweeps/params_radEB1.txt (+3)` |
| KBC-6 | M | S | ✓ | repo-locations states that HEMTRAD, its worktrees and its results live on the home path while only FANGS is on /blue, and that 'writing /blue/ee1/... | `kb/workflow/repo-locations.md:24, kb/workflow/hpg-workflow.md:22 (+4)` |
| KBC-7 | M | S | ✓ | hpg-workflow describes an older bin/hpg_reconnect.sh: `ssh -fN hpg` in a detached tmux window, or in its own session `hpg-auth` when no tmux server is running. | `kb/workflow/hpg-workflow.md:13, bin/hpg_reconnect.sh:5 (+2)` |
| KBC-8 | M | S | ✓ | Which energy-balance mode is 'standard' is muddled. | `kb/model/energy-balance.md:9, kb/model/energy-balance.md:25 (+4)` |
| KBC-9 | M | S | ✓ | Several notes treat Math iterLimit and the per-solution convergence parameters as live settings. | `kb/numerics/flooxs-gotchas.md:18, kb/numerics/flooxs-gotchas.md:25 (+9)` |
| KBC-18 | L | S | ✓ | Three notes cite `flooxs-crashfix.patch` (munmap-crash adds '(untracked, repo root)'), but no such file exists in the repo root or anywhere under /home/staffian. | `kb/numerics/munmap-crash.md:18, kb/flooxs/flooxs-builds.md:11 (+2)` |
| KBC-20 | L | S | ✓ | munmap-crash.md says there have been zero munmap crashes in HPG sweeps since the retry driver of Sep 27. | `kb/numerics/munmap-crash.md:20, kb/model/energy-balance.md:21` |
| KBC-22 | L | S | ✓ | insulator-traps.md says the insulator charge was 'Only tested with static mobility; | `kb/model/insulator-traps.md:10, kb/model/insulator-traps.md:16 (+2)` |
| KBC-23 | L | S | ✓ | model-caveats lists only static- and field-era caveats. | `kb/model/model-caveats.md:9, kb/model/model-caveats.md:12 (+2)` |
| KBC-24 | L | S | ✓ | git-conventions.md:7-12 and local-runs.md:8-12 restate CLAUDE.md §3 and §4 nearly word for word, and the copies have already drifted together. | `kb/workflow/git-conventions.md:7, kb/workflow/local-runs.md:8 (+3)` |
| KBC-25 | L | S | ✓ | dashboard.md presents the rad-model explainer as belonging to 'branch explore/rad-model', but that branch is merged into main. | `kb/workflow/dashboard.md:9, kb/workflow/dashboard.md:14 (+2)` |
| KBC-26 | L | S | ~ | local-runs.md:7's 'run from the repo root' fits pulsedIV (ivCSV defaults to figures/...). | `kb/workflow/local-runs.md:7, kb/workflow/local-runs.md:10 (+2)` |
| KBC-27 | L | M | ✓ | Several notes break the 'atomic notes' convention of CLAUDE.md §9 and index.md:8. | `kb/model/3d-plan.md:85, kb/model/levers.md:58 (+2)` |
| KBC-28 | L | S | ✓ | Several references point to CLAUDE.md §10 sections, which no longer exist: the static-era sections moved to archive/static_mobility/RESULTS.md, where 10h and 10j are headings. | `kb/device/mesh.md:10, kb/model/insulator-traps.md:10 (+4)` |
