---
title: Figures to rerun after the FP contact fix
tags: [results, figures, plan, rad-model]
date: 2026-11-22
source: figure inventory workflow wf_66ec8acb-5c0 (four classifiers and a completeness critic over figures/, archive figures and dashboard/fig/); Nov 18 deck read 2026-11-22
---
# Figures to rerun after the FP contact fix

Every simulation before 2026-11-20 used the FP contact box that also held the drain half of the T-gate head at the FP potential ([[fp-contact-fix]]). What changes depends on the bias:
- **Stress field at Vg −10 V (or another off-state bias):** about 5× more gate-edge damage at the same scale. The scale refit restores the Nov 11 curves at 1.5e18.
- **Pre-irradiation and non-biased curves at Vg +1:** under 1%.
- **Vg −2 curve-tracer studies:** not measured yet.

**Scope.** The inventory covers 118 figure items (frames folders counted as one), 36 archived static-era PNGs and the 63 web copies in `dashboard/fig/`.

| Class | Count |
|---|---|
| Must rerun (A) | 45 figures and data files, 19 with a dashboard copy |
| Check (B) | 84, plus their web copies |
| Unaffected (C) | 5 |

## A1. Current results to remake (in this order)

| What | Figures | Remade by |
|---|---|---|
| Nov 11 model (17.66 V stress) | `figures/rad/radFinalEB_IdVd.png` | fpFixScaleEB1 done (scale 1.5e18); replotted as `figures/rad/fpfix/nov11_IdVd.png` |
| 28 V scale | `figures/rad/step28/rad28fit.png` (the Nov 18 deck slide "28 V stress, no strikes") | fpFixScale28 (HighK running 52354341; SiN when the library reaches 28 V). Replot with the new scales |
| 28 V strike series (rounds A-F) | `figures/rad/step28/series_*.png` (8 files, including `series_deliverable.png`), `step_best3.png`, `step_highlights.png` | new strike rounds at the refit 28 V scale on the fixed library (to submit after fpFixScale28) |
| Mesh-robust series | `figures/rad/step28/mesh_series.png`, `mesh_deliverable.png`, `meshchk_steps.png` | the same strike series on the fixed m10 / m5fix / m2p5 stresses (m5fix and m2p5 fixed-box states are done; m10 needs a fixed-box stress) |
| Step mechanism | `figures/rad/step28/diag/pocket_volts.png`, `lib_{C_N0,A_N1,B_N2,A_N3}.png` | vdCuts reruns of the chosen series on the fixed library |
| Field-scaled strikes (rounds H, I) | `figures/rad/step28/fieldstrike_H.png`, `fieldscaled_series.png`, `fieldscaled_segments.png` | rounds H/I again on the fixed library at the refit scale (the head-edge field they rely on changed most) |
| Round S strike count at 28 V | `figures/rad/strike28/strike28_1.5e18.png`, `strike28_2e18.png` | rad28strikeL again on the fixed library, or drop (superseded by the series) |
| Strike transients at 28 V | `figures/see/map28_holeJ.png`, `map28_elecJ.png` | done: fxSeeMap28 52357004, `map28_fix_holeJ.png`, `map28_fix_elecJ.png` |

## A2. Superseded models: mark "pre-fix", do not rerun

These plot models that were already replaced before the fix: the Oct 17 V finals, the hand-placed second site, the Nov 13 strike counts. Rerunning them adds nothing. Mark their KB and dashboard captions as pre-fix instead.
- **Oct 17 V final models:** `figures/radFinal_model.png` (radFinal 47693156), `figures/radFinal8_model.png` (radFinal8 47887339), `figures/radMech_SiN_IdVd.png`, `figures/radMech_damage.png` (radFinal8/11).
- **Rad-week exploration:** `figures/rad/hotEb_final.png` (radChk2 / radFine / radEB1), `figures/rad/radExp1.png` (radExp1/1c), `figures/rad/radFine.png` (radFine Nov 5, radMulti, radMesh).
- **Nov 12-13 checks and strike counts (remade on request, `figures/rad/fpfix/strikeN_IdVd.png` and `strike2_radHV.png`):** `figures/rad/radHV_28V.png` (radHV 51027334), `figures/rad/radStrike2_pos.png` (radStrike2 51027921), `figures/rad/strikeN/{sin_IdVd,hk_IdVd,summary}.png` and `metrics.json` (radStrikeN 51174895).
- **Strike-map proof of concept:** `figures/see/poc_holeJ.png`, `poc_elecJ.png` (local, Vg −5 / Vd 10 V; superseded by map28).

