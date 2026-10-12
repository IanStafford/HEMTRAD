---
title: FLOOXS gotchas
tags: [numerics, reference]
---
# FLOOXS gotchas (learned the hard way)

- **Tcl word splitting in `solution ... val = (...)`:** `val = (($Ntrap) * $occ)` fails with "Ambiguous or unknown parameter *". Build the expression in a variable: `set e "..."; solution ... val = ($e)`.
- **Constant data fields are folded into the equations at `device init`** (`src/BasePDE/ExprStore.cc:527`, `DataConst`). `sel z=0.0 name=F` becomes literal 0, later `sel` updates are ignored. Initialise switch fields with a tiny spatial variation: `sel z=1.0e-30*(1.0+x*x) name=F`.
- **Redefining a `const` solution after `device init`** doesn't reach the assembled equations (`sel` sees it, Poisson doesn't). Switch behaviour at runtime with data fields.
- `sqrt(dot(DevPsi,DevPsi))` is |E| in V/cm (lengths are cm internally); `dot(Qfn,Qfn)` = |∇Qfn|².
- Current in CSVs: `abs([contact name=D sol=Qfn flux])*1e6` = mA/mm (flux is A/µm).
- **`catch {device}` + retry is not safe; `catch` + `device restore` is** — see [[munmap-crash]] and [[retry-bisection]].
- A solution needs the **`damp` flag** for its `DampValue` to do anything ([[energy-balance]] lost days to this).
- `abs()`-based `max()` inside equations has a kink that can make Newton cycle; use a smooth form (softplus) instead.
- `print1d yv=` exactly on a mesh line (e.g. y = −0.125) panics ("WTF in PlotMesh"); offset by ~1 nm. `print1d xv=` / `yv=` abbreviate `xvalue`/`yvalue`.
- `pdbSetDouble Math iterLimit N` caps Newton iterations (default 20) — handy for capped-iteration debug dumps.
- **Headless runs segfault on `chart`/`plot1d`/`window`**: run a copy with `sed -i 's/^window.*//; s/^\(\s*\)chart /\1#chart /'` (the flooxs-pyplot build draws them with matplotlib instead).
- FLOOXS source for checking behaviour: `~/flooxs/src` (e.g. Newton limits in `diffuse/Newton.cc`, Fermi integrals `f12`/`f32` in `math/Vector.cc`).
- Three model files are **CRLF**: `GaN_modelfile_masterD`, `Metal.tcl`, `Continuity.tcl` ([[git-conventions]]).

Related: [[local-runs]], [[hpg-workflow]].
