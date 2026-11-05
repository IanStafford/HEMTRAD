---
title: Ron increase after biased irradiation
tags: [results, radiation]
date: 2026-11-04
---
# Ron increase after biased irradiation

Simulation study of candidate causes of the larger Ron rise after biased than after unbiased irradiation, and of the abrupt Id–Vd steps onto a nearly gate-independent line. In progress. Literature: [[rad-literature]].

## Results (2026-11-05)

Model numbers. Ron is the 0–0.5 V slope. radRon job 49606877 (46 tasks, no crashes), SiN shown; HighK agrees within about 1–5%. These low-field results use smooth or wide damage, and the fine-mesh checks in [[damage-region-map]] left Ron unchanged within about 2%.

| Case | ΔVth (V) | gm ratio | Ron (Ω·mm) at Vg +1 / 0 / −1 / −2 |
|---|---|---|---|
| Undamaged | 0 | 1 | 2.58 / 2.68 / 2.90 / 3.99 |
| Non-biased model (gate acceptors + surface charge) | +0.21 | 0.99 | 2.70 / 2.82 / 3.10 / 5.20 |
| Mobility ×0.5, gate–drain | −0.01 | 0.86 | 3.95 / 4.05 / 4.25 / 5.02 |
| Mobility ×0.3, source access | −0.01 | 0.80 | 3.69 / 3.82 / 4.09 / 5.35 |
| Mobility ×0.8, whole channel | 0 | 0.85 | 3.08 / 3.19 / 3.45 / 4.61 |
| Channel acceptors 5e17, gate–drain | 0 | 0.91 | 3.21 / 3.31 / 3.52 / 4.42 |
| Channel acceptors 2e18, source access | 0 | 0.78 | 3.31 / 3.44 / 3.73 / 5.17 |
| AlGaN acceptors 5e18, gate–drain | 0 | 0.93 | 3.07 / 3.16 / 3.38 / 4.35 |
| Dielectric charge 5e17, y ≥ 0.30 | −0.01 | 0.92 | 3.32 / 3.41 / 3.60 / 4.46 |
| Dielectric charge 1e18, y ≥ 0.30 | −0.02 | 0.79 | 5.50 / 5.57 / 5.74 / 6.33 |

- **Location shows in Ron(Vg), not in Ron at one Vg.** Drain-side damage adds a nearly constant series resistance, about the same at every Vg down to −1, and less at −2. Source-side damage adds slightly more as Vg falls, because it also reduces the gate drive.
- **A Vth shift only shows at low Vg.** +0.21 V adds 0.12 Ω·mm at Vg +1 and 1.21 at −2, since Vg −2 is close to threshold. Any comparison at Vg −2 depends on the device's Vth.
- **Dielectric charge, access acceptors and mobility loss are all viable, and can't be told apart by Ron(Vg) alone.** gm gives some leverage, at a given Ron dielectric and acceptor cases cost less gm than whole-channel mobility loss.
- **Against R33's trend (qualitative):** the gap between biased and non-biased Ron grows as Vg falls. A constant series term alone doesn't do that; a series term plus some extra Vth shift or source-side damage would. This is two different devices with no same-device pre curve, so it's a lead, not a result.
- **Low-exponent field damage doesn't reach it** (radStress, job 49606875): Ron rises at most 9% (E¹, peak 2e18), with no steps and almost the same loss on both decks. So it doesn't explain the larger low-field loss seen on HPD either.
- Contact resistance is still to do as post-processing.

## What's needed from the measurements

Same-device pre and post Id–Vd over several Vg, device width, Vth from the same device, and the order of the Vg curves. Ian has been told a comprehensive dataset is not in hand yet.

Related: [[rad-model]], [[damage-region-map]].
