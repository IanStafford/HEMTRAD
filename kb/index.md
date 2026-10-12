---
title: HEMTRAD knowledge base
tags: [moc]
updated: 2026-10-12
---
# HEMTRAD knowledge base

Second brain for the FLOOXS model of **radiation-induced current collapse** in an AlGaN/GaN HEMT (HfO2/HighK passivation, T-gate + field plate). Notes are atomic and linked with Obsidian wikilinks (double square brackets); open the vault `~/notes/HEMTRAD-vault` (the `kb` folder there is a symlink to this directory) or read them as plain Markdown.

**Rules for agents** live in `CLAUDE.md` (repo root). This KB holds the *knowledge*: what the model is, how things work, what was found. The dated log of what happened is `progress.md`; the day-by-day dashboard is [[dashboard]].

## Start here
- [[project-goal]] — what we are trying to reproduce and why
- [[current-status]] — where the work stands, open questions, next steps
- [[glossary]] — terms, symbols and run names (Run F, deep/medium/shallow, stalled …)

## Device
- [[device-structure]] — geometry, layers, contacts, coordinates
- [[mesh]] — spacing and its known resolution problem
- [[mobility-models]] — `field` vs `static`
- [[calibration]] — fit to the measured HfO2 transfer curve

## Physics model
- [[trap-model]] — `IonizedAcceptor`, trap memory, freeze/capture
- [[hot-electron-capture]] — Te from the local field, capture barrier `hotEb`
- [[insulator-traps]] — static charge in Nitride/HighK
- [[energy-balance]] — ETemp PDE (parked)
- [[levers]] — every model/driver knob and its default
- [[model-caveats]] — what the model leaves out or gets wrong

## Numerics
- [[flooxs-gotchas]] — FLOOXS behaviours that bite
- [[munmap-crash]] — root cause of the old crash
- [[retry-bisection]] — catch + store/restore + Vd bisection
- [[te-ramp]] — the stall fix at the runaway

## Workflow and tools
- [[hpg-workflow]] — HiPerGator connection, environment, SLURM rules
- [[sweep-pattern]] — params.txt / task dirs / checks / rsync
- [[local-runs]] — running FLOOXS on the workstation
- [[git-conventions]] — what to commit, CRLF files, archiving
- [[dashboard]] — the work-log artifact and the "wrap up for the day" procedure
- [[drivers]] — `pulsedIV.tcl`, `calibIdVg.tcl`, `stressFreeze.tcl` …
- [[analysis-scripts]] — Python analysis and plotting
- [[notebook]] — `figures.ipynb`
- [[repo-locations]] — the three repo copies, Obsidian vault, flooxs checkouts

## Results
- [[collapse-classification]] — deep / medium / shallow / stalled / off at rest
- [[run-F]] — the reference trap set
- [[field-mobility-trap-map]] — Run F map with the calibrated mobility
- [[late-onset-search]] — pushing the onset out (rounds 1–4)
- [[position-maps]] — onset vs trap position, GIF surfaces, level/conc sets
- [[gate-bias]] — Vg −1 / 0 V: current-driven collapse
- [[field-driven-trapping]] — candidate mechanisms, proposed tests
- [[static-era-lessons]] — what the constant-mobility era (Sep 23 – Oct 1) taught
- [[highk-vs-sin]] — passivation dielectric does not matter at ≤3 V
- [[critical-strike]] — strike probability at 1e7 ions/cm²
- [[flooxs-pyplot-regression]] — GaN regression baselines run on HPG for the solver work
