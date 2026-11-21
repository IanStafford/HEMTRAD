# HEMTRAD

FLOOXS (Tcl) TCAD model of **radiation-induced current collapse** in an AlGaN/GaN HEMT (HfO2/HighK passivation, T-gate + field plate), with HiPerGator sweep templates and Python analysis.

Knowledge base: **`kb/index.md`** (Obsidian second brain). Agent rules: `CLAUDE.md`. Dated log: `progress.md`.

The repository is public. Measured radiation data stays on the workstation and is gitignored (`kb/workflow/git-conventions.md`).

## Layout

| Folder | Contents |
|---|---|
| `model/` | the device model, sourced together: `GaN_modelfile_masterD` (levers, materials, equations), `GaN.tcl`, `AlGaN.tcl`, `Insulator.tcl`, `Metal.tcl`, `Continuity.tcl`, `Poisson.tcl` (traps), `ETemp.tcl` (energy balance), device decks `rfdevice.tcl` (HighK) / `rfdevice_SiN.tcl` / `rfdevice3d.tcl` (3D slice, `kb/model/3d-plan.md`). Three files are CRLF (`GaN_modelfile_masterD`, `Metal.tcl`, `Continuity.tcl`) |
| `drivers/` | Tcl drivers: `radIV.tcl` (pre/post-irradiation stress, damage and Id–Vg / Id–Vd; the main driver since 2026-10-23), `seeIV.tcl` (single-event transient), `pulsedIV.tcl` (pulsed curve-tracer Id–Vd, the Sep–Oct work), `calibIdVg.tcl` (transfer curve), `fieldPlate.tcl` (trap-free field-plate check), `render3d_build.tcl` (3D slice VTK for rendering); `drivers/trim/` holds the SRIM TRIM input files |
| `sweeps/` | SLURM templates and their `params_*.txt`: `radIV.slurm` for every run since 2026-10-23 (`DRV` picks radIV / seeIV / pulsedIV); the `pulsedIV_*.slurm` files are October records (only `pulsedIV_eTemp.slurm` takes `PARAMS`/`RUN`; the others hard-code one study); index of every params file, its runs and job IDs in `sweeps/README.md` |
| `bin/` | workflow helpers: `hpg_reconnect.sh` (reopen the HPG connection with key + Duo push), `trim_run.sh` (SRIM TRIM in batch under Wine) |
| `analysis/` | Python analysis and plotting (`analyze_*.py`, `plot_*.py`, `rad*.py`, `make_gif.py`, `calib_score.py`) and the params generators `genRadStudy.py` / `genRad3d.py` |
| `data/` | the measured HfO2 device Id–Vg at Vds 10 V used for calibration (`rfDeviceHFO2_Experimental.csv`, raw `.xlsx`); TRIM track tables `data/trim/*_track.json` (model input); FANGS 3D Id–Vd curves `data/rad3d_fangs/` (model output). Measured radiation data (`data/rad_y2/`, `data/rad_y3/`) is local only and gitignored |
| `figures/` | outputs (PNG/CSV/GIF): the root holds frozen October outputs, and each study since November has its own folder (`figures/README.md`) |
| `dashboard/` | sources of the work-log artifact and other pages, and their web figures |
| `kb/` | knowledge base |
| `archive/` | superseded work, each folder with a README: `static_mobility/` (HEMTRAD static-mobility era, also branch `static-mobility`; also `trapPlot.tcl`, `analyze_mobCompare.py` and the `figures.ipynb` notebook); `energy_balance/` (the Oct 8-12 eTempDebug tools and `plot_eTemp.py`); `trim_smoke/` (20-ion TRIM test inputs); `analysis_dayfigs/` (one-off dashboard and deck figure scripts, Nov 5-18); `fangs-hpg-tests/` and `fangs-hpg-first-run/` (FANGS HPG test campaigns, a separate project) |
| `results/` | raw sweep results (gitignored) |

## Running (from the repo root)

```bash
flooxs drivers/pulsedIV.tcl                 # finds model/ automatically; strip window/chart lines when headless
python3 analysis/analyze_onset.py results/<run> <tag>
```

On HiPerGator, from the repo root (recipe in the header of `sweeps/radIV.slurm`):

```bash
RUN=20261023_radCal1 PARAMS=params_radCal1.txt; mkdir -p results/$RUN
sbatch --array=0-7%8 --export=ALL,RUN=$RUN,PARAMS=$PARAMS \
       --output=results/$RUN/slurm_%A_%a.out --error=results/$RUN/slurm_%A_%a.err sweeps/radIV.slurm
```

`radIV.tcl` and `seeIV.tcl` write their outputs into the current directory, so local runs of them go in a scratch folder under `results/` (`kb/workflow/local-runs.md`).

Drivers look for the model files in the current directory first (a sweep task directory has them flat), then in `model/`, then in `../model` next to the driver; set `modelDir` to override. Details: `kb/tools/drivers.md`, `kb/workflow/sweep-pattern.md`.
