# Energy-balance debug tools (2026-10-08 to 2026-10-12)

Archived 2026-11-21 (clean-up stage 4, findings DRV-11 and DRV-17 in `kb/workflow/cleanup-plan.md`). The electron energy balance (`eTemp 1`) is an option and its thermoelectric term is parked; the model standard has been `eTemp 0`, the local-field model, since 2026-10-16. The physics, the decisions and every result are in `kb/model/energy-balance.md`; the dated log is `progress.md` (2026-10-08 to 2026-10-13, "PARKED … electron energy balance").

## What is here

| File | Moved from | What it is |
|---|---|---|
| `eTempDebug_tail.tcl` | `drivers/eTempDebug_tail.tcl` | Tcl appended after `drivers/pulsedIV.tcl` (run with `Vd_max 0`). It was meant to take the 0 → `dbgVd` (default 0.1 V) step with Newton capped at 1 and then 2 iterations, and after each dump ETemp, Qfn, Elec, DevPsi (and Δ with `eTemp 1`): `DBGPEAK` lines in the log and cuts in `dbg_<it>_<field>.txt`. |
| `eTempDebug.slurm` | `sweeps/eTempDebug.slurm` | The template. Per task it writes `dbg_task.tcl` = `trapEn 0`, `eTemp 1`, `etTau 1e-12`, `Vg_meas -2.0`, `Vd_max 0.0`, `dampValue 0.05`, the params line's extra levers, `pulsedIV.tcl` with the GUI lines stripped, then the tail. It copies the model files (with `ETemp.tcl`) from `model/` into `results/20261008_eTempDebug/<tag>/` and runs there; logs go to `results/eTemp_logs/dbg_%A_%a.{out,err}`. Its two paths to the params file and the tail now point into this folder. |
| `params_eTempDebug.txt` | `sweeps/params_eTempDebug.txt` | Two tasks, `tag|levers`: `thermo_full` (`etThermo 1`) and `no_thermo` (`etThermo 0`, the converging reference). |
| `plot_eTemp.py` | `analysis/plot_eTemp.py` | Figures of the first energy-balance run against the local-field model: `figures/eTemp_IdVd.png` (Oct 8 dashboard day) and `figures/eTemp_profiles.png`. |

## The dump readings are unverified

The tail sets `pdbSetDouble Math iterLimit 1` (then 2) after the solver is built. FLOOXS reads `iterLimit` once, when it builds the solver (the solve inside `device init`), so the caps never took effect (`kb/numerics/flooxs-gotchas.md`, `kb/flooxs/flooxs-solver.md`). The dumps followed full, possibly failed, solves under the deck's limit. So every reading that ties a value to "the first Newton update" or "one iteration" (jobs below, in `kb/model/energy-balance.md` and in `progress.md`) is unverified (Ian, 2026-11-20). Rechecking it, with `iterLimit` set before `device init`, is Ian's call if the thermo term is ever resumed.

## Runs and jobs

All debug jobs wrote to the same folder, `results/20261008_eTempDebug/<tag>/`, which the template hard-codes, so each rerun overwrote the last. That folder is on HPG only.

| Job | Date | What changed before it (`progress.md`) |
|---|---|---|
| 45207320 | 2026-10-08 | first try; panicked on a cut that lay exactly on a mesh line |
| 45208486 | 2026-10-08 | print1d cut positions fixed |
| 45209164 | 2026-10-08 | ETemp solution given the `damp` flag |
| 45210603 | 2026-10-08 | density floor `etFloor` 1e10 in the energy equation |
| 45692147 | 2026-10-12 | `etNeg 1` (`negative damp` ETemp); the first Oct 12 submission (45691969 / 45691970, debug pair and thermo set) crashed at setup |

`plot_eTemp.py` reads `results/20261008_eTemp1` (job 45186466, etStats 1, cancelled at about 55 min with 6 of 13 tasks done) and the local-field references in `results/20261002_onsetField1` (job 44359813), `results/20261002_onsetField3` (44435511) and `results/20261002_onsetField3RetryRamp` (44452288).

## How to run them if ever needed

- **Figures:** from the repo root, `python3 archive/energy_balance/plot_eTemp.py [run_dir]` (default `results/20261008_eTemp1`). It writes `figures/eTemp_IdVd.png` and `figures/eTemp_profiles.png` at the figures root, where the tracked copies stay, so write over them only on purpose.
- **Debug job:** ask Ian first (CLAUDE.md §2). On HPG, from the repo root: `sbatch --array=0-1 archive/energy_balance/eTempDebug.slurm`. It uses today's `model/` and `drivers/pulsedIV.tcl`, which have changed since October: `etStats` and `etThermo` default to 0 since 2026-10-13, so both tasks need `etStats 1` added to their params lines to match October (it was the default then), and the FP contact box was fixed on 2026-11-20 (`kb/results/fp-contact-fix.md`). To rerun it exactly as it was, check out the commit before the job's `progress.md` entry; from the 2026-10-12 reorganisation (42ecf73) until this move the tail sat in `drivers/` and the template and params file in `sweeps/`; before it all three were at the repo root.
- To make the caps real, set `iterLimit` before the solver is built (see above); that is a change to the tool, not a rerun.
