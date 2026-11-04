---
title: Repo and tool locations
tags: [workflow, reference]
---
# Where things live

## Repo layout (since 2026-10-12)
| Folder | Contents |
|---|---|
| `model/` | model + device decks (sourced together; 3 CRLF files) |
| `drivers/` | Tcl drivers ([[drivers]]) |
| `sweeps/` | SLURM templates and `params_*.txt` ([[sweep-pattern]]) |
| `analysis/` | Python analysis/plotting ([[analysis-scripts]]) |
| `data/` | measured inputs (HfO2 Id–Vg, raw xlsx) |
| `figures/` | outputs; `figures.ipynb` at the root ([[notebook]]) |
| `bin/` | workflow helpers (`hpg_reconnect.sh`, [[hpg-workflow]]) |
| `dashboard/`, `kb/`, `archive/` | [[dashboard]], this KB, superseded work |
| `results/` | raw sweep results (gitignored) |

Before 2026-10-12 everything sat flat in the root; `progress.md` and old commits use those paths. `README.md` summarises the layout.

## Machines and checkouts

**Two different places on HPG** (checked 2026-11-04): `/home/ianstafford/blue/ee1/ianstafford` is an ordinary folder in the home directory (NFS, 40 GB quota, 12 GB used), not a link to `/blue`. `/blue/ee1/ianstafford` is the real `/blue` storage. HEMTRAD, its worktrees, every sweep's `results/` and stock FLOOXS are on the home path; FANGS is on `/blue`. Writing `/blue/ee1/...` for a HEMTRAD path, or the reverse, points at nothing.

| What | Path |
|---|---|
| HEMTRAD working copy (agent edits here) | workstation `/home/staffian/HEMTRAD` |
| HEMTRAD on HPG (only `git pull`) | `/home/ianstafford/blue/ee1/ianstafford/HEMTRAD` |
| HEMTRAD on Ian's laptop | read-only clone, pull only, never pushes |
| GitHub | `IanStafford/HEMTRAD` (`main`; `static-mobility` frozen) |
| Obsidian vault | `~/notes/HEMTRAD-vault` — symlinks only: `CLAUDE.md`, `progress.md`, `RESULTS.md`, and `kb/` (this knowledge base). Never copy repo files in; `.obsidian/` stays out of the repo |
| Sweep results (not in git) | `results/` on both machines; static era in `results/archive_static_mobility/` |
| Stock FLOOXS on HPG | `/home/ianstafford/blue/ee1/ianstafford/flooxs` (home, `release/flooxs`) — HEMTRAD jobs use it; don't modify |
| flooxs-pyplot (FANGS) on HPG | `/blue/ee1/ianstafford/flooxs-pyplot` with `build-hpg`, env `/blue/ee1/ianstafford/conda/envs/fangs`, runs in `/blue/ee1/ianstafford/runs`. Copied as a git bundle (HPG has no GitHub access) since 2026-11-04. The bundle's ref is remote-tracking, so `git clone` alone gives an empty repo: fetch `+refs/remotes/origin/main-gucs79:refs/remotes/origin/main-gucs79` from it. Older checkout (da619c4c) deleted 2026-10-15 |
| FLOOXS source (workstation) | `~/flooxs/src` |
| Crash-fix build | `~/flooxs-crashfix` (branch `crash-fix`), patch `flooxs-crashfix.patch` |
| SRIM / TRIM (workstation) | `~/.wine-srim/drive_c/SRIM` (Wine prefix `~/.wine-srim`), package in `~/opt/srim-2013/`; run with `bin/trim_run.sh` ([[trim]]) |
| flooxs-pyplot (workstation) | `~/flooxs-pyplot` (private `IanStafford/flooxs-pyplot`; matplotlib plot windows, regression suite; `Test/SimpDev/GaNSuite` = GaN starter decks) |
| GaN regression results | `~/flooxs-pyplot/Test/Regression/hpg_results/20261008/` and `20261015-fangs*` (FANGS HPG campaign, runs 1-3; not committed) |
| FANGS HPG campaign scripts | `archive/fangs-hpg-tests/` (finished 2026-10-15; HPG folder `fangs-hpg-20261015` deleted) |
| HPG SSH key / config | workstation `~/.ssh/id_ed25519_hpg` (no passphrase), `~/.ssh/config` hosts `hpg`, `hpg-login7`, `hpg-tmux` ([[hpg-workflow]]) |
| HPG persistent tmux | session `hemtrad` on `login7` |
| Exploratory worktrees | workstation `~/HEMTRAD-wt/{field-capture,gate-injection}` (branches `explore/*`), HPG `/home/ianstafford/blue/ee1/ianstafford/HEMTRAD-wt/` (created with `git worktree add`; pull only) ([[vg-dependence]]) |
| Start-up script | workstation `~/bin/agent-up` (not in the repo): local tmux `agent`, HPG link via key + Duo push, login7 tmux, Claude ([[hpg-workflow]]) |
| Dashboard | [[dashboard]] |
| Static-era write-ups | `archive/static_mobility/RESULTS.md` |
| Progress-report deck (Sep 30) | https://claude.ai/artifact/4RfyrQi58v7pD8NH6aFLqc |
| Progress deck (Sep 30 – Oct 13, 16 slides) | https://claude.ai/artifact/GXaJFrxHnuC97g8SzKPvjN |
| Trap-model physics reference (equations, functions, references) | https://claude.ai/artifact/4KLdks2Sd8t9zs8wb8wWJ9 |
