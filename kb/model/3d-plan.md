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
