---
title: Analysis scripts
tags: [tools]
---
# Analysis and plotting scripts (`analysis/`, run from the repo root after rsync)

| Script | Purpose | Output |
|---|---|---|
| `analysis/analyze_onset.py <run> <tag> [group levers]` | collapse class/onset per device ([[collapse-classification]]); reads `<run>Retry*` and keeps the furthest run | `figures/<tag>.png`, `<tag>_metrics.csv` |
| `analysis/analyze_trapMapSets.py [run tag]` | 3D depth/suppression surfaces over (depth, y) | `figures/trapMapF_field_*.png` |
| `analysis/analyze_mobCompare.py` | static vs field Run F maps, each vs its own trap-free device | `figures/mobCompare_F_*` |
| `analysis/plot_posVd.py <run> <tag> [Vd list]` | per-Vd 3D suppression surfaces (shared z), frames, onset map; stalled points as orange × | `<tag>_grid.png`, `<tag>_frames/`, `<tag>_onset.png` |
| `analysis/plot_posOnset.py <run> <tag>` | 3D onset surface: positions that collapse in the sweep (deep, medium or stalled) rise to height Vd_max + 0.1 − onset, so the earliest collapse is the highest peak; non-collapsing positions stay flat; frames rise as Vd sweeps | `<tag>_onset3d.png`, `<tag>_onset3d_frames/` (GIF via make_gif.py) |
| `analysis/make_gif.py frames out.gif [ms hold]` | GIF from `Vd_*.png` frames (shared palette, last frame held) | `figures/*.gif` |
| `analysis/plot_lateIdVd.py` | latest deep collapses vs trap-free | `figures/lateOnset_IdVd.png` |
| `analysis/plot_curveTracer.py [run]` | Id–Vd at other Vg, one folder per Vg, −2 V dashed | `figures/Vg_-1V/`, `figures/Vg_0V/` |
| `analysis/plot_eTemp.py [run]` | energy-balance runs vs local-field/DD; ETemp profiles | `figures/eTemp_IdVd.png`, `eTemp_profiles.png` |
| `analysis/calib_score.py`, `analysis/plot_calib.py` | calibration scoring / plot | `figures/calib_IdVg*.{png,csv}` |
| `analysis/plot_sensitivity.py [run]` | one-at-a-time trap-lever sensitivity ([[trap-sensitivity]]) | `figures/sensitivity.png`, `sensitivity_IdVd.png`, `sensitivity_metrics.csv` |
| `dashboard/webfig.py` | web-size figure copies for the [[dashboard]] | `dashboard/fig/*.jpg` |

GIF recipe: `python3 analysis/plot_posVd.py <run> <tag>_gif $(python3 -c "print(','.join(f'{0.1*k:.1f}' for k in range(1,31)))")` then `python3 analysis/make_gif.py figures/<tag>_gif_frames figures/<tag>.gif` (GIF frames not committed). Archived static-era scripts: `archive/static_mobility/analyze_*.py`, `critical_strike.py`.

Plot style used throughout: recessive grid/axes, one-hue sequential blue ramp for magnitude, text in ink colours, legends kept off the data.
