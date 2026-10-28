---
title: FLOOXS gotchas
tags: [numerics, reference]
---
# FLOOXS gotchas (learned the hard way)

How FLOOXS works in general: [[flooxs-overview]], [[flooxs-commands]], [[flooxs-expressions]], [[flooxs-solver]], [[flooxs-pdb]].

- **Tcl word splitting in `solution ... val = (...)`:** `val = (($Ntrap) * $occ)` fails with "Ambiguous or unknown parameter *". Build the expression in a variable: `set e "..."; solution ... val = ($e)`.
- **Constant data fields are folded into the equations at `device init`** (`src/BasePDE/ExprStore.cc:527`, `DataConst`). `sel z=0.0 name=F` becomes literal 0, later `sel` updates are ignored. Initialise switch fields with a tiny spatial variation: `sel z=1.0e-30*(1.0+x*x) name=F`.
- **Redefining a `const` solution after `device init`** doesn't reach the assembled equations (`sel` sees it, Poisson doesn't). Switch behaviour at runtime with data fields.
- `sqrt(dot(DevPsi,DevPsi))` is |E| in V/cm (lengths are cm internally); `dot(Qfn,Qfn)` = |∇Qfn|².
- Current in CSVs: `abs([contact name=D sol=Qfn flux])*1e6` = mA/mm (flux is A/µm).
- **`catch {device}` + retry is not safe; `catch` + `device restore` is** — see [[munmap-crash]] and [[retry-bisection]].
- A solution needs the **`damp` flag** for its `DampValue` to do anything ([[energy-balance]] lost days to this). And for a `!negative` solution a step that would go negative is cut multiplicatively (to as little as ~e^−10 of the old value) **instead of** damped ([[flooxs-solver]]).
- `abs()`-based `max()` inside equations has a kink that can make Newton cycle; use a smooth form (softplus) instead.
- `print1d yv=` exactly on a mesh line (e.g. y = −0.125) panics ("WTF in PlotMesh"); offset by ~1 nm. `print1d xv=` / `yv=` abbreviate `xvalue`/`yvalue`.
- `pdbSetDouble Math iterLimit N` caps Newton iterations (default 20) — handy for capped-iteration debug dumps.
- **Headless runs segfault on `chart`/`plot1d`/`window`**: run a copy with `sed -i 's/^window.*//; s/^\(\s*\)chart /\1#chart /'` (the flooxs-pyplot build draws them with matplotlib instead).
- FLOOXS source for checking behaviour: `~/flooxs/src` (e.g. Newton limits in `diffuse/Newton.cc`, Fermi integrals `f12`/`f32` in `math/Vector.cc`).
- Three model files are **CRLF**: `model/GaN_modelfile_masterD`, `model/Metal.tcl`, `model/Continuity.tcl` ([[git-conventions]]).

Related: [[local-runs]], [[hpg-workflow]].

**`Math iterLimit` is read once per Newton solver** (2026-10-13): FLOOXS builds the Newton object (and reads `iterLimit`, `updateLimit`, `rhsLimit`) at the first `device` solve after `device init` (`DevControl.cc` `Solve`; `device init` calls `Clear()`). Changing `pdbSetDouble Math iterLimit` later has no effect until the next `device init`. Job 45791746 (the first `sweepIterLimit` test) ran with 300 for that reason; `drivers/eTempDebug_tail.tcl`'s 1/2-iteration caps were therefore not real caps either.

**Convergence parameters are read once per solver build** (2026-10-28, `src/BasePDE/Genpde.cc` `SetConvParams`, called from `SetOffsets` in `DevSolver`'s constructor): `<Mat> <Sol> Abs.Error`, `Rel.Error`, `DampValue`, `Damp`, `Negative` are fetched when the device solver is built (first `device` after `device init`, or after a mesh change), like `Math iterLimit`. `pdbSetDouble` on them mid-run has no effect, so set them before `device init`. (This voided the radIV `stressQfnDamp` smoke 47875456 and `stressQfnAbs` job 48141047.)
