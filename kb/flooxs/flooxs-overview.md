---
title: FLOOXS overview
tags: [flooxs, reference]
source: ~/flooxs (marklaw59/flooxs e7c2a30f, 2026-07-02)
---
# FLOOXS overview

**FLOOXS** (FLorida Object Oriented X Simulator) is the University of Florida's Tcl-scripted finite-element **process and device** simulator (Mark Law's group; GitHub `marklaw59/flooxs`; manual and tutorials at <http://www.flooxs.ece.ufl.edu/index.php/Manual>). A C++ core (~340 `.cc` files, ~360k lines) registers Tcl commands; a deck is a Tcl script that builds a mesh, declares solutions and equations as **expression strings**, and calls the solver. The licence (`License.pdf`) restricts use outside UF programmes, so keep repos with FLOOXS code private.

## Source layout (`~/flooxs/src`)
| Dir | What it holds |
|---|---|
| `flooxs.cc`, `main.cc` | entry point, Tcl command registration, `GlobalExit` |
| `BasePDE/` | the generic PDE engine: solutions (`Generic.cc` — the `solution` command), equation assembly (`Genpde.cc`, incl. the Newton update/damping), expression lexer/evaluator (`lexical.cc`, `Expr.cc`, `ExprStore.cc`), solver queues (`Solver.cc`), contacts (`Boundary/bndcmd.cc` — the `contact` command) |
| `device/` | the `device` command (`device.cc`), `DevController` (store/restore, exception catch) |
| `diffuse/` | Newton driver (`Newton.cc`: iteration limits, convergence, iteration table) and process diffusion |
| `math/` | `math` command (linear-solver selection, `MathParam.cc`), sparse matrices, Fermi integrals `f12`/`f32` (`Vector.cc`) |
| `field/`, `mater/`, `front/`, `LevelSet/`, `triangle/` | mesh, materials, interfaces, level sets, triangulation |
| `plot/`, `plplot/`, `pltcltk/` | `sel`, `print1d`, `peak`, plot windows (`window`, `chart`, `plot1d/2d/3d`; PLplot) |
| `implant/`, `etch/`, `db/` … | process simulation (implant, etch, deposit, oxidize, diffuse) — unused here |
| `FLOOXS.models`, `param.tcl` | default models/packages (`DevicePackage`, default `math` settings) and pdb helpers |

Outside `src/`: `Params/` (parameter database files per material/interface), `TclLib/` (Tcl library: models, GUI, plotting), `Test/` (example decks; `Test/SimpDev` device examples), `HPG/` (the HiPerGator environment notes: `module restore flooxsenv` = ufrc, conda, cuda 12.8.1, intel 2025.1.0, boost 1.88.0; conda env `flooxs`).

## How HEMTRAD uses it
Device simulation only: drift–diffusion (Poisson + electron/hole continuity with quasi-Fermi levels `Qfn`/`Qfp` as unknowns), trap charge as expression solutions, contacts as boundary equations. See [[flooxs-commands]], [[flooxs-expressions]], [[flooxs-solver]], [[flooxs-pdb]], [[flooxs-builds]]; project-specific pitfalls in [[flooxs-gotchas]] and [[munmap-crash]].
