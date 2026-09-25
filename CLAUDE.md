# CLAUDE.md

FLOOXS (Tcl) TCAD decks for an AlGaN/GaN HEMT, plus `figures.ipynb` for plots. See README.md for layout.

**Current goal:** reproduce the **radiation-induced current collapse** seen on a pulsed curve tracer. At Vgs=-2V, Id-Vd runs normally, then drops ~1000x at a small Vd (~0.4-0.5 V), then creeps up slightly with Vd. The creep is physical. There are no experimental CSVs for this in the repo.

---

## 0. How this system is set up

- **You (the agent) run on Ian's workstation** (personal, off campus), inside `tmux`. Ian checks in from his laptop or phone via Remote Control. Assume he is **not watching** in real time.
- **HiPerGator (HPG) is reached only through `ssh hpg`**, which reuses a multiplexed master connection that Ian authenticates (Duo) each morning. You cannot answer Duo.
- **The repo exists in two places**, synced through git:
  - Workstation: `/home/ianstafford/blue/ee1/ianstafford`, which is your working copy. Edit here.
  - HPG: `/home/ianstafford/blue/ee1/ianstafford`. Only `git pull` there. Never edit files on HPG directly.
- **Where things run:**
  - Short checks (a few points, syntax tests, debugging a deck) → run locally on the workstation.
  - Sweeps, anything more than ~3 driver runs, anything long → SLURM on HPG.

---

## 1. Progress log (required)

Keep `progress.md` in the repo root up to date. Ian reads it to check in, and you rely on it after context compaction or when resuming the next day. After every milestone (job submitted, job finished, result analyzed, decision made), append a dated entry with:
- what was run: driver, lever values, SLURM job ID;
- the result, in one or two lines with numbers;
- what's next or what you're waiting on.

When you need Ian to decide something, write it in `progress.md` **and** send a push notification. Then wait. Don't guess on physics decisions.

---

## 2. Talking to HPG

### Check the connection first
```bash
ssh -O check hpg
```
If this fails, or any `ssh hpg` command hangs or fails to authenticate: **stop, note it in `progress.md`, notify Ian, and wait.** Don't retry in a loop, and don't try to open a new connection (it would stall on Duo).

### Running commands
Non-interactive SSH doesn't load the login environment (`module`, `conda`, SLURM paths may be missing). Always use a login shell with a quoted heredoc, so nothing gets expanded on the workstation:
```bash
ssh hpg bash -l <<'REMOTE'
cd /blue/ee1/ianstafford/<repo>
git pull --ff-only
squeue -u $USER
REMOTE
```
Use a delimiter like `REMOTE`, not `EOF`, so it can't collide with heredocs inside the remote script.

### HPG environment (used inside every job script)
```bash
module restore flooxsenv
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find $CONDA_PREFIX/share -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

$FLXSHOME/release/flooxs script.tcl
```
- The HPG binary is `$FLXSHOME/release/flooxs`. There's no container.
- If `conda activate` fails inside a batch script, add `eval "$(conda shell.bash hook)"` before it.
- If a job dies immediately with a library, Tcl, `PL_LIBRARY`, or plplot error, the **environment** is the problem, not the deck. Check the env block before touching Tcl.
- Never run `flooxs` on an HPG login node. It always goes through `sbatch` (or `srun` inside an allocation).

### Hard SLURM rules
- `--account=ee1`, `--qos=<ee1-b: ee1>`.
- **The group QOS caps at 19 CPUs total.** Check `squeue -A ee1` (other group members count too) before submitting. Throttle arrays with `%N` (e.g. `--array=0-7%4`) so jobs don't sit in `QOSGrpCpuLimit`.
- **Ask Ian before any `sbatch`** unless he approved that specific run in the current task. **Ask before any `scancel`.** Only cancel your own job IDs, never `scancel -u`.
- Poll with `squeue -u $USER` no more often than every 2-3 minutes. Sleep between polls; don't busy-loop.

