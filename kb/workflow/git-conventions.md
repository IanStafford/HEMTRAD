---
title: Git conventions
tags: [workflow]
---
# Git conventions

- Start of session: `git pull`. After meaningful changes: commit (message names the runs or lever values) and push.
- **Commit:** `model/`, `drivers/`, `sweeps/` (templates + params), `analysis/`, `data/`, `progress.md`, `kb/`, `dashboard/`, small final CSVs and figures used in write-ups.
- **Don't commit:** `results/` sweep directories, `.out`/`.err`, meshes, build artifacts (gitignored), `.obsidian/`.
- **CRLF files:** `model/GaN_modelfile_masterD`, `model/Metal.tcl`, `model/Continuity.tcl` must keep CRLF (no `.gitattributes`). Edit from Python with `open(..., newline='')`, check `file <name>` afterwards.
- Commit **before** changing any model file (`model/GaN_modelfile_masterD`, `model/Poisson.tcl`, `model/GaN.tcl`, `model/AlGaN.tcl`, `model/Metal.tcl`, `model/Insulator.tcl`, `model/Continuity.tcl`, `model/ETemp.tcl`, `rfdevice*.tcl`).
- Superseded work goes to `archive/<name>/` with a README (e.g. `archive/static_mobility/`), not deleted. Branch `static-mobility` (d2eda77) freezes the pre-2026-10-01 tree.
- Commit messages end with the Co-Authored-By / Claude-Session lines from the session's attribution reminder.

Related: [[repo-locations]].
