# CLAUDE.md

FLOOXS (Tcl) TCAD model of an AlGaN/GaN HEMT (HighK/HfO2-passivated, T-gate + field plate). Layout: `model/` (model + device decks), `drivers/` (Tcl drivers), `sweeps/` (SLURM templates + params), `analysis/` (Python), `data/` (measured inputs), `bin/` (workflow helpers), `figures/` (outputs), `dashboard/`, `kb/`, `archive/` (superseded; static-mobility era also on branch `static-mobility`), `results/` (gitignored). See `README.md` and `kb/workflow/repo-locations.md`.

**Context:** model the **radiation-induced current collapse** seen on a pulsed curve tracer: at Vgs = −2 V, Id–Vd runs normally, then drops ~1000× at a small Vd (~0.4–0.5 V), then creeps up slightly with Vd (the creep is physical). The deck is calibrated against a measured HfO2 transfer curve with the field-dependent mobility.

**This file holds the rules for working here. The knowledge lives in the knowledge base `kb/`** (an Obsidian second brain: atomic Markdown notes linked with `[[wikilinks]]`). Start at `kb/index.md`; the current state of the work is `kb/current-status.md`; the dated log is `progress.md`. Read the relevant KB notes before working on a topic, and keep them current (§9).

---

## 0. How this system is set up

- **You (the agent) run on Ian's workstation** (personal, off campus), inside `tmux`. Ian checks in from his laptop or phone via Remote Control. Assume he is **not watching** in real time.
- **HiPerGator (HPG) is reached only through `ssh hpg`**, a multiplexed master connection. Since 2026-10-13 it authenticates with the workstation key `~/.ssh/id_ed25519_hpg` (no password) **plus one Duo push that Ian approves on his phone**. You can trigger the push (`bin/hpg_reconnect.sh`), but only Ian can approve it.
- **The repo exists in three places**, synced through GitHub (`IanStafford/HEMTRAD`, branch `main`):
  - Workstation `/home/staffian/HEMTRAD`: your working copy. Edit here.
  - HPG `/home/ianstafford/blue/ee1/ianstafford/HEMTRAD`: only `git pull` there. Never edit files on HPG. Despite its name this path is in the 40 GB NFS home, not on `/blue` (`/blue/ee1/ianstafford` is a different directory, `kb/workflow/repo-locations.md`).
  - Ian's laptop: a read-only clone (pull only, never pushes). Anything Ian should see must be committed and pushed from the workstation.
- **Obsidian vault** `~/notes/HEMTRAD-vault` (outside the repo): symlinks only — `CLAUDE.md`, `progress.md`, `archive/static_mobility/RESULTS.md` and the `kb/` folder. Never copy or move repo files into it; never open the repo itself as a vault (`.obsidian/` is gitignored as a safety net). To add something, `ln -s` it there.
- **Where things run:** short checks (a few points, syntax, debugging a deck) locally; sweeps, more than ~3 driver runs or anything long → SLURM on HPG. When Ian says to run everything on HPG for the day, don't run FLOOXS locally.
- All paths, binaries and checkouts: `kb/workflow/repo-locations.md`.
- **Run everything from the repo root:** `flooxs drivers/<driver>.tcl` (drivers find `model/` themselves, or the flat model files in a sweep task directory), `python3 analysis/<script>.py`, `sbatch sweeps/<template>.slurm`.

---

## 1. Progress log (required)

Keep `progress.md` up to date. Ian reads it to check in, and you rely on it after context compaction or the next day. After every milestone (job submitted, job finished, result analysed, decision made), append a dated entry with:
- what was run: driver, lever values, SLURM job ID;
- the result, in one or two lines with numbers;
- what's next or what you're waiting on.

When you need Ian to decide something, write it in `progress.md` **and** send a push notification. Then wait. Don't guess on physics decisions. Parked work gets a "PARKED … where to pick up" entry.

---

## 2. HPG rules (details: `kb/workflow/hpg-workflow.md`, `kb/workflow/sweep-pattern.md`)