### Sweep workflow (the standard pattern)
1. Commit the driver and the SLURM template on the workstation, then `git push`.
2. On HPG: `git pull --ff-only`.
3. Write `params.txt`: one line per array task, parameter bundle **pipe-delimited**. Task `$SLURM_ARRAY_TASK_ID` reads line N+1 (the `trapPlot.slurm` pattern).
4. Each task copies the driver into its own directory `results/<YYYYMMDD>_<tag>/task_<id>/` and prepends `set <lever> <value>` lines (every lever has an `info exists` default). It then strips the GUI lines (§4) and runs there. **Never edit the repo copy in place.**
5. Write per-task CSVs (`pulsedIV_<tag>.csv`), never the shared `figures/pulsedIV.csv`. Also write the full parameter set into a `params.json` next to each CSV.
6. Format float parameters explicitly in names (`printf '%.2e'`), so you don't get `1.3000000000000001e-13` filenames.
7. After the array finishes, check **every** task's `.out`/`.err` for `Newton failed`, NaN, OOM (`oom-kill`, signal 9), or a missing CSV. Use `grep`/`tail`, not `cat` on whole logs. Report failures before plotting.
8. `rsync -av hpg:/blue/ee1/ianstafford/<repo>/results/<run>/ results/<run>/` to bring results back. Analyze and plot on the workstation.

Starting resources for a 17-point `pulsedIV` run: `--cpus-per-task=1 --mem=4gb --time=00:45:00`. OOM core dumps have happened before. If a task hits OOM, raise `--mem`; don't change the deck.

---

## 3. Running locally on the workstation

- `flooxs <driver>.tcl` from the repo root (paths like `figures/...` are relative).
- **Run one FLOOXS process at a time.** Simultaneous runs slow each other to a crawl. Check `pgrep -x flooxs` first, because Ian may be running one himself.
- Kill runs by PID. `pkill -f "<pattern>"` also matches the shell that issued it.
- A driver point takes roughly 30-60 s. A 17-point `pulsedIV.tcl` sweep takes about 12-15 min. Anything longer than one sweep goes to HPG.
- FLOOXS source for checking behavior: `~/flooxs/src`.

---

## 4. Headless runs (both machines)

Headless runs segfault on `chart`/`plot1d`/`window`. You are always headless, locally and on HPG. Run a *copy* of the deck with those lines stripped:
```bash
sed -i 's/^window.*//; s/^\(\s*\)chart /\1#chart /'
```

---

## 5. Git

- Start of session: `git pull`. After meaningful changes: commit with a message naming the runs or lever values, then push.
- **Commit:** decks, drivers, `.slurm` templates, `params.txt`, analysis scripts, `progress.md`, small final CSVs used in figures.
- **Don't commit:** `results/` sweep directories, `.out`/`.err` logs, meshes, build artifacts (these are in `.gitignore`).
- `GaN_modelfile_masterD` has **CRLF** line endings and must keep them. `.gitattributes` contains `GaN_modelfile_masterD -text`. Python edits must use `open(..., newline='')`.
- Commit **before** changing any model file (`GaN_modelfile_masterD`, `Poisson.tcl`).

---

## 6. FLOOXS gotchas (learned the hard way)

- **Tcl word splitting in `solution ... val = (...)`:** `val = (($Ntrap) * $occ)` fails with "Ambiguous or unknown parameter *". Build the expression in a variable first: `set e "..."; solution ... val = ($e)`.
- **Constant data fields are folded into the equations at `device init`** (`src/BasePDE/ExprStore.cc:527`, `DataConst`). A field set with `sel z=0.0 name=F` becomes the literal 0 in any equation, so later `sel` updates are ignored. Initialize switch fields with a tiny spatial variation, e.g. `sel z=1.0e-30*(1.0+x*x) name=F`.
- **Redefining a `const` solution after `device init` doesn't reach the assembled equations.** `sel` sees the new definition, but Poisson doesn't. To switch behavior at runtime, use data fields as above.
- `sqrt(dot(DevPsi,DevPsi))` is |E| in V/cm (lengths are internally cm).
- Current in the CSVs is `abs(contact flux)*1e6` = mA/mm.

---

## 7. Trap model (Poisson.tcl)

