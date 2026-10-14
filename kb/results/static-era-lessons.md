---
title: Static-mobility era lessons
tags: [results, archive]
period: 2026-09-23 to 2026-10-01
---
# Lessons from the static-mobility era

Everything here used constant mobility 600 (superseded; field mobility collapses earlier and deeper, so treat numbers as indicative). Full write-ups: `archive/static_mobility/RESULTS.md` (§10–§10l), scripts and figures in `archive/static_mobility/`, branch `static-mobility`.

- **Run F tuning (§10):** runs A–G against `radPlot1` (9.75, 19.0, 27.2, 32.0 mA/mm at 0.1–0.4 V, then 0.011 at 0.5 V). Shallower level → more pre-collapse current and a deeper collapse; more charge → deeper until it pinches at rest (~5e18 × 0.025²); onset ∝ ~1/√`hotTau`. → [[run-F]].
- **Late-onset rounds A–I (§10b):** onset and depth are coupled — more `trapPeak`, `hotTau` or `hotEb` gives earlier *and* deeper. Escape by moving diagonally (less charge, higher `hotEb`/`hotTau`, shallower level); `hotEb` is the strongest depth lever. Accepted answer (Ian, 09-25): **3e18 / σ 0.04 / 0.35 eV / `hotEb` 0.85 / `hotTau` 6e-14 → onset ~2.2–2.3 V, ~2000×** (123 → 0.061 mA/mm, creep to 0.54 by 4 V).
- **Placement (§10c):** lateral position is the strongest placement lever; the gate edge pinches at rest; traps nearer the 2DEG collapse earlier and deeper. **Closest `radPlot1` match: x = 0, y = 2.0 µm** (onset exactly 0.5 V, depth matches; 0.4 V point sags). Open question: is a blob ~2 µm into the access region physically plausible?
- **50-location map (§10d):** traps under the gate/at its edge are the most damaging (off at rest, ~1e6× suppression); near source and drain ~1e5×; y = 2.5 µm weakest (600×); y = 3.0 may be contact-proximity behaviour.
- **Concentration × level × position (§10e):** three regimes — deep levels (0.75 eV) at ≥4e18 or 0.55 eV at 8e18 fill at rest (off); the hot-electron collapse lives in a band (4e18/0.35, 4e18/0.55, 8e18/0.35); 2e18 only matters under the gate. Level acts more strongly than concentration.
- **3D map sets (§10f):** first sweep with the retry driver — 0 crashes. Gate region most damaging in every set; onset moves later with distance from the gate; collapse metric changed to depth vs trap-free (peak/min is biased by onset, corr ~+0.9).
- **Cone vs Gaussian (§10g):** at 2e18/0.75 nothing collapses; only near-surface charge over the gate matters; cone length irrelevant past ~50 nm. Access-region cone results are mesh artifacts ([[mesh]]).
- **Insulator traps (§10j)** → [[insulator-traps]]. **Deep traps (§10k):** the "deep" collapse at 40 nm was the σ = 40 nm tail at the 2DEG; with σx 10 nm, traps ≥25 nm below the 2DEG do nothing outside the gate (only damage within ~15–25 nm of the 2DEG matters — relevant for TRIM).
- **HighK vs SiN (§10l)** → [[highk-vs-sin]]. **Critical strike (§10i)** → [[critical-strike]].
- Tooling from this era: [[munmap-crash]] diagnosis and [[retry-bisection]].
