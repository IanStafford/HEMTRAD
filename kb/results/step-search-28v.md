---
title: Stepped collapse at the 28 V stress (rounds S, A-K, M; mesh checks)
tags: [results, rad-model, strikes]
date: 2026-11-20
source: progress.md 2026-11-17 to 2026-11-20; HPG jobs rad28strikeL 51763582, radStepA-K, radStepM 52044406, radStepM2 52072550, meshChkStress 51883722, meshChkLoad 51939191/51939192; test register https://claude.ai/artifact/QEhm71DSp92bNCYGRHNXTm
---
# Stepped SiN collapse at the 28 V stress with ion strikes

Goal set by Ian on 2026-11-17: reproduce stepped Id-Vd curves at the 28 V stress with 1, 2 and 3 strikes, qualitatively like the measured devices or the Nov 11 model. All runs load the 28 V stress state from the library (`stressLoad`, [[levers]], [[stress-library]]) and add Gaussian strikes (`damGauss`, σ 40 nm, at the AlGaN top) to the E⁴ stress damage ([[damage-model]]; scale `damPeak` 1.5e18, trap level 0.30 eV unless stated, hotEb 1.0 eV, occSafe, Vd step 0.1 V, Vg +1 V). Model output only; the measured curves are compared qualitatively ([[rad-model]]).

## Current answer (2026-11-20; pre-fix, being rerun, [[fp-contact-fix]])

- **Steps:** trap level 0.30 eV with 8e18 strikes gives 2 / 3 / 3 drops for 1 / 2 / 3 strikes on the library, m10 and m5fix meshes. The first drop starts within 0.1 V across meshes; the later drops move with the mesh.
- **No deck contrast with these strikes:** HighK collapses with the same strikes (library, one strike: 262 → 7 mA/mm near 1 V).
- **Field-scaled strikes** (`gaussFieldM` 4, rounds H-J) keep HighK flat but give SiN only one drop, which deepens with each strike.
- **Pre-fix:** every run in this note loaded a 28 V stress state saved with the old FP contact box. The library (fpFixStress 52134552) and the 5 nm and 2.5 nm mesh stresses (fpFixMesh 52135538) are being redone with the fixed box, and the key series follow (fpFixLoad).

## Corrected geometry (2026-11-25; fx-prefixed remakes, damage scale 6e17, 28 V library and m10 / 5 / 2.5 nm meshes)

Figure `figures/rad/fpfix/step_series_fixed.png` (`analysis/plot_fxStepSeries.py`). Drops by the table rule (hyst, at least 8 mA/mm), SiN, 0 / 1 / 2 / 3 strikes:

| Setting | Library (9.5-17 nm) | 10 nm | 5 nm (m5fix) | 2.5 nm (m2p5) |
|---|---|---|---|---|
| trap 0.40, 7e18 | 1 / 3 / 2 / 3 | 1 / 2 / 2 / 3 | **1 / 1 / 2 / 3** | **1 / 1 / 2 / 3** |
| trap 0.30, 8e18 | 1 / 2 / 3 / 2 (3 strikes gave up at 6.6 V) | 1 / 2 / 3 / 3 | 1 / 2 / 3 / 3 | **1 / 1 / 2 / 3** |