- **Check the connection first:** `ssh -O check hpg`. Every other agent ssh uses `-o BatchMode=yes` (fails instead of prompting).
- **If the master is down:** push-notify Ian ("HPG reconnect: Duo push coming"), then run `bin/hpg_reconnect.sh` **once** (answers the Duo menu with option 1 = push to XXX-8915, waits 2 min). If it fails or the push isn't approved: **stop, note it in `progress.md`, notify Ian, and wait.** No loops, no second attempt until Ian says so. If any prompt ever asks for a **password**, stop: never type, store or ask for Ian's UF password.
- **Persistent tmux on HPG:** session `hemtrad` on `login7` (`ssh hpg-tmux` attaches; `ssh hpg-login7 <cmd>` runs on that node). For rsyncs, builds, `srun --pty` debugging; never `flooxs` itself. Details: `kb/workflow/hpg-workflow.md`.
- Run remote commands in a login shell with a quoted heredoc (`ssh hpg bash -l <<'REMOTE' … REMOTE`), delimiter `REMOTE`, not `EOF`.
- Job scripts use the environment block in `kb/workflow/hpg-workflow.md`. A job that dies immediately with a library/Tcl/plplot error is an environment problem, not the deck.
- **Never run `flooxs` on an HPG login node** (only via `sbatch`/`srun`).
- `--account=ee1`. QOS `ee1` = 19 CPUs for the whole group; burst `ee1-b` ≈ 171 CPUs. Check `squeue -A ee1` before submitting; throttle arrays with `%N`.
- **Ask Ian before any `sbatch`** unless he approved that specific run in the current task. **Ask before any `scancel`.** Only cancel your own job IDs, never `scancel -u`.
- Poll every 5 minutes with a background `sleep 300` loop, never a busy loop.
- Follow the sweep pattern exactly (`kb/workflow/sweep-pattern.md`: submit from the repo root, per-task directories with the model files copied flat, never edit the repo copy in place, `params.json` per task, check **every** task's logs before plotting for crashes/OOM/timeouts/core files **and for the driver's failure markers in the per-driver table there** (`PULSED GAVE UP` for pulsedIV; the `GAVE UP` and `failed` lines, except the normal `RETRY … failed` bisections, Tcl errors and a missing `RADIV DONE`/`SEEIV DONE` for radIV/seeIV), rsync back excluding cores).

---

## 3. Local runs (details: `kb/workflow/local-runs.md`)

- **Run one FLOOXS process at a time** — check `pgrep -x flooxs` first (Ian or another agent may be running one). Chain several tests in one background loop that checks before each.
- Kill runs by PID (`pkill -f` also matches the issuing shell).
- **Headless runs segfault on `chart`/`plot1d`/`window`**: run a *copy* with `sed -i 's/^window.*//; s/^\(\s*\)chart /\1#chart /'`.

---

## 4. Git (details: `kb/workflow/git-conventions.md`)

- `git pull` at session start; commit (message names runs/levers) and push after meaningful changes.
- Commit `model/`, `drivers/`, `sweeps/`, `analysis/`, `data/` (the HfO2 calibration curve and model-side files, never measured radiation data), `progress.md`, `kb/`, `dashboard/`, `README.md`, small final CSVs/figures. Keep new files in the matching folder. **Don't commit** `results/`, logs, meshes, build artifacts, `.obsidian/`.
- **The repo is public** (HPG pulls it anonymously). Measured radiation data and notes are never tracked (the HfO2 calibration curve in `data/`, csv and raw xlsx, is the only measured data in git), and tracked files give measured results in words only, never numbers. Their paths are in `.gitignore` (`data/rad_y2/`, `data/rad_y3/`, `kb/results/measured-*.md`, `drivers/trim/*NCY2*`). Add a new measured folder or note to `.gitignore`, and commit that, **before** creating it. **Stage by explicit path**: never `git add -A`, `git add .`, `git add data/` or `git add kb/`; check `git diff --cached --name-only` before every push.
- **CRLF files:** `model/GaN_modelfile_masterD`, `model/Metal.tcl`, `model/Continuity.tcl` must keep CRLF. Edit from Python with `open(..., newline='')`; check `file <name>` afterwards.
- **Commit before changing any model file** (`model/GaN_modelfile_masterD`, `model/Poisson.tcl`, `model/GaN.tcl`, `model/AlGaN.tcl`, `model/Metal.tcl`, `model/Insulator.tcl`, `model/Continuity.tcl`, `model/ETemp.tcl`, `rfdevice*.tcl`).
- Superseded work goes to `archive/<name>/` with a README, not deleted.

