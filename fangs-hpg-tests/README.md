# FANGS (flooxs-pyplot) tests on HiPerGator, October 2026

A one-off test campaign for Ian's other project, **flooxs-pyplot** (FLOOXS being turned into FANGS: Python front end,
compiled expression tape, threaded assembly). It is not HEMTRAD physics; it lives here because this repo is the one with
the HPG workflow. When it is done, the results go to the flooxs-pyplot checkout on the workstation and everything on HPG
is deleted.

Everything in HEMTRAD's `CLAUDE.md` section 2 applies.
- Check the connection first.
- **Ask Ian before every `sbatch` and every `scancel`.**
- Never run `flooxs` or a deck on a login node.
- Check `squeue -A ee1` before submitting.
- Poll with `sleep 300`.

Don't edit anything in flooxs-pyplot: neither the workstation copy `~/flooxs-pyplot`, which another agent works in, nor the HPG checkout. Don't commit there either. The one exception is the results folder that `fetch_results.sh` writes, `Test/Regression/hpg_results/20261015-fangs/`, which flooxs-pyplot gitignores. If something in flooxs-pyplot looks wrong, stop and report it.

## What is tested, and why

At flooxs-pyplot commit `28d8af2b` (`COMMIT` in `config.env`):

| Stage | What | Why |
|---|---|---|
| build | a fresh conda environment, the Tcl-free default build (`build/`) and the Tcl reference build (`build-tcl/`), `tools/fangs --selftest`, the whole `ctest` of both builds | first real test of flooxs-pyplot's `docs/runbooks/hipergator-setup.md` (written but never followed on HPG) |
| tier, set `tcl` | the seven `gan_hpg` cases on the Tcl deck, expression tape on (the default since 2026-10-13) | the D1 bake-in requires this tier on HPG with the tape on |
| tier, set `py` | the same cases from their Python ports | the Python ports have never run on HPG; they are the precondition for removing Tcl after 2026-10-19 |
| tier, set `tcl-dag` | the Tcl deck with `FLOOXS_TAPE=0` (the old evaluation path) | separates a tape effect from a compiler effect if the `tcl` set differs from the stored baselines |
| tier, set `tcl-thr4v` | `gan_quickIV` and `gan_trapF` with threaded assembly and `FLOOXS_ASSEMBLY_VERIFY=1` | threaded assembly on the 36,188-node device, checked bit for bit against serial assembly |
| compare | `tools/regress.py compare` for every pair | written to `results/compare/` |

The seven cases are the ones of the 2026-10-08 run (`kb/results/flooxs-pyplot-regression.md`): `gan_quickIV`,
`gan_calibIdVg`, `gan_trapF`, `gan_vg0`, `gan_vgm1`, `gan_sin` and `gan_rescue`. The node type and the slice size are the
same as then: `hpg-milan`, 16 cores, threads capped at 16. That keeps the timings comparable with the stored baselines.

## Files

| File | Where it runs | What it does |
|---|---|---|
| `config.env` | both | commit, paths, account/QOS/partition (the only file to edit) |
| `make_bundle.sh` | workstation | git bundle of flooxs-pyplot at `COMMIT`, copied to HPG and checked out (HPG has no GitHub credentials) |
| `env.sh` | HPG | creates once, then activates, the conda environment in `$BASE/env` |
| `build.slurm` | HPG batch | environment, both builds, selftest, ctest of both |
| `hpg_tier.slurm` | HPG array | 23 tasks: 7 `tcl`, 7 `py`, 7 `tcl-dag`, 2 `tcl-thr4v` |
| `compare.slurm` | HPG batch | all comparisons, plus a sha256 manifest of the results |
| `submit.sh` | HPG | submits one stage with the settings of `config.env` |
| `fetch_results.sh` | workstation | copies the results into flooxs-pyplot, checks the manifest, writes `REPORT.md` |
| `cleanup.sh` | workstation | deletes the HPG folder and the bundle (dry run unless `--yes`) |

