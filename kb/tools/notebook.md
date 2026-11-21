---
title: figures.ipynb
tags: [tools, static-era]
date: 2026-11-20
source: archive/static_mobility/figures.ipynb (15 cells, read 2026-11-20; moved from the repo root 2026-11-21); git log --follow archive/static_mobility/figures.ipynb
---
# `figures.ipynb`

Static-era paper plots, in `archive/static_mobility/figures.ipynb` since 2026-11-21 (stage 4 of [[cleanup-plan]]; it was at the repo root before). Its content last changed on 2026-09-24. The 2026-10-12 reorganisation (42ecf73) only pointed its two reads of `rfDeviceHFO2_Experimental.csv` (cells 4 and 14) at `data/`, and the 2026-11-21 move pointed its four reads of the `radPlot` CSVs at `archive/static_mobility/figures/`.

**Kernel.** The workstation's system `python3` (numpy, pandas, matplotlib, scipy). `jupyter_client` and `ipykernel` are installed; `nbformat` and `nbconvert` are not.

**Paths.** Every data path is absolute.
- The `/home/staffian/banjo-wombat/highK/figures/{SiN,highK}_channel.csv` files of cell 8 still exist on the workstation.
- Four inputs moved to `archive/static_mobility/figures/` in the reorganisation, but their cells still point at `figures/`: `rfDeviceHFO2_Simulated.csv` (cell 4), `hotStressIV_*` (cell 10), `pulsedIV_F.csv` (cell 12) and `mobility_*` (cell 14). Cells are counted from 0.
- Cell 10 prints "no data" for a missing file instead of failing. Of its four stress cases, only `hotStressIV_q0_0.csv` and `hotStressIV_qm2_10.csv` exist in the archive.
- `Vt.png` appears only in a commented-out `savefig` (cells 4 and 6).

**What the cells show.**
- Cells 4 and 6 read `radPlot.csv`, `radPlot1.csv` and `radPlot2.csv` from `archive/static_mobility/figures/` (static era, [[static-era-lessons]]; moved from `figures/` 2026-11-21). Cell 6 labels radPlot and radPlot1 "x=0.14" and "x=0.16". Cell 12 plots Run F (`pulsedIV_F.csv`) against radPlot1, labelled "old model".
- Cells 9 and 10 show the stress-then-freeze runs of `stressFreeze.tcl`, which was archived on 2026-11-20 to `archive/static_mobility/stressFreeze.tcl`.

**To add results.** Append a cell and execute only it plus the setup cells 1 (imports) and 2 (`flooxsRead`) through `jupyter_client`, so other outputs stay untouched. Keep the JSON `indent=1` with a trailing newline. All plotting happens on the workstation; nothing on HPG touches the notebook.
