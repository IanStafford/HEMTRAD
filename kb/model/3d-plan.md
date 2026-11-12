---
title: Plan for a 3D device
tags: [model, plan, flooxs]
date: 2026-11-12
---
# Plan for a 3D device

## Why 3D

The 2D model assumes every damage site spans the full 200 µm gate width. A real ion track is about 0.16 µm wide, and at 1e7 cm⁻² about 93 land on the device ([[critical-strike]]). The partial-width estimate ([[damage-region-map]]) says isolated tracks are far too narrow to matter, but it leaves out two things only 3D can show:
- how current spreads around a damaged column;
- whether a local strike can switch a large part of the width at once.

That second point is the leading candidate for R33's large single-point drops, which would need 26–92 µm of width to switch together.

## What FLOOXS supports (source survey, 2026-11-12)

| Need | Status | Where |
|---|---|---|
| 3D tensor mesh | yes: `line z`, `region ... zlo= zhi=` | `src/field/PermStore/Tensor.cc:38, 134-137, 224-226` |
| Elements | bricks with `init quad`; plain `init` remeshes to tets with TetGen | `initialize.cc:163, 197-199` |
| Extrusion of a 2D mesh | none; every `line`/`region` gets z tags by hand | `initialize.cc:71-83` (compiled out) |
| Device equations, `grad`/`dot` | dimension-generic; 3D branches present | `BasePDE/Genpde.cc:842-847`, `Reduce.cc:652-654` |
| Contacts | `zlo`/`zhi`; flux in 3D is total current, so divide by the width | `Bound.cc:35-47` |
| Interfaces (our polarization charge) | code is generic, but no 3D test with an interface equation exists | `field/SuperBound.cc:61-90` |
| Solvers | UMFPACK direct (32-bit indices), ILU/BiCGSTAB/GMRES, Woodbury; no PARDISO/MUMPS/PETSc/MPI; `math` settings are per dimension | `math/MathParam.cc:127-131, 259-295` |
| Output | `print1d` with two of x/y/z values, `slice`, `struct vtk=` | `plot/print_1d.cc:52-61` |
| 3D device examples | single-material only (resistor, diodes) | `Test/SimpDev/res3d.tcl`, `ZeroBiasDiode` |

**Main risks, in order:**
1. **`MakeInterfaces` panic** ("Border Problems") where three or more materials meet along a line in a non-uniform arrangement (`field/fsint.cc:131-205`). A plain extrusion, with every region spanning the full z range, is the case that works. Our deck has six materials, plus the `gas` region `init` adds unless `nogas` is given.
2. **No validated multi-material 3D device case** to compare against.
3. **Size.** Our 2D meshes have 37–56k points (up to about 100k with local refinement), and times 20–40 z lines that is millions of unknowns. That's too much for UMFPACK, and ILU/BiCGSTAB convergence on this Jacobian is unproven.
4. **Brick accuracy on strongly graded meshes** (1 nm next to 0.25 µm) is untested.

## The simulation to aim for

A **slice of the gate width**, not the whole 200 µm:
- width W along z, with reflecting (zero-flux) side walls;
- one track as a Gaussian column at one wall.

By symmetry that's a periodic row of tracks spaced 2W apart along the width. Then:
- W of 0.16 µm reproduces the 2D full-width result;
- large W approaches the undamaged device;
- the curve in between measures current spreading directly, against the parallel-column estimate.

## Phases

**Phase 0: does it build? (local, small, one FLOOXS run at a time)**
- Write `model/rfdevice3d.tcl`: the 2D deck with `line z` (3–5 lines over 0.5 µm) and every region spanning the full z range, as a plain extrusion.
- Try `init quad` (bricks), with and without `nogas`.
- Coarsen it first: buffer cut from 7.5 to about 1.5 µm deep, coarser y away from the gate and damage. Check the 2D current is unchanged by the coarsening.
- **Pass:** `init` succeeds, with no `MakeInterfaces` panic.

**Phase 1: does it match 2D?**
- Pre-irradiation Id–Vg and Id–Vd at Vg +1 on the extruded mesh, z-uniform, with `math device dim=3` set explicitly.
- Current divided by W has to match the coarsened 2D deck within about 1%. This also tests the polarization interface equation in 3D.
- Then the final rad model, z-uniform, against its 2D curve.