Everything on HPG lives under one folder, `BASE=/home/ianstafford/blue/ee1/ianstafford/fangs-hpg-20261015`:
- `flooxs-pyplot/`, with its builds
- `env/` and `conda-pkgs/`
- `results/`

The group's other conda environments, `~/.condarc`, the stock FLOOXS and the older flooxs-pyplot checkout are not touched.

## Steps

### 0. Get this folder to HPG
On the workstation:
1. Commit and push this folder in HEMTRAD (`fangs-hpg-tests/`, plus a `progress.md` entry).
2. Check the connection: `ssh -O check hpg`.
3. On HPG, `git pull --ff-only` in the HEMTRAD checkout.

```bash
ssh -o BatchMode=yes hpg bash -l <<'REMOTE'
cd /home/ianstafford/blue/ee1/ianstafford/HEMTRAD && git pull --ff-only && ls fangs-hpg-tests
REMOTE
```

### 1. Bundle flooxs-pyplot and check it out on HPG
Workstation, HEMTRAD repo root:
```bash
fangs-hpg-tests/make_bundle.sh
```
It must end with `HPG checkout: 28d8af2b ...`. The bundle is about 135 MB; the copy runs over the `hpg` master connection.

### 2. Build and test (one batch job, about 1-2 h)
First ask Ian: "submit the FANGS build job (8 CPUs, up to 4 h, QOS ee1-b)?" Then, on HPG, from the HEMTRAD repo root:
```bash
ssh -o BatchMode=yes hpg bash -l <<'REMOTE'
cd /home/ianstafford/blue/ee1/ianstafford/HEMTRAD && fangs-hpg-tests/submit.sh build
REMOTE
```
The job creates the conda environment on its first run, which downloads about 1-2 GB from conda-forge.
- If the log says a package could not be fetched, the compute node cannot reach conda-forge. Create the environment on login7 instead, in the `hemtrad` tmux session: `cd .../HEMTRAD && bash fangs-hpg-tests/env.sh create`. Conda is allowed there, but flooxs is not. Then resubmit.

When it finishes, read `results/logs/build-<job>.out`. It must show:
- `cmake rc=0` and `make rc=0` for both builds;
- `selftest rc=0`;
- the two ctest summaries.

Expected: build `build` (Tcl-free) **86 tests**, `build-tcl` **165 tests**, all passing, with these exceptions:
- `Regression-Fast` and `Regression-Fast-Py` compare with baselines made on the workstation. A different compiler and BLAS can move the last digits, so a failure there with deviations near 1e-12 or below is expected; note the numbers.
- The STRUMPACK tests are not registered (no STRUMPACK here).

Any other failure: stop and report it with the test's output (the logs are in `results/ctest/`).

Also check `results/logs/cmake-summary.txt`. It should show `FANGS_WITH_TCL` OFF and ON, FFTW3 found, HDF5 found, UMFPACK and OpenMP.

### 3. The tier (one array job, about 1 h wall)
Before asking Ian, check `squeue -A ee1`. Each task takes 16 CPUs, and `submit.sh tier 6` runs at most 6 tasks at once (96 CPUs of `ee1-b`); lower the number if the group's sweeps need room. Ask Ian:
"submit the FANGS tier array (23 tasks x 16 CPUs on hpg-milan, at most N at once, up to 5 h each)?"

```bash
ssh -o BatchMode=yes hpg bash -l <<'REMOTE'
cd /home/ianstafford/blue/ee1/ianstafford/HEMTRAD && fangs-hpg-tests/submit.sh tier 6
REMOTE
```
Note the array job id. Then submit the comparisons, which wait for the array: `fangs-hpg-tests/submit.sh compare <array job id>`. Ask for this one in the same question as the array.

Expected times on hpg-milan, from 2026-10-08: about 2-11 min per case, and 22 min for `gan_rescue`. The `tcl-dag` and `tcl-thr4v` sets are slower: the latter assembles every load twice. After the array, check every task: `results/logs/tier-*.out` must end with `RC=0`. Look for OOM, timeouts, core files and `PULSED GAVE UP`, as in the sweep pattern.