- **Sign bug (fixed in 760b388):** the old `NeutralAcceptor` put *empty* traps into Poisson as negative charge. That made trapping feed on itself, and Newton diverged into NaN at Vd≈1.5 V. The abrupt collapse in `radPlot.csv`/`radPlot1.csv` came from this bug, so only their onset and depth are targets, not the decay to 1e-9 after the collapse.
- `IonizedAcceptor Mat Ntrap Etrap Efwhm {g 2}`: acceptors are neutral when empty and -q when filled. `IonAcceptor = Ntrap * f`, where `f` is the Fermi-Dirac occupancy at level `Econd - Etrap`, with a Gaussian energy spread via 3-point Gauss-Hermite. Poisson uses `- IonAcceptor`.
- **Hot-electron capture:** capture over a barrier `hotEb` with electron temperature Te, and emission at the lattice T. This is equivalent to lowering the trap level by `hotEb*(1 - T/TeTrap)`. `TeTrap` is a data field. `UpdateTe` sets it from a local-field model: `Te = T + (2/3) tau v(E) E / (k/q)`, with E = |grad Qfn|. It uses Qfn, not DevPsi, so the polarization field doesn't heat electrons at equilibrium. It is under-relaxed.
- **Trap memory:** when not frozen, the charge is `max(TrapFrozen, live)`, written as `0.5*(a+b+abs(a-b))`.
  - `CaptureTraps` stores the current charge in `TrapFrozen`, so traps fill but never empty.
  - `FreezeTraps` holds the charge fixed via `FrozenFlag`.
  - `ThawTraps` resets everything to live, Fermi-level occupancy with cold electrons.
  - `HotStress` iterates Te and the device solve at a fixed bias.
  - `FillStep` does the same with capture after every solve.
- `Initialize` (in `GaN_modelfile_masterD`) creates the `TrapFrozen`, `FrozenFlag` and `TeTrap` fields.

**Don't change the physics to get convergence.** If a run diverges, first try solver-side fixes: a smaller Vd step, damping, or a better initial guess. Propose any change to trap physics, capture/emission, or Poisson terms to Ian (via `progress.md` + notification) before making it, and explain why.

---

## 8. Levers

In `GaN_modelfile_masterD`, each has an `info exists` default, so a driver or array task can override it before sourcing:

| Lever | Default | Meaning |
|---|---|---|
| `trapEn` | 0 | enable traps |
| `trapPeak` | 4e18 | peak density (cm⁻³) of the 2D Gaussian |
| `trapMeanX`, `trapMeanY` | 0.0, 0.20 | center in µm (x = depth; 0 = AlGaN top, 0.015 = 2DEG; y: gate drain edge = 0.125) |
| `trapSigma` | 0.025 | spatial sigma (µm) |
| `trapLevel`, `trapWidth` | 0.68, 0.1 | depth below Ec and energy FWHM (eV) |
| `hotEb` | 0.3 | capture barrier (eV); larger = earlier, deeper collapse; 0 = no hot-electron effect |
| `hotTau` | 1e-13 | energy relaxation time (s); larger = hotter = earlier collapse |
| `hotMu`, `hotVsat` | 600, 1.9e7 | used only for Te |

---

## 9. Drivers

- `pulsedIV.tcl`: curve-tracer model and the main tool for the collapse. The device rests at `Vg_meas` (traps at steady state), then Vd is swept with `FillStep` at each point (fill-only, no emission). Levers are at the top. It writes `figures/pulsedIV.csv` with columns Vd, Id, peak Te. **The repo copy still has the original defaults (0.68 / 0.3 / 1e-13), not the tuned values below.**
- `stressFreeze.tcl`: pulsed-IV quiescent-stress model. It stresses at (VgQ, VdQ) with `HotStress`, freezes the traps, then measures Id-Vd at Vg=-2. Stress (-2,10) gave a 46% drop plus knee walkout (`figures/hotStressIV_*.csv`). The (-4,20) stress NaNs at Vd≈17.5 V during the ramp.
- `trapPlot.tcl` / `trapPlot.slurm`: older dynamic-trap driver (Id-Vd plus trap profile), and the array-job template to copy for new sweeps.

---

## 10. Tuning results

