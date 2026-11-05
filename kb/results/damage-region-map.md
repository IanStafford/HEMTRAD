---
title: Damage-region map
tags: [results, radiation, model]
date: 2026-11-04
---
# Damage-region map

Empirical map of what a damaged section does, by position, on both decks. **Corrected 2026-11-05: the steps and the position dependence at high Vd in radMap1 were mesh artifacts** (radMesh, job 49606872). Vth, Ron and gm stand. Density and width thresholds on a fine mesh are running (radFine, job 49735196). The multi-strike study is on hold until Ian decides how to proceed.

## Mesh check (radMesh, job 49606872, 11 tasks, no crashes)

Figure: `figures/rad/radMesh_curves.png`. HighK, Vg +1 V, Id in mA/mm.

| Site | Mesh in the site | Largest step | Id at 4 V | Id at 10 V |
|---|---|---|---|---|
| 0.3 µm, 4e18, y 3.0 | standard (about 50 nm) | 100 at 4 V | 399 | 369 |
| | 10 nm | 3.8 | 540 | 562 |
| | 5 nm | 3.7 | 542 | 562 |
| 0.3 µm, 4e18, y −0.9 | standard | 157 at 4.5 V | 552 | 250 |
| | 10 nm | 7.8 | 555 | 526 |
| | 5 nm | none | 556 | 558 |
| 0.3 µm, 4e18, y 1.5 | standard | 84 at 3.75 V | 437 | 565 |
| | 5 nm | 4.1 | 547 | 566 |
| 0.1 µm, 1.2e19, y 1.5 | standard | 110 at 1 V | 0.1 | 0.1 |
| | 10 nm | 126 at 1 V | 3.0 | 26 |
| | 5 nm | 103 at 1 V | 124 | 76 |

- **At 0.3 µm and 4e18 there is no real step.** At 10 and 5 nm the curve saturates smoothly near 560 mA/mm, 0.55 of the undamaged current, the same at all three positions. The two meshes agree.
- **Halving the Vd step doesn't remove the coarse-mesh steps** (0.1 V, same mesh), which is why this needed a mesh test.
- **Likely mechanism (not shown directly):** a sharp-edged site on 25–50 nm cells fills about one cell at a time, so each cell flips as a step.
- **The 0.1 µm site with the same total charge does collapse, near 1 V on all three meshes.** So density matters, not just total charge. What happens after the collapse isn't converged: Id at 10 V goes 0.1, 26, 76 mA/mm. Nothing after the collapse can be quoted yet.
- **Untested elsewhere:** the final SiN two-step curve (radFinal11) relies on `dam3` at y 1.0–1.6 on the same coarse cells, so its steps may have the same problem. Earlier position maps used Gaussians, and the Sep 27 check there found onset shifts of about 0.1 V. radFine includes the final curve at 10 nm.

## Setup

radMap1 (job 49570571, 58 tasks, all finished, no crashes; 3 stopped before 10 V). One uniform acceptor site, 0.3 µm wide, top 50 nm (x 0–0.05 µm), level 0.30 eV, no stress solve, Vg +1 V for Id–Vd. It covers 14 positions from y = −0.9 to 3.0 µm at 1e18 and 4e18 cm⁻³. A 2D site spans the full device width, so this is a whole-width section, not one ion track.

Figures: `figures/rad/radMap1.png`, `figures/rad/radMap1_curves.png`. Table: `results/20261104_radMap1/map.csv` (not committed; rebuild with `analysis/radMap.py`).

## What holds up from radMap1

Standard-mesh numbers; the fine-mesh runs confirm them at the three positions checked (Ron 1.27–1.28 and gm 0.88–0.92 at 4e18).

| Site | ΔVth (V) | gm ratio | Ron ratio |
|---|---|---|---|
| Under the gate (y 0), 1e18 / 4e18 | +0.78 / +1.96 | 0.78 / 0.59 | 1.07 / 1.32 |
| Gate edge, source side (y −0.3), 1e18 / 4e18 | 0 / −0.005 | 0.96 / 0.80 | 1.07 / 1.28 |
| Source access (y −0.9), 1e18 / 4e18 | −0.002 / −0.006 | 0.97 / 0.90 | 1.06 / 1.25 |
| Gate edge, drain side (y 0.3), 1e18 / 4e18 | 0 / −0.003 | 0.97 / 0.89 | 1.06 / 1.28 |
| Mid drift (y 1.5), 1e18 / 4e18 | −0.002 / −0.005 | 0.98 / 0.93 | 1.06 / 1.25 |
| Drain edge (y 3.0), 1e18 / 4e18 | −0.002 / −0.005 | 0.98 / 0.92 | 1.07 / 1.27 |

- **Vth is set only under the gate.** A site that doesn't overlap the gate foot moves Vth by at most 0.007 V.
- **Ron barely depends on position.** The wiggle with y was mesh aliasing: it mostly goes away on the fine mesh.
- **Current at high Vd no longer distinguishes positions** at 0.3 µm and 4e18: 0.54–0.55 at 10 V on the fine mesh. The earlier claim that the source side is worst, and the Id(4 V) and Id(10 V) panels of `figures/rad/radMap1.png`, are withdrawn.
- **The decks barely differ here.** Without a stress solve the deck's main route to the damage is gone, so this says nothing about how irradiation would place damage in each deck.

## Vg family (radFam, job 49606874): standard mesh, so provisional

SiN, curves run in the order Vg +1, then −2 up to +0.5, with traps kept filled from curve to curve, because capture is fill-only. Six of 7 tasks finished; the trap-free reference stalled at Vg −0.5 and was cancelled.

- **Filled sites give a nearly Vg-independent rising line.** At y 3.0 and 4e18, the curves for Vg −1.5 to +0.5 agree within about 10% from 5 to 10 V (7.6 to 325 mA/mm), with almost no current below 4 V.
- **This depends on trap memory and on the coarse mesh.** The first curve doesn't show this line. radFine repeats it on 5 nm, and takes fresh curves with no memory. Until then, this is a lead only.
- **A question this raises for the measured data:** the order of the Vg curves matters if traps persist.

## Open

Collapse threshold in density and width, convergence after a collapse, the Vg family on the fine mesh (all radFine); whether to run depth and multi-strike, and on what mesh.

Related: [[rad-model]], [[ron-increase]], [[rad-literature]], [[critical-strike]], [[mesh]], [[hot-electron-capture]].
