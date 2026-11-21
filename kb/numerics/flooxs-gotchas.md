---
title: FLOOXS gotchas
tags: [numerics, reference]
---
# FLOOXS gotchas (learned the hard way)

How FLOOXS works in general: [[flooxs-overview]], [[flooxs-commands]], [[flooxs-expressions]], [[flooxs-solver]], [[flooxs-pdb]]. FLOOXS source for checking behaviour: `~/flooxs/src` (e.g. Newton limits in `diffuse/Newton.cc`, Fermi integrals `f12`/`f32` in `math/Vector.cc`). Three model files are **CRLF**: `model/GaN_modelfile_masterD`, `model/Metal.tcl`, `model/Continuity.tcl` ([[git-conventions]]).

## Structure and mesh

- **A contact takes every border node of its material inside its box** (`src/BasePDE/Boundary/Bound.cc`, `Bound::Build` and `ContactBound::InSide`). So a box that reaches another body of the same material takes that body's border nodes too. FLOOXS says nothing; it panics ("node on two contacts") only when a node lands on two contacts. Until 2026-11-20 the FP box in all three decks took the drain half of the T-gate head this way ([[fp-contact-fix]]). Check a new box with `contact name=<C> size` against a box drawn round the metal alone.
- **`struct infile` clears the device setup:** re-issue the `contact name=… voltage supply=…` lines after it ([[flooxs-commands]]; radIV's stressLoad does this).
- **A loaded structure keeps its own contacts.** The `.str` file holds the contact boundaries, so a state saved before a deck change keeps the old contacts. radIV writes `fpBox=fixed|old` into each saved state's settings file for this reason ([[fp-contact-fix]], [[stress-library]]).
- **Initialize on a state saved at high bias overflows.** With DevPsi at tens of volts near the drain and Qfn = 0, the carrier densities need exp(38.7·30), and FLOOXS stops with "computed a nan or infinite" (rad28strikeL, job 51762900). radIV sets DevPsi, Qfn and Qfp to 0 after `struct infile` and before Initialize, as in a freshly built deck.
- **Mesh spacing grades only between neighbouring lines.** A deck line inside a `meshY` patch keeps its own spacing and breaks the patch. A `meshY` line exactly on a deck line makes zero-area faces and FLOOXS aborts; put helper lines just beside the deck line instead ([[levers]] `meshY`, [[mesh]]).
- `struct nodedataout=` / `nodedatain=` fail on our decks (several regions of one material), so a saved state can only be reused on exactly the same mesh ([[flooxs-commands]]).

## Equations

- **Tcl word splitting in `solution ... val = (...)`:** `val = (($Ntrap) * $occ)` fails with "Ambiguous or unknown parameter *". Build the expression in a variable: `set e "..."; solution ... val = ($e)`.
- **Constant data fields are folded into the equations at `device init`** (`src/BasePDE/ExprStore.cc:527`, `DataConst`). `sel z=0.0 name=F` becomes literal 0, and later `sel` updates are ignored. Initialise switch fields with a tiny spatial variation: `sel z=1.0e-30*(1.0+x*x) name=F`.
- **Redefining a `const` solution after `device init`** doesn't reach the assembled equations (`sel` sees it, Poisson doesn't). Switch behaviour at runtime with data fields.
- `sqrt(dot(DevPsi,DevPsi))` is |E| in V/cm (lengths are cm internally); `dot(Qfn,Qfn)` = |∇Qfn|². Both are wrong on 3D brick meshes in stock FLOOXS (see 3D below).
- `abs()`-based `max()` inside equations has a kink that can make Newton cycle; use a smooth form (softplus) instead.
- **`exp` overflows above an argument of ~709** and FLOOXS stops with "computed a nan or infinite". The trap occupancy w/(1 + g·exp(a)) hit this in off-state stress above Vd ~17.7 V, where a = (Et − Qfn)/Vt > 709 in the deep buffer (jobs 48125435-48161617). Lever `occSafe 1` writes it as w·exp(−a)/(exp(−a) + g), which tends to 0 instead (`model/Poisson.tcl`, `occTerm`). A min(a, 700) cap through abs() (job 48174580) slowed Newton about 10×.
- **Continuity sign (`tranSign`).** FLOOXS reads `grad(S)` as div(coef·∇S), and its own decks write `ddt(Elec) - mob*Elec*grad(Qfn)`. Our continuity equations have the opposite transport sign: `ddt(Elec) + …` and `ddt(Hole) - …` (`model/Continuity.tcl`, `ElecContinuity` and `HoleContinuity`). DC solutions don't see the sign, but a transient is anti-diffusive: the no-strike control could not take a 1 fs step. `tranSign 1` (default 0; seeIV sets 1) flips the transport and thermoelectric terms to FLOOXS's form. Recombination keeps the sign of `ddt` and generation the opposite. DC solutions are unchanged and the contact fluxes change sign (progress.md 2026-11-02, [[see-plan]]).
- **A unary minus on `ddt` doesn't work.** The first tranSign form, `-ddt(Elec)`, let the control run, but every strike failed its first step at every dt: the time term's Jacobian doesn't take the unary minus. Flip the other terms instead (progress.md 2026-11-02).
- **Long expressions overflow the parser buffer.** A one-line F½⁻¹ injection expression segfaulted in `sel` (seeSmoke3, job 48965450), and the field-dependent electron mobility of two materials in one expression stopped with "buffer overflow detected". Build such expressions in stages, one `sel` per part ([[see-plan]]).

## Solver

