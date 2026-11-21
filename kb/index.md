---
title: HEMTRAD knowledge base
tags: [moc]
date: 2026-11-20
---
# HEMTRAD knowledge base

Second brain for the FLOOXS model of radiation effects in an AlGaN/GaN HEMT (HfO2/HighK or SiN passivation, T-gate + field plate). The work had two phases: the pulsed curve-tracer **current collapse** (Sep 23 – Oct 23), and since 2026-10-23 the **pre/post-irradiation model** of HighK and SiN devices after biased heavy-ion irradiation ([[project-goal]]). Notes are atomic and linked with Obsidian wikilinks (double square brackets); open the vault `~/notes/HEMTRAD-vault` (the `kb` folder there is a symlink to this directory) or read them as plain Markdown.

**Rules for agents** live in `CLAUDE.md` (repo root). This KB holds the *knowledge*: what the model is, how things work, what was found. The dated log of what happened is `progress.md`; the day-by-day dashboard is [[dashboard]].

## Start here
- [[project-goal]] — what we are trying to reproduce, in both phases
- [[current-status]] — where the work stands, open questions, next steps
- [[glossary]] — terms, symbols and run names (Run F, deep/medium/shallow, strike, pocket, stress library, m5fix …)

## Device
- [[device-structure]] — geometry, layers, contacts, coordinates; the FP contact box (fixed 2026-11-20)
- [[mesh]] — deck spacing, `meshY` refinement and its pitfalls, the library / m10 / m5fix / m2p5 meshes, convergence status
- [[mobility-models]] — `field` vs `static`, and the mob* calibration levers
- [[calibration]] — the Oct 1 fit to the measured HfO2 transfer curve and the 2026-10-23 rad-device baseline

## Physics model
- [[trap-model]] — `IonizedAcceptor`, trap memory, freeze/capture
- [[hot-electron-capture]] — Te from the local field, capture barrier `hotEb`
- [[insulator-traps]] — static charge in Nitride/HighK; the radIns passivation damage
- [[damage-model]] — rad-era damage laws (E⁴ stress damage, strikes, field-scaled strikes), which field each uses, which runs used them
- [[energy-balance]] — ETemp PDE, optional (`eTemp 1`); the local-field model (`eTemp 0`) is standard since 2026-10-16; thermo term parked
- [[levers]] — every model/driver knob and its default
- [[model-caveats]] — what the model leaves out or gets wrong
- [[3d-plan]] — 3D slice of the gate width: FLOOXS support, phases, the brick-gradient fix, results (Nov 12-18)

## FLOOXS (the simulator, `~/flooxs`)
- [[flooxs-overview]] — what FLOOXS is, source layout
- [[flooxs-commands]] — Tcl commands the decks use
- [[flooxs-expressions]] — expression language (operators, functions, grad/ddt/dot, Fermi integrals)
- [[flooxs-solver]] — Newton loop, convergence, iteration table, damping and positivity
- [[flooxs-pdb]] — parameter database
- [[flooxs-builds]] — binaries and builds

## Numerics
- [[flooxs-gotchas]] — FLOOXS behaviours that bite
- [[munmap-crash]] — root cause of the old crash
- [[retry-bisection]] — catch + store/restore + Vd bisection
- [[te-ramp]] — the stall fix at the runaway

## Workflow and tools
- [[hpg-workflow]] — HiPerGator connection, environment, SLURM rules
- [[sweep-pattern]] — params.txt / task dirs / checks / rsync (index of every params file: `sweeps/README.md`)
- [[stress-library]] — saved off-state stress states: save, load, resume, the `fpBox` stamp, mesh caveat
- [[local-runs]] — running FLOOXS on the workstation
- [[git-conventions]] — what to commit, CRLF files, archiving
- [[dashboard]] — the work-log artifact and the "wrap up for the day" procedure
- [[cleanup-plan]] — code legibility clean-up plan and KB audit (2026-11-20): decisions for Ian, staged steps with acceptance tests, the list of KB conflicts
- [[drivers]] — `drivers/radIV.tcl` (the rad model, all work since Oct 23), `drivers/seeIV.tcl` (transients); `drivers/pulsedIV.tcl` (the Sep–Oct curve tracer), `drivers/calibIdVg.tcl` …
- [[analysis-scripts]] — Python analysis and plotting
- [[notebook]] — `archive/static_mobility/figures.ipynb`, the static-era paper plots
- [[trim]] — SRIM-2013 TRIM under Wine on the workstation, batch wrapper, HEMT template
- [[repo-locations]] — the three repo copies, Obsidian vault, flooxs checkouts

## Results: radiation model (since 2026-10-23, current work)
Every result here that uses a stress state saved before 2026-11-20 predates the FP contact fix and is being rerun ([[fp-contact-fix]]).
- [[fp-contact-fix]] — the FP contact covered the drain half of the T-gate head (head drain edge ~0 V instead of Vg during the stress); fixed 2026-11-20, tests of the effect
- [[step-search-28v]] — stepped SiN collapse at the 28 V stress with strikes, HighK contrast, field-scaled strikes, mesh checks and the mesh-robust series (rounds S, A-K, M, Nov 17-20)
- [[step-mechanism]] — why the strike curves step: each damaged pocket switches at ~0.5 V across it (barrier traps fill with hot electrons); pockets in series share the drain voltage (Nov 19)
- [[rad-model]] — pre/post-irradiation model, HPD vs SiN (qualitative); the Nov 11 model and its history
- [[damage-region-map]] — what damage in each device region does, one to five sites (Nov 2026)
- [[ron-increase]] — Ron rise after biased irradiation: candidates and simulations (Nov 2026)
- [[see-plan]] — single-event transient (ion strike): method as run and results (Oct 29 – Nov 19)
- [[rad-literature]] — literature on Vth, Ron and steps in irradiated HEMTs; nothing at our fluence (Nov 4)
- [[rad-literature-steps]] — stepped collapse after heavy ions: what is reported, proposed mechanisms, what the model can test (Nov 17)

## Results: pulsed-IV collapse (Sep 23 – Oct 23)
- [[collapse-classification]] — deep / medium / shallow / stalled / off at rest
- [[run-F]] — the reference trap set
- [[field-mobility-trap-map]] — Run F map with the calibrated mobility
- [[late-onset-search]] — pushing the onset out (rounds 1–4)
- [[position-maps]] — onset vs trap position, GIF surfaces, level/conc sets
- [[gate-bias]] — Vg −1 / 0 V: current-driven collapse
- [[field-driven-trapping]] — candidate mechanisms, proposed tests
- [[vg-dependence]] — measured onset later at higher Vg; EB vs field-driven / virtual-gate worktrees (Oct 15)
- [[trap-sensitivity]] — one-at-a-time sweep of every trap lever (Oct 17)
- [[highk-vs-sin]] — with the same hand-placed traps both decks collapse at the same onset (passivation changes only the recovery); the rad model's deck difference comes from where the stress field places damage ([[rad-model]]; pre-fix; being rerun, [[fp-contact-fix]])

## Results: earlier and side work
- [[static-era-lessons]] — what the constant-mobility era (Sep 23 – Oct 1) taught
- [[critical-strike]] — strike probability at 1e7 ions/cm² (Sep 28)
- [[flooxs-pyplot-regression]] — GaN regression baselines run on HPG for the solver work (Oct 8)
