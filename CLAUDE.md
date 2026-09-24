# CLAUDE.md

FLOOXS (Tcl) TCAD decks for an AlGaN/GaN HEMT, plus `figures.ipynb` for plots. See README.md for layout.

**Current goal:** reproduce the **radiation-induced current collapse** seen on a pulsed curve tracer. At Vgs=-2V, Id-Vd runs normally, then drops ~1000x at a small Vd (~0.4-0.5 V), then creeps up slightly with Vd. The creep is physical. There are no experimental CSVs for this in the repo.

---

## 0. Which machine am I on? (check first)

This repo is cloned on two machines and synced through git. Run `hostname` before doing anything else.

| | Workstation (Linux) | HiPerGator (`*.ufhpc`) |
|---|---|---|
| Repo location | `~/<repo>` | `/blue/<group>/<gatorlink>/<repo>` (never `$HOME`, quota is small) |
| How to run FLOOXS | directly: `flooxs <driver>.tcl` | **only through `sbatch`**, never on a login node |
| Parallel runs | **one at a time** (see §1) | many at once as a SLURM array (see §2) |
| Display | may have X; GUI lines may work | always headless: GUI lines **must** be stripped |
| FLOOXS source | `~/flooxs/src` | `<FILL IN: path>` |
| Python/notebook | system `python3` kernel | `<FILL IN: module load ... / conda env>` |

Machine-specific paths and modules belong in `env.hpg.sh` / `env.local.sh`, which `env.sh` sources by hostname. Don't hardcode them in drivers.

---

## 1. Running on the workstation

- Run `flooxs <driver>.tcl` from the repo root (paths like `figures/...` are relative).
- **Run one FLOOXS process at a time.** Simultaneous runs slow each other to a crawl. Chain runs in one sequential loop, and check `pgrep -x flooxs` first, because the user may be running one in the VS Code terminal.
- Kill runs by PID. `pkill -f "<pattern>"` also matches the shell that issued it.
- Headless runs segfault on `chart`/`plot1d`/`window`. For batch runs, copy the deck to a scratch dir and comment those lines out:
  `sed -i 's/^window.*//; s/^\(\s*\)chart /\1#chart /'`
- A driver point takes roughly 30-60 s. A 17-point `pulsedIV.tcl` sweep takes about 12-15 min.

---

## 2. Running on HiPerGator

### Hard rules
- **Never run `flooxs`, Python sweeps, or anything heavy on a login node.** Everything goes through `sbatch`. For short interactive tests, use `srun --pty` inside an allocation.
- Allocation: `--account=ee1`. **The QOS caps the group at 19 CPUs.** An array plus other running jobs must stay under that total, otherwise jobs sit in `QOSGrpCpuLimit` pending. Throttle arrays with `%N` (e.g. `--array=0-7%4`). Check `squeue -u $USER` before submitting.
- **Ask before `sbatch`** for anything bigger than a single job, and before any `scancel`. Only cancel your own job IDs, never `scancel -u`.
- Never edit files outside the repo and `/blue/<group>/<gatorlink>/`.

### Environment
FLOOXS runs from the Apptainer container. The Intel compiler is used for builds. The conda environment came from labmate stephencea. Every job script must set up the environment the same way, by sourcing `env.hpg.sh`:
```bash
# env.hpg.sh  — FILL IN exact values
module load intel/<ver>
module load conda  # or the correct module
conda activate <env>
export FLXSHOME=<path>
export PL_LIBRARY=<path>
FLOOXS="apptainer exec <container.sif> flooxs"
```
If a job fails right away with a library, `PL_LIBRARY`, or linker error, the environment is the cause, not the deck. Check `env.hpg.sh` before touching the Tcl.

### Sweeps = SLURM job arrays
Use the existing `trapPlot.slurm` pattern. `params.txt` has one line per array task, with the parameter bundle **pipe-delimited**. Task `$SLURM_ARRAY_TASK_ID` reads line N+1.
- Each task works in its **own copy** of the deck in `$SLURM_TMPDIR` or `results/<run>/task_<id>/`. Strip the GUI lines there (sed above). Never edit the repo copy in place.
- Pass levers by prepending `set` lines to the copied driver. This works because every lever has an `info exists` default.
- **Filenames from float parameters:** format them explicitly, e.g. `printf '%.2e'`, so you don't get `1.3000000000000001e-13` names. Also record the full parameter set inside each output CSV or a sidecar `params.json`.
- Resources (starting point): `--cpus-per-task=1`, `--mem=4gb`, `--time=00:45:00` for a 17-point `pulsedIV` sweep. OOM core dumps have happened before. If a task dies with signal 9 / `oom-kill` in the `.err` file, raise `--mem`. Don't change the deck.
- After submitting, poll with `squeue -u $USER` at reasonable intervals (≥1 min), then check every task's `.out`/`.err` for `Newton failed`, NaN, or a missing CSV. Report which tasks failed and why before plotting anything.

