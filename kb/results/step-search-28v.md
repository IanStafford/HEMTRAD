---
title: Stepped collapse at the 28 V stress (rounds A-K, mesh check)
tags: [results, rad-model, strikes]
date: 2026-11-19
source: progress.md 2026-11-17/18/19; HPG jobs radStepA-K, meshChkStress 51883722, meshChkLoad 51939191/51939192; test register https://claude.ai/artifact/QEhm71DSp92bNCYGRHNXTm
---
# Stepped SiN collapse at the 28 V stress with ion strikes

Goal set by Ian on 2026-11-17: reproduce stepped Id-Vd curves at the 28 V stress with 1, 2 and 3 strikes, qualitatively like the measured devices or the Nov 11 model. All runs load the 28 V stress state from the library (`stressLoad`, [[levers]]) and add Gaussian strikes (`damGauss`, σ 40 nm, at the AlGaN top) to the E⁴ stress damage (scale `damPeak` 1.5e18, trap level 0.30 eV unless stated, hotEb 1.0 eV, occSafe, Vd step 0.1 V, Vg +1 V). Model output only; the measured curves are compared qualitatively ([[rad-model]]).

## SiN steps (rounds A-G, strikes at y 0.8 / 1.6 / 2.4 µm)

- Stress damage alone (scale 1.5-1.8e18) gives one drop near 1.5-2 V (C_p1.5_N0: 395 → 281 mA/mm at 1.6-2.0 V, then a creep to ~430 at 12 V).
- Strikes of 5-8e18 add later steps. One 6e18 strike: drops near 2, 6.3 and 10.5 V (the Nov 11 shape plus one). Trap level 0.40 eV with two 6e18 strikes: drops near 1.5, 2.8 and ~10.5-11 V. Figures `figures/rad/step28/step_best3.png`, `series_*.png`.
- Convergence at Vd step 0.05 V (rounds D/F): step counts hold, step positions move by up to ~0.7-1 V; steps under ~15 mA/mm are not robust (trap 0.40 with three strikes loses its small middle step).
- Strikes interact: any two of the three strikes give a step near 4 V.

## HighK also drops with dense strikes (rounds C, F, G)

Strikes dense enough to step SiN (≥ 5e18) also step HighK (C_hk 6e18: 374 → 234 at 1.5-1.9 V; G_hk 5e18: 453 → 388 near 2 V; trap 0.40 with 4e18: 414 → 388). No strike density keeps HighK flat while SiN steps. At y 0.8-2.4 µm HighK's 28 V field is the larger one, so scaling strike damage by the field does not help there.

## Field-scaled strikes (round H, 51871249, partial at 10:30 on Nov 18)

Lever `gaussFieldM` m multiplies strike damage by (E/E_ref)^m from the stored stress field (default 0). SiN's field exceeds HighK's only over y 0.45-0.65 µm, at the T-gate head's drain edge under the field plate: (E_SiN/E_HK)⁴ = 17 / 30 / 17 / 8.3 / 3.7 at y 0.45 / 0.5 / 0.55 / 0.6 / 0.65 µm, 10 nm below the AlGaN top; HighK's is larger from 0.7 µm on.

- Strikes at y 0.5 (then 0.35, 0.65): HighK with m 4 stays on its no-strike curve (932 mA/mm at 6.7 V); with m 2 and 4e18, 857 at 5.7 V.
- SiN collapses completely at 0.4-1.0 V: m 4 with 3e18 gives 88 → 5e-6 mA/mm, 2e18 gives 138 → 1.5e-3. Strikes 2 and 3 change nothing because the first one dominates, so there are no steps. The collapse is far deeper than the measured ~1000×.
- Unscaled 3e18 at y 0.5: SiN 240 → 8 near 1 V; HighK flattens to ~650.
- Figure `figures/rad/step28/fieldstrike_H.png` (`analysis/plot_radStepH.py`).

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

- **Denser or deeper settings keep their steps, smaller:** E_lev0.4_N2 drops at 1.4 / 2.4 / 6.3 V; C_n8e18_N2 at 1.4 / 3.3 V plus a dip at 11.4 V.
- **Why the steps move:** see [[step-mechanism]]. The first-switch threshold (~0.5 V across a damaged pocket) agrees within 0.04 V on both meshes. The switched region (22-35 nm) is only ~2 cells on the library mesh at y 0.84, so it holds more voltage there, and the next pocket switches later. Why the 10.5 V second-stage drop is missing on 5 nm is open.
- **Next level:** 2.5 nm at the strike sites (new stress, ~90 h); Ian's call.

## Mesh-robust series (2026-11-20, radStepM 52044406, radStepM2 52072550)

