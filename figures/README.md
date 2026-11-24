# figures/

Tracked figures and small CSVs. Which script writes which file: `kb/tools/analysis-scripts.md`. Rule written 2026-11-21 (clean-up findings LAY-12 and AN-17, `kb/workflow/cleanup-plan.md`).

## The root is frozen

The files at the root are October outputs, kept as they are:
- the field-mobility curve-tracer era (pulsedIV, 2026-10-01 to 2026-10-23): calibration `calib_IdVg*` (`calib_IdVg_fpfix.*`: the fixed FP contact, 2026-11-24), the Run F trap map `trapMapF_field_*` and `mobCompare_F_*`, onset maps `onsetField{1,2,3}*` and `lateOnset_IdVd.png`, position maps `posMap*`, energy balance `eTemp*`, gate bias `vgOnset_*`, `sensitivity*`, the field-plate check `fieldPlateFM_{sweep,cuts}.csv`, the talk figures `posSlide_*`, `strikeSlide_*`, `fieldSlide_highk.png` and `eTempStd_headline.png`, and `deckVg1_IdVd.png`;
- the first rad-model figures (2026-10-25 to 2026-10-27): `radFinal_model.png`, `radFinal8_model.png`, `radMech_*.png`;
- `device_mesh.png`, the mesh picture.

Add nothing new at the root. Several scripts still in `analysis/` write here by default (for example `analyze_onset.py`, `plot_posVd.py`, `plot_radFinal.py`, `plot_radMechanism.py`). A rerun on the same inputs overwrites the tracked file, so give them another tag or output path unless that is the point.

## New studies go in `figures/<study>/`

As since November:
- `rad/`: the rad model. `rad/step28/` is the 28 V step search (`diag/` holds the vdCuts diagnostics), `rad/strike28/` the strikes on the 28 V stress library, `rad/strikeN/` the 0-3 strikes on the 17 V model.
- `rad3d/`: the 3D slice.
- `see/`: single-event current-density maps.

## Other folders

- `Vg_-1V/`, `Vg_0V/`: the curve-tracer runs at other gate biases (job 44573629, `kb/results/gate-bias.md`). `analysis/plot_curveTracer.py` writes the figure and copies of the CSVs into `Vg_<Vg>V/`.
- Static-era figures and CSVs are in `archive/static_mobility/figures/`.

## Frames

- The six `posMap*_frames/` folders are tracked: ten `Vd_<v>.png` frames each, from `analysis/plot_posVd.py`.
- `*_onset3d_frames/` (`analysis/plot_posOnset.py`) and `*_gif_frames/` (the GIF recipe in `kb/tools/analysis-scripts.md`) are regenerated when needed and gitignored, at any depth under `figures/`. Only the GIFs made from them are committed.
- Stage figures by explicit path, never the whole folder.

## Measured data

Never here. The repo is public. `radMetrics.guard_private_output()` refuses to write a figure with measured curves under `figures/` or `dashboard/` (`kb/workflow/git-conventions.md`).
