---
title: Damage-region map
tags: [results, radiation, model]
date: 2026-11-04
---
# Damage-region map

Empirical map of what a damaged section does, by position, on both decks. **Corrected 2026-11-05: the steps and the position dependence at high Vd in radMap1 were mesh artifacts** (radMesh, job 49606872). Vth, Ron and gm stand. On a fine mesh, a dense site acts as a current limit set by its density, independent of Vg and mostly of position (radFine, job 49735196), and each extra site adds a fixed series resistance (radMulti, job 49735488).

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
- **The 0.1 µm, 1.2e19 site looked like a collapse, but the drop shrinks as the mesh refines:** from about 139 mA/mm down to 12, 36 and 96 at Vd 1 V for 10, 5 and 2.5 nm. The level after it does settle at 5 and 2.5 nm (below), so the drop may be numerical too. It isn't converged at 2.5 nm.
- **The final SiN two-step curve has the same problem** ([[rad-model]]): both steps vanish at 10 nm.
- **Earlier position maps** used Gaussians, and the Sep 27 check there found onset shifts of about 0.1 V. They haven't been rechecked for the current limit picture.

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

## A dense site is a current limit (radFine, job 49735196)

Figure: `figures/rad/radFine.png`. 5 nm in the site, y 1.5, top 50 nm. 17 of 19 tasks finished, no crashes. Id is the mean from 3 to 10 V, in mA/mm.

| Density (cm⁻³) | 0.3 µm wide | 0.1 µm wide |
|---|---|---|
| 4e18 | 558 | 595 |
| 6e18 | 346 | 374 |
| 8e18 | 229 | 254 |
| 1.2e19 | stopped at 4 V (near 100) | 121 (5 nm), 128 (2.5 nm) |

- **Density sets the level; width barely matters.** Undamaged is about 1000 mA/mm over the same range. Wiggles of up to 30–60 mA/mm remain at 6e18 and above, and are not to be read as steps.
- **The level doesn't depend on Vg.** Fresh curves with no trap memory (SiN, 0.1 µm, 1.2e19) sit on the same 125–140 mA/mm line at Vg −2, −1, 0 and +1, even at Vg −2, where the undamaged device reaches 250. This is the series-limit idea from [[rad-literature]], now in the model. Our inference is a section that can pass only so much current; field cuts haven't been checked.
- **The line here is flat**, unlike the rising line in the measured R33 data, and onset doesn't move later at higher Vg as measured.
- **Position matters only on the source side.** At y 0.3–3.0 the level is about 130–140 mA/mm; at y −0.3 about 68, and at y −0.6 and −0.9 between 69 and 121. HighK and SiN differ at y −0.6 (94 and 69), which should not be a deck effect, so these aren't tightly converged.

## Trap memory gives a rising, Vg-independent line

With curves run in the order Vg +1, then −2 upward, traps stay filled, because capture is fill-only.

- **It survives 5 nm (radFine; 2 family tasks still running at the last Vg values).** At y 3.0, 0.3 µm, 4e18, the Vg −1 and −0.5 curves agree within 8% over the whole sweep, from nearly zero at low Vd up to about 500 mA/mm at 10 V. Curves at lower Vg leave that line when the gate limits them (244 at Vg −2, 378 at −1.5). The first +1 V curve doesn't show this; it stays at about 557.
- **A denser site blocks almost completely, then turns on.** At 0.1 µm and 1.2e19, Vg −2 to 0 pass nearly no current to 7 V, then rise together to 129–137 mA/mm at 10 V.
- **Unlike R33, low Vd is dead here.** R33 curves start normally and then drop onto their line. The model has no emission, so it overstates memory. A real device may sit between the two.
- **The earlier standard-mesh results (radFam, job 49606874) agree in kind but not in numbers.**
- **A test on real devices:** the model predicts a strong difference between a first and a repeated sweep, and dependence on Vg order.

## Multiple strikes (radMulti, job 49735488)

61 tasks: 0.1 µm, 1.2e19, 5 nm in each site, both decks, no site under the gate. 8 ran out of memory at 4 GB (mostly 4–5 sites). 13 stopped at the current limit. All 33 tasks with 1 or 2 sites reached 10 V, against 7 of 25 with 3 or more; 3 of the large tasks have no data.

