# Progress log

## 2026-09-24

- Checked HPG connection: `ssh -O check hpg` → master running (pid=55446), OK.
- Ran `squeue -u $USER` on HPG: no jobs queued or running (empty queue).
- Nothing pending; no run submitted this check.

### Task: push Run F's collapse onset from Vd~0.3V to Vd~3V

Goal: keep Run F's dramatic collapse shape (7.8/7.0 mA/mm pre-collapse, ~1000x
drop, creep-up after) but move the onset ~10x later in Vd.

Per the "onset Vd scales roughly as 1/sqrt(hotTau)" trend (section 10),
reaching onset~3V from F's onset~0.3V by hotTau alone needs hotTau scaled by
(0.3/3)^2 = 1/100, i.e. hotTau ~= 1.3e-13/100 = 1.3e-15 s. That is a 100x
extrapolation past anything tested (smallest tested/planned so far is
4e-14, then 0.4-0.6e-13 next). 1.3e-15 s (1.3 fs) is faster than typical
energy relaxation times (~0.1-1 ps) - i.e. this pushes hotTau to a value
that isn't really physical on its own.

Ran two local coarse probes (uncommitted, deleted after use), Vd 0-4V in
0.25V steps, F's trap params (trapPeak=4e18, trapSigma=0.04, trapLevel=0.55,
hotEb=0.5), varying only hotTau:

- **hotTau=1.3e-15** (the naive 1/sqrt(hotTau) extrapolation): no collapse
  at all through Vd=4V. Id rises smoothly to 115 mA/mm (normal saturating
  Id-Vd), peak Te only reaches 353K vs 300K lattice - nowhere near enough
  to cross the 0.5 eV hot-capture barrier. The scaling law was fit from a
  2-point range near hotTau~1e-13 and does not hold 100x out; at this
  hotTau the hot-electron heating term is just too weak, full stop, not
  merely "later."
- **hotTau=1e-14** (10x below F, not 100x): partial effect. Id peaks at
  42.4 mA/mm (Vd=0.75V), sags to 28.9 (Vd=1.25V, ~1.5x drop, not ~1000x),
  then recovers/creeps up to 45.7 by Vd=4V. Peak Te reaches 1044K by Vd=4,
  much hotter than the 1.3e-15 case but still nowhere near F's Te at its
  own collapse point (peak Te ~3000-8500K in `pulsedIV_F.csv`). So lower
  hotTau alone trades onset delay for collapse depth - it does not give a
  later *and* dramatic collapse with F's trap charge.

**Conclusion:** hotTau alone can't hit onset~3V while keeping the dramatic
(~1000x) depth. Getting there needs more total trapped charge
(trapPeak x trapSigma^2) to compensate the weaker/later heating, i.e. a
joint (trapPeak, hotTau) search, not a 1-D hotTau extrapolation. This
is a physics/lever decision beyond what the documented single-variable
trend covers, so flagging before committing HPG resources to a grid.

