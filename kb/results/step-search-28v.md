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

## Round I (51878761, submitted 2026-11-18)

Field-scaled (m 4) strikes at lower density inside the SiN-favoured band: y 0.5 at 3e17 / 6e17 / 1e18; y 0.6 at 1e18; y 0.65 at 3e18; three strikes at 0.65 / 0.6 / 0.55 (3e18 / 1e18 / 3e17 and 2e18 / 6e17 / 2e17). Both decks, 20 tasks. Question: do partial SiN drops stack into steps while HighK stays flat?

Related: [[rad-literature-steps]] (mechanisms), [[3d-plan]] (part-width tracks), [[rad-model]].
