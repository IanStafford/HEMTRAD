---
title: Glossary
tags: [reference]
date: 2026-11-20
---
# Glossary

## Device and general
- **2DEG** — two-dimensional electron gas at the AlGaN/GaN interface, x = 0.015 µm. See [[device-structure]].
- **HighK / SiN deck** — HighK is the deck material for the HfO2 passivation (εr 35, `model/rfdevice.tcl`); the SiN deck (`model/rfdevice_SiN.tcl`, lever `deviceDeck`) has Nitride in its place ([[device-structure]]).
- **HPD** — the HfO2-passivated device of the measured rad set, which the HighK deck stands in for ([[rad-model]]). In the decks `HPD_Thick` (0.1 µm) is the HighK layer over the T-gate head.
- **fpBox / `fpBoxOld`** — the FP contact box. `fpBoxOld` 0 (default since 2026-11-20) builds a box matching the FP metal; 1 rebuilds the old box, which also covered the drain half of the T-gate head. radIV writes `fpBox=fixed|old` into each saved state's settings file and refuses to load a state whose box differs from the run's ([[fp-contact-fix]]).
- **HPG** — HiPerGator, UF's cluster ([[hpg-workflow]]). **ee1-b** — the group's burst QOS (~171 CPUs).
- **FANGS / flooxs-pyplot** — Ian's private port of FLOOXS (repo `flooxs-pyplot`, called FANGS): matplotlib plot windows, a regression suite, the STRUMPACK solver and threaded assembly ([[repo-locations]], [[flooxs-pyplot-regression]]). **HEMTRAD-FANGS** is a separate private copy of this model on FANGS (`~/HEMTRAD-FANGS`). It ran the 3D brick-gradient probe and the FANGS 3D reruns ([[3d-plan]]).

## Pulsed-IV era (Sep 23 – Oct 23)
- **Run F** — the reference trap set: `trapPeak` 4e18, `trapSigma` 0.04, `trapLevel` 0.55, `hotEb` 0.5, `hotTau` 1.3e-13 at x = 0, y = 0.2 µm. See [[run-F]].
- **Late-onset set** — 0.30 eV / 5e18 / `hotTau` 1e-14 / `hotEb` 1.0, σ 40 nm; the round-3 best ([[late-onset-search]]).
- **Deep / medium / shallow** — largest single-step loss >95% / 50–95% / <50%. **Off at rest** — <10% of trap-free at Vd 0.1 V. **Stalled** — `PULSED GAVE UP` with no recorded collapse. See [[collapse-classification]].
- **Onset** — Vd of the first step that reaches the class threshold.
- **Suppression** — Id(trap-free)/Id(trapped) at a given Vd; **collapse depth vs trap-free** — Id_no-trap / Id at the post-collapse minimum.
- **Runaway** — positive feedback: trapped charge depletes the channel → local field ↑ → electrons hotter → more capture. Appears as a discontinuous jump that Vd continuation cannot follow ([[te-ramp]]).
- **Creep** — slow rise of Id with Vd after the collapse; physical, seen in the measurement ([[project-goal]]).
- **Te / TeTrap / ETemp** — electron temperature: local-field estimate ([[hot-electron-capture]]), the under-relaxed data field the traps see, and the solved PDE variable ([[energy-balance]]).
- **Qfn / Qfp** — electron / hole quasi-Fermi levels (eV-like units; current ∝ n μ ∇Qfn).
- **FillStep** — 4 × (UpdateTe w 0.5 → device → CaptureTraps) per Vd point ([[trap-model]]).
- **radPlot / radPlot1** — the old measured-like collapse curves used as onset/depth targets in the static era; their post-collapse decay came from a sign bug ([[trap-model]]).
- **Static era** — 2026-09-23 to 10-01, constant mobility 600 ([[static-era-lessons]]); **field era** — calibrated field-dependent mobility from 10-01 on.

