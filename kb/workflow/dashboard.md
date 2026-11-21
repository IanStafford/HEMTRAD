---
title: Work-log dashboard
tags: [workflow, procedure]
---
# Work-log dashboard and "wrap up for the day"

A private claude.ai artifact, **https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd** ("HEMT Collapse Log"): an Overview page plus one page per working day (Done, Needed work, example figures). Source `dashboard/hemt-collapse-log.html`, web figures `dashboard/fig/`, helper `dashboard/webfig.py`. Always edit the repo copy; never start a new artifact.

Other pages built from `dashboard/` (each is republished to its own URL, never as a new artifact):

| Page | Artifact | Source |
|---|---|---|
| "HEMT Rad Model", explainer for the rad model (written on branch `explore/rad-model`, merged into `main` 2026-11-04) | https://claude.ai/artifact/FArVrMfXX8JNvoFRqYWHLu | `dashboard/rad-model.html` |
| "Rad Study, Nov 4–12", one-off summary of the rad study (commit 60e32e6, 2026-11-12; URL matched by title in the artifact list on 2026-11-20) | https://claude.ai/artifact/5bSeoWJa483VtVGKZuPY31 | `dashboard/rad-week.html` |
| "HEMTRAD Clean-up Plan" ([[cleanup-plan]]) | https://claude.ai/artifact/QTDF84jNysUWQcsTfsswKp | `dashboard/cleanup-plan.html`, built by `python3 dashboard/build_cleanup_page.py` from `kb/workflow/cleanup-plan.md` |

The rad-model and rad-week pages use the same `dashboard/fig/` folder as the work log. Every page stays model-only: model figures, no measured numbers, because the repo is public ([[git-conventions]]).

## When Ian says "wrap up for the day"
1. `git pull`. Gather the day's work from `progress.md`, `git log --since=<date>`, [[current-status]] and running jobs (`squeue`).
2. **Day page** at the top of `<main>`, right after the Overview section and its `<div class="no-js-sep"></div>`, copying the existing structure:
   - `<section class="page" id="mmmdd" data-title="Mon D">`, `.pagehead` with `<h2>Mon D · short headline</h2>`, a one-sentence `<p>`, `.chips` (era chip `chip era-field` "field mobility" or `era-static`; one chip with the day's job IDs).
   - `.cols` with **Done** (`ul.done`, 3–6 one-sentence items, key number in `<span class="num">`) and **Needed work** (`ul.todo`, pill + text). Pills: `pill resolved` ("fixed" / "fixed Mon D"), `pill open`, `pill progress` ("in progress"), `pill noted` ("noted"/"accepted"/"stopped"/"parked").
   - `.figs` with 1–5 `<figure>`s (`.figs wide` for grids/GIFs). Web copies via `python3 dashboard/webfig.py figures/<a>.png ...`; each figure `<a class="img" href="fig/x.jpg" target="_blank" rel="noopener"><img src="fig/x.jpg" alt="…" loading="lazy"></a>` + `<figcaption><b>title</b>takeaway with the number</figcaption>`.
   - `.pager` with `← Overview` and the previous day; point the previous newest day's `← …` link at the new day.
   - **A page that covers several days:** the id comes from the last day and the title is the range, e.g. `id="nov18" data-title="Nov 17–18"` and `<h2>Nov 17–18 · …</h2>`; the rail entry shows the range too.
3. **Nav rail:** `<a href="#mmmdd" data-page="mmmdd"><span class="d">Mon D</span><span class="t">2-3 word topic</span></a>` at the top of the "Field mobility" group.
4. **Overview** (distilled 2026-10-14, keep it short — Ian reads it on his phone): the `.meta` snapshot line under the title ("Snapshot Mon D, end of day"); a 1–2 sentence "where things stand" paragraph ending with the next step; **three** status tiles (values must match the latest results); **Open items** = only the live ones (≤ 5–6, link with `<a class="daylink" href="#mmmdd">`), with superseded or long-standing side questions moved into the `<details class="older">` "Older questions (N)" list. No timeline (the rail lists every day), no eyebrow above the title, no coloured tile borders.
5. **Older days:** only change a fixed item's pill to "fixed Mon D".
6. Style: plain, specific, real numbers, same voice; relative `fig/` paths.
7. **Publish to the same URL:** Artifact `read` first if this conversation hasn't read/published it; then publish `file_path` `dashboard/hemt-collapse-log.html`, `url` above, `root` `dashboard`, `files` = new `fig/...` entries. No `icon`.
8. Commit `dashboard/`, add a dated `progress.md` line, push, push-notify Ian with the link. Also refresh [[current-status]] in this KB.

Same-day re-wraps update that day's page instead of adding a second one.