Full 0-3 strike series of the settings that kept steps at 5 nm, rerun on m5fix and m10. Figures `figures/rad/step28/mesh_deliverable.png` (`analysis/plot_meshDeliverable.py lev30_n8 lev40_n7`) and `mesh_series.png` (`analysis/plot_meshSeries.py`, every setting × mesh). Drops ≥ 8 mA/mm for 1 / 2 / 3 strikes:

| Setting | Library (15 nm at y 0.8) | m10 | m5fix |
|---|---|---|---|
| trap 0.30, 8e18 | 2 / 3 / 3 (N3 gave up at 7.0 V) | 2 / 3 / 2 (N1, N3 partial at 7.7 / 8.8 V) | 2 / 3 / 3 |
| trap 0.40, 7e18 | 3 / 2 / 2 (N3 gave up at 6.1 V) | 2 / 3 / 2 (partial, 7.4-7.7 V) | **1 / 2 / 3** |
| trap 0.40, 6e18 | 2 / 3 / 3 | 3 / 3 / 4 | 2 / 3 / 3 (later drops 10-12 mA/mm) |
| trap 0.40, 5e18 | 2 / 2 / 2 | — | 1 / 1 / 1 (stress drop only) |
| trap 0.30, 7e18 | 2 / 3 / 4 | — | 3 / 2 / 2 (later drops 8-18 mA/mm) |
| trap 0.30, 6e18 (row A) | 3 / 2 / 1 | 3 / 3 / 3 | 2 / 1 / 0 |

- **Trap 0.30 eV with 8e18 strikes is the mesh-robust stepped series.** Every 1-, 2- and 3-strike curve drops two or three times on all three meshes. The first drop starts at 1.1-1.2 / 1.4 / 1.6-1.7 V for 1 / 2 / 3 strikes, within 0.1 V on every mesh. The second moves with the mesh: for 2 and 3 strikes at 3.3-4.1 V on library and m5fix and 5.8-6.8 V on m10; for 1 strike at 4.5-6.1 / 5.6-7.2 / 8.8-9.1 V (library / m10 / m5fix). HighK with the same strikes collapses (library: one strike 262 → 7 mA/mm near 1 V), so the SiN vs HighK contrast is not part of this result.
- **Trap 0.40 eV with 7e18 gives one drop per strike only on m5fix** (3 strikes at 1.4, 3.3, 5.5 V).
- **Next:** the 2.5 nm stress (meshChkStress2p5 52044407, Ian: keep it running), then these series on it.

## Mesh (audit 2026-11-18, before the check)