(The first number is the stress damage alone, whose single drop is at 1.6-2.0 V for 0.30 eV and 1.0-1.4 V for 0.40 eV.)
- **Trap 0.40 eV with 7e18 strikes gives one drop per strike on both the 5 nm and the 2.5 nm mesh.** At 2.5 nm: 1 strike 173 → 40 at 0.8 V; 2 strikes 170 → 76 at 1.0 V and 119 → 84 at 2.2 V; 3 strikes 168 → 91 at 1.2 V, 163 → 123 at 3.0 V, 163 → 130 at 4.5 V. The current stays low (about 190-225 mA/mm at 12 V, against 277 without strikes).
- **Trap 0.30 eV with 8e18** gives 1 / 2 / 3 at 2.5 nm (262 → 108; 260 → 166 and 215 → 182; 257 → 184, 256 → 229, 261 → 239) but 2 / 3 / 3 at 5 nm. The 5 nm and 2.5 nm curves agree to 6-11 mA/mm rms over 0.2-12 V (3 for no strike), so the first drops are close to converged and the later ones move by a few tenths of a volt and 10-20% in size.
- **Density scan, plain strikes, base damage scale (library mesh, `figures/rad/fpfix/contrast_density.png`, `analysis/plot_fxContrast.py`; number of drops / size of the largest, % of the current before it):** trap 0.30 eV, SiN 4e18 1 / 32% (the stress drop alone; N2 not run), 5e18 N1-3 3 / 2 / 2 at 31 / 29 / 27%, 5.5e18 3 / 2 / 2 at 29 / 25 / 21%, 6e18 3 / 2 / 1 at 43 / 21 / 17%. HighK at the same densities: 4e18 1 / 1 / 0 at 3 / 2 / 0%; 5e18 2 / 2 / 1 at 23 / 17 / 9%; 5.5e18 2 / 1 / 1 at 39 / 19 / 17%; 6e18 2 / 1 / 1 at 55 / 32 / 28%. Trap 0.40: SiN has its extra steps from 5e18, and HighK drops 12% at 4e18 and 21-29% at 5e18.
- **So there is no density where SiN has extra steps and HighK is flat.** SiN's extra steps (beyond the stress drop) appear from 5e18, and HighK's first visible drops also appear there (tiny at 4e18). HighK at 0.40 / 7e18 is expected to drop as well: its 0.40 / 6e18 runs already show 64 / 62 / 52% drops. Tuning the strike density cannot give the contrast; a different strike law (or a passivation-dependent damage) is needed.
- **Contrast:** not recovered. The same plain strikes also make HighK drop (library: 6e18 2 / 1 / 1, 8e18 3 / 4 / 1); field-scaled and hybrid strikes keep HighK flat but give SiN one drop. HighK has not been run at 0.40 eV / 7e18 or on the fine meshes.
- **Field-scaled strikes on a weak stress band (fxFieldStrike1 52761027, 2026-11-25; figure `figures/rad/fpfix/fieldstrike1.png`, `analysis/plot_fxFieldStrike1.py`).** Stress band at 2e17 / 3e17 / 4.5e17 (trap 0.30 eV; 3e17 also at 0.40), too weak to drop on its own at 2e17 and 3e17 (fpFixScale28: 939 and 796 mA/mm at 12 V, no drop). On top, 1-3 field-scaled strikes (`damGaussF`, m 4, σ 30 nm, y 0.55 / 0.50+0.60 / 0.47+0.56+0.65 µm) at base density 2e17 / 4e17 / 8e17 at 5e5 V/cm; library mesh with 10 nm at the strikes. All 72 completed; the 25 that gave up before 12 V (at 9.2-11.9 V) are all HighK, flat when they stopped.
  - **HighK is flat in all 36 runs:** no drop, no fall of more than 1 mA/mm, 946-961 mA/mm at the last point (its undamaged level).
  - **SiN has one drop in most runs** (0.4-2.9 V), whose size grows with band and strike density from 3% to 100%; afterwards the current stays low (3-782 mA/mm at 12 V). With the weakest setting (band 2e17, strikes 2e17) there is no drop, only a lower current (744-782 against 939).
  - **Two drops only with a single strike at the highest density:** band 2e17, b 8e17: 282 → 152 at 1.0-1.3 V and 328 → 231 at 6.8-8.0 V; band 3e17: 240 → 48 and a 3% drop at 10.0-10.6 V; trap 0.40 / band 3e17: 31% + 7% (b 4e17) and 100% + 29% at 9.1-10.1 V (b 8e17). Two or three strikes never add drops: inside y 0.47-0.65 µm they act as one pocket.
  - So the field-scaled law gives the deck contrast at every setting, but the strike count does not step SiN, as expected from the field argument below (SiN-favoured damage stays in one band near the gate). The success criterion set for this study (SiN with more than one drop, HighK flat) is met only by the single-strike runs at the highest density, on the library mesh; not mesh-checked.
- **Caveats:** 2D, full-width lines of damage, hand-placed at y 0.8 / 1.6 / 2.4; the drop count is a property of this spacing and density; 14 of the finished runs gave up before 12 V.

## Labels

