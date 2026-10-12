---
title: munmap_chunk crash
tags: [numerics]
date: 2026-09-27
---
# The `munmap_chunk(): invalid pointer` crash

Diagnosed 2026-09-27 (task 64 of job 43373001, reproduced under gdb on both builds). **It is a teardown artifact, not the real failure.** Chain:
1. Newton diverges at the collapse transition inside `FillStep`'s `device` (RHS → ~1e12); an expression evaluates to NaN/inf and `Values::TestProb` (`BasePDE/Values.cc:207`) throws.
2. The throw unwinds mid-assembly; the solver queues `eq0`/`eq1` (`BasePDE/Solver.h:219`), filled by `ElementQueue::Build()` (sets `InQueue`), are only partly drained and never cleared.
3. `DevController` catches it (`device/DevControl.cc:167`, "Caught Exception!"), `device` returns a Tcl error, the script aborts, Tcl calls `GlobalExit` (`flooxs.cc:727`).
4. `GlobalExit` deletes `fslist` → mesh teardown → a Node still `InQueue` → `Element::~Element` calls `FLPS_panic("Fudge")` → Tcl `exit 1` → re-enters `GlobalExit` → deletes `fslist` again; ~3,300 recursions ("too many nested evaluations") and a double free that glibc reports as `munmap_chunk`, plus a 1–2 GB core.

So "crash" and "Newton iteration-limit stall" are **the same numerical failure** at the runaway with two outcomes (oscillate → limit; diverge → NaN → crash); trajectory-dependent, only partly helped by damping or smaller steps.

- A bare `catch {device}` + retry is **unsafe**: `Solver::InitializeAssembly` (`Solver.cc:433`) refills the queues without clearing, so stale elements are assembled twice, silently.
- `catch` + **`device restore` is safe** on the existing builds: `DevController::Restore()` copies PREV → CURR and `Solver::Restore()` clears the queues. This is the basis of [[retry-bisection]].
- **FLOOXS fix** (local only): branch `crash-fix` in worktree `~/flooxs-crashfix` (built `~/flooxs-crashfix/build/flooxs`) clears the queues and makes `FLPS_panic`/`GlobalExit` non-reentrant; exported as `flooxs-crashfix.patch` (untracked, repo root). Also carried in the flooxs-pyplot repo (commit bddf6092). Not on HPG's stock flooxs.

Since the retry driver (Sep 27) there have been zero `munmap` crashes in HPG sweeps.