### 4. Read the comparisons
In `results/compare/`, one file per pair:

| File | Expected |
|---|---|
| `tcl-vs-dag.txt` | **deviation 0** in all 7 cases (tape against the old path, same binary) |
| `thr4v-vs-tcl.txt`, `thr4v-verify-lines.txt` | outputs identical; every `diffs=` in the VERIFY lines is 0 |
| `py-vs-tcl.txt` | `ok` in all 7 (the Python port against the Tcl deck of this session; on the workstation they are identical) |
| `tcl-vs-baseline.txt`, `dag-vs-baseline.txt`, `py-vs-baseline.txt` | `ok` within each case's tolerance. The baselines came from an Intel build of an older commit, so small differences and slightly different Newton counts are possible; `dag-vs-baseline` shows what the compiler and code changes alone do |

Report every case that is not `ok`. Don't rerun to make a failure go away; a rerun is for a crash or a timeout only.

### 5. Bring the results back
Workstation, HEMTRAD repo root:
```bash
fangs-hpg-tests/fetch_results.sh
```
This copies `results/` into `~/flooxs-pyplot/Test/Regression/hpg_results/20261015-fangs/`, which flooxs-pyplot gitignores, so nothing is committed there. It checks every file against the HPG manifest and writes `REPORT.md` there. The flooxs-pyplot session reads that folder; tell Ian it is there.

### 6. Report
- **`progress.md`:** one entry with the commit, the job ids, the ctest totals, one line per comparison, and anything that failed.
- **KB:** a short update of `kb/results/flooxs-pyplot-regression.md`: a new dated section with the same facts and the results path.
- Commit and push, then send Ian a push notification: "FANGS HPG tests done: <one-line verdict>; results in ~/flooxs-pyplot/Test/Regression/hpg_results/20261015-fangs/REPORT.md; OK to delete the HPG copy?"

### 7. Delete (after Ian says yes)
Workstation, HEMTRAD repo root:
```bash
fangs-hpg-tests/cleanup.sh          # dry run: what would go, and that the fetched copy still matches the manifest
fangs-hpg-tests/cleanup.sh --yes    # deletes $BASE on HPG and the bundle on the workstation
```
It refuses while campaign jobs are still queued, while the fetched copy does not match the manifest, or if `BASE` is not a `fangs-hpg-*` folder.

Then:
- **This folder:** move it to `archive/fangs-hpg-tests/` (HEMTRAD's rule for superseded work) or delete it, whichever Ian prefers. Commit and push.
- **The older checkout:** `/home/ianstafford/blue/ee1/ianstafford/flooxs-pyplot` (da619c4c, 2026-10-08) is not deleted by the script. Ask Ian whether it can go too, and update `kb/workflow/repo-locations.md` if it does.

## If something goes wrong

| Symptom | Likely cause | What to do |
|---|---|---|
| `make_bundle.sh`: `commit ... not in` | flooxs-pyplot on the workstation is behind | ask Ian (do not pull or edit there yourself) |
| build job: conda cannot fetch packages | no internet on the compute node | `env.sh create` on login7 (step 2), resubmit |
| `cmake` cannot find nanobind | the environment is not active, or `nanobind` is missing | check `results/logs/versions.txt`; `pip install nanobind` inside the environment as a fallback |
| a ctest fails other than `Regression-Fast*` | a real problem, or an HPG difference | stop; report the test name and its output from `results/ctest/` |
| a tier task fails at once | environment (library, `PYTHONPATH`), or the build is missing | read `results/logs/tier-<job>_<task>.err`; `fangs._core` must import with the env's Python |
| `regress.py` refuses "other flooxs processes are running" | it should not: the tasks pass `--force` | report it |
| OOM in a task | `--mem 32gb` too small | raise `--mem` in `hpg_tier.slurm` for a rerun of that task only (ask Ian) |

Questions about flooxs-pyplot itself (what a test means, an unexpected result) go to Ian. The flooxs-pyplot session can
answer them from the results folder.
