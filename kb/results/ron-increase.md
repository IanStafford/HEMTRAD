---
title: Ron increase after biased irradiation
tags: [results, radiation]
date: 2026-11-04
---
# Ron increase after biased irradiation

Simulation study of candidate causes of the larger Ron rise after biased than after unbiased irradiation, and of the abrupt Id–Vd steps onto a nearly gate-independent line. In progress. Literature: [[rad-literature]].

## First results (2026-11-04)

Interim; Ron here is the 0–0.5 V slope at Vg +1 V, against the undamaged reference.

- **A damaged section adds about the same Ron anywhere** (radMap1): +6–7% at 1e18 and +23–32% at 4e18 cm⁻³ for 0.3 µm over the top 50 nm. So Ron alone can't locate the damage.
- **Dielectric charge away from the gate raises Ron with no Vth shift** (radVth, y ≥ 0.30): 1.04, 1.27 and 2.0–2.1× at 1e17, 5e17 and 1e18, with |ΔVth| at most 0.016 V. On both sides of the gate it's 1.05, 1.35–1.38 and 2.2–2.4× (radVth2). This fits a Ron rise that doesn't come with an extra Vth shift, and charge injected under bias is a plausible way to get it, but nothing yet shows that's what happens.
- **Whole-device channel acceptors** give 1.09, 1.35 and 2.15× at 1e17, 5e17 and 2e18, but cost gm too (0.93, 0.78, 0.53).

## Running

radRon (job 49606877, 46 tasks): mobility loss, channel and AlGaN acceptors, and dielectric charge in the gate–drain and source access, each with Ron at Vg −2, −1, 0, +1. radStress (job 49606875, 8 tasks): damage following the irradiation field at exponent 1 and 2. radFam (job 49606874, 7 tasks): Id–Vd from Vg −2 to +1 on SiN, testing whether the current after a step stops depending on Vg.

Related: [[rad-model]], [[damage-region-map]].
