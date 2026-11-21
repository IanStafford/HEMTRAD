---
title: Git conventions
tags: [workflow]
---
# Git conventions

The rules are in `CLAUDE.md` §4 (pull at session start, what to commit and what not, CRLF files, commit before a model change, archive instead of delete). This note holds the details.

## Public repo and measured data
- `IanStafford/HEMTRAD` is **public** (`gh repo view` reports PUBLIC, checked 2026-11-20), and HPG pulls it anonymously over HTTPS ([[hpg-workflow]]). Anything pushed is public.
- Measured device data and notes are never tracked. `.gitignore` lists them: `data/rad_y2/`, `data/rad_y3/`, `kb/results/measured-*.md`, `drivers/trim/*NCY2*`. A tracked file describes measured results in words only, never with their numbers (Ian, 2026-11-20).
- Before creating a new folder or note for measured data, add its path to `.gitignore` and commit that first.
- The HfO2 transfer curve used for calibration (`data/rfDeviceHFO2_Experimental.csv`, raw `.xlsx`) has been tracked since 2026-09-23 (the `.xlsx` since 2026-10-01). These two files are the only measured data in git.
- `data/` is otherwise model-side: TRIM track tables (`data/trim/*_track.json`) and FANGS 3D curves (`data/rad3d_fangs/`, model output). Commit those like any model input or output ([[repo-locations]]).

## Staging
- Stage by explicit path (`git add <file> ...`). Never `git add -A`, `git add .`, `git add data/` or `git add kb/`.
- Before each push, check `git diff --cached --name-only` (and `git log origin/main..` for the commits going out) for measured files.
- Why: on 2026-11-19 a `git add -A kb/` staged two untracked measured notes, and they were pushed in commit 48f40f1. On 2026-11-20 they were purged from history (`git filter-branch`, `main` force-pushed); every commit hash after 902efe7 quoted in `progress.md` before then changed.

## CRLF files
`model/GaN_modelfile_masterD`, `model/Metal.tcl` and `model/Continuity.tcl` must keep CRLF; there is no `.gitattributes`. Edit them from Python so the line endings pass through unchanged:
```python
s = open(p, newline='').read()      # keeps \r\n
s = s.replace(old, new)             # write old and new with \r\n
open(p, 'w', newline='').write(s)
```
Afterwards `file <name>` must still say `with CRLF line terminators`.

## Branches and archive
- `main` is the working branch. `static-mobility` (d2eda77) freezes the pre-2026-10-01 tree.
- `explore/rad-model` was merged into `main` on 2026-11-04. `explore/field-capture` and `explore/gate-injection` are unmerged exploration branches with worktrees in `~/HEMTRAD-wt/` ([[repo-locations]], [[vg-dependence]]).
- Superseded work goes to `archive/<name>/` with a README: `archive/static_mobility/` (HEMTRAD static era), `archive/fangs-hpg-tests/` and `archive/fangs-hpg-first-run/` (FANGS HPG campaigns).
- Commit messages name the runs or lever values and end with the Co-Authored-By / Claude-Session lines from the session's attribution reminder.

Related: [[repo-locations]], [[sweep-pattern]].
