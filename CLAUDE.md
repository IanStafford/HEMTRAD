# CLAUDE.md

FLOOXS (Tcl) TCAD decks for an AlGaN/GaN HEMT (HighK/HfO2-passivated, T-gate + field plate), driver scripts, HPG sweep templates, Python analysis scripts and `figures/`; `figures.ipynb` holds older paper plots. Superseded work is in `archive/` (static-mobility era: `archive/static_mobility/`, also branch `static-mobility`).

**Context:** model the **radiation-induced current collapse** seen on a pulsed curve tracer: at Vgs=-2 V, Id-Vd runs normally, then drops ~1000x at a small Vd (~0.4-0.5 V), then creeps up slightly with Vd (the creep is physical; no experimental CSVs for this in the repo). The deck is now calibrated against a measured HfO2-device transfer curve with the field-dependent mobility (§10.1).

**Current work:** with the calibrated field mobility, push the collapse onset to higher Vd (late-onset search, §10.3), classifying collapses as deep / medium / shallow (§10.0).

---

## 0. How this system is set up

- **You (the agent) run on Ian's workstation** (personal, off campus), inside `tmux`. Ian checks in from his laptop or phone via Remote Control. Assume he is **not watching** in real time.
- **HiPerGator (HPG) is reached only through `ssh hpg`**, which reuses a multiplexed master connection that Ian authenticates (Duo) each morning. You cannot answer Duo.
- **The repo exists in two places**, synced through git:
  - Workstation: `/home/staffian/HEMTRAD`, your working copy. Edit here.
  - HPG: `/home/ianstafford/blue/ee1/ianstafford/HEMTRAD`. Only `git pull` there. Never edit files on HPG directly.
  - GitHub: `IanStafford/HEMTRAD`. Branch `main` is current; branch `static-mobility` is the frozen pre-2026-10-01 tree.
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
cd /home/ianstafford/blue/ee1/ianstafford/HEMTRAD
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
- `--account=ee1`. QOS `ee1` caps at **19 CPUs** for the whole group; burst QOS **`ee1-b`** allows ~171 and is what the large sweeps use. Check `squeue -A ee1` (other group members count too) before submitting, and throttle arrays with `%N` (e.g. `--array=0-72%80`) so jobs don't sit in `QOSGrpCpuLimit`.
- **Ask Ian before any `sbatch`** unless he approved that specific run in the current task. **Ask before any `scancel`.** Only cancel your own job IDs, never `scancel -u`.
- Poll with `squeue -u $USER` every 5 minutes (Ian's standard) unless he says otherwise for a specific run: a background loop with `sleep 300`, never a busy loop.

### Sweep workflow (the standard pattern)
1. Commit the driver and the SLURM template on the workstation, then `git push`.
2. On HPG: `git pull --ff-only`.
3. Write `params.txt`: one line per array task, parameter bundle **pipe-delimited**. Task `$SLURM_ARRAY_TASK_ID` reads line N+1. Template: `pulsedIV_trapMapF_field.slurm` (older ones are in `archive/static_mobility/`).
4. Each task copies the driver into its own directory `results/<YYYYMMDD>_<tag>/task_<id>/` and prepends `set <lever> <value>` lines (every lever has an `info exists` default). It then strips the GUI lines (§4) and runs there. **Never edit the repo copy in place.**
5. Write per-task CSVs (`pulsedIV_<tag>.csv`), never the shared `figures/pulsedIV.csv`. Also write the full parameter set into a `params.json` next to each CSV.
6. Format float parameters explicitly in names (`printf '%.2e'`), so you don't get `1.3000000000000001e-13` filenames.
7. After the array finishes, check **every** task's `.out`/`.err` for `munmap`/`FLPS_panic`, OOM (`oom-kill`, signal 9), `DUE TO TIME`, `PULSED GAVE UP`, a missing CSV, and core files (delete them; 1-2 GB each). Use `grep`/`tail`, not `cat` on whole logs. Report failures before plotting.
8. `rsync -a --exclude='core*' hpg:/home/ianstafford/blue/ee1/ianstafford/HEMTRAD/results/<run>/ results/<run>/` to bring results back. Analyze and plot on the workstation.

Resources: `--cpus-per-task=1 --mem=4gb --time=03:00:00` for a 0-3 or 0-4 V `pulsedIV` sweep (most finish in 20-60 min; tasks bisecting through a collapse can take 2 h). If a task hits OOM, raise `--mem`; don't change the deck.

---

## 3. Running locally on the workstation

- `flooxs <driver>.tcl` from the repo root (paths like `figures/...` are relative).
- **Run one FLOOXS process at a time.** Simultaneous runs slow each other to a crawl. Check `pgrep -x flooxs` first, because Ian may be running one himself.
- Kill runs by PID. `pkill -f "<pattern>"` also matches the shell that issued it.
- A `pulsedIV.tcl` point takes roughly 20-60 s; a 0-3 V sweep 10-30 min. A trap-free `calibIdVg.tcl` transfer curve takes ~5 min (~25 min with contact resistance). Anything longer than one or two sweeps goes to HPG.
- When running several local tests, chain them in one background loop that checks `pgrep -x flooxs` before each, so they run consecutively.
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
- `GaN_modelfile_masterD`, `Metal.tcl` and `Continuity.tcl` have **CRLF** line endings and must keep them (there is no `.gitattributes`; git stores them as-is). Edit them from Python with `open(..., newline='')` and check `file <name>` afterwards; a plain `open()` rewrite converts every line.
- Commit **before** changing any model file (`GaN_modelfile_masterD`, `Poisson.tcl`, `GaN.tcl`, `AlGaN.tcl`, `Metal.tcl`, `Insulator.tcl`, `rfdevice*.tcl`).
- Superseded work goes to `archive/<name>/` with a README (see `archive/static_mobility/`), not deleted.

---

## 6. FLOOXS gotchas (learned the hard way)

- **Tcl word splitting in `solution ... val = (...)`:** `val = (($Ntrap) * $occ)` fails with "Ambiguous or unknown parameter *". Build the expression in a variable first: `set e "..."; solution ... val = ($e)`.
- **Constant data fields are folded into the equations at `device init`** (`src/BasePDE/ExprStore.cc:527`, `DataConst`). A field set with `sel z=0.0 name=F` becomes the literal 0 in any equation, so later `sel` updates are ignored. Initialize switch fields with a tiny spatial variation, e.g. `sel z=1.0e-30*(1.0+x*x) name=F`.
- **Redefining a `const` solution after `device init` doesn't reach the assembled equations.** `sel` sees the new definition, but Poisson doesn't. To switch behavior at runtime, use data fields as above.
- `sqrt(dot(DevPsi,DevPsi))` is |E| in V/cm (lengths are internally cm).
- Current in the CSVs is `abs(contact flux)*1e6` = mA/mm.
- **The `munmap_chunk(): invalid pointer` crash is a teardown artifact, not the real failure** (diagnosed 2026-09-27, reproduced locally under gdb on task 64 of job 43373001; same failure point on both builds). Chain:
  1. Newton diverges at the collapse transition inside `FillStep`'s `device` (RHS norm → ~1e12). An expression evaluates to NaN/inf and `Values::TestProb` (`BasePDE/Values.cc:207`) throws.
  2. The throw unwinds mid-assembly. The solver's member queues `eq0`/`eq1` (`BasePDE/Solver.h:219`) were loaded with every node/element via `ElementQueue::Build()`, which sets `InQueue`, and were only partly drained. Nothing clears them on the exception path.
  3. `DevController` catches the string (`device/DevControl.cc:167`, prints `Caught Exception!`), `device` returns a Tcl error, the script aborts, and Tcl calls `GlobalExit` (`flooxs.cc:727`).
  4. `GlobalExit` does `delete fslist` (never NULLed) → mesh teardown → a Node still flagged `InQueue` → `Element::~Element` calls `FLPS_panic("Fudge")` (`field/Element.cc:119`) → `FLPS_panic` runs Tcl `exit 1` → re-enters `GlobalExit` → deletes `fslist` again. It recurses ~3,300 times (`too many nested evaluations`) with a double free, which glibc reports as `munmap_chunk`. That's also why each crash leaves a 1-2 GB core.
  - So "crash" and "Newton iteration-limit stall" are **the same numerical failure** (non-convergence at the runaway trap-filling transition) with two outcomes: oscillate → iteration limit → clean-ish exit; diverge → NaN → crash. That's why it's trajectory-dependent and only partly helped by damping or a smaller Vd step.
  - **A bare `catch {device}` + retry is NOT safe:** `Solver::InitializeAssembly` (`Solver.cc:433`) refills `eq0`/`eq1` without clearing them, and `Build()` doesn't check `InQueue`, so stale elements from the failed solve would be assembled twice, silently. **But `catch` + `device restore` IS safe on the existing builds (local and HPG):** `device restore` → `DevController::Restore()` copies PREV → CURR and calls `Solver::Restore()`, which clears `eq0`/`eq1`. So call `device store` before each attempt and `device restore` after any failure. Tested 2026-09-27: catch + store/restore of the solution and `TrapFrozen`/`TeTrap` with Vd-step bisection (now built into `pulsedIV.tcl`) takes task 64 past its NaN at 0.4 → 0.5 V with one bisection and completes to 3 V, with identical results on the stock and patched binaries.
  - **FLOOXS fix** (local only): branch `crash-fix` in worktree `~/flooxs-crashfix`, built in `~/flooxs-crashfix/build/flooxs`. It clears the queues in `InitializeAssembly` and in the solve catch blocks, and makes `FLPS_panic`/`GlobalExit` non-reentrant. An unrecovered NaN then ends in a clean Tcl error with no core dump, and results are otherwise identical. Not installed, not on HPG, not sent upstream. Exported as `flooxs-crashfix.patch` (untracked, repo root) for review.

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
| `mobModel` | field | electron mobility: `field` (Farahmand low field + Heller high field; calibrated, §10.1) or `static` (constant 600, used for everything in `archive/static_mobility/`). Default changed to field on 2026-10-01 |
| `trapEn` | 0 | enable traps |
| `trapPeak` | 4e18 | peak density (cm⁻³) of the 2D Gaussian |
| `trapMeanX`, `trapMeanY` | 0.0, 0.20 | center in µm (x = depth; 0 = AlGaN top, 0.015 = 2DEG; y: gate drain edge = 0.125) |
| `trapSigma` | 0.025 | spatial sigma (µm) |
| `trapSigmaY` | unset | optional lateral sigma (µm) for an anisotropic Gaussian; when set, `trapSigma` is the depth (x) sigma only. Unset = the isotropic expression, unchanged |
| `trapShape` | gauss | spatial profile: `gauss` (2D Gaussian, uses `trapMeanX/Y`, `trapSigma`) or `cone` (below). Each shape is a proc `TrapConc_<name>` in `GaN_modelfile_masterD` returning a FLOOXS expression; add new ones (e.g. a TRIM profile) the same way |
| `coneLen`, `coneAngle` | 0.1, 30 | cone: depth extent below the apex (µm), half-angle (deg). Apex at (`trapMeanX`, `trapMeanY`), axis along +x (into the device) |
| `coneW0`, `coneEdge` | 0.01, 0.01 | cone: half-width at the apex (µm), erf edge softness (µm). Uniform density `trapPeak` inside. The mesh is ~10-20 nm laterally near the field plate and ~50 nm farther into the access region, so the narrow apex is barely resolved there |
| `trapLevel`, `trapWidth` | 0.68, 0.1 | depth below Ec and energy FWHM (eV) |
| `insTrapSign` | 0 | trap charge in the insulators (Nitride, HighK): 0 none; −1 the same trap density fully filled (−q·N); +1 fixed positive (+q·N). Static, since no carriers/Qfn are solved there, so no Fermi or hot-electron filling (`InsTrapCharge` in `Poisson.tcl`) |
| `polCharge` | 7.0e12 | net AlGaN/GaN interface (polarization) charge, cm⁻² (`GaN_modelfile_masterD`); sets the 2DEG density |
| `phiB` | 1.65 | effective gate / field-plate barrier vs Nitride Ec, eV (`Metal.tcl`); an empirical Vth parameter (implied work function 2.6 eV). Enters only as `G − phiB`, so it shifts Id-Vg rigidly in Vg |
| `surfCharge` | unset | net fixed charge at the AlGaN/SiN surface, cm⁻² (surface donors in excess of the AlGaN surface polarization). Raises the access-region 2DEG (~25% efficiency) far more than the gate region |
| `hotEb` | 0.3 | capture barrier (eV); larger = earlier, deeper collapse; 0 = no hot-electron effect |
| `hotTau` | 1e-13 | energy relaxation time (s); larger = hotter = earlier collapse |
| `hotMu`, `hotVsat` | 600, 1.9e7 | used only for Te |

---

## 9. Drivers

- `pulsedIV.tcl`: curve-tracer model and the main tool for the collapse (field mobility by default). **Since 2026-09-27 each Vd point is attempted in `catch`; on a solver failure (Newton limit or NaN) it restores the last converged solution + trap memory (`device store/restore`, `TrapFrozen`/`TeTrap`) and bisects the Vd step** (levers `retryDepth`=5, `retrySubFill`=1 = full `FillStep` at bisection substeps, 0 = plain solve there). Output is identical when nothing fails; `PULSED ... retries=N` and `RETRY ...` lines log any retries, `PULSED GAVE UP` if a point can't be reached (the run then stops cleanly, no crash). The device rests at `Vg_meas` (traps at steady state), then Vd is swept with `FillStep` at each point (fill-only, no emission). Levers are at the top. It writes `$ivCSV` (default `figures/pulsedIV.csv`) with columns Vd, Id, peak Te. Its trap defaults are the model file's (0.68 eV / `hotEb` 0.3 / `hotTau` 1e-13), not Run F: sweeps always set the levers explicitly. **Run F** = `trapPeak` 4e18, `trapSigma` 0.04, `trapLevel` 0.55, `hotEb` 0.5, `hotTau` 1.3e-13, at x=0, y=0.2 µm (the standard reference set).
- **Device deck lever** (2026-10-01): `pulsedIV.tcl` sources `$deviceDeck` (default `rfdevice.tcl`). `rfdevice_SiN.tcl` is the same structure with every HighK region (εr 35) replaced by Nitride (εr 6.3): SiN-only passivation, same mesh.
- `calibIdVg.tcl`: trap-free transfer curve for calibration (§10.1): Vd ramp to `Vd_cal` (10 V), gate +1 → −4 V; optional lumped `Rs_contact`/`Rd_contact` (Ω·mm). Scored by `calib_score.py`, plotted by `plot_calib.py`.
- `stressFreeze.tcl`: quiescent-stress model: stress at (VgQ, VdQ) with `HotStress`, freeze the traps, measure Id-Vd at Vg=-2. (Static era: stress (-2,10) gave a 46% drop plus knee walkout; (-4,20) NaNs at Vd≈17.5 V.) Not rerun with field mobility.
- `trapPlot.tcl`: older dynamic-trap driver (Id-Vd plus trap profile).
- Analysis: `analyze_onset.py` (collapse class/onset per device, §10.0), `analyze_trapMapSets.py [run tag]` (3D depth/suppression surfaces), `analyze_mobCompare.py` (static vs field maps).

---

## 10. Results (field mobility, 2026-10-01 onward)

Static-mobility results (2026-09-23 to 10-01: Run F tuning, late-onset search, placement and trap maps, cone shapes, critical strike, insulator traps, deep traps, HighK vs SiN) are archived verbatim in `archive/static_mobility/RESULTS.md`; the lessons that still matter are in §10.4, the model caveats in §10.5.

### 10.0 Collapse classification (Ian, 2026-10-01)

For qualitative analysis, classify a collapse by its **largest single-step loss**, 1 − Id(Vd_n)/Id(Vd_n−1), over the sweep:
- **deep:** > 95% of the previous-step current lost in one step;
- **medium:** 50-95%;
- **shallow:** < 50%.

The collapse onset is the Vd of the **first** step that reaches the class threshold (>95% deep, ≥50% medium; for shallow, the largest step). Changed 2026-10-02: "Vd of the largest step" misreported two-step collapses (e.g. 99.92% at 1.5 V, then 99.95% from the already-collapsed level at 2.3 V); re-scoring round 1 moved 2 of 72 onsets 0.1 V earlier. Devices below 10% of the trap-free current at Vd = 0.1 V are "off at rest" (a threshold shift, not a collapse). Runs that stop early (`PULSED GAVE UP`) with no recorded collapse are **"stalled"**, onset = the Vd they couldn't reach (added 2026-10-02; before that they were wrongly counted as shallow). `analyze_onset.py` implements this.

### 10.1 Transfer-curve calibration vs the HfO2 device (field mobility)

Target: `figures/rfDeviceHFO2_Experimental.csv` = raw `figures/RF_100nmHfOx_IdVgs_Example1.xlsx`: Id-Vgs at **Vds = 10 V**, 25 °C, 100 nm HfO2, standard FP. `Ids` is in **A for a 200 µm device** → mA/mm = A·1e3/0.2 (634 mA/mm at Vg=0, 810 at +1 V). FLOOXS flux is per µm of depth (×1e6 = mA/mm). Gate leakage ≤2e-3 mA/mm; the off-state floor (~0.075 mA/mm) is drain leakage and is not modelled (Ian: qualitative OFF vs ON only). Driver `calibIdVg.tcl` (trap-free, `mobModel field`, Vd ramp then Vg +1 → −4; levers `Vd_cal`, `Rs_contact`/`Rd_contact` lumped contact resistance, `deviceDeck`), scoring `calib_score.py` (aligns by a rigid Vg shift = ΔphiB), plot `plot_calib.py` → `figures/calib_IdVg.png`.

**Result: the existing deck with `mobModel field` is the calibration; no parameters changed.** Id within ±2.4% from Vg −2.6 to +1 V (rms 1.9% to 0 V, 1.8% to +1 V); −2.0 V: −1.5%; 0 V: 649 vs 634; +1 V: 802 vs 810. Threshold region: +16% at −2.8 V, −15% at −3.0 V (model turns on slightly more steeply). Static mobility (600) is 10% rms with the wrong shape. Curves: `figures/calib_IdVg_{field,static,alt_pol8e12_Rc0.6}.csv`.

Known miss: **gm above +0.5 V collapses** (88 vs 160 mS/mm at +1 V), while Id there still matches. Diagnosed at Vd=10 V: no spill-over into the AlGaN; the source access region (2DEG ~5e12 cm⁻², drops 1.5 V at +1 V) and the strip under the T-gate head overhang (1.5-3.7e12, the head couples through the HighK as a weak second gate) quasi-saturate (access-resistance gm roll-off, Palacios et al. TED 2006). Tried, all physically motivated, all trade the turn-on/−2 V region for forward-bias gm:

| change (phiB refit for Vth) | rms to 0 V | at −2 V | gm −1/0/+1 (exp 220/196/159) |
|---|---|---|---|
| none (adopted) | 1.8% | −2% | 232/199/88 |
| polCharge 9e12 / 1.1e13 | 13% / 22% | | 286/262/222, 326/312/281 |
| polCharge 8e12 + Rc 0.6 Ω·mm, phiB 2.07 | 4.5% | −5% | 223/205/170 |
| polCharge 7.5e12 + Rc 0.35, phiB 1.86 | 3.1% | −4% | 225/203/135 |
| polCharge 9e12 + Rc 1.0, phiB 2.50 | 6.8% | −6% | 216/207/188 |
| surfCharge 4e12 (Rc 0) | 22% | | 325/313/293 |
| surfCharge 1.5e12 + Rc 0.6, phiB 1.86 | 3.2% | −4% | 231/219/189 |
| 2DEG mobility excluding buffer doping (~1900) | 36% | | |

More channel charge removes the access bottleneck but raises intrinsic gm, and the series resistance needed to trim it softens the turn-on. Kept the unmodified deck because it is best in the required range and at Vg = −2 V, where all trap studies run. A run at the fitted phiB confirmed the rigid-shift approximation (field plate effect < 0.1%). New levers (defaults = old behaviour): `polCharge`, `phiB`, `surfCharge`.


### 10.2 Run F trap map with the calibrated field mobility

Ian: redo the conc/level surfaces with field mobility; Run F (4e18/0.55 eV) only. Job 44342967 (51 tasks, `ee1-b`, `pulsedIV_trapMapF_field.slurm`), `results/20261001_trapMapF_field/`: the static-era 10f grid (5 depths × 10 positions, Vd 0-3 V, Run F hot-electron levers; `archive/static_mobility/RESULTS.md` §10f) with `mobModel field`. No crashes; 3 source-side tasks (y −0.4, x 3.75/7.5/11.25 nm) gave up cleanly after their collapse (at Vd 2.6/1.4/1.1 V), so their onset and depth are known but no 3 V value. Figures: `figures/trapMapF_field_tp4e+18_tl0.55.png` (same 3D pair as the static map, via `analyze_trapMapSets.py <run> <tag>`), `figures/mobCompare_F_{3d,compare}.png` (`analyze_mobCompare.py`, each model vs its own trap-free device).

| | static (archived 10f) | field (calibrated) |
|---|---|---|
| trap-free Id at 0.1 / 1 / 3 V | 10.0 / 90.1 / 146.9 | 17.6 / 136.9 / 177.2 mA/mm |
| regimes (of 50) | collapse 35, off at rest 15 | collapse 31, off at rest 19 |
| collapse onset | 0.2-0.5 V, later away from the gate | 0.2 V almost everywhere (0.2-0.3 at 2.4 µm) |
| collapse depth vs trap-free | 10^4.1-10^5.8 | 10^4.9-10^7.1 (~1 decade deeper) |
| at-rest Id / trap-free | 0.71-0.87 | 0.04-0.63 |

- **Field mobility gives an earlier, deeper and more uniform collapse.** The static-era lateral onset trend (later with distance from the gate) nearly disappears.
- The 4 extra "off at rest" devices are 11-15 nm deep at the field-plate edge (y 0.285-0.5 µm), at 0.04-0.05 of trap-free, just under the 0.1 cut, so borderline rather than a new regime. The gate region (−0.125…0.125) is off at rest in both.
- Suppression at 3 V is ~1 decade larger with field mobility in the access region and near the source; similar under the gate; slightly smaller at y=0.5 µm.
- **Caveat:** part of the larger ratios is the higher trap-free baseline (low-field mobility ~1160 vs 600 cm²/V·s gives 75% more current at low Vd). The calibration (§10.1) only checked saturation at Vds = 10 V; the low-Vd linear region where these collapses happen is not validated (needs measured Id-Vd).

---

### 10.3 Late-onset search with field mobility (in progress)

Ian (2026-10-01): push the collapse out further using the static-era methods (§10.4). Round 1: job 44359813, `pulsedIV_onsetField1.slurm` / `params_onsetField1.txt`, `results/20261002_onsetField1/`: Run F position (x 0, y 0.2 µm, σ 0.04), `trapLevel` {0.35, 0.45, 0.55} × `trapPeak` {2, 3, 4}e18 × `hotTau` {1e-14, 3e-14, 6e-14, 1.3e-13} × `hotEb` {0.5, 0.85}, Vd 0-4 V / 0.1 V, + trap-free reference (73 tasks). Analyze with `python3 analyze_onset.py results/20261002_onsetField1 onsetField1`.

**Round 1 result** (73/73 clean, 0 retries; `figures/onsetField1.png`): deep 15, medium 12, shallow 44 (mostly no real collapse), off 1. Latest **deep** collapse **1.0 V** (0.35 eV / 4e18 / `hotTau` 3e-14 / `hotEb` 0.85, 97.6% step loss from 85.6 mA/mm); latest medium also 1.0 V (0.35 / 4e18 / 6e-14 / 0.5). Trends: ≥4e18 is needed for deep/medium (2e18 barely collapses); the shallower level collapses later; lower `hotTau` delays onset (0.5 → 0.7 → 1.0 V for 1.3e-13 → 6e-14 → 3e-14 at 0.35/4e18/0.85) until it turns shallow at 1e-14; `hotEb` 0.85 vs 0.5 deepens without much onset change. Much harder to delay than with static mobility (static reached ~2.2 V).

Round 2 (cancelled job 44363616 at Ian's request, **resubmitted 2026-10-02 as job 44433016**), `pulsedIV_onsetField2.slurm`, `results/20261002_onsetField2/`: `trapLevel` {0.30, 0.35, 0.40} × `trapPeak` {4, 5, 6}e18 × `hotTau` {1, 1.5, 2, 3}e-14 × `hotEb` {0.85, 1.0} (more charge and a stronger barrier to keep depth at lower `hotTau`), + reference.

**Round 2 result** (73/73 clean, 5 retried; `figures/onsetField2.png`): deep 53, medium 14, shallow 5. Latest **deep** collapse **1.4 V** (0.30 eV / 5e18 / `hotTau` 1.5e-14 / `hotEb` 0.85, 98.8% from 76 mA/mm); latest medium 1.8 V (0.30 / 4e18 / 1.5e-14 / 1.0). Shallower level is best (0.30 > 0.35 > 0.40 at every point); onset rises along the diagonal lower `hotTau` + more `trapPeak` (charge keeps it deep); `hotEb` 1.0 vs 0.85 is ~0.1 V earlier. Some deep collapses start from an already-sagging current (e.g. pre 11.6 mA/mm), so check pre-collapse Id too.

**Local position check** (round-1 best set at y = 2.0 µm): deep collapse moved 1.0 → 1.5 V, so position is still an onset lever with field mobility (10.2's Run F collapses at 0.2 V everywhere, hiding it).

Round 3: job 44435511, `pulsedIV_onsetField3.slurm` / `params_onsetField3.txt` (`trapPeak|trapLevel|hotTau|hotEb|trapMeanY`), `results/20261002_onsetField3/`: 8 sets (round-2 best at 0.30 eV, plus 0.25 eV with 5-7e18 / `hotTau` 1-1.5e-14) × `trapMeanY` {0.2, 0.5, 0.725, 1.0, 1.5, 2.0, 2.4} µm, + reference. Analyze: `python3 analyze_onset.py results/20261002_onsetField3 onsetField3 trapLevel hotEb trapMeanY trapPeak` (the 8 sets are unique in level × hotEb × trapPeak).

**Round 3 result** (57/57 finished, 0 crashes, but **19 stalled**: `PULSED GAVE UP` at 1.8-4.0 V, mostly at full current, i.e. the runaway continuation can't follow (§10.5); 9 of them at ≥ 2.7 V, so the true latest onset may be later than 2.3 V; `figures/onsetField3.png`): deep 24, medium 5, shallow 8, stalled 19. **Latest deep collapse 2.3 V**: 0.30 eV / 5e18 / `hotTau` 1e-14 / `hotEb` 1.0 at **y = 1.0 µm**, 99.4% in one step from 166 mA/mm (≈ trap-free, ~170 mA/mm), i.e. the device runs normally up to the collapse. Runner-up: 0.25 eV / 6e18 / 1.5e-14 / 1.0 at y = 1.5 µm, deep at 2.1 V from 164 mA/mm. Medium 2.3 V (0.25 / 5e18 / 1e-14 / 0.85 at y 0.2, 65%).
- **Position has an optimum:** for most sets the onset rises from y = 0.2 to ~1.0-1.5 µm (e.g. 0.30/1.0/5e18: 1.5 → 1.7 → 2.1 → 2.3 V at y 0.2/0.5/0.725/1.0), then the collapse turns shallow at y ≥ 1.5-2.0 (traps too far from the hot spot to run away).
- Pre-collapse current: the best late collapses start from 150-166 mA/mm (near trap-free); some deep ones start from an already-sagged current (e.g. 0.30/0.85/5e18 at y 0.725: 8 mA/mm), so they are less clean.

Round 4: job 44440027, `pulsedIV_onsetField4.slurm` / `params_onsetField4.txt`, `results/20261002_onsetField4/`: refine around the 2.3 V device: 0.30 eV / `hotEb` 1.0, `trapPeak` {4.5, 5, 5.5}e18 × `hotTau` {0.8, 1, 1.2}e-14 × `trapMeanY` {0.85, 1.0, 1.15, 1.3, 1.5, 1.7}, plus 0.25 eV / 1.5e-14 / 1.0 at {5.5, 6, 6.5}e18 × y {1.3, 1.7}; + reference (61 tasks). Analyze: `python3 analyze_onset.py results/20261002_onsetField4 onsetField4 trapLevel hotTau trapMeanY trapPeak`.

### 10.4 Lessons from the static-mobility era (details in `archive/static_mobility/RESULTS.md`)

These were all found with constant mobility 600; field mobility collapses earlier and deeper (§10.2), so treat numbers as indicative.
- **Run F** (4e18 / σ 0.04 / 0.55 eV / `hotEb` 0.5 / `hotTau` 1.3e-13 at y 0.2) gave the best `radPlot1`-like shape (collapse at 0.3 V, creep after). A surface blob at y = 2.0 µm matched `radPlot1`'s 0.5 V onset (§10c).
- **Onset and depth are coupled** (§10b): more `trapPeak`, `hotTau` or `hotEb` all give an earlier *and* deeper collapse. Delaying onset while keeping depth needed diagonal moves: lower `trapPeak` with higher `hotEb`/`hotTau`, and a shallower `trapLevel` (0.35 eV). `hotEb` is the strongest depth lever. Best static late onset: 3e18 / σ 0.04 / 0.35 eV / `hotEb` 0.85 / `hotTau` 6e-14 → onset ~2.2 V, ~2000x.
- **Regimes** (§10e): deep levels (0.75 eV) at ≥4e18, or 0.55 eV at 8e18, fill at rest and switch the device off (threshold shift). The hot-electron collapse lives in a band: 4e18/0.35, 4e18/0.55, 8e18/0.35. 2e18 only matters under the gate.
- **Position** (§10c-f, §10j-k): the gate region (y −0.125…0.125) is always the most damaging (off at rest). Traps nearer the 2DEG are worse. Only trap density within ~15-25 nm of the 2DEG matters: deeper blobs (or the deep part of a cone) do nothing (§10g, §10k).
- **Insulator traps** (§10j): fully filled (−q·N) Nitride traps turn every near-surface blob off at rest; positive (+q·N) ones cancel the collapse; neutral ones restore it. The passivation fill fraction is the key unknown.
- **HighK vs SiN** (§10l): identical collapse at Vd ≤ 3 V (the only hot spot is the gate drain edge, under ~5 nm of nitride). HighK does flatten the T-gate-head/field-plate field, but only above ~5 V. `fieldpeak.tcl` (archived) set HighK εr before sourcing the model file, so its "SiN" run was HighK.
- **Critical strike** (§10i): at 1e7 ions/cm², a 2D critical strike is near-certain, but in 3D a single cascade damages only a few % of the 200 µm gate width.

### 10.5 Known model caveats

- **Mesh** (static §10h, still applies): lateral spacing is 5 nm at the gate, 10-20 nm at the field plate, 25-40 nm from y ≈ 0.725 µm to the drain. Narrow traps there are unresolved (cones in the access region were mesh artifacts); access-region Gaussian results are qualitatively robust but onset can shift ~0.1 V and pre-collapse current halve on a 4 nm mesh. Refine (`line y` at `trapMeanY`) before shape or TRIM work.
- **Calibration covers saturation only** (Vds = 10 V); the low-Vd linear region where collapses occur is unvalidated, and gm above +0.5 V is not reproduced (§10.1). Off-state drain leakage isn't modelled.
- **Not modelled:** self-heating (Temp is constant 300 K), dielectric fixed/interface charge by default (`surfCharge` lever exists, unset), dynamic surface or dielectric trapping (insulator traps are static, `insTrapSign`), non-local electron heating (Te is local-field).
- **Numerics:** a few devices still stall at the runaway even with 7 bisection levels and heavy damping (a discontinuous jump that Vd continuation can't follow); they stop cleanly (`PULSED GAVE UP`) and are reported as incomplete.

---

## 11. Notebook and plotting

`figures.ipynb` runs on the workstation's system `python3` kernel (numpy/pandas/matplotlib/scipy; `jupyter_client` + `ipykernel` installed, `nbformat`/`nbconvert` not). Several older cells point at `/home/staffian/banjo-wombat/...` paths that no longer exist.

- To add results, append a cell and execute only it plus the setup cells (1: imports, 2: `flooxsRead`) through `jupyter_client`, so other cells' outputs are untouched. Keep the JSON as `indent=1` with a trailing newline.
- Cells that load static-era outputs (`pulsedIV_F.csv`, `hotStressIV_*`, `mobility_*`, `rfDeviceHFO2_Simulated.csv`) now need the `archive/static_mobility/figures/` prefix; `figures/pulsedIV_F.csv` was plotted against `radPlot1` in the last cell.
- All plotting happens on the workstation, after `rsync`. Nothing on HPG touches the notebook.