## B. Check: small effect expected, one representative rerun per family

| Family | Figures | Suggested check |
|---|---|---|
| Oct curve-tracer trap studies at Vg −2 V (HighK, hand-placed traps; the head drain half was ~0 V instead of −2 V) | `onsetField{1,2,3}`, the six `posMap_*` sets with their GIFs and frames, `posMapLate*`, `posSlide_*`, `sensitivity*`, `lateOnset_IdVd`, `strikeSlide_*`, `trapMapF_field_*`, `mobCompare_F_*`, `eTemp*` and `eTempStd*`, `Vg_-1V/`, `vgOnset_*`, and the 36 archived static-era PNGs | Rerun Run F and the late set at y 0.2, 1.0 and 2.4 µm at Vg −2 with the fixed box (a few pulsedIV tasks). Traps at y 0.2-0.5 sit under the head and are the most exposed. If onsets move under ~0.1 V, mark the family unchanged |
| Field-plate field cuts, Vg −2, trap-free | `figures/fieldSlide_highk.png`, `fieldPlateFM_cuts.csv`, `fieldPlateFM_sweep.csv` | First to check: they plot the head/FP field peak itself. 2 tasks of ~7 min (`sweeps/fieldPlate.slurm`) |
| Calibration (Oct 1, Id-Vg at Vd 10 V, trap-free) | `figures/calib_IdVg.png` and the `calib_IdVg_*.csv` | One trap-free calibIdVg run with the fixed deck. fpFixPre already checked the rad-era Id-Vg at Vd 0.1 (within 1%) |
| Vg +1 V, no stress field (hand sites, Gaussian traps, deck comparison) | `figures/rad/radMap1.png`, `radMap1_curves.png`, `radMesh_curves.png`, `placement_{4e18,8e18,w0.1}.png`, `gauss_mesh.png`, `gaussFine_decks.png`, `figures/deckVg1_IdVd.png` | One damSites case and one deckVg1 trap case at Vg +1. The pre and nb curves already moved under 1% |
| Vg 0 | `figures/Vg_0V/` | Expected unchanged: gate and FP both at 0 V |
| 3D track-only (Vg +1, no stress) | `figures/rad3d/rad3d_fix.png`, `half3d_render.png` | Rerun one full-width and one half-width track on the fixed 3D deck. The 3D-vs-2D match should hold, because both decks had the same box |

## C. Unaffected

`figures/README.md`, `figures/device_mesh.png` (geometry only), `figures/rad3d/sin3d_track_overview.png` and `sin3d_track_closeup.png` (TRIM-based track drawings), and `figures/rad/fpfix_scale_eb1.png` (made after the fix).

## Published pages that show A figures

| Page | Affected parts |
|---|---|
| Work-log dashboard https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd | Day pages Oct 24-27 (radFinal8, radMech), Nov 5 (radFine), Nov 7-11 (hotEb_final), Nov 12-13 (radHV, radStrike2), Nov 14-16 (strikeN summary), Nov 17-18 (step_best3, strike28_2e18, fieldstrike_H), Nov 19 (pocket_volts, meshchk_steps, series_deliverable, map28_holeJ), Nov 20 (mesh_deliverable, mesh_series). Add a pre-fix banner to those pages; the Nov 22 page carries the new curves |
| Rad-model explainer https://claude.ai/artifact/FArVrMfXX8JNvoFRqYWHLu (`dashboard/rad-model.html`) | "What the model reproduces" (radFinalEB_IdVd) and radMech_damage: swap in the refit curves |
| Rad-week page https://claude.ai/artifact/5bSeoWJa483VtVGKZuPY31 (`dashboard/rad-week.html`) | hotEb_final, radExp1, radFinalEB: a pre-fix note (history) |
| Nov 18 deck https://claude.ai/artifact/5gkYKv6DZjGL7PAuTvZxR6 | Slides "28 V stress" (rad28fit), "Steps" (step_best3), "Checks" (numbers), "Catch" (series_lev04_n6), "Field-scaled strikes" (fieldstrike_H), and the "Since the last deck" table. The 3D slides are class B; the literature, 3D bug, method and next-steps slides are unaffected |
| Strike-count slides https://claude.ai/artifact/JPnVbhvJAwrKyBm2XTFFLs | strikeN figures (A2): pre-fix note |
| Test register https://claude.ai/artifact/QEhm71DSp92bNCYGRHNXTm | Every round (A-H) is pre-fix; rebuild it from the new rounds |

Related: [[fp-contact-fix]], [[step-search-28v]], [[rad-model]], [[cleanup-plan]].
