---
title: Run F
tags: [results, reference-set]
---
# Run F — the reference trap set

`trapPeak` 4e18, `trapSigma` 0.04, `trapLevel` 0.55, `hotEb` 0.5, `hotTau` 1.3e-13, at x = 0, y = 0.2 µm (just past the gate drain edge), Vg −2.

- **Static era** (mobility 600): the best `radPlot1`-like shape among runs A–G — 7.8, 7.0 mA/mm at 0.1/0.2 V, then 0.006 at 0.3 V (~1000×), creeping to 0.018 by 1.6 V. Its pre-collapse current fell with Vd where the target rose; moving the blob to y = 2.0 µm fixed most of that ([[static-era-lessons]]).
- **Field mobility:** ~5.6 mA/mm at 0.1 V, collapses at **0.2 V** almost wherever it sits ([[field-mobility-trap-map]]); unchanged at Vg −1/0 (rest ~6–7 mA/mm, collapse 0.2 V, creep to 0.3–0.4 mA/mm by 4 V; [[gate-bias]]). With the [[energy-balance]] at τ 1 ps it collapses at 0.2 V then recovers strongly.
- Exact Run F with field mobility at y = 0.2 is in late-onset round 1 (`results/20261002_onsetField1`); the field Run F map has no y = 0.2 point.
- Used as the base for the flooxs-pyplot regression cases `gan_trapF`, `gan_vg0`, `gan_vgm1`, `gan_sin` ([[flooxs-pyplot-regression]]).
