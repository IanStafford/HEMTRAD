---
title: Te-ramp fallback
tags: [numerics, driver]
date: 2026-10-02
source: pulsedIV.tcl (TeRampPoint)
---
# Te-ramp fallback (stall fix at the runaway)

**Problem:** many late-onset devices stalled (`PULSED GAVE UP`) at full current at the runaway (round 3: 19/56; position map: 11/65). Diagnosis: at the stall the plain solve at the new Vd converges, but the next solve after `UpdateTe` moves Te halfway (w 0.5) to its target diverges.

**Fix** (`TeRampPoint`, lever `teRamp` 1, only runs where a point would otherwise give up): hold Vd, step Te with adaptive w — start `teRampW0` 0.1, halve on failure down to `teRampMin` 0.002, ×1.5 on success (max 0.5) — with `CaptureTraps` after each sub-step, until Te is within `teRampTol` 1% of target (max `teRampMax` 300 sub-steps). Results up to the stall are byte-identical. Log lines `TERAMP Vd=… step k w=… mismatch=…`.

**Results:** jobs 44452288 / 44452289 rescued **15/19** round-3 stalls and **9/11** position-map stalls → latest deep collapse 2.3 → **3.5 V** ([[late-onset-search]]).

**Still open:** 6 stalls left, all near y = 2.0 µm (2.8–3.7 V); w shrinks below 0.002 at full current, so a lower `teRampMin` may get them.

**Caveat:** a rescued point is driven closer to the fill-only steady state (Te within 1%) than a normal point (4 × w 0.5), so its depth is not strictly comparable.

With the [[energy-balance]] on, the ramp never starts because the plain solve at the next Vd already fails.

Related: [[retry-bisection]], [[collapse-classification]].
