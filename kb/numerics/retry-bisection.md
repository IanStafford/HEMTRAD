---
title: Retry with store/restore and Vd bisection
tags: [numerics, driver]
date: 2026-09-27
source: drivers/pulsedIV.tcl
---
# Retry: catch + store/restore + Vd bisection

Built into `drivers/pulsedIV.tcl` since 2026-09-27. Each Vd point:
1. `SaveState`: `device store`, copy `TrapFrozen` → `TFsave`, `TeTrap` → `TEsave`.
2. `TryPoint`: set Vd, `device`, then `FillStep` (inside `catch`).
3. On failure: `RestoreState` (`device restore` — clears the solver queues, see [[munmap-crash]] — plus the trap memory fields), then **bisect** the Vd step (`retryDepth` levels, default 5; `retrySubFill` 1 = full FillStep at substeps, 0 = plain solve).
4. If bisection fails, try the [[te-ramp]]; if that fails too, print `PULSED GAVE UP at Vd=…` and stop cleanly (no crash).

Output is byte-identical when nothing fails. Log lines: `PULSED Vd=… Id=… peakTe=… retries=N ramps=M`, `RETRY Vd a -> b failed (depth d), bisecting`, `PULSED TERAMP rescued Vd=…`.

Limits: at the runaway, 18/19 round-3 stalls could not step even 0.8 mV past the stall from full current, even with `dampValue` 0.02 and `retryDepth` 7 — a discontinuous jump, not a step-size problem. That's what [[te-ramp]] fixes.

**Step-history dependence (2026-10-13, job 45801978):** after a collapse, each bisection adds accepted solves, and the trap fill and `TeTrap` relaxation are updated once per accepted solve. So a run that bisects more (e.g. with `sweepIterLimit 50`) reaches a different post-collapse Id: late24_t1e-12 gave 0.40 vs 0.13 mA/mm at 0.5 V and 9x at 1 V. Pre-collapse Id is unaffected. Compare post-collapse curves only at the same Vd step and Newton limit ([[levers]]).
