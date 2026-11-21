# Static-mobility archive (2026-09-23 to 2026-10-01)

Everything here was simulated with the old default `mobModel static` (constant
GaN electron mobility 600 cm²/V·s). On 2026-10-01 the deck was calibrated against
the measured HfO2 transfer curve (`kb/device/calibration.md`) and the field-dependent mobility
(`mobModel field`) replaced it. Results in this folder are kept for reference but
are superseded.

- **Write-ups:** `RESULTS.md` here (the old CLAUDE.md §10-§10l, verbatim). File
  names there refer to this folder. `kb/results/static-era-lessons.md` summarizes the lessons.
- **Snapshot:** branch `static-mobility` (commit d2eda77) has every file in its
  original place, if anything here needs to be rerun exactly as it was.
- **Contents:** sweep `pulsedIV_*.slurm` / `params_*.txt` (late-onset rounds A-I,
  trap placement, 50-location map, conc × level × position, 10f map sets, cone,
  critical-strike band, x-y map + sign-0 companion, deep traps, HighK vs SiN),
  their analysis scripts (`analyze_*.py`, `critical_strike.py`,
  `plot_*.py`), old drivers (`fieldpeak.tcl` — note its HighK εr bug,
  `transfer.tcl`, `run_measurements.tcl`, `mobilityCompare.tcl`, `stressFreeze.tcl` (quiescent off-state stress then
  Id–Vd; moved here 2026-11-20, superseded by the stress stage of `drivers/radIV.tcl`), `IV.tcl` — which
  sources a missing `powerdevice.tcl`), `trapPlot.tcl`, `analyze_mobCompare.py`,
  `figures.ipynb` (the last three moved here 2026-11-21, below), and `figures/` with all their outputs.
- **Raw results** (not in git): `results/archive_static_mobility/` on the
  workstation; the HPG copies are still under `results/` there. The analysis
  scripts here read the workstation archive paths; run them from the repo root
  (`python3 archive/static_mobility/analyze_trapCone.py ...`). They write into
  the root `figures/`, so move any regenerated output back here.
- `figures.ipynb` cells that load `figures/pulsedIV_F.csv`, `hotStressIV_*`,
  `mobility_*` or `rfDeviceHFO2_Simulated.csv` still point at the root `figures/` and
  need the `archive/static_mobility/figures/` prefix (`kb/tools/notebook.md`).

## Moved here on 2026-11-21 (clean-up stage 4, `kb/workflow/cleanup-plan.md`)

Nothing in the current work reads or runs these. Their code is unchanged: only usage lines, paths that point at other moved files, and a header comment in `trapPlot.tcl` were edited.

| File here | Moved from | What it is | Runs and jobs | How to run it |
|---|---|---|---|---|
| `trapPlot.tcl` | `drivers/trapPlot.tcl` | The 2026-09-23 dynamic-trap driver (commit 8629f4e; `modelDir` lookup added in the 2026-10-12 reorganisation). Vg ramps to −2 V, then Id–Vd from 0 to 10 V in 0.1 V steps with `trapEn 1` on `rfdevice.tcl`, and an `IonAcceptor` cut along x 0.018 µm at every half volt. | Local GUI runs before the trap sign-bug fix (760b388); no HPG job. Its outputs are `radPlot2.csv` and `trapOccupation2.csv` in this folder's `figures/`. | `flooxs archive/static_mobility/trapPlot.tcl` from the repo root, with a display (`window`, `chart`, `plot1d`; no template strips them). It writes `radPlot2.csv` and `trapOccupation2.csv` into the root `figures/` folder; move them back here. |
| `archive/static_mobility/figures/radPlot.csv`, `radPlot1.csv`, `radPlot2.csv` | `figures/radPlot.csv`, `figures/radPlot1.csv`, `figures/radPlot2.csv` | Id–Vd curves (Vd in V, Id in mA/mm) from 2026-09-23. `radPlot1` was the static-era onset and depth target (`RESULTS.md`, `kb/results/static-era-lessons.md`). Their abrupt collapse came from the trap sign bug (`kb/model/trap-model.md`). Whether `radPlot1` is a measured curve is an open question in `kb/workflow/cleanup-plan.md`. | as `trapPlot.tcl` | Read by `plot_trapPlacement.py` (`radPlot1`) and `figures.ipynb` cells 4, 6 and 12, both pointed here. |
| `analyze_mobCompare.py` | `analysis/analyze_mobCompare.py` | Static vs field-dependent mobility on the Run F trap map, each map against its own trap-free device (2026-10-01). Its `onset_Vd` is the first Vd where Id falls below a tenth of its running maximum, which predates the collapse-class rule (`kb/tools/analysis-scripts.md`). | Static: job 43513462 + retry 43515232 (`results/archive_static_mobility/20260927_trapMapSets{,Retry}`). Field: job 44342967 (`results/20261001_trapMapF_field`). | `python3 archive/static_mobility/analyze_mobCompare.py [trapPeak trapLevel field_run tag]` from the repo root. It writes `figures/mobCompare_F_{metrics.csv,3d.png,compare.png}` at the figures root, where the tracked copies stay (shown on the Oct 1 dashboard day; `kb/results/field-mobility-trap-map.md`). |
| `figures.ipynb` | `figures.ipynb` (repo root) | Static-era paper plots; content last changed 2026-09-24 (`kb/tools/notebook.md`). | as the CSVs it reads | Open it in Jupyter with the workstation's system `python3`. Every path in it is absolute, so moving it changed nothing else; its four reads of the `radPlot` files now point here. |
