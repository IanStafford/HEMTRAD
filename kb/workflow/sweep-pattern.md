---
title: Sweep pattern
tags: [workflow, hpg]
---
# The standard sweep pattern

1. Commit the driver and the SLURM template on the workstation; `git push`.
2. On HPG: `git pull --ff-only`.
3. `params_<tag>.txt`: one line per array task, **pipe-delimited**; task N reads line N+1. Current templates: `pulsedIV_trapMapF_field.slurm`, `pulsedIV_posMapLM.slurm` (one run dir per set), `pulsedIV_curveTracer.slurm`, `pulsedIV_eTemp.slurm` (optional `extra` column of `lever value;…` settings). Static-era templates are in `archive/static_mobility/`.
4. Each task copies the model files (incl. `ETemp.tcl`) and the driver into `results/<YYYYMMDD>_<tag>/task_<id>/`, prepends `set <lever> <value>` lines, strips the GUI lines, and runs there. **Never edit the repo copy in place.**
5. Per-task CSVs (`pulsedIV_<tag>.csv`, never the shared `figures/pulsedIV.csv`) plus a `params.json` with the full parameter set.
6. Format floats in names (`printf '%.2e'`).
7. After the array: check **every** task's `.out`/`.err` for `munmap`/`FLPS_panic`, OOM (`oom-kill`, signal 9), `DUE TO TIME`, `PULSED GAVE UP`, missing CSV, core files (delete; 1–2 GB each). `grep`/`tail`, not `cat`. Report failures before plotting.
8. `rsync -a --exclude='core*' hpg:/home/ianstafford/blue/ee1/ianstafford/HEMTRAD/results/<run>/ results/<run>/`, then analyse and plot on the workstation.

Rescue/retry runs go into `<run>Retry*/` directories; `analyze_onset.py` and `plot_posVd.py` read every `<run>Retry*` and keep the run that got furthest ([[analysis-scripts]]).

Related: [[hpg-workflow]], [[git-conventions]].