**Phase 2: size and solver (HPG)**
- Scale z lines (5, 10, 20) and the 2D base mesh.
- Record nodes, memory and time per Newton step for UMFPACK and for ILU/BiCGSTAB.
- Ask for 32–64 GB per task if needed.
- Outcome: the largest mesh that solves an Id–Vd sweep in under about 24 h.

**Phase 3: damage that varies along the width**
- Driver levers, default off: z limits on `damSites`, and a z centre and width on `damGauss`, so a track becomes a column in (y, z).
- The stress-field E⁴ damage stays z-uniform (the stress field is), multiplied by a z profile when a strike is local.
- Contact current divided by W.

**Phase 4: science runs**
- Slice width W = 0.16, 0.5, 1, 2, 4 µm with one track: Id(Vd) per mm against W, compared with 2D and the partial-width estimate.
- Track density and depth near the threshold where the 2D section collapses.
- Two tracks at different z: do their collapses merge or stay separate?
- Field and trap-occupancy cuts along z: does a collapse spread sideways from the track?

## Fallbacks

- **If bricks fail:** TetGen tets (plain `init`), or a mesh imported through `gmsh_read=`/`tdr=`. Both have unverified units or element mapping.
- **If size defeats UMFPACK:** ILU/BiCGSTAB, a thinner slice, or only the y range around the gate and damage. The flooxs-pyplot port (FANGS) has STRUMPACK and threaded assembly; that would be Ian's call, since it's a separate private project.
- **If the interface panics:** move the material boundary where three meet, or simplify the T-gate/field-plate geometry for the 3D deck only.

Related: [[critical-strike]], [[damage-region-map]], [[mesh]], [[flooxs-overview]], [[flooxs-solver]].

## Results so far (2026-11-12)

**TRIM, model-deck stacks** (Au 2256 MeV, full cascades, 200 ions, local, 22 s each; `analysis/trimTrack.py`, `data/trim/*_track.json`):
- Totals agree with TRIM's own vacancy counts within 3%.
- Top 50 nm of GaN: 0.21–0.27 vacancies per nm per ion, median radius 1.5–2 nm, on-axis density about 1e17–2e18 cm⁻³.
- Most ions leave no vacancy in the 15 nm AlGaN.
- Nuclear displacements alone are below the collapse threshold, so the electronic track core (Se about 41 keV/nm in GaN) carries the damage.

**Build** (rad3dBuild, job 51045898):
- Bricks without the gas region (`init quad nogas`) build the full multi-material deck with no MakeInterfaces failure.
- Tetrahedra fail (TetGen error code 2).
- 3 z lines over 0.5 µm: 51k points, 1.9 GB, about 1 min per Vd point.
- UMFPACK fails ("numeric factorization") at 5 z lines (85k points) and 11 (187k), at about 4.4 GB, so not memory.

**Validation** (rad3dSolve, job 51052220): pre-irradiation 3D at 3 z lines against 2D at the same coarsening (buffer 1.5 µm, y spacing ×2).

| Deck | Id–Vd max difference | Vth 3D / 2D | gm 3D / 2D |
|---|---|---|---|
| HighK | 0.15% | −2.9979 / −2.9964 V | 68.67 / 68.14 |
| SiN | 0.14% | −2.9976 / −2.9961 V | 69.05 / 68.51 |

- The coarsening itself adds +1.6% at 1 V and +0.4% at 10 V against the standard 2D mesh, a little over the 1% target at low Vd. It's the same for 2D and 3D, so comparisons on one mesh are clean.
- The polarization interface works in 3D.

**Solver:**
- ILU+BiCGSTAB (`mathDev3d={row ilu bcgs scale}`) at 5 z lines gives the UMFPACK 3-line answer within 0.05% (373.55 against 373.60 mA/mm at 1 V). It's slower, about 15 min per Vd point against about 1 min.
- ILU+GMRES gives nonsense (3080 mA/mm at 0.75 V) and is not used.
- 11 z lines (187k points) with BiCGSTAB: 373.60 mA/mm at 1 V, identical to 3 lines; 4 points in 2h25, 4.4 GB.
- UMFPACK at 5 z lines fails with "ERROR: out of memory" at 4.4 GB even with 128 GB allocated (job 51061333): the 32-bit index limit of the `di` interface, not RAM. Above about 50k points BiCGSTAB is the solver.
- First tracks (rad3dTrack1 51061334, SiN, core sigma 30 nm): about 1-1.5 h per Vd point; results pending.

