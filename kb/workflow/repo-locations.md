---
title: Repo and tool locations
tags: [workflow, reference]
---
# Where things live

## Repo layout (since 2026-10-12)
| Folder | Contents |
|---|---|
| `model/` | model files and device decks, sourced together: `rfdevice.tcl` (HighK/HfO2), `rfdevice_SiN.tcl`, `rfdevice3d.tcl` (3D slice, [[3d-plan]]); 3 CRLF files |
| `drivers/` | Tcl drivers ([[drivers]]): `radIV.tcl` (all HPG runs since 2026-10-23), `seeIV.tcl`, `pulsedIV.tcl` (Sep-Oct curve tracer), `calibIdVg.tcl`, `fieldPlate.tcl`, `render3d_build.tcl`; `drivers/trim/` holds the SRIM TRIM input files ([[trim]]) |
| `sweeps/` | `radIV.slurm`, the Oct-era `pulsedIV_*.slurm` records and every study's `params_*.txt` ([[sweep-pattern]]) |
| `analysis/` | Python analysis, plotting and the params generators `genRadStudy.py` / `genRad3d.py` ([[analysis-scripts]]) |
| `data/` | tracked: the measured HfO2 Id–Vg calibration curve (`rfDeviceHFO2_Experimental.csv`, raw `.xlsx`), TRIM track tables `data/trim/*_track.json` (model input), FANGS 3D curves `data/rad3d_fangs/` (model output). Local only and gitignored: the measured radiation data `data/rad_y2/`, `data/rad_y3/` ([[git-conventions]]) |
| `figures/` | outputs: the root holds frozen October outputs, each study since November has its own folder (`figures/README.md`) |
| `bin/` | workflow helpers: `hpg_reconnect.sh` ([[hpg-workflow]]), `trim_run.sh` ([[trim]]) |
| `dashboard/` | artifact sources and web figures ([[dashboard]]) |
| `kb/` | this KB |
| `archive/` | superseded work, each folder with a README: `static_mobility/` (HEMTRAD static-mobility era; also `stressFreeze.tcl`, archived 2026-11-20, and `trapPlot.tcl`, `analyze_mobCompare.py` and `figures.ipynb` ([[notebook]]), archived 2026-11-21); `energy_balance/` (the eTempDebug tools and `plot_eTemp.py`, [[energy-balance]]); `trim_smoke/` (the 20-ion TRIM inputs, [[trim]]); `analysis_dayfigs/` (one-off dashboard and deck figure scripts, [[analysis-scripts]]); `fangs-hpg-tests/` and `fangs-hpg-first-run/` (FANGS HPG test campaigns, not HEMTRAD physics) |
| `results/` | raw sweep results (gitignored) |

Before 2026-10-12 everything sat flat in the root; `progress.md` and old commits use those paths. `README.md` summarises the layout.

## Machines and checkouts

**Two different places on HPG** (checked 2026-11-04): `/home/ianstafford/blue/ee1/ianstafford` is an ordinary folder in the home directory (NFS, 40 GB quota, 12 GB used), not a link to `/blue`. `/blue/ee1/ianstafford` is the real `/blue` storage. The HEMTRAD checkout, its worktrees, every sweep's `results/` and stock FLOOXS are on the home path. Large state files (the stress library) and FANGS / HEMTRAD-FANGS are on `/blue`. The two prefixes are not interchangeable: write each path exactly as this table gives it. The `stressLoad=/blue/ee1/ianstafford/stress/...` paths in the params files are correct.