**Proposed HPG grid** (`ee1` QOS currently idle - `squeue -A ee1` shows
0 jobs, full 19-CPU headroom):
- trapPeak in {4e18 (F), 6e18, 8e18}, trapSigma=0.04 fixed (watch for
  channel pinch-off at rest/Vd=0 - the noted risk point for high trapPeak
  was with trapSigma=0.025; 0.04 spreads it more, but should still check
  each task's Vd=0.1-0.2 baseline before trusting the rest)
- hotTau in {1e-14, 0.7e-14, 0.5e-14}
- hotEb=0.5, trapLevel=0.55, trapMeanY=0.20 fixed (F's values)
- 9-task array, coarse Vd_step=0.15 out to Vd_max=4.05 (28 points/task,
  ~74 min extrapolated from the 45min/17-point baseline; asking for
  --time=01:30:00, --mem=4gb, --cpus-per-task=1, --array=0-8%9)
- Once a combo lands onset near 3V with a ~1000x drop, follow up with a
  single full-resolution (0.1V step) confirmation run.

**Ian approved the grid as proposed.** Made `pulsedIV.tcl`'s levers
`info-exists`-guarded (defaults unchanged) so tasks can override them,
committed `pulsedIV_lateOnset.slurm` + `params_lateOnset.txt`, pushed
(ea69ef7), pulled on HPG, `mkdir -p results/20260924_lateOnset`, and
submitted: **job 43252782, array 0-8 (9 tasks)**, `ee1` QOS was idle
before submit. Writing per-task CSVs `pulsedIV_tp<trapPeak>_ht<hotTau>.csv`
+ `params.json` into `results/20260924_lateOnset/task_<id>/`.

**Job 43252782 finished, all 9 tasks clean** (no Newton failures/NaN/OOM
in any `.out`/`.err`, all 9 CSVs present with the full 28 rows). Pulled
back with `rsync`, analyzed. **Result: none of the 9 combos hit the
target** - see CLAUDE.md section 10b for the full table. Summary:

- `trapPeak`=4e18 (F's charge) + any tested `hotTau` (1e-14, 7e-15, 5e-15):
  no collapse at all through Vd=4.05V - current just rises and plateaus
  (46.6 / 66.4 / 88.5 mA/mm at 4.05V respectively). Confirms the local
  probes: below a certain `hotTau`, the hot-electron effect just doesn't
  trigger a collapse at F's charge, it doesn't merely delay it.
- `trapPeak`=6e18 or 8e18 (more charge, meant to restore depth): channel
  is **already collapsed by Vd=0.15V**, the very first sweep point - e.g.
  6e18/1e-14 drops from 2.5 to 0.49 mA/mm by Vd=0.6V, and 8e18 cases sit
  at 0.03-0.6 mA/mm from the start. This isn't a late onset, it's an
  always-on collapse: the *cold*, zero-field trap occupancy at
  `trapLevel`=0.55 eV is already large enough at these densities to pinch
  the channel at rest, independent of `hotTau`.

So `trapPeak` and `hotTau` don't decompose into independent "depth" and
"onset" knobs the way the section 10 trends (fit near F) suggested -
that breaks down over this much wider a sweep.

**Proposed next round** (see CLAUDE.md 10b for the reasoning): use
`trapLevel` to decouple cold (at-rest) occupancy from hot (Vd-driven)
capture - shallower `trapLevel` empties more at rest, buying headroom to
push `trapPeak` higher without an always-on collapse, while `hotEb`/
`hotTau` still gate how much extra density the hot-electron process pulls
in once the channel heats up. Grid: `trapLevel` ∈ {0.35, 0.45} ×
`trapPeak` ∈ {8e18, 1.2e19, 1.6e19}, `hotTau`=1e-14 fixed, `trapSigma`=0.04,
`hotEb`=0.5 - 6 tasks.

**Ian asked to stop here for now and review before another HPG run.**
Nothing further submitted. No pending jobs on HPG (`ee1` QOS idle). Task
is paused, not abandoned - the `trapLevel`×`trapPeak` grid above is ready
to go (driver already supports it via the `info-exists` overrides) once
he says go.

## 2026-09-25

Checked HPG connection (`ssh -O check hpg`, master pid=11377, OK) and
resumed. Ian approved the round B grid. Submitted:
**job 43283546, array 0-5 (6 tasks)**, `ee1` QOS idle before submit.
`trapLevel` ∈ {0.35, 0.45} × `trapPeak` ∈ {8e18, 1.2e19, 1.6e19},
`hotTau`=1e-14, `trapSigma`=0.04, `hotEb`=0.5, Vd 0-4.05V in 0.15V steps.
CSVs `pulsedIV_tl<trapLevel>_tp<trapPeak>.csv` + `params.json` into
`results/20260925_lateOnsetB/task_<id>/`.

**Job 43283546 finished, all 6 tasks clean** (no Newton failures/NaN/OOM,
all 6 CSVs present, full 28 rows). Pulled back, analyzed. Full table in
CLAUDE.md section 10b. Summary: `trapLevel`=0.35 is clearly better than
0.45 or the original 0.55 - real "normal rise, then knee, then partial
recovery" shapes instead of "no collapse" or "collapsed from the start."
Best onset so far: `trapPeak`=8e18 gives a knee at Vd~1.5-1.8V (85.5→30.2
mA/mm, ~2.8x, still shallow). Best depth so far: `trapPeak`=1.2e19 gives
~10x (21.1→2.0 mA/mm) but onset is early (~0.6-0.9V). Neither is close to
F's ~1000x, and both cases creep back up more than F did (30→52, 2→9 vs
F's 0.006→0.018) - we're still short on total trapped charge to keep the
channel pinched as Vd keeps rising.

Proposing round C: `trapPeak` ∈ {8.5e18, 9.5e18, 1.05e19} (bracketing the
round-B gap) × `hotTau` ∈ {1e-14, 2e-14} (more heating, for depth) at
`trapLevel`=0.35, `trapSigma`=0.04, `hotEb`=0.5 - 6 tasks. Checking with
Ian before submitting.

Ian approved. Submitted **job 43297414, array 0-5 (6 tasks)**, `ee1`
QOS idle before submit (confirmed via the heredoc form - a bare
`ssh hpg bash -l -c 'squeue -A ee1'` earlier printed the whole cluster's
queue instead of filtering, looks like an argument-passing quirk with
`-c`; sticking to the `bash -l <<'REMOTE' ... REMOTE` heredoc form for
all HPG commands per CLAUDE.md). CSVs
`pulsedIV_tp<trapPeak>_ht<hotTau>.csv` + `params.json` into
`results/20260925_lateOnsetC/task_<id>/`.

**Job 43297414 finished: 5/6 tasks clean, 1 crashed.** Task 5
(`trapPeak`=1.05e19, `hotTau`=2e-14) aborted mid-sweep (Vd≈1.35V) with
`munmap_chunk(): invalid pointer` - a solver-level crash/core dump, not a
Newton-failed or NaN. Deleted the 1.9GB core file (both copies, HPG and
local) after confirming it wasn't needed for diagnosis. Not retrying that
point for now - flagging rather than guessing at a physics fix, per the
"propose before changing anything trap/Poisson-related" rule, though
this looks like a numerical edge-case crash rather than a physics issue.

**Big result: `trapPeak`=8.5e18, `hotTau`=2e-14 gives a real ~300x
collapse** (54.6 → 0.174 mA/mm at Vd=0.75→1.2V), creeping to 0.627 by
4.05V - the same qualitative shape as F, first time we've beaten ~10x
depth. `trapPeak`=9.5e18 at the same `hotTau` gave ~346x (onset a bit
earlier, ~0.6-0.9V). Full table in CLAUDE.md section 10b.

Trend: raising `trapPeak` *or* `hotTau` makes the collapse both earlier
**and** deeper together - looks like a threshold/runaway effect (more
trapping → more field → more heating → more trapping) rather than two
independently-tunable knobs. Onset is still only ~0.9-1.2V, well short
of 3V, but depth is finally in the right ballpark.

Proposing round D: test whether *lowering* `trapPeak` while keeping
`hotTau`=2e-14 (the heating level that crosses the runaway threshold)
pushes the same threshold-crossing later in Vd while keeping the depth.
`trapPeak` ∈ {6e18, 6.5e18, 7e18, 7.5e18, 8e18}, `hotTau`=2e-14 fixed,
`trapLevel`=0.35, `trapSigma`=0.04, `hotEb`=0.5 - 5 tasks. Checking with
Ian before submitting.

Ian approved. Submitted **job 43298204, array 0-4 (5 tasks)**, `ee1`
QOS idle before submit. CSVs `pulsedIV_tp<trapPeak>.csv` + `params.json`
into `results/20260925_lateOnsetD/task_<id>/`.

**Job 43298204 finished, all 5 tasks clean.** Full table in CLAUDE.md
10b. Clean monotonic trend: lowering `trapPeak` 8e18→6e18 (at `hotTau`=
2e-14) pushes onset later (1.05V→1.8V) but weakens depth (231x→12x) -
the two axes don't decouple, confirms round C's hypothesis exactly.
Best balance so far is `trapPeak`=6.5e18 (onset ~1.5-1.8V, ~39.5x) or
7e18 (onset ~1.35-1.5V, ~80x) - getting onset further out than round C
but still well short of 3V, and depth keeps shrinking as onset grows.

Proposing round E: push `trapPeak` down *and* `hotTau` up together, so
weaker charge still gets a strong runaway once triggered. `trapPeak` ∈
{5e18, 5.5e18, 6e18} × `hotTau` ∈ {3e-14, 4e-14} - 6 tasks. `hotTau` this
high hasn't been tried in this search but F itself ran at 1.3e-13 fine;
the round-C crash was high `trapPeak` + high `hotTau` together, this is
low `trapPeak` + higher `hotTau`, different corner. Checking with Ian
before submitting.

Ian approved. Submitted **job 43299061, array 0-5 (6 tasks)**, `ee1`
QOS idle before submit. CSVs `pulsedIV_tp<trapPeak>_ht<hotTau>.csv` +
`params.json` into `results/20260925_lateOnsetE/task_<id>/`.

**Job 43299061 finished, all 6 tasks clean.** Full table in CLAUDE.md
10b. **Real breakthrough:** moving `trapPeak` down and `hotTau` up
*together* beats moving along either axis alone -
`trapPeak`=6e18/`hotTau`=4e-14 gives onset ~1.35-1.5V *and* ~395x depth,
better on both counts than round D's best (`trapPeak`=8e18/`hotTau`=2e-14:
onset ~1.05-1.2V, ~231x). Latest onset yet is `trapPeak`=5e18/`hotTau`=
3e-14 at ~2.1-2.25V (but shallow, ~6.8x there).

Proposing round F: keep pushing the same diagonal - `trapPeak` ∈
{4e18, 4.5e18, 5e18} × `hotTau` ∈ {5e-14, 6e-14} - 6 tasks. `trapPeak`
=4e18 is F's own charge, but staying well below F's `hotTau`=1.3e-13
(which we know collapses at 0.3V) should keep this safely in the
late-onset regime. Checking with Ian before submitting.

Ian asked for bigger rounds - up to 18 tasks at once (near the 19-CPU
QOS cap) instead of 6, to cover more ground per round-trip. Revised round
F to an 18-task grid: `trapPeak` ∈ {3.5e18, 4e18, 4.5e18, 5e18, 5.5e18,
6e18} × `hotTau` ∈ {3e-14, 4e-14, 5e-14}, same fixed levers, skipping the
4 cells round E already covered (swapped in `trapPeak` up to 6.5e18 and
`hotTau` up to 6e-14 instead). Submitted **job 43300970, array 0-17
(18 tasks)**, `ee1` QOS idle before submit. CSVs
`pulsedIV_tp<trapPeak>_ht<hotTau>.csv` + `params.json` into
`results/20260925_lateOnsetF/task_<id>/`.

**Job 43300970 finished: 12/18 tasks clean, 6 crashed** (33%), same
`munmap_chunk(): invalid pointer` solver abort as round C's single crash
- not Newton/NaN. Deleted ~7.5GB of core dumps (HPG + local). Also
noticed 2 of the 18 cells were accidental duplicates of round E (my
mistake building the exclusion list) - harmless, just wasted 2 slots.
Full table and detail in CLAUDE.md section 10b.

**The tension is now clear:** deepest collapses found (`trapPeak`=6e18/
`hotTau`=5e-14: ~833x; `trapPeak`=6.5e18/`hotTau`=4e-14: ~761x) both sit
at onset ~1.0-1.35V - close to F's depth but nowhere near 3V. Pushing
onset later by backing off `trapPeak`/`hotTau` further costs nearly all
the depth: onset ~2.4-2.55V (`trapPeak`=4.5e18/`hotTau`=3e-14) only gets
~1.8x, barely a collapse. This might be a real limit of this `trapLevel`/
`trapSigma`/`hotEb` combination, not just needing a finer grid.

**Stopping to ask Ian** (written up fully in CLAUDE.md 10b) on two
things: (1) whether to try `hotEb` (untested so far, fixed at F's 0.5)
as a way to restore depth without more `trapPeak`/`hotTau`, or accept a
softer target; (2) the 33% crash rate is now costing real compute right
in the region we care about - worth addressing (smaller `Vd_step` or
more damping near the transition, solver-side per the rules) before
another big grid, or push forward on the current driver as-is.

**Ian's answers:** try `hotEb` next, and add the solver-side fix first.
Made `pulsedIV.tcl`'s Newton damping an `info-exists` lever
(`dampValue`, default 0.10 - unchanged behavior unless overridden).
Round G: `Vd_step`=0.1 (was 0.15), `dampValue`=0.05 (was 0.10), plus a
new `hotEb` sweep at 4 "late onset, weak depth" anchor points from
round E/F (`trapPeak`/`hotTau` = 4e18/5e-14, 4.5e18/3e-14, 4.5e18/5e-14,
5e18/3e-14) × `hotEb` ∈ {0.6, 0.7, 0.8, 0.9}, plus 2 extra at the
best-depth control point (6e18/5e-14) × `hotEb` ∈ {0.6, 0.7} - 18
tasks. `trapLevel`=0.35, `trapSigma`=0.04 fixed. Submitted **job
43303128, array 0-17 (18 tasks)**, `ee1` QOS idle before submit. Longer
`--time=02:30:00` given the finer `Vd_step` and heavier damping. CSVs
`pulsedIV_tp<trapPeak>_ht<hotTau>_eb<hotEb>.csv` + `params.json` into
`results/20260925_lateOnsetG/task_<id>/`.

**Job 43303128 finished: 8/18 clean, 10 crashed (56%)** - worse than
round F's 33%, despite the solver-side fix. Crash pattern doesn't
correlate cleanly with `hotEb` (alternates success/crash at the same
`trapPeak`/`hotTau` as `hotEb` increases), so this looks like a genuine
FLOOXS numerical edge case, not something fixable from the driver side.
Deleted ~11.6GB of core dumps.

**But huge result from the 8 that succeeded: `hotEb` is a massive,
mostly-independent depth lever.** At `trapPeak`=4e18/`hotTau`=5e-14
(only ~2.3x deep at `hotEb`=0.5), `hotEb`=0.7 gives **~750x depth at
onset ~1.9-2.0V** - the best combined late-onset + F-matching-depth
result of the whole search. `trapPeak`=5e18/`hotTau`=3e-14/`hotEb`=0.7
does even better on depth: ~8,300x at onset ~1.6-1.8V. Higher `hotEb`
(0.8-0.9) overshoots to essentially fully-off (100,000x-2,000,000x),
more dramatic than F but with an earlier onset. Full table in CLAUDE.md
10b.

Proposing round H: keep lowering `trapPeak`/`hotTau` while holding
`hotEb` around 0.7-0.8 to push onset further toward 3V while keeping
depth near F's ~1000x. `trapPeak` ∈ {3e18, 3.5e18} × `hotTau` ∈
{4e-14, 5e-14, 6e-14} × `hotEb` ∈ {0.7, 0.8} - up to 18 tasks. Given the
crash isn't fixable from our side, budgeting for losing 30-55% of tasks
per round going forward. Checking with Ian before submitting.

Ian approved. `trapPeak` ∈ {3e18, 3.5e18, 4e18} × `hotTau` ∈
{4e-14, 5e-14, 6e-14} × `hotEb` ∈ {0.7, 0.8} (skipping cells already
covered in round G) plus one extra (5e18/4e-14/0.7) - 18 tasks.
`trapLevel`=0.35, `trapSigma`=0.04, same solver settings as round G
(`Vd_step`=0.1, `dampValue`=0.05). Submitted **job 43305778, array 0-17
(18 tasks)**, `ee1` QOS idle before submit. CSVs
`pulsedIV_tp<trapPeak>_ht<hotTau>_eb<hotEb>.csv` + `params.json` into
`results/20260925_lateOnsetH/task_<id>/`.

**Job 43305778 finished: 12/18 clean, 6 crashed (33%, back down from
round G's 56%)** - reinforces that the crash rate is idiosyncratic per
point, not controlled by our driver settings. **Best results of the
whole search:**
- `trapPeak`=3e18/`hotTau`=6e-14/`hotEb`=0.8: **onset ~2.3-2.4V, ~336x
  depth** (124.2→0.369, creeps to 2.17 by 4.05V) - latest onset with
  real depth yet, and the closest overall shape match to F.
- `trapPeak`=3.5e18/`hotTau`=6e-14/`hotEb`=0.8: onset ~2.0-2.1V, **~1277x
  depth** (118.8→0.093) - almost exactly F's target depth.

Both on the same `hotTau`=6e-14/`hotEb`=0.8 line; lower `trapPeak` keeps
buying later onset without the depth collapsing to nothing, unlike at
`hotEb`=0.5. Full table in CLAUDE.md 10b.

Proposing round I: push further down this line - `trapPeak` ∈
{2.5e18, 2.75e18, 3e18, 3.25e18} × `hotTau` ∈ {6e-14, 7e-14} × `hotEb`
∈ {0.8, 0.85, 0.9} (skipping known cells) - 18 tasks, aiming for onset
~2.7-3V with depth still in the hundreds-x range. Checking with Ian
before submitting.

Ian approved. Submitted **job 43307897, array 0-17 (18 tasks)**, `ee1`
QOS idle before submit. CSVs `pulsedIV_tp<trapPeak>_ht<hotTau>_eb<hotEb>.csv`
+ `params.json` into `results/20260925_lateOnsetI/task_<id>/`. Polling
`squeue -u ianstafford` every 5 min.

**Job 43307897 finished: 17/18 clean, only 1 crash (6%)** - crash rate
keeps dropping (56%→33%→6%) with no driver-setting change behind it,
strong evidence it's idiosyncratic per parameter point, not something we
control from the driver.

**Best result of the whole search:** `trapPeak`=3e18/`hotTau`=6e-14/
`hotEb`=0.85 - peak 123.1 mA/mm at Vd=2.1V, sharp collapse to 0.132 at
2.3V, min 0.061 at 2.4V (**onset ~2.2-2.3V, depth ~2004x**, same order
of magnitude as F's ~1000x target), then creeps 0.061→0.542 by 4.05V -
same qualitative shape as F. Onset is now 7x later than F's own 0.3V.
Full table in CLAUDE.md 10b.

Proposing round J: push further - `trapPeak` ∈ {2.5e18, 2.6e18, 2.75e18}
× `hotEb` ∈ {0.9, 0.95} × `hotTau` ∈ {7e-14, 8e-14}, aiming for onset
~2.5-2.8V while holding depth in the hundreds-to-thousands range.
Checking with Ian before submitting.

**Ian said stop here - this is a good enough match.** Task complete.

**Final answer:** `trapPeak`=3e18, `trapSigma`=0.04, `trapLevel`=0.35,
`hotEb`=0.85, `hotTau`=6e-14 gives F's dramatic-collapse-then-creep
shape with onset delayed to **~2.2-2.3V** (vs F's ~0.3V, a 7x delay) and
depth **~2004x** (vs F's ~1000x, same order of magnitude). Saved as
`figures/pulsedIV_lateOnset3V.csv`. Full writeup and search summary in
CLAUDE.md section 10b. This does not change the repo's `pulsedIV.tcl`
defaults or Run F's status as the best match to the project's primary
goal (radPlot1, ~0.4-0.5V onset) - it's a separate result for the
"what if onset were ~3V" question.

No jobs pending on HPG. Nothing else outstanding on this task.

### Task: trap placement study (trapMeanX / trapMeanY)

New task from Ian: use the existing single-Gaussian trap distribution's
`trapMeanX` (depth) and `trapMeanY` (lateral, along the channel) to see
how trap *placement* affects the collapse - one location per device/run,
not multiple locations in one device (the model already only supports a
single Gaussian, so no code changes needed, just a parameter sweep).

Baseline (Ian's choice): Run F's tuned levers - `trapPeak`=4e18,
`trapSigma`=0.04, `trapLevel`=0.55, `hotEb`=0.5, `hotTau`=1.3e-13,
`Vg_meas`=-2, Vd 0-1.6V in 0.1V steps - matching the project's primary
goal (radPlot1, ~0.4-0.5V onset), so this asks "where do traps matter
most for the actual target collapse."

Device geometry (from `rfdevice.tcl`): gate spans y=[-0.125,0.125]
(`Gate_Length`=0.25), field plate spans y=[0.285,0.725] (`leftFP`/
`rightFP`), drain contact at y=3.41. AlGaN top (surface) is x=0, the
2DEG/AlGaN-GaN interface is x=`Al_Thick`=0.015.

Grid (Ian approved): `trapMeanX` ∈ {0.0, 0.0075, 0.015} (surface,
mid-AlGaN, 2DEG interface) × `trapMeanY` ∈ {0.125, 0.20, 0.285, 0.725,
2.0} (gate edge, the value used throughout tuning, field-plate-left
edge, field-plate-right edge, deep access near drain) - 15 devices.
Committed `pulsedIV_trapPlacement.slurm` + `params_trapPlacement.txt`.

**HPG connection dropped mid-submit.** The `ssh hpg` command to pull,
check QOS, `mkdir`, and `sbatch` the array hung past 120s and was killed
by Ian; a follow-up `squeue` check also hung and was killed. `ssh -O
check hpg` then failed outright: `Control socket connect(...): No such
file or directory` - the multiplexed master connection is gone, not
just slow. Per the hard rule: **stopping here, not retrying, not
opening a new connection** (would stall on Duo, which I can't answer).
**Unknown whether `sbatch` actually ran** before the first command was
killed - need to check `squeue`/job history once the connection is back
before resubmitting, to avoid a duplicate array.

Also updated CLAUDE.md per Ian: HPG polling interval is now 5 minutes
as the standing default (was "every 2-3 minutes"), for all future
submissions unless he says otherwise for a specific run.

**Waiting on Ian to re-authenticate the HPG connection** (his morning
Duo tmux session) before the trap-placement job can be confirmed/
submitted.

Tried the retry twice more at Ian's explicit request (one rejected by
the permission prompt, one hung and revealed the real cause): the
attempt got as far as a password prompt but `ksshaskpass` (a GUI askpass
helper) failed to parse it - `Unable to parse phrase
"(ianstafford@hpg.rc.ufl.edu) Password: "` - because my attempt is
non-interactive/backgrounded, so there's nowhere to actually show Ian
the prompt. No Duo push is triggered until the password step succeeds.
Not a HiPerGator-side problem. Per CLAUDE.md, only Ian can authenticate
this (he can't answer Duo through me) - he needs to run `ssh hpg`
directly in his own terminal/tmux (password, then approve the Duo push)
to recreate the shared control socket.

**Ian will pick this back up later.** Next session: resume the
trap-placement study (`pulsedIV_trapPlacement.slurm` +
`params_trapPlacement.txt`, committed, 15-task array over `trapMeanX`
× `trapMeanY` on Run F's baseline - see the "Task: trap placement
study" section above for the full grid). First check `ssh -O check hpg`
and `squeue -u ianstafford` / recent job history once he's
re-authenticated, to make sure the earlier `sbatch` didn't already go
through before resubmitting (avoid a duplicate array).

## 2026-09-26

`ssh -O check hpg` OK (master running, pid=75249) - Ian re-authenticated.
Checked `sacct` history: no `pulsedIV_trapPlacement` job ever ran, so
the earlier `sbatch` never went through before the connection dropped -
no duplicate risk. Pulled latest repo on HPG, `ee1` QOS was idle, and
submitted the trap-placement array: **job 43366825, array 0-14
(15 tasks)**. CSVs `pulsedIV_mx<trapMeanX>_my<trapMeanY>.csv` +
`params.json` into `results/20260925_trapPlacement/task_<id>/`. Polling
`squeue -u ianstafford` every 5 min.
