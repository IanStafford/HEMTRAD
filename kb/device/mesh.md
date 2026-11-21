---
title: Mesh
tags: [device, numerics, caveat]
date: 2026-11-20
source: model/rfdevice.tcl; ~/flooxs/src/field/PermStore/Tensor.cc (LineExpand), ~/flooxs/src/field/Utils/dvpram.cc; progress.md 2026-11-19/20; sweeps/params_meshChk*.txt, params_fpFix*.txt
---
# Mesh

## Deck lines (`model/rfdevice.tcl`, no `meshY`)

- **Depth (`line x`):** 1 nm from x −0.005 to 0.015 µm (the 5 nm nitride under the gate stem and the 15 nm AlGaN), so the first GaN line is 1 nm below the interface. It grades to 10 nm at x −0.05 and x 0.1, then to 0.25 µm at the buffer bottom (x 7.5). Above the SiN: 10-25 nm through the T-gate head layer, about 50 nm in the FP.
- **Lateral (`line y`), spacing at each deck line:** 50 nm at the mesh edges (−1.25, 3.41) and the drain contact edge (3.285); 30 nm at `SourceT` (−0.325); 10 nm at the gate source edge; **5 nm at the gate drain edge** (0.125); 10 nm at `leftFP` (0.285) and `DrainT` (0.485); 20 nm at `rightFP` (0.725).
- So the gate-drain access region grades from 20 nm at y 0.725 to 50 nm at 3.285: about 21 / 30 / 40 nm at y 0.8 / 1.6 / 2.4 (computed with the line rule below).
- `bot2d` and `yCoarse` (2026-11-12, default off) coarsen the buffer depth and the y spacing for 3D comparisons ([[3d-plan]]).

## How FLOOXS places lines

Each `line` sets the wanted spacing at that line. Between two neighbouring lines FLOOXS grades the spacing geometrically from one value to the other, with the ratio capped at 1.5 (`dvpram.cc`). Two neighbours with the same spacing give a uniform interval. A line's spacing acts only on the two intervals next to it.

## `meshY` refinement (all decks)

`meshY={y spacing y spacing ...}` in µm adds y lines ([[levers]]). Rules:
- Order doesn't matter; FLOOXS sorts the lines.
- **A deck line inside a patch keeps its own spacing.** `rightFP` (0.725, 20 nm) and `DrainT` (0.485, 10 nm) break any patch around them. Cancel them with helper lines just beside them, for example 0.72 and 0.73 at 5 nm (as m5fix does).
- **A `meshY` line exactly on a deck line** makes zero-area faces and FLOOXS aborts.
- Two patch lines with the same spacing make everything between them uniform. The library's 0.96 and 1.44 lines at 5 nm make y 0.96-1.44 a uniform 5 nm.
- Check a new mesh from its true nodes (`struct vtk=`, read with vtkXMLUnstructuredGridReader). **Don't read spacings from `print1d` cuts:** FLOOXS resamples a cut to at most 500 points per direction by merging the closest pairs (`src/plplot/PlotMesh.cc`). The library (520), m5fix (554) and m2p5 (947, computed; see the table below) meshes have more than 500 y lines, so a cut shows their fine patches coarser than they are ([[flooxs-gotchas]]).

## Meshes in use

Lines marked * are computed with a Python port of the FLOOXS line rule. The port reproduces the VTK counts of the library (520) and m5fix (554) and the m10 count implied by its job log exactly, but the starred values were not checked against a VTK export.

