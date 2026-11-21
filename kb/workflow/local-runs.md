---
title: Local runs
tags: [workflow]
---
# Running FLOOXS on the workstation

The rules are in `CLAUDE.md` §3 (one FLOOXS process at a time, kill by PID, headless copies) and §0 (short checks locally, sweeps on HPG). This note holds the details.

**Where to run.** `flooxs drivers/<driver>.tcl` from the repo root suits `pulsedIV.tcl` and `calibIdVg.tcl`: their default outputs (`ivCSV`, `calCSV`) are paths under `figures/`, and the driver finds `model/` itself. `radIV.tcl` and `seeIV.tcl` write everything into the current directory: `<tag>_summary.txt`, `<tag>_IdVg.csv`, `<tag>_IdVd.csv`, cuts, and saved stress states (`stressSaveDir` defaults to `.`). From the repo root these land in the root, untracked and not covered by `.gitignore`. So run them from a scratch folder under `results/` (gitignored), giving the driver path relative to it:
```bash
mkdir -p results/local/<tag> && cd results/local/<tag>
flooxs ../../../drivers/radIV.tcl        # finds ../../../model by itself (modelDir fallback)
```
They have no `window`/`chart` lines, so they need no stripped copy. A copied driver (outside `drivers/`) needs `modelDir` set. If a test does write into the root, move its files out before the next commit.

**Headless.** `pulsedIV.tcl` has GUI lines: strip `window`/`chart` lines in a copy ([[flooxs-gotchas]]). A stripped copy can live anywhere; run it from the repo root.

**One process at a time.** Simultaneous runs slow each other to a crawl. Check `pgrep -x flooxs` first (Ian or another agent may be running one). Chain several local tests in one background loop that checks `pgrep -x flooxs` before each. On days Ian says "everything on HPG", don't run locally at all. Kill by PID; `pkill -f` also matches the issuing shell.

**Timings:**
- `drivers/pulsedIV.tcl`: a point 20–60 s; a 0–3 V sweep 10–30 min.
- `drivers/calibIdVg.tcl` (trap-free): ~5 min, ~25 min with contact resistance.
- `drivers/radIV.tcl` (2026-11-14, SiN, 2 V stress, Id–Vd to 0.5 V): about 14 min with the stress solve, about 1 min when the same state is loaded with `stressLoad`. A gzipped saved state is about 8 MB at 52k points.
- `drivers/seeIV.tcl`: the DC ramp to Vg −5 / Vd 10 V took 2 h (2026-11-18).
- `quickIV.tcl` (trap-free 0–1 V, ~2.5 min) is not in this repo. It was part of the GaN starter package for flooxs-pyplot (copies under `~/flooxs-pyplot/build-*/Test/SimpDev/GaNSuite/`, [[drivers]]).
- More than one or two sweeps, or any full 28 V stress, goes to HPG ([[hpg-workflow]]).

**Local binaries:** stock `flooxs`; crash-fix build `~/flooxs-crashfix/build/flooxs` ([[munmap-crash]]); brick-fix build `~/flooxs-brickfix/build/flooxs` for 3D slices ([[flooxs-builds]]); `~/flooxs-pyplot` (matplotlib plotting, regression harness; [[repo-locations]]).
