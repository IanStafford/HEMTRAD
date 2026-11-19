---
title: Stepped collapse at the 28 V stress (rounds A-I)
tags: [results, rad-model, strikes]
date: 2026-11-18
source: progress.md 2026-11-17/18; HPG jobs radStepA-I; test register https://claude.ai/artifact/QEhm71DSp92bNCYGRHNXTm
---
# Stepped SiN collapse at the 28 V stress with ion strikes

Goal set by Ian on 2026-11-17: reproduce stepped Id-Vd curves at the 28 V stress with 1, 2 and 3 strikes, qualitatively like the measured devices or the Nov 11 model. All runs load the 28 V stress state from the library (`stressLoad`, [[levers]]) and add Gaussian strikes (`damGauss`, σ 40 nm, at the AlGaN top) to the E⁴ stress damage (scale `damPeak` 1.5e18, trap level 0.30 eV unless stated, hotEb 1.0 eV, occSafe, Vd step 0.1 V, Vg +1 V). Model output only; the measured curves are compared qualitatively ([[rad-model]]).

## SiN steps (rounds A-G, strikes at y 0.8 / 1.6 / 2.4 µm)

- Stress damage alone (scale 1.5-1.8e18) gives one drop near 1.5-2 V (C_p1.5_N0: 395 → 280 mA/mm at 1.6-2 V, then a creep to ~430 at 12 V).
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

## Mesh (audit 2026-11-18): the strike steps are not mesh-checked

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
- Step positions are provisional until the mesh check (meshChkStress 51883722) reports; the y 0.8 strike sits on 15 nm cells.

Round J (51922589, follow-up, field-scaled m 4, both decks): a deeper trap level or depth-separated strikes don't split the drop. HighK flat in all 8 cases (946-956 mA/mm at 12 V). SiN: one drop per curve, earlier and deeper at 0.40 eV (band b 1/2/3 strikes 244 -> 45, 208 -> 5, 172 -> 0 near 0.8-1.5 V; 0.35 eV 311 -> 99, 272 -> 33, 239 -> 5); strikes at 0, 30 and 60 nm depth at y 0.55 also give one drop (287 -> 79 with one, ~0 with two or three). The halved Vd step reproduces the 3-strike drop (175 -> 5 at 0.8-1.1 V). So strikes confined to the SiN-favoured band act on one onset whatever the trap level or depth.

## Where the goal stood before Ian's choice (2026-11-18 evening)

No single strike model yet gives both stepped SiN and flat HighK: plain strikes step SiN but drop HighK; field-scaled strikes keep HighK flat but give SiN one drop. A what-if (not a simulation): if each strike switched only its own share of the gate width and the columns carried current independently, the round I single strikes (whose onsets move with density) would add a small step each between ~0.9 and 2 V while HighK stays flat (`figures/rad/step28/fieldscaled_segments.png`, 25% of the width per strike). Whether one strike can switch that much width is the open 3D question ([[3d-plan]]); decision for Ian.

Related: [[rad-literature-steps]] (mechanisms), [[3d-plan]] (part-width tracks), [[rad-model]].
