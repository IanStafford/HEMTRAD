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

| What | Path |
|---|---|
| HEMTRAD working copy (agent edits here) | workstation `/home/staffian/HEMTRAD` |
| HEMTRAD on HPG (only `git pull`) | `/home/ianstafford/blue/ee1/ianstafford/HEMTRAD` |
| HEMTRAD on Ian's laptop | read-only clone, pull only, never pushes |
| GitHub | `IanStafford/HEMTRAD` (`main`; `static-mobility` frozen) |
| Obsidian vault | `~/notes/HEMTRAD-vault` — symlinks only: `CLAUDE.md`, `progress.md`, `RESULTS.md`, and `kb/` (this knowledge base). Never copy repo files in; `.obsidian/` stays out of the repo |
| Sweep results (not in git) | `results/` on both machines; static era in `results/archive_static_mobility/` |
| Stock FLOOXS on HPG | `/home/ianstafford/blue/ee1/ianstafford/flooxs` (`release/flooxs`) — HEMTRAD jobs use it; don't modify |
| flooxs-pyplot on HPG | `/home/ianstafford/blue/ee1/ianstafford/flooxs-pyplot` (da619c4c, built with Intel + eigen3 module) |
| FLOOXS source (workstation) | `~/flooxs/src` |
| Crash-fix build | `~/flooxs-crashfix` (branch `crash-fix`), patch `flooxs-crashfix.patch` |
| flooxs-pyplot (workstation) | `~/flooxs-pyplot` (private `IanStafford/flooxs-pyplot`; matplotlib plot windows, regression suite; `Test/SimpDev/GaNSuite` = GaN starter decks) |
| GaN regression results | `~/flooxs-pyplot/Test/Regression/hpg_results/20261008/` (not committed) |
| HPG SSH key / config | workstation `~/.ssh/id_ed25519_hpg` (no passphrase), `~/.ssh/config` hosts `hpg`, `hpg-login7`, `hpg-tmux` ([[hpg-workflow]]) |
| HPG persistent tmux | session `hemtrad` on `login7` |
| Dashboard | [[dashboard]] |
| Static-era write-ups | `archive/static_mobility/RESULTS.md` |
| Progress-report deck (Sep 30) | https://claude.ai/artifact/4RfyrQi58v7pD8NH6aFLqc |
| Progress deck (Sep 30 – Oct 13, 16 slides) | https://claude.ai/artifact/GXaJFrxHnuC97g8SzKPvjN |
| Trap-model physics reference (equations, functions, references) | https://claude.ai/artifact/4KLdks2Sd8t9zs8wb8wWJ9 |