Every round A-I task runs on the 28 V library mesh (93,080 points, identical for SiN and HighK; stressLoad keeps the file's mesh). The depth (x) mesh is fine: 1 nm through the AlGaN, first GaN line 1 nm below the interface. The channel (y) spacing at the 2DEG:
- y 0.8 (first strike of every A-G case): **15 nm**, 2.7 cells per σ. The deck's rightFP line (y 0.725, 20 nm) sits inside the 0.64-0.96 meshY patch, so the patch is not 5 nm there.
- y 1.6 and 2.4: a true 5 nm (8 cells per σ).
- Rounds H/I: 9.7 / 9.9 / 8.0 / 6.5 / 5.9 nm at y 0.35 / 0.5 / 0.55 / 0.6 / 0.65.
- The SiN E⁴ damage core (y 0.48-0.63 at 28 V) is on 6-10 nm and has never been refined in any check so far (DrainT at 0.485 and rightFP at 0.725 fix the spacing between them).

The dose is resolved (box integration of the Gaussian within 0.4% at every site); the transport response is the question. Existing evidence on related cases: the onset of the first stress drop holds across meshes (1.1-1.6 V), but its size and the level after it do not (28 V, 1.5e18: 141 vs 115 mA/mm drop and +10% after it; 2e18: post-collapse level ~3x apart at 2 V). A σ 40 nm Gaussian with no stress damage converges its first drop between 5 and 2.5 nm, but its later drops (7-10 V) move and change size, which is the kind of late step the staircases rely on.

Mesh-check stresses (meshChkStress 51883722, SiN, 28 V, saved every volt to `/blue/ee1/ianstafford/stress/meshchk/`): **m10**, 10 nm uniform over 0.3-2.6 µm (~64k points, ~22 h), and **m5fix**, the library mesh with a true 5 nm at y 0.8 (~99k points, ~51 h). The best step cases and a no-strike reference get rerun on each. A 2.5 nm mesh at the strike sites (~135k points, ~90 h) is the next level if needed.

## Round I (51878761, 2026-11-18): field-scaled strikes in the SiN-favoured band

Field-scaled (m 4) strikes at lower density inside y 0.5-0.65 µm, both decks, all to 12 V (no GAVE UP):
- HighK stays on its no-strike curve in every case (~955 mA/mm at 12 V).
- SiN has exactly one drop, near 0.9-2.1 V, whose depth follows strike density and count, then partly recovers. y 0.5 single strikes: 3e17 337 -> 164 at 1.3-1.7 V, 6e17 287 -> 68 at 1.1-1.5 V, 1e18 232 -> 5 at 0.9-1.3 V. Band b (0.65 / 0.6 / 0.55 at 2e18 / 6e17 / 2e17): 1 / 2 / 3 strikes 386 -> 174, 345 -> 91, 310 -> 38. No later steps: strikes in the band all act on the same first collapse.
- Figure `figures/rad/step28/fieldscaled_series.png` (`analysis/plot_radStepFS.py`): 0-3 strikes, SiN collapses deeper with each strike, HighK flat.

Round H at 12 V: SiN with field-scaled strikes at y 0.5 (base 2-4e18) stays at ~0 after its 0.4-1.0 V collapse; HighK flat (m 4: 951-956 at 12 V; m 2 with 4e18: 860-902).

## Deliverable (Ian, 2026-11-18: option (b), the partial result is fine)

`figures/rad/step28/series_deliverable.png` (`analysis/plot_radStepSeries.py figures/rad/step28/series p15_n6 fs_bandb`), 0-3 strikes on the 28 V stress damage, Vg +1 V, with the Nov 11 model as reference:
- **A. Plain strikes** (damage scale 1.5e18, 6e18 strikes at y 0.8 / 1.6 / 2.4 µm): stepped SiN curves, qualitatively like the Nov 11 model (one strike: drops near 2, 6.3 and 10.5 V). HighK with the same strikes drops too (near 1.5-2.5 V), unlike the measured HighK.
- **B. Field-scaled strikes** (damage × (E/E_ref)⁴, y 0.65 / 0.6 / 0.55 µm): HighK stays on its no-strike curve; SiN has one drop near 1.3-2.1 V that deepens with each strike (386 -> 174, 345 -> 91, 310 -> 38 mA/mm), then partly recovers.
- Mesh check (2026-11-19): row A's steps are not mesh-robust. With 5 nm at y 0.8, the 1-strike curve's y 0.8 drop shrinks from 105 to 20 mA/mm, its stress-band drop moves from 6.3 to 3.3 V and its 10.5 V drop is gone. The 2-strike curve keeps one 22 mA/mm drop at 6.5 V; the 3-strike curve has none. The mechanism is in [[step-mechanism]].

Round J (51922589, follow-up, field-scaled m 4, both decks): a deeper trap level or depth-separated strikes don't split the drop. HighK flat in all 8 cases (946-956 mA/mm at 12 V). SiN: one drop per curve, earlier and deeper at 0.40 eV (band b 1/2/3 strikes 244 -> 45, 208 -> 5, 172 -> 0 near 0.8-1.5 V; 0.35 eV 311 -> 99, 272 -> 33, 239 -> 5); strikes at 0, 30 and 60 nm depth at y 0.55 also give one drop (287 -> 79 with one, ~0 with two or three). The halved Vd step reproduces the 3-strike drop (175 -> 5 at 0.8-1.1 V). So strikes confined to the SiN-favoured band act on one onset whatever the trap level or depth.

Why no field-weighted strike law can give SiN-only steps far from the gate (28 V library states, 2DEG row 1 nm below the interface): the stress-time n·E (ElecStress × Estress) peaks at each deck's depletion edge, y ~0.8 µm in SiN (n 5.4e17, SiN/HighK ratio ~5e13) and ~1.1-1.2 µm in HighK (ratio 0.40 at 1.2, 0.13 at 1.6, 0.09 at 2.4). Beyond SiN's depletion edge HighK's lateral field is larger at every position (it spreads the field toward the drain), so any damage law increasing with the stress field, or with field × electron density, favours HighK there. SiN-favoured strike damage stays in one band near the gate, which gives one onset (rounds H-J).

## Where the goal stood before Ian's choice (2026-11-18 evening)

No single strike model yet gives both stepped SiN and flat HighK: plain strikes step SiN but drop HighK; field-scaled strikes keep HighK flat but give SiN one drop. A what-if (not a simulation): if each strike switched only its own share of the gate width and the columns carried current independently, the round I single strikes (whose onsets move with density) would add a small step each between ~0.9 and 2 V while HighK stays flat (`figures/rad/step28/fieldscaled_segments.png`, 25% of the width per strike). Whether one strike can switch that much width is the open 3D question ([[3d-plan]]); decision for Ian.

Related: [[step-mechanism]] (why the curves step), [[rad-literature-steps]] (mechanisms), [[3d-plan]] (part-width tracks), [[rad-model]].
