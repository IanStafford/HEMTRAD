---
title: FLOOXS Tcl commands
tags: [flooxs, reference]
source: ~/flooxs/src (flooxs.cc, BasePDE/Generic.cc, device/device.cc, BasePDE/Boundary/bndcmd.cc, math/MathParam.cc, plot/tclsel.cc)
---
# FLOOXS Tcl commands (the ones HEMTRAD uses)

Parameters are `name=value` or boolean flags (`flag` / `!flag`); names can be abbreviated when unique (`xv` = `xvalue`).

## Structure
- `line x|y loc=<µm> spac=<µm> tag=<name>` — mesh lines and spacing (e.g. `model/rfdevice.tcl`).
- `region <Material> xlo=<tag> xhi=<tag> ylo=… yhi=…` — assign a material to a box of tags.
- `init` — build the mesh (`init nogas`).
- `mater add name=<M> [alias=…]` — declare a material.
- `contact name=<C> <Material> xlo= xhi= ylo= yhi= add depth=1 width=1` — define a contact on a material's nodes in a box; then `contact name=<C> [current=<expr>] voltage supply=<V>`; `contact name=D supply=$d` sets the bias; `contact name=D sol=Qfn flux` returns the flux (A/µm in our units → ×1e6 = mA/mm). Also `list`, `size`, `get_supply`, `ac` options.

## Solutions and equations
- `solution add name=<S> solve|nosolve|const [pde|linear] [damp] [negative|!negative] [continuous] [val=<expr>]` — declare an unknown (`pde`), an expression evaluated from others (`const val=…`), or a fixed field. Flags: `damp` enables Newton damping with the pdb `DampValue` ([[flooxs-solver]]); `negative` allows negative values (otherwise positivity is enforced multiplicatively); `continuous` = continuous across material interfaces; `dampval=` sets a damping value directly. Material-restricted form: `solution add name=Elec solve GaN const val=(...)`. `solution list|status|print`.
- Equations are pdb strings: `pdbSetString <Mat> <Sol> Equation "<expr>"`, interfaces `<Mat1>_<Mat2> <Sol> Equation`, contacts `<Contact> <Sol> Equation` with `Fixed 1` (Dirichlet), `Flux 1`, `Flux.Scale 1.602e-19` ([[flooxs-pdb]]).
- `sel z=<expr> [name=<field>]` — evaluate an expression on every node and store it as a data field (default name `z`); used for doping, trap memory fields, Te. `newton <Mat> eqn=<expr> var=<sol> damp=<v>` — scalar Newton on one material (initial guesses in `Initialize`).

## Solving
- `device` — solve the coupled steady-state system (Newton; [[flooxs-solver]]). Options: `init` (build/initialise the device system), `store` / `restore` (save the converged solution PREV↔CURR; `restore` also clears the solver queues — see [[munmap-crash]]), `time=`/`offset=`/`userstep=` (transient), `freq=` (AC), `Temperature=`, `diagnostic=`, `clear`, `silent`.
- `math <analysis> dim=<n> <matrix> <precond> <iter> [scale] [tolerance=] [max.iter=]` — linear solver per analysis (`device`, `diffuse`, `ac.device`): matrix `col`/`row`/`eigencol`/`eigenrow`, method `umf` (UMFPACK LU) or `ilu`, iteration `none` (direct) / `bcgs` / `gmres`. HEMTRAD: `math device dim=2 col umf none scale`.
- `pdbSetDouble Math iterLimit N` (and `updateLimit`, `rhsLimit`, `rhsMax`, `noimpLimit`) — Newton controls.

## Output and inspection
- `peak <Material>` — "Peak <value> at <x> <y> <z>" of the selected field (locations in cm); `[lindex [peak GaN] 1]` = value.
- `print1d xv=<x>` / `yv=<y>` — text cut through the selected field along y (or x); returns `{distance value material}` rows on the plot grid, which is resampled to at most 500 points per direction (not the mesh nodes on fine meshes). A cut exactly on a mesh line can panic ([[flooxs-gotchas]]).
- `window`, `chart graph= curve= xval= yval=`, `plot1d`, `plot2d`, `plot3d` — PLplot windows (segfault headless in the stock build; strip them).
- `interpolate`, `profile`, `integrate`, `struct` (save/load), `select`.

All registered commands also include the process-simulation set (`implant`, `etch`, `deposit`, `oxidize`, `diffuse`, `furnace`, `rta`, `stress`…), Schrödinger/k·p solvers (`schro`, `kp`), `picard`, `mc`, `pod` — unused in HEMTRAD.

## `struct`: saving and reloading a solved device (tested 2026-11-14)

- `struct outfile=f.str` writes the whole structure: mesh, contact boundaries and every node field, including the solution variables and any `sel` field (e.g. `Estress`). The 2D deck is about 15 MB.
- `struct infile=f.str` in a fresh run (after sourcing `GaN_modelfile_masterD`, without the device deck) restores it. After re-issuing the five `contact name=… voltage supply=…` lines, `device` converged in **1 Newton iteration** and gave the same drain current to all printed digits (9.751801e-05 at Vd 0.5 V) as the run that wrote it. `Estress` came back with the same peak.
- `struct nodedataout=` / `nodedatain=` (fields only, onto a mesh rebuilt by the deck) **fails on our decks**: the reader finds regions by material name (`FieldServer::ReadNodeData`, `src/field/PermStore/struct.cc:887`) and our decks have several regions of one material (Metal, HighK, Nitride ×3), so it panics "Node not found in node data read in". It would need a FLOOXS change to match regions by index.
- No command maps a 2D field onto a different mesh (`profile` is 1D), so reuse needs exactly the same mesh: same deck, same `meshY`, same coarsening levers.

