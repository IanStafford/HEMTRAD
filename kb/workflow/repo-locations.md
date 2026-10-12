---
title: Repo and tool locations
tags: [workflow, reference]
---
# Where things live

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
| Dashboard | [[dashboard]] |
| Static-era write-ups | `archive/static_mobility/RESULTS.md` |
| Progress-report deck (Sep 30) | https://claude.ai/artifact/4RfyrQi58v7pD8NH6aFLqc |