| What | Path |
|---|---|
| HEMTRAD working copy (agent edits here) | workstation `/home/staffian/HEMTRAD` |
| HEMTRAD on HPG (only `git pull`) | `/home/ianstafford/blue/ee1/ianstafford/HEMTRAD` |
| HEMTRAD on Ian's laptop | read-only clone, pull only, never pushes |
| GitHub | `IanStafford/HEMTRAD` (`main`; `static-mobility` frozen) |
| Obsidian vault | `~/notes/HEMTRAD-vault` — symlinks only: `CLAUDE.md`, `progress.md`, `RESULTS.md`, and `kb/` (this knowledge base). Never copy repo files in; `.obsidian/` stays out of the repo |
| Sweep results (not in git) | `results/` on both machines; static era in `results/archive_static_mobility/` |
| HPG stress library (real `/blue`) | `/blue/ee1/ianstafford/stress/`: `sin_Vg-10/`, `hk_Vg-10/` (the Vg -10 V library: a state saved every volt up to 84 V), `meshchk/sin_m10`, `meshchk/sin_m5fix`, `meshchk/sin_m2p5` (mesh checks); `fpfix/sin_Vg-10`, `fpfix/hk_Vg-10` (to 28 V), `fpfix/meshchk/{sin_m5fix,sin_m2p5}` (fixed FP box, from 2026-11-20). Every state saved before 2026-11-20 has the old FP contact box ([[fp-contact-fix]], [[stress-library]]) |
| Stock FLOOXS on HPG | `/home/ianstafford/blue/ee1/ianstafford/flooxs` (home, `release/flooxs`) — HEMTRAD jobs use it; don't modify |
| flooxs-pyplot (FANGS) on HPG | `/blue/ee1/ianstafford/flooxs-pyplot` with `build-hpg`, env `/blue/ee1/ianstafford/conda/envs/fangs`, runs in `/blue/ee1/ianstafford/runs`. Copied as a git bundle (HPG has no GitHub access) since 2026-11-04. The bundle's ref is remote-tracking, so `git clone` alone gives an empty repo: fetch `+refs/remotes/origin/main-gucs79:refs/remotes/origin/main-gucs79` from it. Older checkout (da619c4c) deleted 2026-10-15 |
| FLOOXS source (workstation) | `~/flooxs/src` |
| Crash-fix build | `~/flooxs-crashfix` (branch `crash-fix`; the fix is commit bddf6092, with the matplotlib renderer 350e41d4 on top; no patch file exists) |
| Brick-fix build | `~/flooxs-brickfix` (branch `brick-gradient-fix`): FLOOXS with the 3D brick gradients fixed, local only ([[flooxs-builds]], [[3d-plan]]) |
| SRIM / TRIM (workstation) | `~/.wine-srim/drive_c/SRIM` (Wine prefix `~/.wine-srim`), package in `~/opt/srim-2013/`; run with `bin/trim_run.sh` ([[trim]]) |
| HEMTRAD-FANGS | separate private repo `IanStafford/HEMTRAD-FANGS`: the HEMTRAD model ported to FANGS (Python). Workstation `~/HEMTRAD-FANGS`, worked on by its own Claude session; HPG `/blue/ee1/ianstafford/HEMTRAD-FANGS` (`repo/` the old checkout, `proj/` the reorganised project). Used for the 3D brick-gradient work ([[3d-plan]]); curves copied to `data/rad3d_fangs/` |
| flooxs-pyplot (workstation) | `~/flooxs-pyplot` (private `IanStafford/flooxs-pyplot`; matplotlib plot windows, regression suite; `Test/SimpDev/GaNSuite` = GaN starter decks) |
| GaN regression results | `~/flooxs-pyplot/Test/Regression/hpg_results/20261008/` and `20261015-fangs*` (FANGS HPG campaign, runs 1-3; not committed) |
| FANGS HPG campaign scripts | `archive/fangs-hpg-tests/` (finished 2026-10-15; HPG folder `fangs-hpg-20261015` deleted) |
| FANGS first HPG run inputs | `archive/fangs-hpg-first-run/` (finished 2026-11-04, at FANGS 6570d19) |
| HPG SSH key / config | workstation `~/.ssh/id_ed25519_hpg` (no passphrase), `~/.ssh/config` hosts `hpg`, `hpg-login7`, `hpg-tmux` ([[hpg-workflow]]) |
| HPG persistent tmux | session `hemtrad` on `login7` |
| Exploratory worktrees | workstation `~/HEMTRAD-wt/{field-capture,gate-injection}` (branches `explore/*`) and `~/HEMTRAD-wt/rad-model` (branch `explore/rad-model`, merged into `main` 2026-11-04; removing it is Ian's call), HPG `/home/ianstafford/blue/ee1/ianstafford/HEMTRAD-wt/` (created with `git worktree add`; pull only) ([[vg-dependence]]) |
| Start-up script | workstation `~/bin/agent-up` (not in the repo): local tmux `agent`, HPG link via key + Duo push, login7 tmux, Claude ([[hpg-workflow]]) |
| Dashboard | [[dashboard]] |
| Static-era write-ups | `archive/static_mobility/RESULTS.md` |
| Progress-report deck (Sep 30) | https://claude.ai/artifact/4RfyrQi58v7pD8NH6aFLqc |
| Progress deck (Sep 30 – Oct 13, 16 slides) | https://claude.ai/artifact/GXaJFrxHnuC97g8SzKPvjN |
| Trap-model physics reference (equations, functions, references) | https://claude.ai/artifact/4KLdks2Sd8t9zs8wb8wWJ9 |
