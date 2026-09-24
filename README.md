# HEMTRAD

TCAD simulation decks and figure-generation notebook for a GaN HEMT device paper. This repo generates the simulated I-V and field data used in the paper's figures and combines it with imported experimental measurements.

## Overview

Device simulations are run with [FLOOXS](https://www.flooxs.ece.ufl.edu/) (Florida Object Oriented X-platform Simulator), a TCL-scripted TCAD tool. The Tcl files here define the device structure, material physics, and bias sweeps for a GaN HEMT (field-plate and T-gate variants). Simulation output is written as CSV to `figures/`, and `figures.ipynb` loads those CSVs — together with experimental data received from collaborators (e.g. Dr. Anderson) — to produce the plots used in the paper.

## Repository layout

**Device structure**
- [`rfdevice.tcl`](rfdevice.tcl) — defines the field-plate/T-gate HEMT geometry, mesh, contacts, and doping (`HEMT_Struct`)

**Material and physics models** (sourced by the model file, generally not run directly)
- [`GaN.tcl`](GaN.tcl), [`AlGaN.tcl`](AlGaN.tcl), [`Insulator.tcl`](Insulator.tcl), [`Metal.tcl`](Metal.tcl) — material parameters (bandgap, affinity, mobility, effective mass) for each region
- [`Poisson.tcl`](Poisson.tcl), [`Continuity.tcl`](Continuity.tcl) — Poisson and electron/hole continuity equation definitions; `Poisson.tcl` also holds the acceptor trap model (hot-electron capture, freeze/fill-only trap memory)
- [`GaN_modelfile_masterD`](GaN_modelfile_masterD) — top-level model file; sources the material/physics files above, sets up solution variables, interface charge, and trap distributions, and defines `Initialize`

**Measurement/sweep drivers**
- [`IV.tcl`](IV.tcl) — sweeps drain voltage at several fixed gate voltages, writes `figures/fpIV*.csv`
- [`run_measurements.tcl`](run_measurements.tcl) — `run_measurements` proc: gate sweep at fixed Vd, plus a peak-field vs. Vds sweep when a peak-field CSV path (not `"null"`) is given
- [`transfer.tcl`](transfer.tcl), [`fieldpeak.tcl`](fieldpeak.tcl) — call `run_measurements` for the transfer curve / peak field
- [`trapPlot.tcl`](trapPlot.tcl) — I-V sweep with trap occupation enabled, plots trap concentration profiles across the channel
- [`pulsedIV.tcl`](pulsedIV.tcl) — pulsed curve-tracer Id-Vd sweep with trap memory (radiation-induced current collapse); tunable trap/hot-electron levers at the top
- [`stressFreeze.tcl`](stressFreeze.tcl) — stress at a quiescent bias, freeze the traps, then measure Id-Vd

**Figures**
- [`figures/`](figures/) — output directory for simulation CSVs (empty until simulations are run; also where experimental CSVs should be placed)
- [`figures.ipynb`](figures.ipynb) — Python notebook that reads the simulation and experimental CSVs and generates the paper's figures

> **Note:** `IV.tcl` sources `powerdevice.tcl`, which is not currently present in this repo. That deck (or a replacement such as `rfdevice.tcl`) needs to be added before `IV.tcl` will run.

## Generating simulation data

1. Install FLOOXS and make sure the `flooxs` executable is on your `PATH`.
2. From the repo root, run the desired driver script, e.g.:
   ```sh
   flooxs IV.tcl
   flooxs trapPlot.tcl
   ```
3. Output CSVs are written to `figures/` (paths are relative, so always run from the repo root).

To change device geometry or bias points, edit the `set` variables at the top of [`rfdevice.tcl`](rfdevice.tcl) (gate length, field-plate offsets, layer thicknesses, etc.) or the sweep ranges in the driver script's `for` loops.

## Importing experimental results

Experimental data (e.g. from collaborators) should be dropped into `figures/` as CSV, matching the format the notebook expects for that measurement (see the `flooxsRead`/`loadtxt` calls in `figures.ipynb`). The notebook currently has some hardcoded absolute paths from an earlier version of this repo (`/home/staffian/banjo-wombat/highK/figures/...`) — update these to relative `figures/...` paths as they're revisited.

## Generating figures

Open [`figures.ipynb`](figures.ipynb) and run the cells. It requires `numpy`, `pandas`, `matplotlib`, and `scipy`. Each figure section loads its simulation CSV(s) and, where available, the corresponding experimental CSV, and plots them together (I-V curves, peak electric field, trap occupation profiles, etc.).

## Status

See git history for progress notes. Known open items:
- High-k dielectric variants need threshold voltage and slope tuning against experimental data
- Microstructure near the gate contact is not fully characterized (possible hole accumulation at high doping)

radplot + trapOccupation stats
level = 0.78
location = 0.145
density = 3.68e18

will update for each fine tuned solution

radplot1 + trapOccupation1 stats
level = 0.75
location = 0.16
density = 3.78e18