- **`device init` clears the solver, and its own DC solve builds a new one** (`src/device/device.cc`; `DevControl.cc`, `Clear` and `Solve`). The solver is also rebuilt when the number of points changes (a mesh change), and at the first transient step after `device init` (`DoStep` builds the TR-BDF2 stepper and a new solver when there is none). Settings that are read "when the solver is built" are read at these moments only.
- **`Math iterLimit` is read once per Newton solver** (2026-10-13). The Newton constructor (`diffuse/Newton.cc`) reads `iterLimit`, `updateLimit`, `rhsLimit`, `rhsMax` and `noimpLimit` when the solver is built. A later `pdbSetDouble Math iterLimit` has no effect until the solver is rebuilt (above), so set it before `device init` (as `drivers/pulsedIV.tcl` does with `sweepIterLimit`). Job 45791746, the first `sweepIterLimit` test, ran with 300 for that reason. The 1- and 2-iteration caps of `drivers/eTempDebug_tail.tcl` never took effect either, so its dumps followed full solves ([[energy-balance]]).
- **Convergence parameters are read once per solver build** (2026-10-28, `src/BasePDE/Genpde.cc` `SetConvParams`, called from `SetOffsets` in `DevSolver`'s constructor). `<Mat> <Sol> Abs.Error`, `Rel.Error`, `DampValue`, `Damp` and `Negative` are fetched when the device solver is built, like `Math iterLimit`. `pdbSetDouble` on them mid-run has no effect, so set them before `device init`. This voided the radIV `stressQfnDamp` smoke 47875456 and the `stressQfnAbs` job 48141047; use `qfnAbs`, which radIV sets before `device init`.
- **`catch {device}` + retry is not safe; `catch` + `device restore` is.** See [[munmap-crash]] and [[retry-bisection]].
- A solution needs the **`damp` flag** for its `DampValue` to do anything ([[energy-balance]] lost days to this). For a `!negative` solution, a step that would go negative is cut multiplicatively (to as little as ~e^−10 of the old value) **instead of** damped ([[flooxs-solver]]).
- **The transient is TR-BDF2, hard-coded** (`src/device/DevControl.cc` builds a `Time_TRBDF`; no command switches it). The TR stage enforces F_new = −F_old on rows with no effective time term, such as carrier-free regions and the Qfn/Qfp continuity condition at the AlGaN/GaN interface (`drivers/seeIV.tcl` header). From a quasi-Fermi reset (seeIV `seeMethod qf`, 2026-11-02) no first step converged at any dt down to 1e-75 s, even for a 1e-4 strike. Start a transient from a converged state and add the disturbance as a generation term instead (`seeMethod gen`, `seeGenExpr`; [[see-plan]]).

## Output

- `print1d yv=` exactly on a mesh line (e.g. y = −0.125) panics ("WTF in PlotMesh"); offset by ~1 nm. `print1d xv=` / `yv=` abbreviate `xvalue`/`yvalue`.
- **`print1d` (and the plot mesh) resample to at most 500 points per direction** (`src/plplot/PlotMesh.cc` `MakePlot`: while more than 500 coordinates, merge the closest pair into its midpoint). On a mesh with more than 500 lines along the cut, the printed rows are not the mesh nodes and fine patches are sampled coarser. The 28 V library mesh has 520 y lines and m5fix 554, so a cut showed m5fix's 5 nm patch at y 1.6 as 5-10 nm. Read true node positions from `struct vtk=` (XML VTK; vtkXMLUnstructuredGridReader) instead. Found 2026-11-19.
- **`struct vtk=` writes `const` solutions such as Elec and Hole as 1.0 placeholders.** Copy them into `sel` fields before the dump (seeIV's `MapN` and `MapP`; [[see-plan]]).
- Current in CSVs: `abs([contact name=D sol=Qfn flux])*1e6` = mA/mm (flux is A/µm).
- **Headless runs segfault on `chart`/`plot1d`/`window`**: run a copy with `sed -i 's/^window.*//; s/^\(\s*\)chart /\1#chart /'` (the flooxs-pyplot build draws them with matplotlib instead).

## 3D

- **Stock FLOOXS gradients are wrong on brick meshes** (`src/field/GeomInfo.cc`, `GeomInfoBrick::Gradient` and the brick constructor). On bricks dot(x·1e-4, x·1e-4) = (hx/hz)² and dot(z·1e-4, z·1e-4) = (hz/hx)²; only y is exact. Tets and 2D are exact. Every `dot` and gradient expression on bricks is affected, including the field mobility, the hot-electron field `sqrt(dot(Qfn,Qfn))` in `HotTeExpr` (`model/Poisson.tcl`), ETemp's heating and the stress fields that place damage. It is fixed in `~/flooxs-brickfix` (local only) and in FANGS. HPG's stock FLOOXS still has the bug, and `sweeps/radIV.slurm` runs the stock binary. So don't run a FLOOXS `deviceDim 3` case with traps or field mobility on a stock build ([[3d-plan]], [[flooxs-builds]]).
- **UMFPACK runs out of indices on large 3D meshes.** At 5 z lines it fails with "ERROR: out of memory" at 4.4 GB even with 128 GB allocated (job 51061333): that is the 32-bit index limit of its `di` interface, not RAM. Above about 50k points use ILU+BiCGSTAB (`mathDev3d={row ilu bcgs scale}`), which gave the UMFPACK 3-line answer within 0.05%; ILU+GMRES gives nonsense ([[3d-plan]]).

Related: [[local-runs]], [[hpg-workflow]].