| Sites | Vd/Id at 0.25 V (Ω·mm, mean) | Spread across sets | Vd at the current peak |
|---|---|---|---|
| 0 | 2.25 | | |
| 1 | 3.46 | 3.44–3.52 | 0.75 V |
| 2 | 4.56 | 4.53–4.60 | 1 V |
| 3 | 5.62 | 5.60–5.66 | about 1.5 V |
| 4 | 6.68 | 6.65–6.71 | 1.5–2 V |
| 5 | 7.73 | 7.70–7.76 | about 2 V |

- **Resistance simply adds:** +1.21 Ω·mm for the first site, then +1.05–1.09 for each more, whatever the location or deck. So in this 2D model the low-Vd resistance counts strikes.
- **Extra sites don't lower the current limit.** The peak stays at about 130–139 mA/mm from 1 to 5 sites. It just takes more Vd to reach it. Where the runs reach 10 V, the level is 100–140, or lower with source-side sites.
- **No separate step per strike can be claimed.** The dips at higher Vd are the same kind as those that shrink with the mesh.
- **Caveat:** each site spans the whole device width and is far denser than TRIM gives at 1e7 cm⁻². This shows how sections combine, not what a real fluence does.

## Partial width (2026-11-05, no solver)

`analysis/radPartialWidth.py`: Id_total = f·Id_damaged + (1−f)·Id_undamaged, with parallel columns and no current spreading between them. At 1e7 cm⁻² about 93 ions land on the 200 µm device, and one 0.16 µm track covers 0.08% of the width, so 7.5% if every track has its own column.

| Columns damaged | 0.3 µm, 4e18: resistance, Id(10 V) | 0.1 µm, 1.2e19: resistance, Id(10 V) |
|---|---|---|
| 0.08% (one track) | 1.000, 1.000 | 1.000, 0.999 |
| 7.4% (all tracks) | 1.016, 0.967 | 1.027, 0.931 |
| 20% | 1.045, 0.910 | 1.075, 0.815 |
| 50% | 1.121, 0.775 | 1.212, 0.537 |
| 100% | 1.274, 0.550 | 1.538, 0.074 |

- **Isolated tracks can't move the device much.** One track changes the current by at most about 0.1%, and all tracks by 3–7%. Even a column that passes nothing gives only +8% resistance at 7.5%.
- **So an abrupt step can't be one track switching.** A step's size is the fraction of the width that switches. The measured steps are many times what one track's column could give, and larger than all the tracks together, which needs damage or switching that spreads across a large part of the width, or a measurement effect.
- **Limits:** this leaves out current spreading, which would shrink the effect further, and lateral spread of damage under bias, which would enlarge it. 0.16 µm is the estimate from [[critical-strike]].

## Trap emission (radEmit, job 49834170, 2026-11-05)

Crude levers, with no time constant: `emitFrac` releases a fraction of the excess charge per capture. SiN, 5 nm in the site, Id–Vd at Vg +1 V. 15 tasks, no crashes; 12 stopped before 10 V or nearly so.

| Site | Fill-only, 10 V | With `emitFrac` 0.01 to 1 |
|---|---|---|
| y 3.0, 0.3 µm, 4e18 | smooth, 557 | same to about 7 V (574 at 7 V for 0.3 and 1), wiggles of 15–26 at 0.01–0.03, solver stops at 7.5–8 V for 0.1 and above |
| y 1.5, 0.3 µm, 8e18 | about 240 | same limit near 243, solver stops at 2.25–3.75 V |
| y 1.5, 0.1 µm, 1.2e19 | about 130 | level 120–150, with single-point spikes to 12–38 that recover at the next point |

- **No clean step onto a lower line.** The current limit doesn't move with emission. The spikes recover at once, so they look numerical.
- **Removing memory makes the solver stop sooner**, so what lies past those points is unknown. A last drop of about 45 mA/mm just before stopping at site A hasn't been followed.
- **`emitRest` had a bug:** it left TeTrap hot from the previous curve, which refilled the traps at the next capture. Those 6 tasks were cancelled. Fixed; rerun as radEmit2 (8 tasks).

## Open

Trap emission (radEmit, job 49834170), which limits how far the memory result can be pushed; what actually produces abrupt steps in the measured curves, since neither the 2D sites nor isolated tracks do.

Related: [[rad-model]], [[ron-increase]], [[rad-literature]], [[critical-strike]], [[mesh]], [[hot-electron-capture]].