All `pulsedIV.tcl` runs, Vg=-2, Vd 0-1.6 in 0.1 V steps, `trapMeanY`=0.20. Target: `radPlot1` (9.75, 19.0, 27.2, 32.0 at 0.1-0.4 V, then 0.011 at 0.5 V).

| Run | trapPeak | trapSigma | trapLevel | hotEb | hotTau | Result |
|---|---|---|---|---|---|---|
| defaults | 4e18 | 0.025 | 0.68 | 0.3 | 1e-13 | 5.7 → 1.2 at 0.2 V, shallow |
| A | 4e18 | 0.025 | 0.68 | 0.3 | 3e-14 | only sags (too many traps filled at rest) |
| B | 4e18 | 0.025 | 0.55 | 0.5 | 1e-13 | pre-collapse matches; 30 → 2 at 0.6 V, shallow |
| C | 4e18 | 0.025 | 0.55 | 0.5 | 4e-14 | onset 0.85 V, shallow |
| D | 8e18 | 0.025 | 0.55 | 0.5 | 1.3e-13 | collapsed from the first step |
| E | 1.2e19 | 0.025 | 0.55 | 0.5 | 1.3e-13 | collapsed from the first step (stopped early) |
| **F** | 4e18 | **0.04** | 0.55 | 0.5 | 1.3e-13 | **best shape**: 7.8, 7.0, then 0.006 at 0.3 V, creeps up to 0.018 at 1.6 V |
| G | 5.5e18 | 0.025 | 0.55 | 0.5 | 1.3e-13 | 5.3, then 0.003 at 0.2 V, creeps up |

Trends:
- A shallower `trapLevel` means fewer traps filled at rest, so a higher pre-collapse current and a deeper collapse.
- More total trapped charge (`trapPeak` × `trapSigma`²) gives a deeper collapse, but past about 5e18 × 0.025² it pinches the channel at rest.
- Onset Vd scales roughly as 1/√`hotTau`.

**Keep this table current.** Add every completed run and commit it.

**Next step:** run F with `hotTau` ∈ {0.6e-13, 0.5e-13, 0.4e-13} as a 3-task HPG array, to move the onset to 0.4-0.5 V. Then set the best values as the defaults in `pulsedIV.tcl`. Note that F's pre-collapse current is also off: 7.8 / 7.0 mA/mm at 0.1 / 0.2 V vs target 9.75 / 19.0, and it *falls* with Vd where the target rises. Check pre-collapse shape against target before declaring a match.

### 10b. Late-onset tuning (target: Run F's shape, but onset ~3 V instead of ~0.3 V)

