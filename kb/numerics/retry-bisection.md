---
title: Retry with store/restore and Vd bisection
tags: [numerics, driver]
date: 2026-09-27
source: drivers/pulsedIV.tcl, drivers/radIV.tcl, drivers/seeIV.tcl, drivers/fieldPlate.tcl
---
# Retry: catch + store/restore + Vd bisection

Built into `drivers/pulsedIV.tcl` since 2026-09-27; radIV, seeIV and fieldPlate have their own variants (see the table below). In pulsedIV, each Vd point:
1. `SaveState`: `device store`, copy `TrapFrozen` → `TFsave`, `TeTrap` → `TEsave`.
2. `TryPoint`: set Vd, `device`, then `FillStep` (inside `catch`).
3. On failure: `RestoreState` (`device restore`, which also clears the solver queues ([[munmap-crash]]), plus the trap memory fields), then **bisect** the Vd step (`retryDepth` levels, default 5). `retrySubFill` 1 runs the full FillStep at the intermediate substeps, 0 a plain solve there; the measured Vd point always gets FillStep.
4. If bisection fails, try the [[te-ramp]]; if that fails too, print `PULSED GAVE UP at Vd=…` and stop cleanly (no crash).

Output is byte-identical when nothing fails. Log lines: `PULSED Vd=… Id=… peakTe=… retries=N ramps=M`, `RETRY Vd a -> b failed (depth d), bisecting`, `PULSED TERAMP rescued Vd=…`.

Limits: at the runaway, 18/19 round-3 stalls could not step even 0.8 mV past the stall from full current, even with `dampValue` 0.02 and `retryDepth` 7. That is a discontinuous jump, not a step-size problem, and [[te-ramp]] fixes it.

**Step-history dependence (2026-10-13, job 45801978):** after a collapse, each bisection adds accepted solves, and the trap fill and `TeTrap` relaxation are updated once per accepted solve. So a run that bisects more (e.g. with `sweepIterLimit 50`) reaches a different post-collapse Id: late24_t1e-12 gave 0.40 vs 0.13 mA/mm at 0.5 V and 9x at 1 V. Pre-collapse Id is unaffected. Compare post-collapse curves only at the same Vd step and Newton limit ([[levers]]).

## The four variants (2026-11-20)

Four drivers carry their own copy of the retry. The core is the same in all four: `device store`, try the step, on failure `device restore` and reset the contact, then bisect up to `retryDepth` levels. The differences:

| Driver | Contact | Saved with the solution | Substep solves | Fallback | Retry log line | Give-up line | `retryDepth` default |
|---|---|---|---|---|---|---|---|
| `pulsedIV.tcl` (`SaveState`, `RestoreState`, `TryPoint`, `Reach`) | D only | `TrapFrozen`, `TeTrap` | intermediate points: `retrySubFill` (1 = FillStep, 0 = plain solve); the target: the caller's `fill` | [[te-ramp]] (`teRamp 1`) | `RETRY Vd a -> b failed (depth d), bisecting`; counted in `::nRetry` (`retries=N`) | `PULSED GAVE UP at Vd=…` | 5 |
| `radIV.tcl` (`SaveState`, `RestoreState`, `TryBias`, `Reach`, `Ramp`) | any contact | `TrapFrozen`, `TeTrap` when `useTraps` | the caller's `fill` at every point (like `retrySubFill 1`); FillStep only when `useTraps` | none | `RETRY <c> a -> b failed (depth d)`; not counted | `IDVD GAVE UP`, `IDVG GAVE UP`, `RAMP GAVE UP`; the stress drain ramp stops there (an error only below `Vd_stressMin`) | 6 |
| `seeIV.tcl` (`TryBias`, `Reach`, `Ramp`) | any contact | nothing (bare `device store` / `device restore`) | plain solve | none | `RETRY <c> a -> b failed (depth d)` | `RAMP GAVE UP` | 6 |
| `fieldPlate.tcl` (`Reach`) | D only | nothing | plain solve | none | `RETRY Vd a -> b failed (depth d), bisecting` | `FP GAVE UP at Vd=…` | 5 |

- In every variant a failed `Reach` leaves the device at the furthest converged bisection point (the last `device store`), not at the start of the step.
  - radIV records the bias of every converged attempt in `::lastOK($c)`. The stress ramp reports `::lastOK(D)` as the Vd actually reached (since 2026-11-13; the old final runs had stopped at 17.66 V and were labelled 17.0).
  - pulsedIV's `TeRampPoint` starts from that point too: its `RestoreState $dPrev` restores the last stored state and only resets the contact to dPrev.
- seeIV runs with `trapEn 1` but an empty trap density (TrapN 1e-30), and fieldPlate with `trapEn 0`, so neither has trap memory to save.
- seeIV's transient is not bisected by the driver; FLOOXS's own time-step control runs it, and a transient that stops early is written to the summary.
- **Merging them is deferred** ([[cleanup-plan]], DRV-12). `sweeps/radIV.slurm` copies only the model files and builds the task driver from the driver alone, so a `source drivers/lib/…` would fail in HPG task directories. A merge would also change log tags that the crash checks grep for, and could change pulsedIV's `retrySubFill 0` path or radIV's `lastOK` bookkeeping, which changes results through the bisection history (above).
