# HEMTRAD

FLOOXS (Tcl) TCAD model of **radiation-induced current collapse** in an AlGaN/GaN HEMT (HfO2/HighK passivation, T-gate + field plate), with HiPerGator sweep templates and Python analysis.

Knowledge base: **`kb/index.md`** (Obsidian second brain). Agent rules: `CLAUDE.md`. Dated log: `progress.md`.

## Layout

| Folder | Contents |
|---|---|
| `model/` | the device model, sourced together: `GaN_modelfile_masterD` (levers, materials, equations), `GaN.tcl`, `AlGaN.tcl`, `Insulator.tcl`, `Metal.tcl`, `Continuity.tcl`, `Poisson.tcl` (traps), `ETemp.tcl` (energy balance), device decks `rfdevice.tcl` / `rfdevice_SiN.tcl`. Three files are CRLF (`GaN_modelfile_masterD`, `Metal.tcl`, `Continuity.tcl`) |
| `drivers/` | Tcl drivers: `pulsedIV.tcl` (curve-tracer Id–Vd, main tool), `calibIdVg.tcl` (transfer curve), `stressFreeze.tcl`, `trapPlot.tcl`, `eTempDebug_tail.tcl` |
| `sweeps/` | SLURM templates (`*.slurm`) and their `params_*.txt` |
| `analysis/` | Python analysis and plotting (`analyze_*.py`, `plot_*.py`, `make_gif.py`, `calib_score.py`) |
| `data/` | measured inputs: HfO2 device Id–Vg at Vds 10 V (`rfDeviceHFO2_Experimental.csv`, raw `.xlsx`) |
| `figures/` | outputs (PNG/CSV/GIF); `figures.ipynb` (repo root) holds older paper plots |
| `dashboard/` | work-log artifact source and web figures |
| `kb/` | knowledge base |
| `archive/` | superseded work (`static_mobility/`) |
| `results/` | raw sweep results (gitignored) |

## Running (from the repo root)

```bash
flooxs drivers/pulsedIV.tcl                 # finds model/ automatically; strip window/chart lines when headless
python3 analysis/analyze_onset.py results/<run> <tag>
sbatch sweeps/<template>.slurm              # on HiPerGator, from the repo root
```

Drivers look for the model files in the current directory first (a sweep task directory has them flat), then in `model/`; set `modelDir` to override. Details: `kb/tools/drivers.md`, `kb/workflow/sweep-pattern.md`.
