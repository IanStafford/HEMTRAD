---
title: Analysis scripts
tags: [tools]
---
# Analysis and plotting scripts (workstation, after rsync)

| Script | Purpose | Output |
|---|---|---|
| `analyze_onset.py <run> <tag> [group levers]` | collapse class/onset per device ([[collapse-classification]]); reads `<run>Retry*` and keeps the furthest run | `figures/<tag>.png`, `<tag>_metrics.csv` |
| `analyze_trapMapSets.py [run tag]` | 3D depth/suppression surfaces over (depth, y) | `figures/trapMapF_field_*.png` |
| `analyze_mobCompare.py` | static vs field Run F maps, each vs its own trap-free device | `figures/mobCompare_F_*` |
| `plot_posVd.py <run> <tag> [Vd list]` | per-Vd 3D suppression surfaces (shared z), frames, onset map; stalled points as orange × | `<tag>_grid.png`, `<tag>_frames/`, `<tag>_onset.png` |
| `make_gif.py frames out.gif [ms hold]` | GIF from `Vd_*.png` frames (shared palette, last frame held) | `figures/*.gif` |
| `plot_lateIdVd.py` | latest deep collapses vs trap-free | `figures/lateOnset_IdVd.png` |
| `plot_curveTracer.py [run]` | Id–Vd at other Vg, one folder per Vg, −2 V dashed | `figures/Vg_-1V/`, `figures/Vg_0V/` |
| `plot_eTemp.py [run]` | energy-balance runs vs local-field/DD; ETemp profiles | `figures/eTemp_IdVd.png`, `eTemp_profiles.png` |
| `calib_score.py`, `plot_calib.py` | calibration scoring / plot | `figures/calib_IdVg*.{png,csv}` |
| `dashboard/webfig.py` | web-size figure copies for the [[dashboard]] | `dashboard/fig/*.jpg` |

GIF recipe: `plot_posVd.py <run> <tag>_gif $(python3 -c "print(','.join(f'{0.1*k:.1f}' for k in range(1,31)))")` then `make_gif.py figures/<tag>_gif_frames figures/<tag>.gif` (GIF frames not committed). Archived static-era scripts: `archive/static_mobility/analyze_*.py`, `critical_strike.py`.

Plot style used throughout: recessive grid/axes, one-hue sequential blue ramp for magnitude, text in ink colours, legends kept off the data.
