# TRIM smoke-test inputs (2026-11-12)

Archived 2026-11-21 (clean-up stage 4, finding DRV-17 in `kb/workflow/cleanup-plan.md`).

| File | Moved from | What it is |
|---|---|---|
| `TRIM_HighK_Au2256_test20.IN` | `drivers/trim/TRIM_HighK_Au2256_test20.IN` | `drivers/trim/TRIM_HighK_Au2256.IN` with 20 ions instead of 200 |
| `TRIM_SiN_Au2256_test20.IN` | `drivers/trim/TRIM_SiN_Au2256_test20.IN` | `drivers/trim/TRIM_SiN_Au2256.IN` with 20 ions instead of 200 |

**Why archived.** Each differs from its production input only in the ion count on line 3. They were quick checks that the full-cascade Au 2256 MeV inputs run under SRIM before the 200-ion runs of 2026-11-12 (commit f59ee0b). Nothing refers to them, and the track tables `data/trim/{HighK,SiN}_track.json` come from the 200-ion runs (`kb/tools/trim.md`).

**Runs.** Workstation only (SRIM is not on HPG); no job IDs. The SiN smoke output is in `results/trim_SiN_test20/` on the workstation (gitignored).

**How to run one if ever needed.** From the repo root on the workstation: `bin/trim_run.sh archive/trim_smoke/TRIM_SiN_Au2256_test20.IN results/trim_SiN_test20`. One TRIM at a time; it opens a window on Ian's desktop while it runs (`kb/tools/trim.md`).