---

## 3. Git / sync between machines

- `git pull` at the start of a session. Commit and push at the end with a message naming the runs and lever values.
- **Commit:** decks, drivers, `.slurm` templates, `params.txt`, analysis scripts, small final CSVs used in figures (e.g. `figures/pulsedIV_F.csv`), `CLAUDE.md`.
- **Don't commit:** raw sweep directories, `.out`/`.err` logs, meshes, container images, build artifacts. These are in `.gitignore`. Move bulk results with `rsync`.
- `GaN_modelfile_masterD` has **CRLF** line endings and must keep them. `.gitattributes` should contain `GaN_modelfile_masterD -text`. Python edits must use `open(..., newline='')`, otherwise the whole file shows as changed.
- Commit before changing any model file (`GaN_modelfile_masterD`, `Poisson.tcl`), so the change can be diffed and reverted.

---

## 4. FLOOXS gotchas (learned the hard way)

- **Tcl word splitting in `solution ... val = (...)`:** `val = (($Ntrap) * $occ)` fails with "Ambiguous or unknown parameter *". Build the expression in a variable first: `set e "..."; solution ... val = ($e)`.
- **Constant data fields are folded into the equations at `device init`** (`src/BasePDE/ExprStore.cc:527`, `DataConst`). A field set with `sel z=0.0 name=F` becomes the literal 0 in any equation, so later `sel` updates are ignored. Initialize switch fields with a tiny spatial variation, e.g. `sel z=1.0e-30*(1.0+x*x) name=F`.
- **Redefining a `const` solution after `device init` doesn't reach the assembled equations.** `sel` sees the new definition, but Poisson doesn't. To switch behavior at runtime, use data fields as above.
- `sqrt(dot(DevPsi,DevPsi))` is |E| in V/cm (lengths are internally cm).
- Current in the CSVs is `abs(contact flux)*1e6` = mA/mm.

---

## 5. Trap model (Poisson.tcl)

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

**Don't change the physics to get convergence.** If a run diverges, first try solver-side fixes: a smaller Vd step, damping, or a better initial guess. Propose any change to trap physics, capture/emission, or Poisson terms to the user before making it, and explain why.

---

## 6. Levers

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

## 7. Drivers

- `pulsedIV.tcl`: curve-tracer model and the main tool for the collapse. The device rests at `Vg_meas` (traps at steady state), then Vd is swept with `FillStep` at each point (fill-only, no emission). Levers are at the top. It writes `figures/pulsedIV.csv` with columns Vd, Id, peak Te. **The repo copy still has the original defaults (0.68 / 0.3 / 1e-13), not the tuned values below.** In array jobs, write per-task CSVs (`results/<run>/pulsedIV_<tag>.csv`), not the shared `figures/pulsedIV.csv`.
- `stressFreeze.tcl`: pulsed-IV quiescent-stress model. It stresses at (VgQ, VdQ) with `HotStress`, freezes the traps, then measures Id-Vd at Vg=-2. Stress (-2,10) gave a 46% drop plus knee walkout (`figures/hotStressIV_*.csv`). The (-4,20) stress NaNs at Vd≈17.5 V during the ramp.
- `trapPlot.tcl` / `trapPlot.slurm`: older dynamic-trap driver (Id-Vd plus trap profile), and the array-job template used for the sensitivity analysis.

---

## 8. Tuning results

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

**Keep this table current.** Add every completed run with its lever values and a one-line result, and commit it.

**Next step:** run F with `hotTau` ∈ {0.6e-13, 0.5e-13, 0.4e-13} to move the onset to 0.4-0.5 V. On HiPerGator this is a 3-task array. On the workstation, run them sequentially. Then set the best values as the defaults in `pulsedIV.tcl`. Note that F's pre-collapse current is also off: 7.8 / 7.0 mA/mm at 0.1 / 0.2 V vs target 9.75 / 19.0, and it *falls* with Vd where the target rises. Pushing the onset out alone will expose that mismatch over more points. Check pre-collapse shape against target before declaring a match.

---

## 9. Notebook

`figures.ipynb` runs on a `python3` kernel (numpy/pandas/matplotlib/scipy; `jupyter_client` + `ipykernel` installed on the workstation, `nbformat`/`nbconvert` not installed). Several older cells point at `/home/staffian/banjo-wombat/...` paths that no longer exist.

- When adding results, append a cell and execute only it plus the setup cells (1: imports, 2: `flooxsRead`) through `jupyter_client`, so other cells' outputs are untouched. Keep the JSON as `indent=1` with a trailing newline.
- `figures/pulsedIV_F.csv` is plotted against `radPlot1` in the last cell.
- On HiPerGator, prefer a standalone plotting script, run inside a job or on the workstation after `rsync`, over editing the notebook. This avoids notebook merge conflicts between machines.