| Name | `meshY` | y lines | Spacing at the 2DEG | Used by |
|---|---|---|---|---|
| deck | none | 211* | ~21 nm at y 0.8, 30 at 1.6, 40 at 2.4* | pulsedIV era, Oct runs without meshY |
| Nov 11 model | {0.3 0.01 2.0 0.01} | 273* | 10 nm over y 0.3-0.485 and near 2.0; 10-16 nm over y 0.5-0.65 and ~20 nm at y 0.8, because `rightFP` (0.725, 20 nm) sits inside the patch (`DrainT` has the patch's 10 nm)* | radFinal12, radEB1 50411481, fpFixEB1 52134554 |
| library | {0.3 0.01 2.6 0.01 0.64 0.005 0.96 0.005 1.44 0.005 1.76 0.005 2.24 0.005 2.56 0.005} | 520 (VTK) | 9.5-17.2 nm at y 0.76-0.90 (15 nm at 0.8); 5 nm over 0.96-2.56; 5.5-10 nm over the SiN damage core (y 0.48-0.63)*, which no check has refined | the 28 V stress library and every strike round loaded from it ([[stress-library]]) |
| m10 | {0.3 0.01 0.715 0.01 0.735 0.01 2.6 0.01} | 356 (the job log's 63,724 points = 179 x lines × 356) | 10 nm uniform over y 0.3-2.6 | meshChkStress 51883722, meshChkLoad_m10 51939191, radStepM 52044406 (3 tasks), radStepM2 52072550 |
| m5fix | the library plus 0.72 and 0.73 at 5 nm | 554 (VTK) | a true 5 nm over y 0.64-2.56; identical to the library elsewhere | meshChkStress 51883722, meshChkLoad_m5fix 51939192, radStepM 52044406 (14 tasks) |
| m2p5 | m5fix with 2.5 nm patches | 947* | 2.5 nm over y 0.64-2.56 | old-box stress meshChkStress2p5 52044407 cancelled at Vd 20; fixed-box stress fpFixMesh 52135538 queued |

The radEB2 "5 nm check" of the Nov 11 model (job 50470082, meshY {0.3 0.005 2.0 0.005}) has the same problem: DrainT and rightFP sit inside the patch, so y 0.5-0.65 stays at 10-16 nm and y 0.8 at ~19 nm*. That check refined only the two ends of the patch, not the SiN damage region.

All library, m10 and m5fix stress states were saved with the old FP contact box. The library and the m5fix / m2p5 stresses are being redone with the fixed box ([[fp-contact-fix]]).

## Convergence status (pre-fix; being rerun, [[fp-contact-fix]])

- **28 V stress damage alone** (scale 1.5e18): the drop at 1.6-2.0 V, 395 → 273-281 mA/mm, agrees within 8 mA/mm on the library, m10 and m5fix meshes ([[step-search-28v]]).
- **Strike steps are mesh-sensitive.** Row A (6e18 strikes, trap 0.30 eV) gives 3 / 2 / 1 drops for 1 / 2 / 3 strikes on the library mesh and 2 / 1 / 0 on m5fix. Only trap 0.30 eV with 8e18 strikes keeps 2 / 3 / 3 drops on all three meshes. Its first drop starts within 0.1 V across meshes; the later drops move with the mesh. The mechanism is in [[step-mechanism]]; 2.5 nm is the next check.
- **Hand-placed Gaussian traps** (σ 40 nm, no stress damage): the first drop converges between 5 and 2.5 nm; later drops (7-9 V) move and change size ([[damage-region-map]]).
- **Uniform sharp-edged sites** (radMesh, job 49606872, 2026-11-05): a 0.3 µm, 4e18 site gives steps of 84-157 mA/mm on the deck mesh and under 8 at 10 and 5 nm. The SiN two-step curve of the Nov 5 radFine run (job 49735196) lost its steps at 10 nm. So steps from sharp-edged sites were mesh artifacts ([[damage-region-map]]).
- **Rule of thumb from these checks:** use `meshY` for any sharp-edged site before trusting a step, and 5 nm or finer above about 6e18. It is not sufficient for strikes: row A (6e18) still changes between 10 and 5 nm.

## Static and field era (history)

Before `meshY` existed, traps narrower than a few cells in the access region were not resolved, though their total charge was (±15%). The runaway depends on the local field, which a coarse mesh smears (static §10h, `archive/static_mobility/RESULTS.md`). A local check (4e18 / 0.55 eV at the surface, y 1.25 µm, `line y loc=1.25 spac=0.004`) found:
- A 0.1 µm / 45° cone: no effect on the deck mesh, but a ~325× collapse at 0.2 V on the 4 nm mesh. So the static-era cone results in the access region are mesh artifacts.
- A Gaussian with σ 40 nm still collapses, but the onset comes ~0.1 V earlier and the pre-collapse peak roughly halves on the fine mesh.

So access-region Gaussian results of that era are qualitatively robust and quantitatively mesh-sensitive (onset ±0.1 V).

Gotcha: `print1d yv=` exactly on a mesh line at the gate edge (y = −0.125) panics FLOOXS ("WTF in PlotMesh"); offset cuts by ~1 nm ([[flooxs-gotchas]]).

Related: [[device-structure]], [[stress-library]], [[step-search-28v]], [[static-era-lessons]].