All runs below: Vg=-2, Vd 0-4.05 V in 0.15 V steps (coarse search resolution), `trapMeanY`=0.20, `hotEb`=0.5, `trapLevel`=0.55 (F's values). Job 43252782, `results/20260924_lateOnset/`.

Local probes first (F's own trapPeak=4e18/trapSigma=0.04, hotTau only):
| hotTau | Result |
|---|---|
| 1.3e-15 (naive 1/√hotTau extrapolation, 100x below F) | no collapse through Vd=4V; peak Te only 353K - heating too weak, full stop |
| 1e-14 (10x below F) | only a shallow ~1.5x sag (42.4→28.9 mA/mm, Vd 0.75-1.25V), not dramatic |

HPG grid (trapPeak × hotTau, trapSigma=0.04 fixed):
| trapPeak | hotTau | Result |
|---|---|---|
| 4e18 | 1e-14 | no collapse; rises to 46.6 mA/mm by 4.05V |
| 4e18 | 7e-15 | no collapse; rises to 66.4 mA/mm by 4.05V |
| 4e18 | 5e-15 | no collapse; rises to 88.5 mA/mm by 4.05V |
| 6e18 | 1e-14 | already collapsed at Vd=0.15 (2.5→0.49 mA/mm by 0.6V), not a late onset |
| 6e18 | 7e-15 | already collapsed at Vd=0.15, same pattern |
| 6e18 | 5e-15 | mostly flat ~3.5-4.8 mA/mm, barely any collapse |
| 8e18 | 1e-14 | already collapsed at Vd=0.15 (channel pinched at rest) |
| 8e18 | 7e-15 | already collapsed at Vd=0.15, same |
| 8e18 | 5e-15 | already collapsed at Vd=0.15, same |

**None of these hit the target.** trapPeak=4e18 (F's charge) never collapses once hotTau is cut enough to matter - lower hotTau trades depth for onset delay and there's no crossover before the effect just vanishes. trapPeak=6e18/8e18 (more charge, to try to restore depth) instead pinch the channel at rest (before the Vd sweep even starts, at Vd=0.15), because the *cold*, zero-field trap occupancy at `trapLevel`=0.55 eV is already large enough at that density - this has nothing to do with `hotTau`. So `trapPeak` alone can't add "hot-only" depth without also adding "always-on" depth.

**Working hypothesis for next round:** decouple those two effects with `trapLevel`. A shallower level (smaller eV, e.g. 0.35-0.45) empties out more at cold/zero-field equilibrium (per the existing trend row above), which should buy headroom to raise `trapPeak` well past 6-8e18 *without* pinching at rest, while `hotEb`/`hotTau` still control how much of that extra density gets pulled in once the channel heats up. Proposed next grid: `trapLevel` ∈ {0.35, 0.45} × `trapPeak` ∈ {8e18, 1.2e19, 1.6e19}, `hotTau` fixed at 1e-14 first (weakest tested so far that still shows any hot effect), `trapSigma`=0.04, `hotEb`=0.5. Check baseline (Vd≈0.15-0.3V) isn't already collapsed before trusting the rest.

**Round B (job 43283546, `results/20260925_lateOnsetB/`):** `trapLevel` × `trapPeak` grid, `hotTau`=1e-14, `trapSigma`=0.04, `hotEb`=0.5, same Vd 0-4.05V/0.15V sweep.

| trapLevel | trapPeak | Result |
|---|---|---|
| 0.35 | 8e18 | rises cleanly to 85.5 mA/mm (peak Vd=1.35V), knee down to 30.2 at Vd=1.8V (~2.8x drop, **onset delayed to ~1.5-1.8V**), creeps back up to 52.3 by 4.05V |
| 0.35 | 1.2e19 | peaks 21.1 mA/mm (Vd=0.45V), drops ~10x to ~2.0 by Vd=0.75-0.9V, creeps back to 9.07 by 4.05V |
| 0.35 | 1.6e19 | already declining by Vd=0.15V (peak only 2.76), too much charge again |
| 0.45 | 8e18 | peaks 12.0 at Vd=0.3V, drops to 1.6-1.7 by Vd=0.6-0.9V (~7x), creeps to 5.6 by 4.05V |
| 0.45 | 1.2e19 | already declining from the first point (peak 0.82 at Vd=0.15V), too much charge |
| 0.45 | 1.6e19 | already fully collapsed at Vd=0.15V (peak 0.07) |

`trapLevel`=0.35 clearly has more dynamic range than 0.45 or the original 0.55 - it's the first time we've gotten a real "normal rise, then knee, then partial recovery" shape instead of either "no collapse" or "collapsed from the start." But nothing here is close to F's ~1000x depth (best is ~10x, at `trapPeak`=1.2e19), and the deepest case (8e18) has the latest onset (~1.5-1.8V) but only ~2.8x depth - the sweet spot for *both* late onset and F-like depth is somewhere between these two `trapPeak` values, not yet bracketed. Also notable: all these collapses **partially recover** with rising Vd (30→52, 2→9) rather than staying collapsed like F's slow creep (0.006→0.018) - a much bigger relative recovery, suggesting we're still short of the total trapped charge needed to keep the channel pinched as Vd keeps rising.

**Proposed round C:** narrow `trapPeak` between the two round-B extremes - {8.5e18, 9.5e18, 1.05e19} - crossed with `hotTau` ∈ {1e-14, 2e-14} (more heating, to deepen the collapse) at `trapLevel`=0.35, `trapSigma`=0.04, `hotEb`=0.5. 6 tasks.

**Round C (job 43297414, `results/20260925_lateOnsetC/`):** same fixed levers as round B (`trapLevel`=0.35, `trapSigma`=0.04, `hotEb`=0.5), Vd 0-4.05V/0.15V.

| trapPeak | hotTau | Result |
|---|---|---|
| 8.5e18 | 1e-14 | peak 74.7 (Vd=1.2V) → 16.1 (Vd=1.65V), ~4.6x, recovers to 33.6 by 4.05V |
| 8.5e18 | 2e-14 | peak 54.6 (Vd=0.75V) → **0.174 (Vd=1.2V), ~314x** - creeps to 0.627 by 4.05V, much closer to F's shape |
| 9.5e18 | 1e-14 | peak 54.8 (Vd=0.9V) → 6.58 (Vd=1.35V), ~8.3x, recovers to 16.7 by 4.05V |
| 9.5e18 | 2e-14 | peak 40.1 (Vd=0.6V) → **0.116 (Vd=0.9V), ~346x** - creeps to 0.596 by 4.05V |
| 1.05e19 | 1e-14 | peak 37.4 (Vd=0.6V) → 3.59 (Vd=1.05V), ~10.4x, recovers to 11.9 by 4.05V |
| 1.05e19 | 2e-14 | **crashed** (`munmap_chunk(): invalid pointer`, core dump, mid-sweep at Vd≈1.35V) - not a Newton/NaN failure, a solver abort. Partial data shows peak 27.8 (Vd=0.45V) → 0.074 (Vd=0.75V), ~378x, already the earliest-onset, deepest trend of the three `trapPeak` values before it died. Not retried; flagging per the "propose before changing physics" rule - this is right at the edge of the grid, not clearly a physics problem, likely just an extreme-value numerical crash. |

**Best result so far by far:** `trapPeak`=8.5e18, `hotTau`=2e-14 - a genuine ~300x collapse (54.6→0.174 mA/mm) with a creep-up afterward (0.174→0.627), the same qualitative shape as F. Onset is ~0.9-1.2V, still short of the ~3V target, but this is the first combo with F-like *depth*.

**Clear trend across B and C:** raising either `trapPeak` or `hotTau` makes the collapse both earlier *and* deeper - they don't trade off independently near this threshold. The jump from "shallow sag" (4-10x, `hotTau`=1e-14) to "dramatic collapse" (200-380x, `hotTau`=2e-14) at the *same* `trapPeak` looks like a threshold/runaway effect (heating fills more traps → more field → more heating), not a smooth function of the levers - consistent with the positive-feedback trap/Te loop described in section 7.

**Proposed round D:** test whether *lowering* `trapPeak` while keeping the strong `hotTau`=2e-14 heating still crosses that runaway threshold, just later in Vd - `trapPeak` ∈ {6e18, 6.5e18, 7e18, 7.5e18, 8e18}, `hotTau`=2e-14 fixed, `trapLevel`=0.35, `trapSigma`=0.04, `hotEb`=0.5. 5 tasks.

**Round D (job 43298204, `results/20260925_lateOnsetD/`):** `hotTau`=2e-14, `trapLevel`=0.35, `trapSigma`=0.04, `hotEb`=0.5 fixed, Vd 0-4.05V/0.15V. All 5 tasks clean, no crashes.

| trapPeak | Result |
|---|---|
| 6e18 | peak 109.9 (Vd=1.65V) → 9.03 (Vd=2.1V), ~12.2x, recovers to 19.2 by 4.05V |
| 6.5e18 | peak 99.9 (Vd=1.5V) → 2.53 (Vd=1.8V), ~39.5x, creeps to 6.91 by 4.05V |
| 7e18 | peak 86.5 (Vd=1.2V) → 1.08 (Vd=1.65V), ~80x, creeps to 3.05 by 4.05V |
| 7.5e18 | peak 75.7 (Vd=1.05V) → 0.527 (Vd=1.5V), ~144x, creeps to 1.51 by 4.05V |
| 8e18 | peak 65.0 (Vd=0.9V) → 0.281 (Vd=1.35V), ~231x, creeps to 0.975 by 4.05V |

**Clean, monotonic trend confirming the round-C hypothesis:** lowering `trapPeak` from 8e18 to 6e18 (at fixed `hotTau`=2e-14) pushes the runaway-collapse onset later (1.05V → 1.8V) *and* weakens the eventual depth (231x → 12x) at the same time - the two don't decouple along this axis alone. Onset is now within range-of-sight of 3V but depth is trading away as we get there.

**Proposed round E:** push further in both directions at once - lower `trapPeak` *and* raise `hotTau` together, so the weaker charge gets more heating leverage once it does cross threshold. `trapPeak` ∈ {5e18, 5.5e18, 6e18} × `hotTau` ∈ {3e-14, 4e-14}, `trapLevel`=0.35, `trapSigma`=0.04, `hotEb`=0.5. 6 tasks. (`hotTau` this high is new territory for this search, though F itself ran at 1.3e-13 without issue - the round-C crash was at *high* `trapPeak` + `hotTau` together, not `hotTau` alone, so this direction - low `trapPeak`, higher `hotTau` - looks lower-risk.)

**Round E (job 43299061, `results/20260925_lateOnsetE/`):** `trapLevel`=0.35, `trapSigma`=0.04, `hotEb`=0.5 fixed, Vd 0-4.05V/0.15V. All 6 clean, no crashes.

| trapPeak | hotTau | Onset | Depth |
|---|---|---|---|
| 5e18 | 3e-14 | **~2.1-2.25V** (latest yet) | ~6.8x (118.9→17.5) |
| 5e18 | 4e-14 | ~1.8-1.95V | ~25x (113.5→4.53) |
| 5.5e18 | 3e-14 | ~1.8-1.95V | ~34.7x (111.3→3.20) |
| 5.5e18 | 4e-14 | ~1.5-1.65V | ~115x (102.6→0.890) |
| 6e18 | 3e-14 | ~1.5-1.65V | ~115x (98.5→0.857) |
| 6e18 | 4e-14 | ~1.35-1.5V | **~395x** (90.1→0.228) |

**Real breakthrough:** moving diagonally (lower `trapPeak`, higher `hotTau` together) beats moving along either axis alone - e.g. `trapPeak`=6e18/`hotTau`=4e-14 gives onset ~1.35-1.5V *and* ~395x depth, better on **both** counts than round D's `trapPeak`=8e18/`hotTau`=2e-14 (onset ~1.05-1.2V, ~231x). So `trapPeak` and `hotTau` aren't just redundant knobs on the same runaway threshold - going to lower charge + stronger (but still well below F's 1.3e-13) heating buys a better trade than either alone. Onset ~2.1-2.25V (at `trapPeak`=5e18/`hotTau`=3e-14) is the closest to 3V so far, though shallow there.

**Round F (revised, wider):** Ian asked for more combos per round (up to 18, near the 19-CPU QOS cap) instead of 6 at a time. `trapPeak` ∈ {3.5e18, 4e18, 4.5e18, 5e18, 5.5e18, 6e18} × `hotTau` ∈ {3e-14, 4e-14, 5e-14} - 18 tasks, `trapLevel`=0.35, `trapSigma`=0.04, `hotEb`=0.5. Covers the whole diagonal region at once instead of one row/column per round. (`trapPeak`=4e18 is F's own charge, but staying at `hotTau`≤5e-14 keeps well clear of F's `hotTau`=1.3e-13, which we know collapses at 0.3V.)

**Round F results (job 43300970, `results/20260925_lateOnsetF/`).** Note: 2 of the 18 cells (`trapPeak`=5.5e18 at `hotTau`=3e-14 and 4e-14) turned out to be accidental duplicates of round E - an error in the exclusion list, harmless (deterministic, matched round E exactly) but wasted 2 of the 18 slots.

**6 of 18 tasks (33%) crashed** with the identical signature to round C's crash - `munmap_chunk(): invalid pointer`, core dump, inside `FillStep`'s `device` solve, not a Newton-failed/NaN. Deleted ~7.5GB of core dumps (both HPG and local) after confirming the signature matched. Crashed cells: (4.5e18,4e-14), (5e18,5e-14), (5.5e18,5e-14), (5.5e18,6e-14), (6e18,6e-14), (6.5e18,3e-14) - mostly in the trapPeak 4.5-6.5e18 / hotTau 4-6e-14 band, i.e. right around the collapse transition itself. Several died before any collapse was visible in their partial CSV (inconclusive), others died just as the collapse was starting.

Non-crashed / informative results:

| trapPeak | hotTau | Onset | Depth |
|---|---|---|---|
| 3.5e18-4.5e18 | 3e-14 | none in range | <10% dip, not a real collapse |
| 4e18 | 5e-14 | ~2.25-2.4V | ~2.3x (124.0→54.8) - weak but the latest onset with any visible collapse |
| 4.5e18 | 3e-14 | ~2.4-2.55V | ~1.8x (124.2→68.8) - **latest onset of the whole search**, but barely a collapse |
| 4.5e18 | 5e-14 | ~1.95-2.1V | ~9.9x (117.9→11.9) |
| 6e18 | 5e-14 | ~1.05-1.35V | **~833x** (81.7→0.098) - close to F's depth, but early |
| 6.5e18 | 4e-14 | ~1.05-1.2V | **~761x** (78.4→0.103) - same story |

**Key tension surfacing clearly now:** the deepest collapses (700-830x, close to F's ~1000x) all sit at onset ~1.0-1.35V. Pushing onset out past ~2V (by further lowering `trapPeak`/`hotTau`) costs nearly all the depth - down to <10x, and past ~2.4V, down to <2x (barely visible). So far, in this `trapLevel`=0.35/`trapSigma`=0.04/`hotEb`=0.5 slice, later onset and F-like depth look like they're in real tension, not just requiring a finer grid - we may be up against something closer to a physical limit of this parameter combination rather than a search-resolution problem.

**Two open questions for Ian, flagging rather than guessing:**
1. **Physics direction:** we haven't touched `hotEb` (fixed at 0.5 throughout, F's value) or `trapSigma` (fixed at 0.04). Raising `hotEb` might restore depth at a given `trapPeak`/`hotTau` without needing more total charge (it directly lowers the effective trap level for a given Te), which could let onset stay late while depth recovers - untested. Alternatively this specific onset/depth target may just not be reachable with this trap geometry and needs accepting a softer match (e.g. onset ~2V with depth ~10-50x) as the practical target.
2. **Crash rate:** 33% of this round's compute was lost to the same solver abort, concentrated exactly in the region we most want to explore. Per the "solver-side fixes first" rule, a smaller `Vd_step` or more damping through the transition (rather than any trap/Poisson physics change) is the sanctioned next move, but changes the driver's behavior generally and is worth a decision rather than a silent change.

**Ian's answers:** try `hotEb` next; also add the solver-side fix before the next grid. `pulsedIV.tcl`'s damping is now a lever (`dampValue`, `info-exists`-guarded, default 0.10 = unchanged behavior) instead of hardcoded 0.10.

**Round G (job 43303128, `results/20260925_lateOnsetG/`):** solver fix (`Vd_step`=0.1 instead of 0.15, `dampValue`=0.05 instead of 0.10) applied together with a new `hotEb` sweep. Anchors (`trapPeak`, `hotTau`) picked from the "late onset, weak depth" cells in round F/E - A=4e18/5e-14, B=4.5e18/3e-14, C=4.5e18/5e-14, D=5e18/3e-14 - each crossed with `hotEb` ∈ {0.6, 0.7, 0.8, 0.9}, plus 2 extra at the best-depth control point 6e18/5e-14 (`hotEb` ∈ {0.6, 0.7}) to see how `hotEb` affects an already-deep case. 18 tasks, `trapLevel`=0.35, `trapSigma`=0.04 fixed.

---

## 11. Notebook and plotting

`figures.ipynb` runs on the workstation's system `python3` kernel (numpy/pandas/matplotlib/scipy; `jupyter_client` + `ipykernel` installed, `nbformat`/`nbconvert` not). Several older cells point at `/home/staffian/banjo-wombat/...` paths that no longer exist.

- To add results, append a cell and execute only it plus the setup cells (1: imports, 2: `flooxsRead`) through `jupyter_client`, so other cells' outputs are untouched. Keep the JSON as `indent=1` with a trailing newline.
- `figures/pulsedIV_F.csv` is plotted against `radPlot1` in the last cell.
- All plotting happens on the workstation, after `rsync`. Nothing on HPG touches the notebook.