A case label is `<round>_<settings>_N<k>`. The leading letter is the HPG round in which the case first ran, not the series it belongs to. `N<k>` is the number of strikes. Plain strikes go to y 0.8, 1.6 and 2.4 µm in that order (N1: 0.8 only; N2: 0.8 and 1.6; N3: all three); rounds H-J, the field-plate-edge cases `E_fp` and the knock-out cases use the positions in the table, and `B_near` uses 0.5 / 0.8 / 1.1. Short forms in the text keep only the round, a distinguishing setting and N: A_N1 is `A_p1.5e+18_n6e+18_N1`, C_N0 is `C_p1.5_N0`, C_n8e18_N2 is `C_p1.5_n8e18_N2`, E_lev0.4_N2 is `E_lev0.4_n6e18_N2`. A matched 0-3 strike series therefore mixes rounds: **row A** (the Nov 18 deliverable's top row, set key `lev30_n6`) is C_N0, A_N1, B_N2 and A_N3. Series keys such as `lev30_n8` are defined in `SETS` of `analysis/plot_meshSeries.py`; `p15_n6` and `fs_bandb` in `analysis/plot_radStepSeries.py`. All params are in `sweeps/params_<run>.txt`.

| Label | Round, job | Deck | Scale | Strikes (density at y in µm) | Trap level | Mesh |
|---|---|---|---|---|---|---|
| `sin28_p<P>_N<k>`, `hk28_p<P>_N<k>` | S, rad28strikeL 51763582 | SiN, HighK | 1.5e18, 2e18 | 3e18 at 0.8 / 1.6 / 2.4 | 0.30 | library |
| `C_p1.5_N0` (C_N0) | C, radStepC 51799741 | SiN | 1.5e18 | none | 0.30 | library |
| `A_p1.5e+18_n6e+18_N1` / `_N3`, `B_n6e18_N2` (row A) | A 51784676, B 51799601 | SiN | 1.5e18 | 6e18 | 0.30 | library |
| `A_p1.5e+18_n8e+18_N1` / `_N3`, `C_p1.5_n8e18_N2` (`lev30_n8`) | A, C 51799741 | SiN | 1.5e18 | 8e18 | 0.30 | library |
| `C_p1.5_n7e18_N1-3` (`lev30_n7`) | C 51799741 | SiN | 1.5e18 | 7e18 | 0.30 | library |
| `E_lev0.4_n6e18_N1-3` (`lev40_n6`) | E 51801897 | SiN | 1.5e18 | 6e18 | 0.40 | library |
| `E_fp_n6e18_N1-3` | E 51801897 | SiN | 1.5e18 | 6e18 at y 0.9, then 0.3, then 2.0 (field-plate edges) | 0.30 | library |
| `E_vs24_p2.8e+18_n6e18_N<k>`, `E_vs30_p1.15e+18_n6e18_N<k>` | E 51801897 | SiN | 2.8e18 on the 24 V state, 1.15e18 on the 30 V state | 6e18 | 0.30 | library |
| `F_lev0.4_N0`, `F_lev0.4_n5e+18_N1-3`, `F_lev0.4_n7e+18_N1-3` (`lev40_n5`, `lev40_n7`) | F 51811467 | SiN | 1.5e18 | none, 5e18, 7e18 | 0.40 | library |
| `C_hk_p1.5_n6e18_N0-3`, `C_hk_p1.5_n8e18_N1-3` (C_hk) | C 51799742 | HighK | 1.5e18 | 6e18, 8e18 | 0.30 | library |
| `G_hk_n5e+18_N1-3` (G_hk), `G_hk_lev0.4_n4e+18_N1-3`; `G_` without `hk` is SiN | G 51823696 | HighK, SiN | 1.5e18 | 4-5.5e18 | 0.30, 0.40 | library |
| `D_p1.5_n8e18_ko1`, `_ko2` | D 51801163 | SiN | 1.5e18 | 8e18 at 1.6 / 2.4 (ko1) or 0.8 / 2.4 (ko2) | 0.30 | library |
| `<label>_dv05` | D 51801163, F 51811468, J 51922589 | as the label | as the label | as the label, Vd step 0.05 V | as the label | library |
| `H_<deck>_fm<m>_n<N>_N<k>` | H 51871249 | both | 1.5e18 | N at y 0.5, then 0.35, then 0.65, times (E/E_ref)^m; `nofm` unscaled; `old` at 0.8 / 1.6 / 2.4 | 0.30 | library |
| `I_<deck>_bandb_N<k>` (band b) | I 51878761 | both | 1.5e18 | m 4, base 2e18 / 6e17 / 2e17 at y 0.65 / 0.6 / 0.55 (band a: 3e18 / 1e18 / 3e17) | 0.30 | library |
| `J_<deck>_lev<L>_bandb_N<k>`, `J_<deck>_depth_N<k>` | J 51922589 | both | 1.5e18 | band b at m 4; depth: 6e17 at y 0.55, x 0 / 30 / 60 nm, m 4 | 0.35, 0.40; depth 0.30 | library |
| `K_<deck>_hyb_far<N>_N<k>`, `K_hk_n4e18_N<k>` | K 51939558 | both | 1.5e18 | 2e18 at y 0.65 (`damGaussF`, m 4) plus k plain strikes of N; `K_hk_n4e18`: plain 4e18 only | 0.30 | library |
| `m10_<label>`, `m5fix_<label>` | meshChkLoad_m10 51939191, meshChkLoad_m5fix 51939192 | SiN | as the label | as the label | as the label | m10, m5fix |
| `M_m5fix_<label>`, `M_m10_<label>` | radStepM 52044406, radStepM2 52072550 | SiN | as the label | as the label | as the label | m5fix, m10 |
| `D_<label>` (a diagnostic rerun, not round D), `D5_m5fix_<label>`, `D5_lib_<label>` | radStepDiag 51998840, radStepDiag5b 52018703 (`vdCuts`) | SiN | as the label | as the label | as the label | library, m5fix |

**Meshes** (point counts from the run logs, y lines and spacings from a VTK export of locally built meshes):
- **library:** the 28 V stress library (stressLib 51459840, SiN resumed to 84 V by 51998839), 93,080 points, 520 y lines. Its meshY asks for 10 nm over y 0.3-2.6 µm with 5 nm patches at 0.64-0.96, 1.44-1.76 and 2.24-2.56. The deck's rightFP line (y 0.725) breaks the first patch, so the true spacing is 9.5-17.2 nm (mean 13) at y 0.76-0.90; it is 5 nm at 1.6 and 2.4. The figure titles say "15 nm at y 0.8", from the Nov 18 cut-based audit.
- **m10:** 10 nm uniform over y 0.3-2.6 µm, 63,724 points (meshChkStress 51883722 task 0).
- **m5fix:** the library mesh with a true 5 nm over y 0.64-0.96, identical elsewhere, 99,166 points, 554 y lines (meshChkStress 51883722 task 1; its stress took about 24 h).
- **m2p5:** 2.5 nm patches at all three strike sites, 157k points (local grid check). The old-box stress (meshChkStress2p5 52044407) reached Vd 20 in 21.6 h and was cancelled on Nov 20; radStepM3 (the `M_m2p5_` series) was never submitted. A fixed-box 5 nm and 2.5 nm pair is queued (fpFixMesh 52135538, `sweeps/params_fpFixMesh.txt`).

## Mesh-robust series (2026-11-20, radStepM 52044406, radStepM2 52072550)

Full 0-3 strike series of the settings that kept steps at 5 nm, rerun on m5fix and m10. Figures `figures/rad/step28/mesh_deliverable.png` and `mesh_series.png` (every setting × mesh). Reproduce them with:
- `python3 analysis/plot_meshDeliverable.py figures/rad/step28/mesh_deliverable.png lev30_n8 lev40_n7` (this key order made the committed figure);
- `python3 analysis/plot_meshSeries.py` (default output `figures/rad/step28/mesh_series.png`).

The committed figures have three mesh columns. Both scripts now add a fourth, 2.5 nm column (`M_m2p5_` runs), which stays empty until those runs exist.

The table counts drops of at least 8 mA/mm (`common.drop_values(..., DROP_MIN_TABLE, "hyst")`, used by `plot_meshSeries.py`). The deliverable figure marks only drops of at least 10 mA/mm with an arrow, so a drop of 8-10 mA/mm counts here but has no arrow. Drops for 1 / 2 / 3 strikes:

| Setting | Library (9.5-17.2 nm at y 0.76-0.90) | m10 | m5fix |
|---|---|---|---|
| trap 0.30, 8e18 | 2 / 3 / 3 (N3 gave up at 7.0 V) | 2 / 3 / 3 | 2 / 3 / 3 |
| trap 0.40, 7e18 | 3 / 2 / 2 (N3 gave up at 6.1 V) | 2 / 3 / 3 | **1 / 2 / 3** |
| trap 0.40, 6e18 | 2 / 3 / 3 | 3 / 3 / 4 | 2 / 3 / 3 (later drops 10-12 mA/mm) |
| trap 0.40, 5e18 | 2 / 2 / 2 | — | 1 / 1 / 1 (stress drop only) |
| trap 0.30, 7e18 | 2 / 3 / 4 | — | 3 / 2 / 2 (later drops 8-18 mA/mm) |
| trap 0.30, 6e18 (row A) | 3 / 2 / 1 | 3 / 3 / 3 | 2 / 1 / 0 |

- **Trap 0.30 eV with 8e18 strikes is the mesh-robust stepped series.** Every 1-, 2- and 3-strike curve drops two or three times, 2 / 3 / 3 on all three meshes. The first drop starts at 1.1-1.2 / 1.4 / 1.6-1.7 V for 1 / 2 / 3 strikes, within 0.1 V on every mesh. The second moves with the mesh: for 2 and 3 strikes at 3.3-4.1 V on library and m5fix and 5.8-6.8 V on m10; for 1 strike at 4.5-6.1 / 5.6-7.2 / 8.8-9.1 V (library / m10 / m5fix). HighK with the same strikes collapses (library: one strike 262 → 7 mA/mm near 1 V), so the SiN vs HighK contrast is not part of this result.
- **Trap 0.40 eV with 7e18 gives one drop per strike only on m5fix** (3 strikes at 1.4, 3.3, 5.5 V).
- **Next:** the 2.5 nm check, now with the fixed FP box (fpFixMesh 52135538, see Meshes above), then these series on it.

## Mesh check result (2026-11-19): the stress drop converges, the strike steps don't

Same six cases on the library mesh, m10 (meshChkLoad_m10 51939191) and m5fix (51939192); figure `figures/rad/step28/meshchk_steps.png` (`analysis/plot_meshChkSteps.py`).
- **Stress only:** 1.6-2.0 V, 395 → 281 / 273 / 279 mA/mm on library / m10 / m5fix. Converged within 8 mA/mm.
- **What the check meshes change** (true nodes, from a VTK export of locally built meshes; 520 / 554 y lines):
  - m5fix is a clean 5 nm over y 0.64-0.96 (library 4.8-19.6 nm there) and identical elsewhere, including 5 nm at 1.6 and 2.4. So it isolates the y 0.8 refinement.
  - m10 is 10 nm uniform: finer at y 0.8, coarser at 1.6 and 2.4.
  - Spacings read from `print1d` cuts are not reliable on these meshes: the cut is resampled to 500 points ([[flooxs-gotchas]]).
- **Row A plain strikes:** from the library mesh to m5fix the drops shrink and fall in number (3 / 2 / 1 → 2 / 1 / 0 for 1 / 2 / 3 strikes). m10 instead gives three smaller drops for every strike count:

| Case | Library | m10 | m5fix |
|---|---|---|---|
| 1 strike | 3 drops (2.0 V 105, 6.3 V 53, 10.5 V 176 mA/mm) | 3 drops (2.0, 4.4, 10.7 V) | 2 drops: y 0.8 at 1.8-2.1 V (20 mA/mm), stress band at 3.1-3.6 V (56 mA/mm, moved from 6.3 V); the 10.5 V drop is gone |
| 2 strikes | 2 drops (2.2, 3.1 V) | 3 drops | one 22 mA/mm drop at 6.3-6.8 V |
| 3 strikes | 1 drop (4.4-4.8 V) | 3 small drops | no drop above 8 mA/mm |

- **Denser or deeper settings keep their steps on m5fix, smaller:** E_lev0.4_N2 drops at 1.4 / 2.4 / 6.3 V; C_n8e18_N2 at 1.4 / 3.3 V plus a dip at 11.4 V.
- **Why the steps move:** see [[step-mechanism]]. The first-switch threshold (~0.5 V across a damaged pocket) agrees within 0.04 V on both meshes. The switched region (22-35 nm) is only ~2 cells on the library mesh at y 0.84, so it holds more voltage there, and the next pocket switches later. Why the 10.5 V second-stage drop is missing on 5 nm is open.
- **Next level:** 2.5 nm at the strike sites; see the mesh-robust series above.

## Round S (rad28strikeL 51763582, 2026-11-17): 3e18 strikes on the 28 V stress

The starting point. SiN and HighK at damage scale 1.5e18 and 2e18, 0-3 strikes of 3e18 at y 0.8 / 1.6 / 2.4 µm, Vd to 10 V. Figures `figures/rad/strike28/strike28_1.5e18.png` and `strike28_2e18.png` (`python3 analysis/plot_rad28strike.py results/20261117_rad28strikeL 2e+18 <out.png>`).
- **SiN has one drop per curve at every strike count.** Scale 1.5e18: the stress drop only, 395 → 281-289 mA/mm at 1.6-2.3 V. Scale 2e18: a collapse, 275-278 → 38-41 mA/mm at 1.1-1.6 V, then a rise to 162-168 at 10 V. Strikes only delay it (onset 1.1 V with no strike, 1.3 V with three).
- **HighK never drops:** 954-956 mA/mm at 10 V with no strike, 718-780 with 1-3 strikes.
- So 3e18 strikes add no steps. Rounds A-G raised the strike density.

## SiN steps (rounds A-G, strikes at y 0.8 / 1.6 / 2.4 µm)

- Stress damage alone (scale 1.5-1.8e18) gives one drop near 1.5-2 V (C_p1.5_N0: 395 → 281 mA/mm at 1.6-2.0 V, then a creep to ~430 at 12 V).
- Strikes of 5-8e18 add later steps. One 6e18 strike (A_N1) drops near 2, 6.3 and 10.5 V on the library mesh (the Nov 11 shape plus one). On m5fix only two drops remain (1.8-2.1 V at 20 mA/mm, 3.1-3.6 V) and the 10.5 V drop is gone (mesh check above). Trap level 0.40 eV with two 6e18 strikes: drops near 1.5, 2.8 and ~10.5-11 V. Figures `figures/rad/step28/step_best3.png`, `series_*.png`.
- Convergence at Vd step 0.05 V (rounds D/F): step counts hold, step positions move by up to ~0.7-1 V; steps under ~15 mA/mm are not robust (trap 0.40 with three strikes loses its small middle step).
- **Knock-out.** With three 8e18 strikes a step sits near 4 V whichever two strikes remain. Knock-out of strike 1 or 2 (radStepD 51801163) moves it from 3.7-4.0 to 3.5-4.1 V, and strikes 0.8 + 1.6 alone (C_p1.5_n8e18_N2, radStepC 51799741) give 3.9-4.1 V. The pockets share the drain voltage in series, so each strike shifts the others' switching Vd slightly ([[step-mechanism]]).

## HighK also drops with dense strikes (rounds C, F, G)

Strikes dense enough to step SiN (≥ 5e18) also step HighK (C_hk 6e18: 374 → 234 at 1.5-1.9 V; G_hk 5e18: 453 → 388 near 2 V; trap 0.40 with 4e18: 414 → 388). No strike density keeps HighK flat while SiN steps. At y 0.8-2.4 µm HighK's 28 V field is the larger one, so scaling strike damage by the field does not help there.

## Field-scaled strikes (round H, radStepH 51871249)

Lever `gaussFieldM` m multiplies strike damage by (E/E_ref)^m from the stored stress field (default 0). SiN's field exceeds HighK's only over y 0.45-0.65 µm, at the T-gate head's drain edge under the field plate: (E_SiN/E_HK)⁴ = 17 / 30 / 17 / 8.3 / 3.7 at y 0.45 / 0.5 / 0.55 / 0.6 / 0.65 µm, 10 nm below the AlGaN top; HighK's is larger from 0.7 µm on.

- Strikes at y 0.5 (then 0.35, 0.65), partial at 10:30 on Nov 18: HighK with m 4 stays on its no-strike curve (932 mA/mm at 6.7 V); with m 2 and 4e18, 857 at 5.7 V.
- SiN collapses completely at 0.4-1.0 V: m 4 with 3e18 gives 88 → 5e-6 mA/mm, 2e18 gives 138 → 1.5e-3. Strikes 2 and 3 change nothing because the first one dominates, so there are no steps. The collapse is far deeper than the measured ~1000×.
- Unscaled 3e18 at y 0.5: SiN 240 → 8 near 1 V; HighK flattens to ~650.
- At 12 V: SiN with field-scaled strikes at y 0.5 (base 2-4e18) stays at ~0 after its 0.4-1.0 V collapse; HighK stays flat (m 4: 951-956 at 12 V; m 2 with 4e18: 860-902).
- Figure `figures/rad/step28/fieldstrike_H.png` (`analysis/plot_radStepH.py`).

## Round I (51878761, 2026-11-18): field-scaled strikes in the SiN-favoured band

Field-scaled (m 4) strikes at lower density inside y 0.5-0.65 µm, both decks, all to 12 V (no GAVE UP):
- HighK stays on its no-strike curve in every case (~955 mA/mm at 12 V).
- SiN has exactly one drop, near 0.9-2.1 V, whose depth follows strike density and count, then partly recovers. y 0.5 single strikes: 3e17 337 -> 164 at 1.3-1.7 V, 6e17 287 -> 68 at 1.1-1.5 V, 1e18 232 -> 5 at 0.9-1.3 V. Band b (0.65 / 0.6 / 0.55 at 2e18 / 6e17 / 2e17): 1 / 2 / 3 strikes 386 -> 174, 345 -> 91, 310 -> 38. No later steps: strikes in the band all act on the same first collapse.
- Figure `figures/rad/step28/fieldscaled_series.png` (`analysis/plot_radStepFS.py`): 0-3 strikes, SiN collapses deeper with each strike, HighK flat.

## Round J (51922589): trap level and depth with field-scaled strikes

Follow-up, field-scaled m 4, both decks: a deeper trap level or depth-separated strikes don't split the drop. HighK flat in all 8 cases (946-956 mA/mm at 12 V). SiN: one drop per curve, earlier and deeper at 0.40 eV (band b 1/2/3 strikes 244 -> 45, 208 -> 5, 172 -> 0 near 0.8-1.5 V; 0.35 eV 311 -> 99, 272 -> 33, 239 -> 5); strikes at 0, 30 and 60 nm depth at y 0.55 also give one drop (287 -> 79 with one, ~0 with two or three). The halved Vd step reproduces the 3-strike drop (175 -> 5 at 0.8-1.1 V). So strikes confined to the SiN-favoured band act on one onset whatever the trap level or depth.

**Why no field-weighted strike law can give SiN-only steps far from the gate** (28 V library states, 2DEG row 1 nm below the interface; no runs): the stress-time n·E (ElecStress × Estress) peaks at each deck's depletion edge, y ~0.8 µm in SiN (n 5.4e17, SiN/HighK ratio ~5e13) and ~1.1-1.2 µm in HighK (ratio 0.40 at 1.2, 0.13 at 1.6, 0.09 at 2.4). Beyond SiN's depletion edge HighK's lateral field is larger at every position (it spreads the field toward the drain), so any damage law increasing with the stress field, or with field × electron density, favours HighK there. SiN-favoured strike damage stays in one band near the gate, which gives one onset (rounds H-J).

## Round K (radStepK 51939558, 2026-11-18/19): hybrid strikes

Both decks: a field-scaled 2e18 strike at y 0.65 (`damGaussF`, m 4, band b's first strike) plus 1-3 plain far strikes of 3e18 or 4e18 at y 0.8 / 1.6 / 2.4 µm. Plain 4e18 HighK without the near-gate strike is the threshold check. All to 12 V except K_hk_n4e18_N1 (stopped at 10.3 V). No committed figure; plot with `python3 analysis/plot_radStep.py results/20261118_radStepK <out.png> 10`.
- **The hybrid fails.** SiN has only the near-gate drop (386-387 → 174-180 mA/mm at 1.7-2.5 V). The far strikes add no steps.
- **HighK:** far 3e18 strikes give no drop (735-795 mA/mm at 12 V). Far 4e18 strikes give one small drop of 9-19 mA/mm at 2.4-3.6 V (552 → 534-544), the same with or without the near-gate strike (within about 1 mA/mm at 10 V). So HighK's threshold for a strike drop is near 4e18 (round G: 5e18 drops 453 → 388).
- So no single strike model gave SiN steps with HighK flat.

## Where the goal stood before Ian's choice (2026-11-18 evening)

No single strike model yet gives both stepped SiN and flat HighK: plain strikes step SiN but drop HighK; field-scaled strikes keep HighK flat but give SiN one drop. A what-if (not a simulation): if each strike switched only its own share of the gate width and the columns carried current independently, the round I single strikes (whose onsets move with density) would add a small step each between ~0.9 and 2 V while HighK stays flat (`figures/rad/step28/fieldscaled_segments.png`, 25% of the width per strike). Whether one strike can switch that much width is the open 3D question ([[3d-plan]]); decision for Ian.

## Deliverable (Nov 18, superseded by `mesh_deliverable.png`)

Ian, 2026-11-18: option (b), the partial result is fine. Superseded by the mesh-checked figure in the mesh-robust series above: row A's steps shrink or vanish at 5 nm (2 / 1 / 0 drops).

`figures/rad/step28/series_deliverable.png` (`analysis/plot_radStepSeries.py figures/rad/step28/series p15_n6 fs_bandb`), 0-3 strikes on the 28 V stress damage, Vg +1 V, with the Nov 11 model as reference:
- **A. Plain strikes** (damage scale 1.5e18, 6e18 strikes at y 0.8 / 1.6 / 2.4 µm): stepped SiN curves, qualitatively like the Nov 11 model (one strike: drops near 2, 6.3 and 10.5 V). HighK with the same strikes drops too (near 1.5-2.5 V), unlike the measured HighK.
- **B. Field-scaled strikes** (damage × (E/E_ref)⁴, y 0.65 / 0.6 / 0.55 µm): HighK stays on its no-strike curve; SiN has one drop near 1.3-2.1 V that deepens with each strike (386 -> 174, 345 -> 91, 310 -> 38 mA/mm), then partly recovers.
- Mesh check (2026-11-19): row A's steps are not mesh-robust. With 5 nm at y 0.8, the 1-strike curve's y 0.8 drop shrinks from 105 to 20 mA/mm, its stress-band drop moves from 6.3 to 3.3 V and its 10.5 V drop is gone. The 2-strike curve keeps one 22 mA/mm drop at 6.5 V; the 3-strike curve has none. The mechanism is in [[step-mechanism]].

## Nov 18 mesh audit (spacings from `print1d` cuts; superseded by the VTK node check)

Every round S and A-K task runs on the 28 V library mesh (93,080 points, identical for SiN and HighK; stressLoad keeps the file's mesh). The depth (x) mesh is fine: 1 nm through the AlGaN, first GaN line 1 nm below the interface. The audit read these channel (y) spacings at the 2DEG from cuts, which resample to 500 points ([[flooxs-gotchas]]):
- y 0.8 (first strike of every A-G case): the audit read 15 nm. The true nodes are 9.5-17.2 nm (mean 13) at y 0.76-0.90, about 3 cells per σ. The deck's rightFP line (y 0.725) sits inside the 0.64-0.96 meshY patch, so the patch is not 5 nm there.
- y 1.6 and 2.4: a true 5 nm (8 cells per σ), confirmed by the node check.
- Rounds H/I (cut-based, approximate): 9.7 / 9.9 / 8.0 / 6.5 / 5.9 nm at y 0.35 / 0.5 / 0.55 / 0.6 / 0.65.
- The SiN E⁴ damage core (y 0.48-0.63 at 28 V) is on 6-10 nm (cut-based) and has not been refined in any check so far: m5fix and m2p5 refine only from y 0.64. DrainT at 0.485 and rightFP at 0.725 fix the spacing between them.

The dose is resolved (box integration of the Gaussian within 0.4% at every site); the transport response is the question. Existing evidence on related cases: the onset of the first stress drop holds across meshes (1.1-1.6 V), but its size and the level after it do not (28 V, 1.5e18: 141 vs 115 mA/mm drop and +10% after it; 2e18: post-collapse level ~3x apart at 2 V). A σ 40 nm Gaussian with no stress damage (HighK, 0.30 eV, 5e18, y 1.0; radGauss 50128863 at 5 nm, radGauss2 50148046 at 2.5 nm) converges its first drop (1.1-1.3 V, 156-157 → 10.5 mA/mm on both). Its later drops move: two drops at 7.2-7.8 and 8.2-9.1 V on 5 nm become one at 7.8-9.1 V on 2.5 nm, with the same Id at 10 V (123 vs 124 mA/mm) ([[damage-region-map]]). That is the kind of late step the staircases rely on.

Mesh-check stresses (meshChkStress 51883722, SiN, 28 V, saved every volt to `/blue/ee1/ianstafford/stress/meshchk/`): **m10** and **m5fix**. The audit estimated ~64k points / ~22 h and ~99k points / ~51 h; the logs give 63,724 and 99,166 points, and the m5fix stress took about 24 h. The best step cases and a no-strike reference were rerun on each (mesh check above). The 2.5 nm mesh was estimated at ~135k points and ~90 h; the local grid check gives 157k points (see Meshes under Labels).

Related: [[step-mechanism]] (why the curves step), [[rad-literature-steps]] (mechanisms and which tests ran), [[3d-plan]] (part-width tracks), [[rad-model]], [[fp-contact-fix]], [[stress-library]], [[damage-model]].
