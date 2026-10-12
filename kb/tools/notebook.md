---
title: figures.ipynb
tags: [tools]
---
# `figures.ipynb`

Older paper plots. Runs on the workstation's system `python3` kernel (numpy/pandas/matplotlib/scipy; `jupyter_client` + `ipykernel` installed, `nbformat`/`nbconvert` not). Several older cells point at `/home/staffian/banjo-wombat/...` paths that no longer exist.

- To add results: append a cell and execute only it plus the setup cells (1 imports, 2 `flooxsRead`) through `jupyter_client`, so other outputs stay untouched; keep the JSON `indent=1` with a trailing newline.
- Cells loading static-era outputs (`pulsedIV_F.csv`, `hotStressIV_*`, `mobility_*`, `rfDeviceHFO2_Simulated.csv`) need the `archive/static_mobility/figures/` prefix; the last cell plotted `figures/pulsedIV_F.csv` against `radPlot1`.
- All plotting happens on the workstation; nothing on HPG touches the notebook.
