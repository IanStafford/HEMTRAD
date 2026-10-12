---
title: FLOOXS builds and binaries
tags: [flooxs, workflow]
---
# FLOOXS builds and binaries

| Build | Where | Notes |
|---|---|---|
| Stock (workstation) | `/usr/local/bin/flooxs`, source `~/flooxs` (`marklaw59/flooxs`, e7c2a30f, 2026-07-02) | what `flooxs …` runs locally; PLplot windows (segfault headless) |
| Stock (HPG) | `/home/ianstafford/blue/ee1/ianstafford/flooxs/release/flooxs` (`FLXSHOME`) | all HEMTRAD sweeps; env `module restore flooxsenv` + conda `flooxs`, `PL_LIBRARY` for plplot ([[hpg-workflow]]); don't modify |
| Crash-fix | `~/flooxs-crashfix/build/flooxs` (branch `crash-fix`), patch `flooxs-crashfix.patch` | clears solver queues on exceptions, non-reentrant exit; results identical ([[munmap-crash]]); local only |

**Building** (stock): CMake; needs Tcl/Tk dev, SuiteSparse (UMFPACK), BLAS/LAPACK, PLplot (`PL_LIBRARY` at run time); `FLXSHOME` must point at the checkout at run time.

**Threads:** UMFPACK uses BLAS threads (OpenBLAS defaults to all cores); assembly is single-threaded. Cap with `OMP_NUM_THREADS`/`OPENBLAS_NUM_THREADS` when several instances share a machine.