---

## 5. Physics rules

- **Don't change the physics to get convergence.** If a run diverges, first try solver-side fixes (smaller Vd step, damping, better initial guess, retry/continuation). Propose any change to trap physics, capture/emission, Poisson or transport terms to Ian (via `progress.md` + notification) before making it, and explain why.
- Every lever keeps an `info exists` default; new options default to the old behaviour (`kb/model/levers.md`).
- Sweeps always set the trap levers explicitly (`drivers/pulsedIV.tcl`'s defaults are not Run F).

---

## 6. FLOOXS pitfalls you must respect (details: `kb/numerics/flooxs-gotchas.md`)

- **A bare `catch {device}` + retry is unsafe** (stale solver queues are assembled twice). Always `device store` before an attempt and `device restore` after a failure (`kb/numerics/munmap-crash.md`, `kb/numerics/retry-bisection.md`).
- Constant data fields are folded into the equations at `device init`: initialise switch fields with a tiny spatial variation (`sel z=1.0e-30*(1.0+x*x) name=F`). Redefining a `const` solution after `device init` doesn't reach the equations.
- Build `solution … val = (…)` expressions in a Tcl variable first (word-splitting error otherwise).
- A solution's `DampValue` only acts if the solution has the `damp` flag.
- **Solver parameters are read once, when the solver is built** (the first `device` after `device init`, or after a mesh change): `Math iterLimit` and each solution's `Abs.Error`, `Rel.Error`, `DampValue`, `Damp`, `Negative`. Set them before `device init`; a `pdbSetDouble` on them after the solver is built does nothing until the next `device init`.
- **`deviceDim 3` only with the patched FLOOXS (`~/flooxs-brickfix`, local) or FANGS with the brick fix on HPG.** Stock FLOOXS, which `sweeps/radIV.slurm` runs, gets gradients wrong on 3D brick meshes (x and z scaled by (hx/hz)^±1, only y exact), so fields, Te and field-scaled damage come out wrong without any error (`kb/model/3d-plan.md`, `kb/flooxs/flooxs-builds.md`).

---

## 7. Knowledge base map (`kb/`)

**The full list of notes, grouped by topic, is `kb/index.md`**; every new note gets a line there (§9). Folders: `kb/` (index, project-goal, current-status, glossary), `kb/device/`, `kb/model/`, `kb/flooxs/` (the simulator, `~/flooxs`), `kb/numerics/`, `kb/workflow/`, `kb/tools/`, `kb/results/`.

Read first:

| For | Notes |
|---|---|
| where the work stands | `current-status.md`, `project-goal.md` |
| the model in use now | `results/rad-model.md`, `model/damage-model.md`, `model/levers.md`, `model/trap-model.md`, `results/fp-contact-fix.md` |
| the current study | `results/step-search-28v.md`, `results/step-mechanism.md` |
| running jobs | `workflow/sweep-pattern.md`, `workflow/hpg-workflow.md`, `workflow/stress-library.md`, `tools/drivers.md` |
| FLOOXS behaviour that bites | `numerics/flooxs-gotchas.md` |

Static-era write-ups verbatim: `archive/static_mobility/RESULTS.md`.

---

## 8. "Wrap up for the day"

When Ian says "wrap up for the day", update and republish the work-log dashboard (https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd, source `dashboard/hemt-collapse-log.html`) by following **`kb/workflow/dashboard.md`** step by step, in the same style as the existing pages. Always edit the repo copy and publish to the same URL; never start a new artifact. Also refresh `kb/current-status.md`.

---

## 9. Keeping the knowledge base current

- When a result is analysed or a decision changes the picture, update the matching `kb/` note (numbers, job IDs, figure paths) and `kb/current-status.md`, in the same commit as the `progress.md` entry. New topic → new atomic note, linked from `kb/index.md` and from related notes.
- Notes: YAML frontmatter (`title`, `tags`, optional `date`/`source`), plain specific sentences with numbers, `[[note-name]]` links (file name without `.md`; names are unique across folders). Keep `progress.md` as the chronological log; the KB says what is true now.
- Check links after editing: every `[[link]]` must match a note file name.
