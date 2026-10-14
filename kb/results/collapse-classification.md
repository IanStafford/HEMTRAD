---
title: Collapse classification
tags: [results, definitions]
date: 2026-10-01
---
# Collapse classification (Ian, 2026-10-01)

Classify a device by its **largest single-step loss**, 1 − Id(Vd_n)/Id(Vd_n−1), over the sweep:
- **deep:** > 95% of the previous-step current lost in one step;
- **medium:** 50–95%;
- **shallow:** < 50%.

**Onset** = Vd of the **first** step that reaches the class threshold (>95% deep, ≥50% medium; for shallow, the largest step). Changed 2026-10-02 from "Vd of the largest step", which misreported two-step collapses (e.g. 99.92% at 1.5 V then 99.95% from the already-collapsed level at 2.3 V).

- **Off at rest:** Id < 10% of trap-free at Vd 0.1 V — a threshold shift, not a collapse.
- **Stalled:** the run stopped (`PULSED GAVE UP`) before `Vd_max` with no recorded collapse; onset = the Vd it couldn't reach (added 2026-10-02 — before that they were wrongly counted shallow, and a write-up missed 19 of them).

Also check the **pre-collapse current**: some deep collapses start from an already-sagged current and are less clean.

Implemented in `analysis/analyze_onset.py` and `analysis/plot_posVd.py` ([[analysis-scripts]]). Earlier metrics (static era): collapse ratio peak/min (biased by onset) → collapse depth vs trap-free, and suppression at a fixed Vd ([[glossary]]).
