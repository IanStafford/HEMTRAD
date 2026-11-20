---
title: Why the 28 V strike curves step
tags: [results, rad-model, strikes, mechanism]
date: 2026-11-19
source: progress.md 2026-11-19; HPG jobs radStepDiag 51998840, radStepDiag5b 52018703, meshChkLoad_m5fix 51939192
---
# Why the 28 V strike curves step (one drop per damaged spot)

Diagnostic reruns of the [[step-search-28v]] cases with `vdCuts=1` ([[levers]]). At every Id-Vd point they cut along the channel 1 nm below the AlGaN/GaN interface (x 0.016 µm) and mid-barrier (x 0.008 µm). SiN deck, 28 V stress damage (scale 1.5e18), 6e18 strikes (σ 40 nm) at y 0.8 / 1.6 / 2.4 µm, trap level 0.30 eV, hotEb 1.0 eV, Vg +1 V. The cuts don't change the curves: they are identical to the original runs to the last digit. Read the cuts with `analysis/vdcuts.py`, tabulate the drops with `analysis/vdcutsDropTable.py`.

## The mechanism

1. **Each damaged spot is a partly depleted "pocket" in the 2DEG.** The damage below the interface (GaN side) is completely filled at rest and stays constant through the sweep (IonAcceptor = TrapN at x 0.016). The same damage in the AlGaN barrier is only partly filled at rest: mid-barrier (x 0.008) 4-5e17 cm⁻³ in the pockets against ~6e18 of damage at the strike centre; at the AlGaN top (x 0.001) ~1% (5e16 of 6e18 under the y 0.8 strike). The pockets are the stress band at y 0.45-0.72 µm (under the field-plate edge) and one per strike.
2. **The pockets sit in series along the channel and share the drain voltage.** The voltage across each one is the integral of the lateral field over its y range.
3. **A pocket switches when about 0.5 V sits across it.** At that point its drain edge heats (barrier electron temperature ~330-370 → 550-700 K). Hot-electron capture lowers the barrier trap level and the barrier traps fill: mid-barrier IonAcceptor rises by 2.5-4e18 cm⁻³ (0.4-1e18 → 3.3-4.5e18) in a 20-40 nm band. This deepens the pocket: 2DEG density there falls 2-10× and the local field rises 1.5-10×. The feedback makes the switch take only 0.3-0.8 V of Vd, which is the drop in Id. Voltage across the switching pocket just before it switches: 0.46-0.59 V for all 14 first switches with a drop of at least 8 mA/mm (6 on the library mesh, 8 on the 5 nm mesh). The two later drops near 10.5 V (library, 1 strike) and 11.5 V (5 nm, 8e18) are a pocket that has already switched switching a second time, with several volts across it.
4. **After it switches, a pocket takes most of any further drain voltage.** One strike, library mesh: the y 0.8 pocket goes from 0.52 V at Vd 1.9 to 1.35 V at 2.2 and 4.3 V at 6.1, while the stress band falls back below 0.5 V. That delays the next pocket's switch and makes the steps separate.

## What switches in the deliverable's row A (library mesh, `figures/rad/step28/diag/pocket_volts.png`)

| Strikes | Drops (≥ 8 mA/mm) | What switches |
|---|---|---|
| 0 | 1.6-2.0 V, 395 → 281 | stress band (0.52 V across it at 1.6 V) |
| 1 | 1.9-2.2 V, 388 → 283; 6.1-6.6 V, 401 → 348; 10.0-10.8 V, 398 → 222 | y 0.8 strike (0.52 V); stress band (0.59 V); the y 0.8 pocket again: its core barrier traps fill further (1.5e18 → 5.3e18 at y 0.81) and it widens toward the drain (6.0 → 9.1 V across it) |
| 2 | 2.1-2.4 V, 379 → 371; 3.0-3.3 V, 390 → 307 | y 1.6 strike (0.54 V); y 0.8 strike (0.52 V) |
| 3 | 4.4-4.8 V, 389 → 324 | y 0.8 strike (0.52 V). The y 2.4 and y 1.6 pockets switch earlier (cross 0.5 V at Vd 2.4 and 3.0 V) with dips under 8 mA/mm (373 → 368 at 2.4-2.6 V) |

- The large drop in the 1-, 2- and 3-strike curves is the same y 0.8 strike pocket each time. It switches at the same ~0.52 V across it, but at Vd 1.9 / 3.0 / 4.4 V, because the strikes further out take a growing share of the drain voltage.
- With 2 and 3 strikes the stress band's drop disappears. With 2 strikes it reaches 0.5 V only at Vd 10.6 V (a small dip near 11 V). With 3 strikes it never does (at most 0.43 V).
- The drop count is therefore the number of pockets (and second-stage switches) that reach the threshold before 12 V. It is not one drop per strike.
- Drop size varies with the spot, the strike density and the mesh. In row A the far strikes' switches cost under 10 mA/mm. With 8e18 strikes on the 5 nm mesh, the y 1.6 strike's switch costs 107 mA/mm (263 → 156).
- Pockets switch in order from the drain side toward the gate. All pockets carry a similar voltage before any switch, with the drain-side ones slightly ahead (e.g. 2 strikes at Vd 1.9: 0.43 V across y 1.6, 0.38 across y 0.8, 0.36 across the stress band).

## Why the steps move with the mesh

- The switch threshold (~0.5 V across a pocket) is the same on the library mesh and the 5 nm mesh.
- What changes is how the drain voltage is shared after a pocket switches, which sets when the next pocket reaches 0.5 V. One strike at Vd 3.1: the switched y 0.8 pocket carries 1.93 V on the library mesh (15 nm cells at y 0.8) and 1.57 V on the 5 nm mesh; the stress band 0.36 V and 0.55 V. So on the 5 nm mesh the stress band switches at 3.1-3.6 V instead of 6.1-6.6 V. The y 0.8 pocket never builds up the ~6 V it carries on the library mesh before its second-stage switch near 10.5 V (2.85 V at Vd 6.1 against 4.31), and that switch doesn't happen.
- The post-switch high-field region is 20-40 nm wide, a few cells, so its extent is set by the mesh ([[step-search-28v]], mesh check).
- 5 nm results with barrier cuts (radStepDiag5b):

| Case | Switch | y (µm) | Voltage across the pocket |
|---|---|---|---|
| A_N1 | 1.8-2.1 V | 0.84 | 0.50 V |
| | 3.1-3.6 V | 0.58 | 0.55 V |
| E_lev0.4_N2 | 1.4-1.7 V | 1.64 | 0.48 V |
| | 2.4-2.7 V | 0.84 | 0.52 V |
| | 6.3-6.8 V | 0.57 | 0.53 V |
| C_n8e18_N2 | 1.4-1.8 V | 1.64 | 0.46 V |
| | 3.3-3.6 V | 0.845 | 0.47 V |
| | 11.4-11.8 V | 1.62 | small |
| C_N0 | 1.6-2.0 V | 0.57 | 0.53 V |

## Open

- Why some switches cost ~100 mA/mm and others under 10. Not analysed.
- The 2- and 3-strike row A cases lost their drops on the 5 nm mesh (meshChkLoad_m5fix). They have no barrier cuts, so it isn't checked whether their pockets still switch, just with smaller current changes.
- A 2.5 nm mesh (new stress run, ~90 h) would show whether the post-switch voltage share converges.

Related: [[step-search-28v]], [[hot-electron-capture]], [[trap-model]], [[rad-literature-steps]].