## Rad era (since 2026-10-23)
Results quoted in these entries (the pocket threshold, row A, band b) predate the FP contact fix and are being rerun ([[fp-contact-fix]]).
- **`radState` pre / post** — the `drivers/radIV.tcl` switch: pre-irradiation curves, or post-irradiation with damage ([[rad-model]]).
- **pre / nb / biased** — the three device states in task labels. **pre**: pre-irradiation. **nb** (non-biased irradiation): `radState post` with only bias-independent damage (`surfCharge` −4e11 and under-gate acceptors, 5e17 in the top 14 nm in the Nov 11 model), no stress damage. **biased** (`_b_` in labels): irradiated at Vg −10 / Vd 28 V, which adds the stress damage.
- **Stress** — the off-state solve at the irradiation bias (Vg −10 V, drain ramped to `Vd_stress`, 28 V). Its field places the damage. Without `occSafe` the ramp stopped at 17.66 V (the Nov 11 model).
- **`occSafe`** — a numerically safe but identical form of the trap occupancy (`model/Poisson.tcl`) that lets the stress reach 28 V.
- **E⁴ damage (stress damage)** — acceptor traps at 0.30 eV with density N = `damPeak`·(E_lat/`damEref`)^4 from the stress field, `damEref` 5e5 V/cm, top 50 nm, y ≥ 0.30 µm, capped at `damMax` ([[damage-model]]).
- **Damage scale** — `damPeak`, the E⁴ damage density at E = `damEref`: 7e18 at the 17.66 V stress, 1.5e18 at 28 V.
- **Strike** — one ion strike as a Gaussian damage site (`damGauss {y x sigma N}`, σ 40 nm, at the AlGaN top), spanning the full gate width in 2D. Plain strikes go to y 0.8, 1.6 and 2.4 µm in that order. **N0-N3** in a label is the number of strikes. **Field-scaled strikes** (`gaussFieldM`, `damGaussF`) multiply the density by (E/E_ref)^m from the stored stress field ([[step-search-28v]], [[damage-model]]).
- **Pocket** — a damaged, partly depleted stretch of the 2DEG: the stress band (y 0.45-0.72 µm) or one strike. Pockets sit in series and share the drain voltage. A pocket switches once about 0.5 V sits across it: the barrier traps over its drain flank fill with hot electrons and Id drops ([[step-mechanism]]).
- **Row A** — the plain-strike series of the Nov 18 deliverable: damage scale 1.5e18, 6e18 strikes, trap level 0.30 eV. Its steps are not mesh-robust ([[step-search-28v]]).
- **Band b** — field-scaled strikes (m 4) in the band where SiN's stress field exceeds HighK's: base densities 2e18 / 6e17 / 2e17 at y 0.65 / 0.6 / 0.55 µm (round I). Band a is 3e18 / 1e18 / 3e17 ([[step-search-28v]]).
- **Stress library** — off-state stress states (Vg −10 V) saved per deck at every volt of the drain ramp, loaded with `stressLoad` so strike runs skip the stress solve; the strike rounds load the 28 V state. Old-box library: `/blue/ee1/ianstafford/stress/<deck>_Vg-10/` (1 V steps to 84 V). Fixed-box library: `/blue/ee1/ianstafford/stress/fpfix/` (to 28 V, fpFixStress 52134552) ([[stress-library]]).
- **Library mesh** — the mesh of the library states, which every load inherits: 520 y lines, 15 nm at y 0.8, 5 nm over y 0.96-2.56 ([[mesh]]).
- **m10 / m5fix / m2p5** — the mesh-check meshes: 10 nm uniform over y 0.3-2.6; the library mesh with a true 5 nm over y 0.64-2.56 (554 y lines); the same at 2.5 nm (947 y lines, computed) ([[mesh]]).
- **Nov 11 model** — the final rad model as of 2026-11-11: hotEb 1.0 eV, `meshY` {0.3 0.01 2.0 0.01}, stress at 17 V nominal (`sweeps/params_radFinal12.txt`), taken at 17.66 V in radEB1 50411481. The reference curve in the step figures; being rerun with the fixed FP box (fpFixEB1 52134554) ([[rad-model]]).
- **EB** — two meanings. In radEB1 / radEB2 / fpFixEB1 labels (`eb1`, `eb0.75`), `plot_radFinalEB.py` and `radEBFig.py` it is the capture barrier `hotEb` (1.0 / 0.75 eV). In vgEB and eTempStd it is the energy balance (`eTemp 1`, [[energy-balance]]).
