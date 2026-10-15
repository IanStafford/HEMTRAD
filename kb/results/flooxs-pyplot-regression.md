---
title: flooxs-pyplot GaN regression baselines
tags: [results, tools]
date: 2026-10-08
---
# GaN regression baselines on HPG (for flooxs-pyplot solver work)

Ian's side task: run flooxs-pyplot's `Test/Regression/gan_hpg` cases on HPG and hand back the results; the flooxs-pyplot session turns them into baselines. **Nothing committed** to either repo.

- Code: flooxs-pyplot **da619c4c**, copied to HPG as a git bundle (HPG has no GitHub credentials) at `/home/ianstafford/blue/ee1/ianstafford/flooxs-pyplot` (deleted 2026-10-15).
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

## 2026-10-15: HPG campaign for FANGS (commit 28d8af2b), stopped after the build
Campaign `fangs-hpg-tests/` (conda env per flooxs-pyplot's HPG runbook, hpg-milan). The runbook needs `eigen=3.4` (conda-forge now gives Eigen 5) and Python ≥ 3.13 (`core.cc` uses `Py_IsFinalizing`); with both, the two builds compile and the selftest passes. ctest: `build` 5/86, `build-tcl` 81/165. All 77 `Py-*` deck tests fail (Python side exits 1, "trace not written"); `Native-Cmd`/`Expr-Diff` fail on `erfc(26.6–27.2)` (conda libm underflow); `TDR-Read`/`TDR-Diff` fail (HDF5 2.2.0?). Jobs 46060195, 46062866, 46064444. Tier array not run. Handed to the flooxs-pyplot session: `~/flooxs-pyplot/Test/Regression/hpg_results/20261015-fangs/REPORT.md`. HPG folder `/home/ianstafford/blue/ee1/ianstafford/fangs-hpg-20261015/` still there.

## 2026-10-15: rerun 3 at commit 2de5aaee, complete
Runs 1 (28d8af2b) and 2 (92b55cee) stopped at ctest; the flooxs-pyplot session fixed each cause (capped.sh under SLURM, SLURM-independent goldens, erfc underflow, TDR writer overflow; then regress ctests on the env Python, POD eigenvector signs, device_failed_build scratch files). Run 1 and run 2 results are kept as `results-run1`/`results-run2` (HPG) and `20261015-fangs-run1`/`-run2` (workstation).
- Build job **46085435**: builds and selftest rc 0, **ctest 86/86 (Tcl-free) and 165/165 (build-tcl)**. It ran on an overloaded EPYC 7702 node (the build job sets no partition), so the tests took 1.4-4x longer than run 2.
- Tier array **46090409** (23 tasks, hpg-milan, 16 CPUs): all RC=0, 2-22 min each; no OOM, timeouts or cores. The nodes were busy (load 30-50), so timings are noisy. Compare **46090410**.
- **Within this build, every comparison is exact:** tape vs DAG 0 deviation in 7/7; Python vs Tcl 0 in 7/7; thr4v identical in 2/2, with all 503 VERIFY lines `diffs=0`.
- **Against the 2026-10-08 Intel baseline (da619c4c):** only gan_quickIV is `ok`. The other 6 FAIL at the default tolerance (rtol 1e-6, atol 0). Max relative deviations: trapF 4.2e-6, vg0 5.6e-6, vgm1 2.6e-6, sin 8.3e-6, rescue 1.0e-4; calibIdVg is 21 relative but 1e-6 absolute (a near-zero value). Newton counts are equal except vgm1 317/318, sin 344/343, rescue 986/955. Tcl, Python and DAG give the same deviations, so they come from the compiler/platform and code since da619c4c, not from the tape or the Python port.
- Manifest: all 520 data files match. `MANIFEST.sha256` had hashed itself and the compare log while they were still being written; fixed in `compare.slurm`, `fetch_results.sh` and `cleanup.sh`.
- Accepted by the flooxs-pyplot session: 49ae8de8 gives the six cases per-case tolerances (toolchain only; calibIdVg differs in its ~1e-8 mA/mm sub-threshold floor), and all 7 are then ok for tcl, py and dag; the 2026-10-08 baselines stay.
- Results: `~/flooxs-pyplot/Test/Regression/hpg_results/20261015-fangs/REPORT.md`. The six regress reports there were recomputed by the flooxs-pyplot session with the new tolerances; the HPG originals are in `hpg-original/`.
- **Cleaned up 2026-10-15 (Ian):** HPG `fangs-hpg-20261015/` (4.6 GB) and the workstation bundle were deleted with `cleanup.sh`, and the old HPG checkout (da619c4c) was deleted too. The campaign scripts are in `archive/fangs-hpg-tests/`.
