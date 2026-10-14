---
title: Late-onset search (field mobility)
tags: [results]
date: 2026-10-02
---
# Late-onset search with field mobility

Goal (Ian, 2026-10-01): push the collapse out to higher Vd with the static-era methods ([[static-era-lessons]]). All at Vg −2, σ 40 nm, Vd 0–4 V, classified per [[collapse-classification]].

| Round | Job | Grid | Result |
|---|---|---|---|
| 1 | 44359813 | level {0.35, 0.45, 0.55} × peak {2,3,4}e18 × hotTau {1, 3, 6, 13}e-14 × hotEb {0.5, 0.85}, y 0.2 | latest deep **1.0 V** (0.35/4e18/3e-14/0.85); ≥4e18 needed |
| 2 | 44433016 | level {0.30, 0.35, 0.40} × peak {4,5,6}e18 × hotTau {1, 1.5, 2, 3}e-14 × hotEb {0.85, 1.0} | latest deep **1.4 V** (0.30/5e18/1.5e-14/0.85); shallower level always later |
| 3 | 44435511 (+ retry 44443669, Te-ramp rescue 44452288) | 8 sets × y {0.2, 0.5, 0.725, 1.0, 1.5, 2.0, 2.4} | latest deep **3.5 V** after rescue |
| 4 | 44440027 | refinement around the 2.3 V device | cancelled by Ian at 44/61, not analysed |

**Best device:** 0.30 eV / 5e18 / `hotTau` 1e-14 / `hotEb` 1.0 at **y = 2.4 µm**: 177 mA/mm at 3.4 V (98.5% of trap-free) → **0.0018 mA/mm at 3.5 V** (~1e5× in one step) → creep to 0.0023 by 4 V, the measured shape. Same set at y = 1.0: deep at 2.3 V from 166 mA/mm. Onset vs y for this set: 1.5, 1.7, 2.1, 2.3, 2.8, (stall 3.7), 3.5 V at y 0.2 … 2.4 µm. Figure `figures/lateOnset_IdVd.png`, `figures/onsetField{1,2,3}.png`.

**Trends:**
- Lower `hotTau` delays onset until the collapse turns shallow; more `trapPeak` keeps it deep — move diagonally.
- Shallower level is better (0.30 > 0.35 > 0.40); `hotEb` 1.0 vs 0.85 ~0.1 V earlier.
- **Position is the strongest lever** — onset rises with distance from the gate ([[position-maps]]).
- Much harder to delay than with static mobility (static reached ~2.2 V at the Run F position).

A local check before round 3 (round-1 best set moved to y = 2.0 µm: deep collapse 1.0 → 1.5 V) showed position is still an onset lever with field mobility.

Round 3 had 19 stalls at the runaway: the damping retry resolved none; the [[te-ramp]] rescued 15. Re-scored: deep 36, medium 7, shallow 9, stalled 4.

Caveat: `hotTau` 1e-14 s is unphysically small; with a solved energy balance at τ ~1 ps these devices collapse at 0.2–0.6 V ([[energy-balance]]).
