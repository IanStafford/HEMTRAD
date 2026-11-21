# One-off dashboard and deck figure scripts (2026-11-05 to 2026-11-18)

Archived 2026-11-21 (clean-up stage 4, finding AN-8 in `kb/workflow/cleanup-plan.md`). Each script below made fixed figures for one dashboard day or slide deck, from results paths hard-coded in it. None takes a run directory, nothing imports them (checked with grep before the move), and the KB cites their figures, not the scripts. They are kept as the record of how each tracked figure was made. All moved from `analysis/` with only their usage lines edited.

**Pages.** "Work log" is `dashboard/hemt-collapse-log.html` (the day anchor in brackets); "rad week" is `dashboard/rad-week.html` (Rad Study, Nov 4–12, section named). Web copies are in `dashboard/fig/<name>.jpg`.

| Script (moved from `analysis/`) | Figure(s) it made | Dashboard day or use | Results dirs (job IDs) | Commit |
|---|---|---|---|---|
| `radFineFig.py` | `figures/rad/radFine.png` | Work log, Nov 5 (`#nov05`) | `20261105_radFine` (49735196, the Nov 5 study, not the Oct 24 radFine), `20261105_radMulti` (49735488), `20261104_radMesh` (49606872), `20261104_radFam` (49606874), `20261104_radMap1` (49570571); plus the CSV named by `FINAL_REF` (below) | 24f98da, 2026-11-05 |
| `radGaussFig.py` | `figures/rad/gauss_mesh.png` | Work log, Nov 7–11 (`#nov11`); rad week, "What does collapse for real" | `20261107_radGauss` (50128863), `20261021_deckVg1` (47062225) | 02c4dfd, 2026-11-07 |
| `radEBFig.py` | `figures/rad/hotEb_final.png` | Work log, Nov 7–11 (`#nov11`); rad week, "What does collapse for real" | `20261104_radMap1` (49570571), `20261107_radChk2` (50128862), `20261105_radFine` (49735196), `20261109_radEB1` (50411481), `20261109_radEB2` (50470082) | 7d5de2f and 4aae681, 2026-11-09 |
| `plot_gaussFine.py` | `figures/rad/gaussFine_decks.png` | Made with the 2026-11-11 final-model update; `dashboard/fig/gaussFine_decks.jpg` exists, but no tracked page shows it | `20261021_deckVg1` (47062225), `20261107_radGauss` (50128863) | 06af71b, 2026-11-11 |
| `plot_radExp1.py` | `figures/rad/radExp1.png` | Rad week, "Exploring toward the measured curves" | `20261104_radMap1` (49570571), `20261109_radEB1` (50411481), `20261111_radExp1` (50831893), `20261111_radExp1c` (50892179) | 13a867d, 2026-11-12 |
| `plot_nov12.py` | `figures/rad/radHV_28V.png`, `figures/rad/radStrike2_pos.png` (into the output folder it is given) | Work log, Nov 12–13 (`#nov13`) | `20261112_radHV` (51027334), `20261112_radStrike2` (51027921) | d55ce8b, 2026-11-13 |
| `plot_radStepHighlights.py` | `figures/rad/step28/step_highlights.png` (default mode); `figures/rad/step28/step_best3.png` (with `best`) | `step_best3`: work log, Nov 17–18 (`#nov18`) and the Nov 18 deck; `step_highlights`: no page | `20261117_radStepA` (51784676), `20261117_radStepC` (51799741, 51799742), `20261117_radStepE` (51801897, 51801898), `20261117_radStepF` (51811467, 51811468), `20261104_radMap1` (49570571), `20261109_radEB1` (50411481) | 8fbcda8, 2026-11-17; `best` added in 4ca8797, 2026-11-18 |
| `plot_rad28fit.py` | `figures/rad/step28/rad28fit.png` | Nov 18 deck; no dashboard page; cited in `kb/results/rad-model.md` | `20261112_rad28fit` (51040272), `20261112_radExp3` (51021670), `20261113_rad28fitB` (51196550, 51249769), `20261104_radMap1` (49570571) | 4ca8797, 2026-11-18 |
| `plot_rad3dFix.py` | `figures/rad3d/rad3d_fix.png` | Work log, Nov 17–18 (`#nov18`) and the Nov 18 deck | `data/rad3d_fangs/` (FANGS port runs, model output, tracked; see its README), `20261112_rad3dSolve/task_6` (51052220) | 4ca8797, 2026-11-18 |

Results dirs are under `results/` (gitignored; synced from HPG). The figures stay where they are; only the scripts moved.

**Caveats.**
- The reference curves several scripts use, the pre-irradiation `20261104_radMap1/task_*/{sin,hk}_ref_IdVd.csv` and the Nov 11 model `20261109_radEB1/task_*/sin_b_eb1_IdVd.csv`, were run with the FP contact box from before the 2026-11-20 fix (`kb/results/fp-contact-fix.md`). So are all the runs in the table.
- `radFineFig.py` reads its "standard mesh" curve from a CSV named by the environment variable `FINAL_REF`, the final SiN biased curve of the radFinal11 set on the standard mesh. Which file that was is not recorded.
- `plot_radStepHighlights.py` draws its drop arrows with `plot_radStep.drops(v, i, 10.0)` from `analysis/plot_radStep.py`, which it finds through `sys.path.insert(0, "analysis")`.

**How to run one if ever needed.** From the repo root (every input path is relative to it), after syncing the results dirs it reads: `python3 archive/analysis_dayfigs/<script>.py <out.png>` (`plot_nov12.py` takes an output folder; `plot_radStepHighlights.py <out.png> best` makes the three-panel version; `radFineFig.py` needs `FINAL_REF=<csv>` in the environment). Write to a scratch path first: the tracked figures are under `figures/rad/`, `figures/rad/step28/` and `figures/rad3d/`.
