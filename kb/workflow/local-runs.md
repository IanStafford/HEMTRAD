---
title: Local runs
tags: [workflow]
---
# Running FLOOXS on the workstation

- `flooxs drivers/<driver>.tcl` from the **repo root** (output paths like `figures/...` are relative to it; the driver finds `model/` itself). A stripped headless copy can live anywhere, but run it from the repo root.
- **One FLOOXS process at a time** — simultaneous runs slow each other to a crawl. Check `pgrep -x flooxs` first (Ian or another agent may be running one). On days Ian says "everything on HPG", don't run locally at all.
- Kill by PID; `pkill -f` also matches the issuing shell.
- Timings: a `drivers/pulsedIV.tcl` point 20–60 s; a 0–3 V sweep 10–30 min; trap-free `drivers/calibIdVg.tcl` ~5 min (~25 min with contact resistance). Trap-free `quickIV` (0–1 V) ~2.5 min. More than one or two sweeps → HPG.
- Chain several local tests in one background loop that checks `pgrep -x flooxs` before each.
- Always headless: strip `window`/`chart` lines in a copy ([[flooxs-gotchas]]).
- Local binaries: stock `flooxs`; crash-fix build `~/flooxs-crashfix/build/flooxs` ([[munmap-crash]]); `~/flooxs-pyplot` (matplotlib plotting, regression harness; [[repo-locations]]).
