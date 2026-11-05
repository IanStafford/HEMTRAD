---
title: Damage-region map
tags: [results, radiation, model]
date: 2026-11-04
---
# Damage-region map

Empirical map of what a damaged section does, by position, on both decks. **Interim:** the steps below are not yet checked for mesh sensitivity (radMesh, job 49606872). Depth, width and multi-strike studies come after that.

## Setup

radMap1 (job 49570571, 58 tasks, all finished, no crashes; 3 stopped before 10 V). One uniform acceptor site, 0.3 µm wide, top 50 nm (x 0–0.05 µm), level 0.30 eV, no stress solve, Vg +1 V for Id–Vd. It covers 14 positions from y = −0.9 to 3.0 µm at 1e18 and 4e18 cm⁻³. A 2D site spans the full device width, so this is a whole-width section, not one ion track.

Figures: `figures/rad/radMap1.png`, `figures/rad/radMap1_curves.png`. Table: `results/20261104_radMap1/map.csv` (not committed; rebuild with `analysis/radMap.py`).

## What each region does

| Site | ΔVth (V) | gm ratio | Ron ratio | Id(10 V) ratio | Steps at 4e18 |
|---|---|---|---|---|---|
| Under the gate (y 0), 1e18 / 4e18 | +0.78 / +1.96 | 0.78 / 0.59 | 1.07 / 1.32 | 0.76 / 0.39 | none |
| Gate edge, source side (y −0.3), 1e18 / 4e18 | 0 / −0.005 | 0.96 / 0.80 | 1.07 / 1.28 | 0.88 / 0.44 | one, about 67 mA/mm at 3.5 V |
| Source access (y −0.9), 1e18 / 4e18 | −0.002 / −0.006 | 0.97 / 0.90 | 1.06 / 1.25 | 0.91 / 0.24 | one, 157–220 mA/mm at 4.5–5 V |
| Gate edge, drain side (y 0.3), 1e18 / 4e18 | 0 / −0.003 | 0.97 / 0.89 | 1.06 / 1.28 | 0.94 / 0.50 | none |
| Mid drift (y 1.5), 1e18 / 4e18 | −0.002 / −0.005 | 0.98 / 0.93 | 1.06 / 1.25 | 1.00 / 0.55 | one, about 84 mA/mm at 3.75 V |
| Drain edge (y 3.0), 1e18 / 4e18 | −0.002 / −0.005 | 0.98 / 0.92 | 1.07 / 1.27 | 1.00 / 0.32–0.36 | two, at 4 V and 7.5–8 V |

## Findings so far

- **Vth is set only under the gate.** A site that doesn't overlap the gate foot moves Vth by at most 0.007 V, at any density tested.
- **Ron barely depends on position.** It's 1.06–1.07 at 1e18 and 1.23–1.32 at 4e18 everywhere, as expected for a series section. The wiggle with y is probably mesh aliasing: a 0.3 µm window catches a varying number of 25–50 nm cells, and refining the source-side site moved Id at 0.5 V by 2.6%.
- **There's a threshold between 1e18 and 4e18 cm⁻³.** Over 50 nm that's 5e12 to 2e13 cm⁻², bracketing the 2DEG (polCharge 1e13). Only the higher density gives steps or a large loss at high Vd.
- **One site can give abrupt steps onto a rising line, sometimes two per curve.** Nothing placed these by hand; a uniform site and hot-electron fill-only capture produce them. Steps depend on position, and none appear when the site sits at the gate or just past its drain edge.
- **The source side is the most damaging place for high-Vd current** at 4e18 (ratio 0.24 at y −0.9, against 0.55 mid-drift). Two source-side HighK/SiN cases at y −0.6 stopped before 10 V, so that point is missing.
- **The decks barely differ here.** HighK and SiN agree closely below about 7 V; the step at y 2.7 is the largest difference (3.75 V against 7.25 V). Without a stress solve, the deck's main route to the damage is gone, so this says nothing about how irradiation would place damage in each deck.

## Open

Mesh dependence of the steps, the current after a step against Vg (radFam, job 49606874), depth, width, and multiple sites.

Related: [[rad-model]], [[ron-increase]], [[rad-literature]], [[critical-strike]], [[mesh]], [[hot-electron-capture]].
