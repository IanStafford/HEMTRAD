---
title: flooxs-pyplot GaN regression baselines
tags: [results, tools]
date: 2026-10-08
---
# GaN regression baselines on HPG (for flooxs-pyplot solver work)

Ian's side task: run flooxs-pyplot's `Test/Regression/gan_hpg` cases on HPG and hand back the results; the flooxs-pyplot session turns them into baselines. **Nothing committed** to either repo.

- Code: flooxs-pyplot **da619c4c**, copied to HPG as a git bundle (HPG has no GitHub credentials) at `/home/ianstafford/blue/ee1/ianstafford/flooxs-pyplot`.
- Build: Intel icpx 2025.1 (`flooxsenv`), `-O2`, `-DEigen3_DIR=/apps/eigen3/3.4.0/share/eigen3/cmake` (HPG `eigen3/3.4.0` module, not installed into the conda env), SuiteSparse/OpenBLAS/Tcl from conda `flooxs`; no FFTW3. Ctests KP-Silicon, Stress-Elastic, Matrix-UMF pass (needs `FLXSHOME` set).
- Runs: array job **45216096**, `hpg-milan` (EPYC 75F3), **16 cores, threads capped at 16, not exclusive** (Ian's option 3: whole nodes weren't being scheduled and the QOS counts every core of an exclusive node; FLOOXS is mostly single-threaded on this device). An exclusive attempt (45214746) was cancelled before starting.
- Results: `~/flooxs-pyplot/Test/Regression/hpg_results/20261008/` (README.txt there); HPG copy `/home/ianstafford/blue/ee1/ianstafford/gan_regress_results/hpg_20261008/`.

| Case | wall s | Newton it | solve s | asm s | last point | RETRY/TERAMP |
|---|---|---|---|---|---|---|
| gan_quickIV | 131.8 | 155 | 88.3 | 35.7 | 136.8518 at 1.0 V | 0/0 |
| gan_calibIdVg | 634.7 | 611 | 481.6 | 147.3 | 2.69e-8 at Vg −4 | 0/0 |
| gan_trapF | 295.3 | 348 | 177.3 | 103.5 | 0.01308 at 1.5 V | 0/0 |
| gan_vg0 | 259.4 | 290 | 160.0 | 85.3 | 0.03557 | 0/0 |
| gan_vgm1 | 284.3 | 318 | 175.6 | 94.5 | 0.01926 | 0/0 |
| gan_sin | 328.1 | 343 | 213.0 | 99.9 | 0.01309 | 0/0 |
| gan_rescue | 1309.8 | 955 | 985.5 | 293.9 | 2.77e-4 at 2.4 V | 6/19 |

Sanity: `gan_quickIV` 17.57962 mA/mm at 0.1 V, 136.8518 at 1.0 V — matches.
