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

**Job 43366825 finished: all 15 tasks clean** (no crashes, no core dumps,
all CSVs full 17 rows). Pulled back. Full table in CLAUDE.md section 10c.

- **Lateral position (`trapMeanY`) is the strongest placement lever.**
  Moving the blob from the gate edge toward the drain delays onset
  (0.2-0.3V → 0.4-0.5V) and raises pre-collapse current (7.8 → 24.3
  mA/mm at the surface), with pre-collapse Id rising with Vd instead of
  falling as in F.
- At the gate edge (y=0.125) the channel is pinched at rest for every
  depth - no normal region.
- Deeper traps (toward the 2DEG) give an earlier onset, lower
  pre-collapse current, and a deeper collapse.
- y=0.20/x=0 reproduces Run F exactly (sanity check).

**Closest match to `radPlot1` yet: `trapMeanX`=0.0, `trapMeanY`=2.0** -
8.62/16.9/24.3/20.6 mA/mm at 0.1-0.4V (target 9.75/19.0/27.2/32.0),
collapse to 0.020 at 0.5V (target 0.011), then creeps 0.010 → 0.023 by
1.6V. Onset exactly at 0.5V. Remaining miss is the 0.4V point, which
already sags. Saved as `figures/pulsedIV_placement_x0_y2.csv`.

**Waiting on Ian:** is a surface trap blob ~2 µm into the access region
physically plausible? If so, next step is a finer `trapMeanY` scan
between ~1.0 and ~3.0 at x=0 (maybe also x=0.0075) to fix the 0.4V
point.

### Task: 50-location trap map (burst QOS)

Ian asked for a 50-location trap placement map on HiPerGator's burst
QOS, collapse ratio per location, and a 3D plot of ratio vs (x, y).
Burst QOS `ee1-b`: 171 CPUs / 1.37 TB, 4-day wall, lower priority (900
vs 36000 for `ee1`) - so all tasks run at once.

Grid: `trapMeanX` ∈ {0, 0.00375, 0.0075, 0.01125, 0.015} (AlGaN surface
→ 2DEG) × `trapMeanY` ∈ {-0.5, 0, 0.125, 0.285, 0.5, 0.725, 1.25, 2.0,
2.5, 3.0} (source side, under gate, gate edge, field plate, access,
near drain) = 50 devices, Run F's other levers, Vd 0-1.6V/0.1V. Plus a
51st effectively trap-free reference (`trapPeak`=1e10; `trapEn`=0 would
break `CaptureTraps`, which needs `IonAcceptor`). Collapse ratio per the
request = pre-collapse peak / post-peak minimum; the reference device
also allows a trap-free vs trapped comparison, which matters for
locations that pinch the channel at rest (peak/min alone understates
those). `pulsedIV_trapMap.slurm` + `params_trapMap.txt`.

Submitted **job 43369760, array 0-50 (51 tasks) on `ee1-b`**. Results
into `results/20260926_trapMap/task_<id>/`. Polling every 5 min.

**Job 43369760 finished** (46/51 complete; 5 Newton iteration-limit
failures at y=1.25/3.0). Retried those 5 with solver-side only changes
(`Vd_step`=0.05, `dampValue`=0.05): **job 43370373**, 4 recovered, 1
(x=7.5nm, y=3.0) hit the known `munmap_chunk` crash - left as a hole.
**49/50 locations complete.** Full writeup in CLAUDE.md 10d; plots
`figures/trapMap_3d.png` (collapse ratio) and
`figures/trapMap_3d_suppression.png` (vs trap-free reference); data in
`figures/trapMap_ratios.csv`.

- Most damaging: traps under the gate / at its drain edge - channel off
  at rest, ~1e6-3.6e6x below trap-free. Their peak/min collapse ratio is
  only ~13x, because there's no "normal" region to collapse from - so
  the collapse ratio alone ranks them *least* harmful. Flagging.
- Next: source side (-0.5 µm) and near drain (3.0 µm), ~1e5x.
- Least: 2.5 µm (~600x). 2.5 → 3.0 is non-monotonic; 3.0 is ~0.3 µm
  from the drain contact doping, possibly a contact-proximity effect.
- Deeper (toward 2DEG) is consistently worse, ~5x suppression.

### Task: trap concentration × level map (burst QOS)

Ian: rerun on burst, traps kept well away from the source/drain contacts
(contact doping likely made the 50-point map's near-contact points
unreliable), single x, vary concentration and energy level. No longer
fitting radPlot1 - studying how these parameters shape the collapse.

Design (my choices, per Ian): x=0 (surface); y ∈ {-0.4, -0.125, 0,
0.125, 0.285, 0.5, 0.725, 1.25, 1.75, 2.4} µm (≥0.7 µm from the source
doping edge at -1.125, ≥0.88 µm from the drain edge at 3.285);
`trapPeak` ∈ {2e18, 4e18, 8e18} × `trapLevel` ∈ {0.35, 0.55, 0.75} eV;
10 positions per (conc, level) = 90 devices + trap-free reference.
`trapSigma`=0.04, `hotEb`=0.5, `hotTau`=1.3e-13 (Run F), Vd 0-3.0V in
0.1V (extended, since weaker traps may collapse later), `dampValue`=0.05.
`pulsedIV_trapConcLevel.slurm` + `params_trapConcLevel.txt`.

Submitted **job 43373001, array 0-90 (91 tasks) on `ee1-b`**. Results into
`results/20260926_trapConcLevel/task_<id>/`. Polling every 5 min.

**Job 43373001 finished** (73/91 COMPLETED; 15 `munmap_chunk` + 3 Newton
stalls, 12 of 18 at 8e18). Retried the 18 with `Vd_step`=0.05: **job
43373919**, 7 recovered. 79/90 ran to 3V; 8 more had already declared
their regime before crashing - **3/90 undetermined**. Writeup in
CLAUDE.md 10e; figures `figures/trapConcLevel_IdVd.png`,
`figures/trapConcLevel_summary.png`, data
`figures/trapConcLevel_metrics.csv`.

- Three regimes: no effect, hot-electron collapse, off at rest
  (threshold shift). Energy level decides which. The collapse only
  shows up in a narrow band: 4e18/0.35, 4e18/0.55, 8e18/0.35.
- 0.75 eV at ≥4e18, or 0.55 eV at 8e18: off at rest everywhere.
- Within the band: 4e18/0.35 late + shallow (onset 1.7-2.9V, 11-106x);
  4e18/0.55 and 8e18/0.35 early + deep (0.3-0.6V, 3e3-4e4x).
- Gate-region traps always go off-at-rest first; in the access region,
  onset moves later with distance from the gate.
- 2e18: no access-region collapse at any level through 3V.

## 2026-09-27

### Deep dive: why FLOOXS crashes (`munmap_chunk`)

Reproduced locally (workstation build: gcc, FLOOXS `e7c2a30f`) under gdb
using task 64 of job 43373001 (8e18 / 0.35 eV / y=0.285): fails at
exactly the same point as on HPG (Intel icpx, `503b936`) - Vd=0.4 V
completes, the Vd=0.5 V FillStep hits NaN. So it isn't the compiler or
the older HPG commit. Backtrace at the first `FLPS_panic`:
`GlobalExit → ~FieldServerList → ~Mesh → ~Tri → ~Edge → ~Node →
Element::~Element → FLPS_panic("Fudge")`.

Root cause (full chain in CLAUDE.md §6):
- **Trigger:** Newton diverges to NaN at the collapse transition - the
  same non-convergence as the "iteration-limit stalls", just diverging
  instead of oscillating.
- **Crash (two FLOOXS bugs):** (1) the NaN exception leaves the
  solver's `eq0`/`eq1` queues half-drained with nodes still flagged
  `InQueue`; (2) at exit, destroying such a node calls `FLPS_panic`,
  which runs `exit` again inside `GlobalExit`, re-deleting `fslist`
  (never NULLed) → ~3,300-deep recursion + double free → `munmap_chunk`
  + 1-2 GB core.
- A driver-side `catch {device}` + retry would silently double-assemble
  stale elements (`InitializeAssembly` doesn't clear the queues), so the
  fix has to be in FLOOXS.

Proposed FLOOXS patch (tool fix, no model physics), ~10 lines:
1. `Solver::InitializeAssembly`: `eq0.Clear(); eq1.Clear();` before refilling.
2. `DevController` catch block(s): clear the solver queues (`ds->Store()`).
3. `GlobalExit`: re-entry guard and `fslist = NULL` after delete;
   `FLPS_panic`: if re-entered, `_exit(1)` instead of Tcl `exit`.
With 1-3, a NaN becomes a clean Tcl error (no core dumps), and
`pulsedIV.tcl` could `catch` it and retry that Vd point with a smaller
step - which should recover most of the ~20-50% of runs we've been
losing.

**Waiting on Ian:** OK to (a) patch + build FLOOXS in a separate local
build dir (installed `/usr/local/bin/flooxs` untouched) and test on task
64, then (b) rebuild on HPG / send upstream?

**Ian approved testing in a separate local build.** Patched FLOOXS on a
git worktree `~/flooxs-crashfix` (branch `crash-fix` off `e7c2a30f`),
built in `~/flooxs-crashfix/build` with the same config as the release
build; `~/flooxs` and `/usr/local/bin/flooxs` untouched. Patch (20
lines, 4 files, no model physics):
- `Solver::InitializeAssembly`: `eq0.Clear(); eq1.Clear();` before refilling.
- `DevController::Solve` / `StressController::Solve` catch blocks:
  `ds->Restore()` (clears the half-drained queues).
- `FLPS_panic`: hard `std::_Exit(1)` if re-entered; `GlobalExit`:
  re-entry guard + `fslist = NULL` after delete.

**Test 1 (task 64 deck, unmodified, patched binary): PASS.** Identical
Id at every Vd through 0.4 V (all digits) - no physics change. At the
NaN it now exits with a normal Tcl error (exit 1): 0 panics, no
`munmap_chunk`, no core dump.

Test 2 running: scratch retry driver (each Vd point in `catch`; on
failure `device restore` + restore `TrapFrozen`/`TeTrap`, then bisect
the Vd step up to 5 levels).

**Test 2 (retry driver, patched binary): PASS.** The 0.4 → 0.5 V step
hit the NaN; one bisection level (via 0.45 V) got past it, and the sweep
completed to 3 V with no further retries: collapse at 0.5 V (30.6 →
0.0012 mA/mm, ~26,000x), creeping to 0.0037 by 3 V - consistent with
its 8e18/0.35 eV neighbors.

**Test 3 (same retry driver, stock unpatched binary): PASS, identical
to every digit, no crash.** `device restore` already clears the stale
queues (`DevController::Restore()` → `Solver::Restore()`). Verified the
HPG source (`503b936`) has the same code path, so **the driver-side
retry alone should end the crashes on HPG without rebuilding FLOOXS**.

- FLOOXS patch committed on local branch `crash-fix`
  (`~/flooxs-crashfix`), not installed, not on HPG, not upstream. Still
  worth having as defense in depth: any *unrecovered* failure then
  exits cleanly with no core dump.
- Tested retry logic saved as `tools/retry_snippet.tcl`; not yet wired
  into `pulsedIV.tcl`.
- Caveat: a bisection substep runs a full `FillStep` at the
  intermediate Vd, adding a little extra trap-fill history compared to
  an un-retried run. The alternative is a plain `device` at substeps,
  with `FillStep` only at grid points.

**Waiting on Ian:** (1) wire the retry into `pulsedIV.tcl` (behavior is
identical when nothing fails)? (2) FillStep vs plain `device` at
bisection substeps? (3) Rebuild HPG FLOOXS with the patch / send
upstream, or leave it local for now?

**Ian: add the retry to pulsedIV.tcl** (and make more 3D plot sets at
other trap levels/concentrations). Retry built into `pulsedIV.tcl`,
levers `retryDepth`=5 and `retrySubFill`=1 (FillStep at bisection
substeps, the tested behavior; Ian didn't pick, so I kept the default
and made it switchable). Local check (task-64 params, Vd 0-0.3 V):
identical to the previous values to every digit. Removed
`tools/retry_snippet.tcl` (now in the driver).

### Task: 3D trap-map sets at several concentrations/levels (burst)

5 sets (`trapPeak`/`trapLevel`), one per regime from the conc × level
study: 2e18/0.55, 2e18/0.75, 4e18/0.35, 4e18/0.55 (Run F, re-mapped on
the contact-safe grid), 8e18/0.35. Skipped the ones that were off at
rest everywhere (4e18/0.75, 8e18/0.55, 8e18/0.75). Each set: 5 depths
(0-15 nm) × 10 positions (-0.4 to 2.4 µm, ≥0.7 µm from contact doping)
= 50, total 250 + trap-free reference. Vd 0-3 V/0.1 V, `dampValue`=0.05,
Run F hot-electron levers, new retry driver. `pulsedIV_trapMapSets.slurm`
+ `params_trapMapSets.txt`, `--array=0-250%160` on `ee1-b`.

Submitted **job 43513462, array 0-250%160 (251 tasks) on `ee1-b`**.
Results into `results/20260927_trapMapSets/task_<id>/`. Polling every 5 min.

**Job 43513462 finished: all 251 COMPLETED, 0 crashes** (no `munmap`,
no panics, no cores) - first sweep with the retry driver. 48 tasks
needed retries, 10 gave up at their collapse point. Solver-side retry
of those 10 (**job 43515232**, `dampValue` 0.02, `retryDepth` 7)
recovered 2 → **242/250 complete**. The last 8 (7 at 8e18/0.35 drain
side) stall exactly at the collapse even at ~0.8 mV steps - looks like
a genuine jump in the model; left as marked holes.

Figures: `figures/trapMapSets_tp<peak>_tl<level>.png` (5 sets, each a
collapse-ratio + suppression 3D pair) and
`figures/trapMapSets_overview_{ratio,suppression}.png`; data
`figures/trapMapSets_metrics.csv`. Writeup CLAUDE.md 10f. Headlines:
gate region most damaging in every set; 2e18 access-region traps do
nothing; onset moves later with distance from the gate (4e18/0.35: 1.5
→ 2.7 V); deeper traps consistently worse; collapse depth scale ~100x →
2e4x → 7e4x for 4e18/0.35 → 4e18/0.55 → 8e18/0.35.

**Collapse metric fixed (Ian's question).** Peak/min is biased by
onset: pre-collapse Id rises with Vd, so late collapses start from a
higher peak (corr(onset, peak) +0.86 to +0.91). It understated the early
gate-edge collapses at 4e18/0.35 by ~8-10x (170-200 vs 1,500-1,900).
(Also: drain-side traps collapse *later*, not earlier; gate-edge traps
collapse earliest.) Figures regenerated with **collapse depth vs
trap-free = Id_no-trap / Id at the post-collapse minimum**;
`figures/trapMapSets_overview_ratio.png` replaced by `_overview_depth.png`;
peak/min kept in the CSV. CLAUDE.md 10f updated.

### Task: cone-shaped trap distribution (displacement-cascade-like)

Ian: replace the Gaussian with a "cone" (cascade-like) shape to see how
shape matters, ahead of importing TRIM profiles; 2e18 cm⁻³ / 0.75 eV;
keep it modular so switching back is trivial.

Model change (committed first, CRLF preserved): `GaN_modelfile_masterD`
now has a `trapShape` lever (default `gauss`) and one proc per shape,
`TrapConc_gauss` / `TrapConc_cone`, returning the FLOOXS expression.
Cone: apex at (`trapMeanX`, `trapMeanY`), axis into the device (+x),
half-width `coneW0` (0.01 µm) at the apex widening at half-angle
`coneAngle` (30°) over depth `coneLen` (0.1 µm), uniform `trapPeak`
inside, `erf`-softened edges (`coneEdge` 0.01 µm; erf avoids exp overflow
→ inf, which would trip the same NaN/inf check behind the crashes).
Checks: (1) FLOOXS-evaluated cone matches an independent Python formula
to 1e-4 (print precision), widens with depth and cuts off at 0.1 µm as
designed; (2) default `gauss` path is bit-identical to before (task-64
params, 0-0.3 V). Mesh caveat: lateral spacing is ~10-20 nm near the
field plate, ~50 nm farther out, so the 10 nm apex is barely resolved in
the access region.

Cone sweep: 2e18 / 0.75 eV, apex at the surface, 5 geometries
(coneLen|coneAngle: 0.05|30, 0.1|30, 0.2|30, 0.1|15, 0.1|45) × the 10
contact-safe apex positions of 10f + trap-free reference = 51 tasks.
In-material cross-sections (µm², ∝ charge per gate width): 0.0024,
0.0078, 0.0271, 0.0047, 0.0120 vs 0.0050 for the surface Gaussian - so
0.1|15° is the equal-charge, pure-shape comparison. Compared against the
Gaussian 2e18/0.75 x=0 row of job 43513462 (same Vd 0-3 V, damping,
retry driver). `pulsedIV_trapCone.slurm` + `params_trapCone.txt`.

Submitted **job 43536494, array 0-50 (51 tasks) on `ee1-b`**. Results into
`results/20260927_trapCone/task_<id>/`. Polling every 5 min.

**Job 43536494 finished: 51/51 COMPLETED, no retries, no crashes.**
Writeup CLAUDE.md 10g; figures `figures/trapCone_shapes.png`,
`_vs_position.png`, `_IdVd.png`; data `figures/trapCone_metrics.csv`.
- No hot-electron collapse for any shape at 2e18/0.75 eV; only the gate
  region switches off at rest; access region untouched for every shape.
- Cone length (0.05/0.1/0.2 µm at 30°) makes no difference at all:
  traps deeper than ~50 nm don't matter here.
- Near-surface trap charge over the gate is what counts: 15° cone
  (≈ Gaussian's total charge) ~270x weaker than the Gaussian under the
  gate; 45° cone ~6x stronger; Gaussian beats 30° cones despite less
  total charge because its charge sits at the surface.
- Next options: repeat the shape comparison at a collapsing set (e.g.
  4e18/0.55 or 8e18/0.35); refine the mesh before TRIM profiles.

### Task: cone vs Gaussian at settings that collapse

Ian: redo the shape comparison where the device actually collapses. Two
collapsing sets run together on burst (same wall time as one): 4e18/0.55
eV (Run F; early, deep collapse everywhere) and 4e18/0.35 eV (onset moves
strongly with position, 0.2-2.7 V, so shape effects on onset should
show). Same 5 cone geometries × 10 contact-safe apex positions at the
surface, + trap-free reference = 101 tasks. Gaussian comparisons: the
4e18/0.55 and 4e18/0.35 x=0 rows of job 43513462 (same settings).
`pulsedIV_trapConeCollapse.slurm` + `params_trapConeCollapse.txt`.

Submitted **job 43538727, array 0-100 (101 tasks) on `ee1-b`**. Results into
`results/20260927_trapConeCollapse/task_<id>/`. Polling every 5 min.

**Job 43538727 finished: 101/101 COMPLETED, 0 crashes, 2 late give-ups.**
Analysis (`analyze_trapCone.py` now takes RUN PEAK LEVEL TAG) →
`figures/trapCone_4e18_0.55_*`, `figures/trapCone_4e18_0.35_*`.
Apparent result: cones mostly remove the hot-electron collapse the
Gaussian produces (4e18/0.55: Gaussian collapses at 7 positions, 30°
cones at 1, 15° at 0; y ≥ 1.25 µm: every cone gives exactly 1.0 = no
effect at all).

**⚠ That is a mesh artifact.** Local check, 4e18/0.55, cone 0.1 µm/45° at
y=1.25 µm with the lateral mesh refined to 4 nm there (scratch copy of
rfdevice.tcl only): collapses 8.2 → 0.025 mA/mm at Vd=0.2 V (~325x),
earlier than the Gaussian - vs *no effect* (9.5 → 85 mA/mm) on the
standard mesh (~25-40 nm lateral spacing there, cone only 25-50 nm
wide). A nodal-sampling check had said the mesh captures the cone's
charge (±15%) - true, but the hot-electron runaway depends on the field
around the narrow stripe, which the coarse mesh doesn't resolve. So the
cone-vs-Gaussian comparisons are mesh-limited wherever the cone is
narrower than a few mesh cells (the access region especially). Running
the same check for the Gaussian (σ 40 nm) at y=1.25 to see whether the
earlier Gaussian maps are also mesh-sensitive there.

**Gaussian mesh check** (same position, refined 4 nm vs standard):
still collapses deeply, but onset 0.3 V vs 0.4 V and pre-collapse peak
12.0 vs 22.8 mA/mm. So Gaussian results are qualitatively robust but
quantitatively mesh-sensitive in the access region (affects 10b-10f
numbers there, incl. the 10c radPlot1 match at y=2.0 µm); cone results
at collapsing settings are qualitatively wrong on the standard mesh.
Full writeup CLAUDE.md 10h.

**Waiting on Ian:** how to fix the mesh before more shape/TRIM work -
(a) local refinement that follows the trap (a `line y` at `trapMeanY`
with ~4 nm spacing, driven by the trap levers; cheap, but the mesh then
differs per trap position), or (b) global refinement of the access
region (uniform, slower everywhere) - plus a short convergence study
(8/4/2 nm) to pick the spacing. Then rerun the cone comparison.

## 2026-09-28

### Task: probability of a critical strike at 1e7 ions/cm²

Ian: estimate the probability of a critical strike at a fluence of 1e7
cm⁻², assuming each strike leaves the Gaussian-style trap blob; run more
tests if needed. Critical = the strike cuts Id ≥10x below trap-free at
any Vd ≤ 3 V (off at rest or collapse). From the 10f maps, the critical
band along the channel is: gate region only for 2e18/0.55 and 2e18/0.75
(edges uncertain by up to 0.28 µm), −0.125 to ~2 µm for 4e18/0.35, and
the whole trusted range (−0.4…2.4 µm) for 4e18/0.55 and 8e18/0.35. No
gate width in the repo → results per µm of width, scaled to examples.

Refining the band edges: `pulsedIV_critBand.slurm` + `params_critBand.txt`
- 12 extra positions around the gate edges for both 2e18 sets, 9 around
the 4e18/0.35 edges, depths 0/7.5/15 nm, same settings as job 43513462;
99 devices + trap-free reference.

Submitted **job 43542730, array 0-99 on `ee1-b`** → `results/20260928_critBand/`.
Polling every 5 min.

**Job 43542730 finished: 100/100 COMPLETED, 0 crashes** (12 retried, 3
gave up). Refined bands: 2e18/0.55 = 0.30 µm (was 0.47 coarse),
2e18/0.75 = 0.47 µm, 4e18/0.35 = 2.67 µm; 4e18/0.55 and 8e18/0.35 cover
the whole trusted range (3.01 µm). **Ian: gate width 200 µm.**

**Result (CLAUDE.md 10i, `critical_strike.py`, `figures/criticalStrike*`):**
at 1e7 cm⁻² and W=200 µm, λ = Φ·Δy·W = 6.0 / 9.4 / 53 / 60 / 60 expected
critical strikes → P(≥1) = 0.9975 / 0.99992 / ≈1 / ≈1 / ≈1. 50% fluence
1.2e6 (2e18/0.55) down to 1.15e5 cm⁻² (4e18/0.55, 8e18/0.35). Caveat: the
2D model makes each blob span the full width. Treating cascades as
~0.16 µm patches along the width, only ~0.5-4.8% of the width is damaged
→ a few-percent Id loss, not a collapse. Device-level collapse would
need overlapping cascades, Φ ≳ 4e9 cm⁻². A 3D run would settle whether
a single patch can trigger the runaway.

## 2026-09-30

Made a 12-slide progress-report deck (claude.ai Slides artifact:
https://claude.ai/artifact/4RfyrQi58v7pD8NH6aFLqc, private until shared):
problem, model, radPlot1 onset match via trap placement, late-onset
(~2.3 V) result, trap maps, conc × level regimes, trap shape, critical-
strike probability, tooling/crash fix, caveats, next steps. Added
`figures/lateOnset_vs_F.png` (Run F vs late-onset Id-Vd) for it.

## 2026-10-01

### Task: full x-y trap sensitivity map incl. insulators (burst)

Ian: full sensitivity run + 3D plot, trap position from the top of the
HighK to 0.5 µm into the GaN (x) and across the channel away from the
contacts (y); put the trap charge into the insulator Poisson. Decisions
(Ian): insulator traps = static charge, **both signs** (no carriers/Qfn
in the insulators, so no Fermi or hot-electron filling there); **Run F
levels** (4e18, 0.55 eV, σ 0.04); **current mesh**, flagged (10h).

Model change: `Poisson.tcl` new `InsTrapCharge` (adds ±Ntrap to the
insulator Poisson); `GaN_modelfile_masterD` new lever `insTrapSign`
(0 default = unchanged; −1 = filled −q·N; +1 = +q·N) applied to Nitride
and HighK. Local tests (Run F levels, y=0.5 µm, Vd 0-1 V), all clean:
default bit-identical (task-64 check); HighK top −1/+1 → −0.13%/+0.12%
(symmetric, so the term is wired right); Nitride just above the AlGaN
(−1) → off at rest (~1e-10 mA/mm; fully-filled 4e18 there ≈ 1e13 cm⁻²,
2DEG-scale); 250 nm into the GaN → identical to trap-free.

Sweep: x ∈ {−275, −225, −150, −100, −30, −2.5, 0, 7.5, 15, 40, 80, 150,
250, 375, 515} nm × y ∈ {−0.4 … 2.5} µm (13), positions inside metal
excluded → grid A (−1) 182 + grid B (+1, insulator-centred) 65 + ref =
248 tasks. `pulsedIV_trapXYMap.slurm` + `params_trapXYMap.txt`,
`analyze_trapXYMap.py`.

Submitted **job 44261474, array 0-247%160 on `ee1-b`** → `results/20261001_trapXYMap/`. Polling every 5 min.

## 2026-10-01 - x-y sensitivity map finished (job 44261474)

243/248 tasks done cleanly (0 crashes, 0 give-ups, 13 retried). The last 5 (sign −1, y=−0.4) are still bisecting at ~1.35 V and are already off at rest at the noise floor; left to finish or time out (3 h). Not cancelling without asking.
Writeup in CLAUDE.md 10j; figures `figures/trapXYMap_{3d,map,map_plus,sign}.png`.
- Sign −1 (filled insulator traps): blobs centred from the nitride to 40 nm into the GaN are off at rest everywhere, because the fully filled nitride tail (0.6-2e13 cm⁻²) outweighs the 2DEG. Below 80 nm, only the gate region is affected; from 150 nm down, nothing.
- HighK at −100 nm turns the device off for y ≥ 1.5 µm; no effect under the T-gate or field plate.
- Sign +1: the positive nitride charge cancels the access-region collapse; only under-gate blobs still turn the device off.
**Decision for Ian:** run a sign-0 companion (insulator traps neutral) at x −30…80 nm × 13 y (~78 tasks, burst) to isolate the semiconductor-trap effect? Waiting.

## 2026-10-01 - sign-0 companion submitted (Ian approved)

Job **44274780**, 91 tasks on `ee1-b` (`pulsedIV_trapXYMap0.slurm`, `params_trapXYMap0.txt`) → `results/20261001_trapXYMap0/`. Same Run F blob, insulator traps neutral (`insTrapSign`=0), x ∈ {−30, −2.5, 0, 7.5, 15, 40, 80} nm × the 13 y positions (90 tasks; 1 centre inside metal skipped) + a trap-free reference. Polling every 5 min.

## 2026-10-01 - sign-0 companion done (job 44274780)

91/91 clean (6 retried, 0 crashes). With the insulator traps neutral, the hot-electron collapse comes back across the access region for blob centres from −2.5 to 40 nm (50 collapses, 0.62-0.90 of trap-free at rest). Earliest and deepest just below the 2DEG (7.5-15 nm: onset 0.2-0.4 V, 4e4-2e6x); at 40 nm it's later and shallower; at 80 nm, nothing. The gate region is off at rest, as in 10f. So filled insulator charge (−1) turns those collapses into "off at rest" and positive charge (+1) removes them. The passivation fill fraction is the key unknown. Figure `figures/trapXYMap_neutral.png`; CLAUDE.md 10j updated. 2 stragglers from job 44261474 (sign −1, y=−0.4, already off at rest) are still running.

## 2026-10-01 - job 44261474 fully finished

The last 5 tasks (sign −1, y=−0.4) gave up cleanly at Vd=1.4 V (`PULSED GAVE UP`, no crash, no cores). They were off at rest at the noise floor, so their regime is settled; not retried. Both maps are complete: 337 devices, 332 to 3 V. Nothing running on HPG.

## 2026-10-01 - deep-trap test (Ian approved)

Question: is the collapse from blobs centred 25+ nm into the GaN due to deep traps, or to the σ=40 nm tail at the 2DEG? New optional lever `trapSigmaY` (anisotropic Gaussian; unset = unchanged, verified bit-identical locally). Local test: σx 10 nm / σy 40 nm, 4e18/0.55 eV, centred 25 nm below the 2DEG at y=0.5: **no collapse through 1 V** (89.6 mA/mm, ≈ trap-free), whereas σ=40 nm at the same centre collapsed at 0.4 V.
Sweep `pulsedIV_trapDeep.slurm`: x ∈ {15,25,30,40,50,60,80} nm × y ∈ {−0.2,0,0.5,1,2} µm × peak {4e18 (same density), 1.6e19 (same total charge)}, insulator traps neutral, + reference = 71 tasks on `ee1-b`. Submitted **job 44286932** → `results/20261001_trapDeep/`. Polling every 5 min.

## 2026-10-01 - deep-trap test done (job 44286932)

71/71 clean (5 retried, 0 crashes). Thin blob (σx 10 nm, σy 40 nm): **the 10j "deep" collapse was the σ=40 nm tail at the 2DEG.** At 4e18, the access-region collapse is gone once the blob centre is 10 nm below the 2DEG; at 1.6e19 (same total charge), gone by 25 nm. Nothing at ≥35 nm anywhere. The gate region reaches deepest (off at rest to 15 nm at 4e18; a collapse at 25 nm at 1.6e19). At 1.6e19, 0-15 nm below is off at rest (static back-barrier). Likely because deep 0.55 eV traps stay empty (Fermi level/hot electrons don't reach them), not yet checked against the band diagram. CLAUDE.md 10k; `figures/trapDeep.png`, `_IdVd.png`. Fixed the collapse detection in `analyze_trapDeep.py` (onset vs the running max, since Id can recover past its pre-collapse peak). Nothing running on HPG.

## 2026-10-01 - HighK vs SiN passivation (Ian's request)

New `rfdevice_SiN.tcl` (every HighK region → Nitride) and a `deviceDeck` lever in `pulsedIV.tcl` (default unchanged; regression bit-identical). Local checks, Vd 0-0.5 V: trap-free SiN is 0.4-0.6% above HighK (10.06 vs 10.02 mA/mm at 0.1 V); 2e18/0.75 eV under the gate matches the HighK device to 4-5 significant figures (off at rest, ~0.0095 mA/mm). So any effect should show at higher Vd.
Sweep `pulsedIV_trapSiN.slurm`: the 10f 2e18/0.75 grid (5 depths × 10 positions) on the SiN device + a trap-free SiN reference = 51 tasks on `ee1-b`. The HighK side reuses job 43513462. Analysis: `analyze_trapSiN.py`.
Submitted **job 44294165** → `results/20261001_trapSiN/`. Polling every 5 min.

## 2026-10-01 - HighK vs SiN done (job 44294165)

51/51 clean (0 retries, 0 crashes). At 2e18/0.75 eV the HighK layer barely matters. Both devices: 15 off at rest (gate region), 35 no collapse, no hot-electron collapse anywhere. Suppression agrees within 0.01-0.02 decades under the gate and in the access region. The only difference: source side (y=−0.4 µm), where HighK is hurt 0.12-0.17 decades more at 3 V. Trap-free SiN carries +0.4% (0.1 V) to +1.5% (3 V) more current. CLAUDE.md 10l; `figures/trapSiN_{3d,compare}.png`.
**Suggested next (needs Ian's OK):** repeat at a collapsing setting (Run F 4e18/0.55) to see whether HighK changes the hot-electron collapse itself.

## 2026-10-01 - HighK vs SiN at Run F (Ian approved)

Ian: repeat at Run F (4e18/0.55 eV); if HighK and SiN are still the same, dig into the dielectric model (he expects some field passivation from the HighK). `pulsedIV_trapSiN_F.slurm` / `params_trapSiN_F.txt`: the 10f Run F grid on `rfdevice_SiN.tcl` + a trap-free SiN reference, 51 tasks on `ee1-b`. HighK side = 10f job 43513462 + retry 43515232. `analyze_trapSiN.py` now takes `trapPeak trapLevel SiN_run tag` arguments.
Submitted **job 44303974** → `results/20261001_trapSiN_F/`. Polling every 5 min. Meanwhile: reviewing the dielectric model locally.

## 2026-10-01 - dielectric model check (local, `fieldPlateTest.tcl`)

The HighK is applied correctly (solver reports εr HighK 35, Nitride 6.3, Metal 1e12; metal acts as a conductor, so the T-gate head is part of the gate). Trap-free, Vg=−2, Vd to 20 V, HighK then SiN (run consecutively):
- **HighK does give field passivation, but only above ~5 V.** At 20 V the T-gate-head/field-plate peak drops from 416 to 202 kV/cm, and the field spreads out to ~1.2 µm (access-region field 116 vs 9 kV/cm). At 10 V: 98 vs 140.
- **At Vd ≤ 3 V (all our trap sweeps) there is no field outside the gate edge** (3-4 kV/cm on both devices). The only hot spot is the gate drain edge (264 kV/cm at 3 V), under the gate stem with ~5 nm of nitride over the AlGaN, which the HighK can't reach; it differs by <2% even at 20 V.
- So the identical HighK/SiN trap maps at 2e18/0.75 are physical for 0-3 V sweeps, not a dielectric-model bug. Trap-free Id: SiN +0.4% at 0.1 V to +2.7% at 20 V.
- Also found: old `fieldpeak.tcl` set HighK εr 6.3 *before* sourcing the model file, which resets it to 35, so its "SiN" run was really HighK. Not fixed (unused script); noted.
`figures/fieldPlate.png`, `_sweep.csv`, `_cuts.csv` (`plot_fieldPlate.py`). Run F SiN job 44303974 still running.

## 2026-10-01 - HighK vs SiN at Run F done (job 44303974)

51/51 clean (6 retried). Same as at 2e18/0.75: identical regimes, **identical collapse onset at every position**, depth within ±0.1-0.2 decades. Matches the field-plate check (no field outside the gate edge at ≤3 V). CLAUDE.md 10l updated. Nothing running on HPG.

## 2026-10-01 - transfer-curve calibration (goal from Ian), checkpoint

Target: `figures/rfDeviceHFO2_Experimental.csv` = raw `figures/RF_100nmHfOx_IdVgs_Example1.xlsx` (Ian): Id-Vgs at **Vds = 10 V**, 25 °C, 100 nm HfO2, std FP, Ids in **A for a 200 µm device → mA/mm = A·1e3/0.2**. Driver `calibIdVg.tcl` (trap-free, field mobility, Vg +1 → −4), plot `plot_calib.py`.
- **Unmodified field mobility already fits:** within ±2.4% from Vg −2.6 to +1 V (rms 1.9% to 0 V, 1.8% to +1 V); 0 V: 649 vs 634, +1 V: 802 vs 810. Static mobility 600: rms 10% (wrong shape). `figures/calib_IdVg.png`.
- Remaining: gm is ~4% high mid-range and **collapses above +0.5 V** (88 vs 160 mS/mm at +1 V), the same with static mobility, so it's electrostatic, not mobility. Diagnosing (charge under the gate, GaN vs AlGaN). Off-state drain leakage (~0.075 mA/mm) ignored per Ian.
- Ian: after calibration, redo the trap studies with field mobility.

## 2026-10-01 - calibration done

**Calibrated model = existing deck with `mobModel field`, no parameter changes**: Id within ±2.4% of the measurement from Vg −2.6 to +1 V at Vds = 10 V (rms 1.9% to 0 V); mA/mm = A·1e3/0.2. Only miss: gm above +0.5 V (88 vs 160 mS/mm at +1 V; Id still matches). Tried interface charge, contact resistance, surface charge and 2DEG mobility (CLAUDE.md 10m table). All fix forward-bias gm only by softening the turn-on and dropping the −2 V region 4-6%, so none adopted. `figures/calib_IdVg.png`.
**Next (Ian):** redo the trap studies with field mobility. Which ones (10f maps, 10j/10k, 10l?), and should field mobility become the default (`mobModel`)? Waiting before any sbatch.

## 2026-10-01 - Run F trap map with field mobility (Ian: replicate the conc/level surface plots, Run F set only)

`pulsedIV_trapMapF_field.slurm` / `params_trapMapF_field.txt`: the 10f 4e18/0.55 grid (5 depths × 10 positions) + trap-free reference, `mobModel field` set per run (deck default stays static), 51 tasks on `ee1-b`. `analyze_trapMapSets.py` now takes `[run_dir [tag]]` (default output byte-identical). Local check (x=0, y=0.5): runs cleanly, ~20 s/point; collapse at **0.2 V vs 0.3 V** with static mobility, ~10× deeper (0.0011 vs 0.010 mA/mm at 0.3 V).
Submitted **job 44342967** → `results/20261001_trapMapF_field/`. Polling every 5 min.

## 2026-10-01 - Run F map with field mobility (job 44342967)

48/51 done (1 gave up cleanly after its collapse; 2 source-side tasks still bisecting post-collapse, onset/depth already known). vs static (10f): collapse **earlier** (0.2 V almost everywhere vs 0.2-0.5 V), **~1 decade deeper** (10^4.9-10^7.1 vs 10^4.1-10^5.8 vs own trap-free), lateral onset trend nearly gone; 19 vs 15 off at rest (4 borderline at the FP edge). Trap-free baseline 75% higher at low Vd (part of the difference); the low-Vd region isn't covered by the calibration. CLAUDE.md 10n; `figures/trapMapF_field_tp4e+18_tl0.55.png`, `figures/mobCompare_F_{3d,compare}.png`.
Job 44342967 finished: the 2 remaining tasks also gave up cleanly after their collapse (2.6 / 1.4 V). 0 crashes; regimes unchanged; figures regenerated. Nothing running on HPG.

## 2026-10-01 - cleanup + late-onset search with field mobility (Ian)

- **Archived** all static-mobility work: `archive/static_mobility/` (scripts, sweep files, figures; README) on main, full snapshot on branch **`static-mobility`** (d2eda77), raw results in `results/archive_static_mobility/` (workstation). `analyze_trapMapSets.py` now defaults to the field map. **Default `mobModel` is now `field`** (a479ca0).
- **Collapse classes** (Ian): largest single-step loss >95% deep, 50-95% medium, <50% shallow (CLAUDE.md).
- **Round 1** `pulsedIV_onsetField1.slurm` / `params_onsetField1.txt`: Run F position (x 0, y 0.2, σ 0.04), trapLevel {0.35,0.45,0.55} × trapPeak {2,3,4}e18 × hotTau {1e-14,3e-14,6e-14,1.3e-13} × hotEb {0.5,0.85}, Vd 0-4 V, + reference = 73 tasks on `ee1-b`.
Submitted **job 44359813** → `results/20261002_onsetField1/`. Polling every 5 min.

## 2026-10-02 - late-onset round 1 done (job 44359813), round 2 submitted

Round 1: 73/73 clean. Latest deep collapse **1.0 V** (0.35 eV / 4e18 / hotTau 3e-14 / hotEb 0.85) vs Run F 0.2 V; ≥4e18 needed for deep/medium; lower hotTau delays onset until the collapse turns shallow at 1e-14. `figures/onsetField1.png`, CLAUDE.md §10.3.
Round 2 `pulsedIV_onsetField2.slurm`: trapLevel {0.30,0.35,0.40} × trapPeak {4,5,6}e18 × hotTau {1,1.5,2,3}e-14 × hotEb {0.85,1.0} + ref = 73 tasks on `ee1-b`.
Submitted **job 44363616** → `results/20261002_onsetField2/`. Polling every 5 min.
**Round 2 cancelled** (Ian, 2026-10-02): job 44363616 scancelled shortly after starting; to be resumed later with the same `pulsedIV_onsetField2.slurm` / `params_onsetField2.txt` (resubmit as-is; partial results in `results/20261002_onsetField2/` on HPG can be ignored).

## 2026-10-02 - session resumed (Ian driving ~1.5 h, continuing without prompts)

- Round 2 of the late-onset search **resubmitted unchanged** as **job 44433016** (`pulsedIV_onsetField2.slurm`, 73 tasks, `ee1-b`). The cancelled run's partial output on HPG was moved to `results/20261002_onsetField2_cancelled/`. Polling every 5 min.
- **Local position check** (round-1 best set 0.35 eV / 4e18 / hotTau 3e-14 / hotEb 0.85, moved from y = 0.2 to **y = 2.0 µm**): deep collapse at **1.5 V** (118.5 → 0.098 mA/mm, 99.9% in one step) vs 1.0 V at y = 0.2, then a second drop at 2.3 V (0.033 → 1.7e-5). Pre-collapse current tracks trap-free to ~1.3 V (139 vs 155 mA/mm). So **trap position is still an onset lever with field mobility** (the 10.2 Run F map hid it because Run F collapses at 0.2 V everywhere). → round 3 should scan y.
- **Onset definition fixed** in `analyze_onset.py`: onset is now the *first* step reaching the class threshold (>95% deep, ≥50% medium), not the largest step, which misreported the two-step collapse above as 2.3 V. Round 1 re-scored: 2/72 onsets moved 0.1 V earlier; best still 1.0 V. Class definitions unchanged. CLAUDE.md §10.0 updated.

### Round 2 done (job 44433016) → round 3

- 73/73 clean (5 retried, 0 crashes/give-ups). deep 53, medium 14, shallow 5. **Latest deep onset 1.4 V** (0.30 eV / 5e18 / hotTau 1.5e-14 / hotEb 0.85; 98.8% loss from 76 mA/mm), up from 1.0 V in round 1. Latest medium 1.8 V (0.30 / 4e18 / 1.5e-14 / 1.0, 71%). 0.30 eV beats 0.35 and 0.40 everywhere; onset rises with lower hotTau + more trapPeak; hotEb 1.0 slightly earlier than 0.85. `figures/onsetField2.png`, `_metrics.csv`.
- Round 3 (`pulsedIV_onsetField3.slurm`, 57 tasks): 8 trap sets × trapMeanY {0.2, 0.5, 0.725, 1.0, 1.5, 2.0, 2.4} µm + ref. Sets: 0.30 eV {5e18/1.5e-14/0.85, 6e18/1e-14/0.85, 5e18/1e-14/1.0, 6e18/1e-14/1.0}; 0.25 eV {5e18/1e-14/0.85, 6e18/1e-14/0.85, 6e18/1.5e-14/1.0, 7e18/1e-14/1.0}.
- Submitted **job 44435511** → `results/20261002_onsetField3/`. Polling every 5 min.

### Round 3 done (job 44435511; 55/57 finished at write-up, last 2 already past their collapse) → round 4

- 0 crashes. deep 24, medium 5, shallow 27. **Latest deep onset 2.3 V**: 0.30 eV / 5e18 / hotTau 1e-14 / hotEb 1.0 at **y = 1.0 µm**, 99.4% one-step loss from **166 mA/mm ≈ trap-free** (~170) — normal operation right up to the collapse. Runner-up 2.1 V (0.25 / 6e18 / 1.5e-14 / 1.0 at y = 1.5, from 164 mA/mm). Up from 1.4 V (round 2) and 1.5 V (local y = 2.0 check).
- **Position optimum ~1.0-1.5 µm:** onset rises with distance from the gate (0.30/1.0/5e18: 1.5 → 1.7 → 2.1 → 2.3 V at y 0.2/0.5/0.725/1.0), then goes shallow at y ≥ 1.5-2.0.
- Onset table by set × y in `figures/onsetField3_metrics.csv`; figure `figures/onsetField3.png`.
- **Round 4** (`pulsedIV_onsetField4.slurm`, 61 tasks): refine around the 2.3 V device — 0.30 eV / hotEb 1.0, trapPeak {4.5,5,5.5}e18 × hotTau {0.8,1,1.2}e-14 × y {0.85,1.0,1.15,1.3,1.5,1.7}; plus 0.25 eV / 1.5e-14 / 1.0 at {5.5,6,6.5}e18 × y {1.3,1.7}.
- Submitted **job 44440027** → `results/20261002_onsetField4/`. Polling every 5 min.

## 2026-10-02 - position map for per-Vd 3D surfaces (Ian's request)

Ian: a series of ~10 static 3D surface plots at different Vd for one trap level/concentration, showing how trap position sets the collapse onset (maybe a GIF later). Chosen set: round-3 best (0.30 eV / 5e18 / hotTau 1e-14 / hotEb 1.0, σ 0.04), whose onset varies 1.5-2.3 V with position. `pulsedIV_posMapLate.slurm` / `params_posMapLate.txt`: trapMeanX {0, 3.75, 7.5, 11.25, 15} nm × trapMeanY {−0.4, −0.125, 0, 0.125, 0.285, 0.5, 0.725, 1.0, 1.25, 1.5, 1.75, 2.0, 2.4} µm + trap-free ref = 66 tasks, Vd 0-3 V. Runs alongside round 4 (job 44440027).
Submitted **job 44441813** → `results/20261002_posMapLate/`. Polling every 5 min.

### Correction: round 3 stalls (2026-10-02, ~11:50)

- Round 3's log check (skipped before its write-up — my mistake) shows **19/56 tasks ended with `PULSED GAVE UP`** (clean, no crashes/cores) at Vd 1.8-4.0 V, mostly from full current (e.g. 0.30/1.0/5e18 at y 1.5: 169 mA/mm at 2.7 V, gave up at 2.8 V). That is the runaway-stall of CLAUDE.md §10.5: the collapse is probably at the stall voltage, but the sweep can't step across it.
- `analyze_onset.py` had counted these as **shallow**. Added a **"stalled"** class (gave up before Vd_max with no recorded collapse; onset = unreached Vd). Rounds 1-2 unchanged (no stalls). Round 3 now: deep 24, medium 5, shallow 8, stalled 19; stalls at 1.8, 1.8, 1.9, 2.0, 2.1, 2.1, 2.3, 2.7, 2.7, 2.8, 2.8, 2.9, 2.9, 2.9, 3.0, 3.5, 3.6, 3.7, 4.0 V.
- So the **2.3 V best is a lower bound**: up to 9 devices may collapse at 2.7-4.0 V. **Proposed (needs Ian's OK):** rerun the stalled tasks with the solver-side settings that rescued the 10f stalls (`dampValue` 0.02, `retryDepth` 7). Physics unchanged. Same check will apply to round 4 and the position map.
- **Ian approved the round-3 stall retry (run alongside the position map if burst capacity allows).** `pulsedIV_onsetField3Retry.slurm` / `params_onsetField3Retry.txt`: the 19 stalled tasks, dampValue 0.02, retryDepth 7 → `results/20261002_onsetField3Retry/`.
- Burst had 83/171 CPUs in use (all ours), so submitted alongside: **job 44443669**. Polling every 5 min (rounds 4, position map, retry together).
- **Round 4 cancelled** (Ian: not expecting good results): job 44440027 scancelled with 17 tasks still running; 44 had completed (results left in `results/20261002_onsetField4/` on HPG, not analysed). Still running: position map 44441813, round-3 retry 44443669.

### Position map done (job 44441813) → per-Vd 3D surfaces

- 66/66 finished, 0 crashes, **11 stalled** (2.1-3.0 V, runaway). Set: 0.30 eV / 5e18 / hotTau 1e-14 / hotEb 1.0, σ 40 nm; 5 depths × 13 y + ref, Vd 0-3 V.
- Figures: `figures/posMapLate_grid.png` (10 surfaces at Vd 0.5, 1.4, 1.6 … 3.0 V; nothing changes below ~1.2 V, so frames are concentrated where the collapse spreads), single frames in `figures/posMapLate_frames/` (ready for a GIF), and `figures/posMapLate_onset.png` (onset/class per position). Stalled positions are marked × on the floor and "stall" on the onset map.
- Result: positions cut >10× grow 15 (gate region only, up to 1.2 V) → 17 / 23 / 30 / 36 / 41 / 43 at 1.4-2.4 V. Onset rises with distance from the gate (surface: 1.6 V at y 0.285 → 2.3 V at y 1.0) and deeper traps (7.5-15 nm) reach farther out (7.5 nm: 2.4 V at y 1.75). The latest points (2.5-3.0 V) are stalls.
- `plot_posVd.py` got the "stalled" class (same rule as analyze_onset).
- Next options: retry the 11 stalls (same solver settings as the round-3 retry) to resolve the right edge; make the GIF.
- **GIF** (Ian): `figures/posMapLate.gif`, 30 frames at Vd 0.1-3.0 V in 0.1 V steps (one per simulated point), 350 ms/frame, last frame held 2 s, 0.6 MB; same fixed z-scale and camera as the static plots. Rebuild: `python3 plot_posVd.py results/20261002_posMapLate posMapLate_gif $(python3 -c "print(','.join(f'{0.1*k:.1f}' for k in range(1,31)))")` then `python3 make_gif.py figures/posMapLate_gif_frames figures/posMapLate.gif` (frames not committed).

### Round-3 stall retry done (job 44443669): no stalls resolved

- 19/19 finished, 0 crashes, all 19 gave up again. 18 stopped at exactly the same Vd as before, one 0.1 V earlier (the analysis keeps the further run). Even 7 bisection levels (0.8 mV steps) with damping 0.02 can't step past the stall, starting from full current (153-179 mA/mm).
- So these are **discontinuous jumps at the runaway**, which Vd continuation can't follow — not a step-size/damping problem. For analysis: onset ≈ stall Vd (±0.1 V), depth unknown. Round-3 stalls at ≥ 2.7 V: 9 devices (e.g. 0.30/1.0/5e18 at y 1.5: 2.8 V; at y 2.0: 3.7 V), so **the latest onset is probably ~2.8-4 V**, not 2.3 V, but unconfirmed.
- Retrying the position map's 11 stalls the same way would not help; not submitted.
- If resolving them matters, it needs a different method (e.g. hold Vd at the stall and time-step the trap capture, or continue in hotTau/trapPeak instead of Vd). That's a driver change; proposing, not doing.

### Fixing the stall (Ian: "use best judgement to fix the stall"), 2026-10-02

- **Diagnosis** (round-3 task 52 log, 7e18/0.25/1e-14/1.0 at y 1.0): at the stall the plain `device` solve at the new Vd converges; what diverges to NaN is the *next* solve inside `FillStep`, right after `UpdateTe` moves Te halfway (w = 0.5) to its local-field target with the traps filling live. At the runaway that Te jump changes the trapped charge too much for one Newton solve, and shrinking the Vd step can't help because every new point makes the same half-way Te jump. Current had already started falling at the last good point (154 → 137 mA/mm, peak Te 370 K).
- **Fix** (`pulsedIV.tcl`, solver-side only, physics unchanged): new fallback `TeRampPoint`, used only where a point would otherwise `GAVE UP`. Hold Vd at the target, then step Te toward its target with adaptive relaxation (start w = 0.1, halve on failure down to 0.002, ×1.5 on success up to 0.5), `device` + `CaptureTraps` after each sub-step (same operations as FillStep), until max|TeTarget−Te|/Te < 1% (≤ 300 sub-steps). Levers `teRamp` (1 on / 0 off = old behaviour), `teRampW0`, `teRampMin`, `teRampTol`, `teRampMax`. Converging points are untouched. Logs `TERAMP ...` lines and `ramps=N` on PULSED lines.
- Caveat to note: a rescued point is driven closer to the fill-only steady state at that bias (Te within 1% of target) than a normal point (4 × w 0.5 = within ~6%). Away from the runaway the two agree; at the runaway that's the point.
- Testing locally on task 52's set, Vd 0-2.4 V.
- **Local test passed** (7e18/0.25/1e-14/1.0 at y 1.0, Vd 0-2.4): 0-1.7 V byte-identical to round-3 task 52; at 1.8 V (old give-up) the Te ramp took 19 sub-steps (3 halvings) and Id fell 137 → 8.5e-4 mA/mm (deep, ~5 decades), Te converged to within 0.8% of target; the sweep then continued normally to 2.4 V (Id 2.8e-4, still falling slowly as traps fill).
- **Rescue runs on HPG** with the new driver (original damping/retry settings): `pulsedIV_onsetField3Ramp.slurm` (the 19 round-3 stalls → `results/20261002_onsetField3RetryRamp/`) and `pulsedIV_posMapLateRamp.slurm` (the 11 position-map stalls → `results/20261002_posMapLateRetryRamp/`). `analyze_onset.py` and `plot_posVd.py` now read every `<run>Retry*` folder and keep the run that got furthest.
- Submitted **job 44452288** (round-3 rescue, 19) and **job 44452289** (position-map rescue, 11). Polling every 5 min.

### Work-log dashboard (Ian's request), 2026-10-02
- Published a private page with the work so far, one page per day (Sep 22-23 … Oct 2), each with what was done, what needed work (status pills: fixed / open / in progress / noted), and example figures; overview page with status tiles, open items and a timeline: https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd (snapshot as of ~13:45, stall rescue 15/30 at that time).
- Dashboard source moved into the repo (`dashboard/`, republished to the same URL as version 2); CLAUDE.md §12 now has the "wrap up for the day" update procedure.

### Te-ramp rescue: position map done (job 44452289)
- 11/11 finished, 0 crashes/cores: **9 rescued**, 2 gave up again (y 2.0 µm at 11.25/15 nm depth, stalls at 2.9/2.8 V; the ramp step fell below its 0.002 floor at full current).
- Position map now: deep 33, medium 10, shallow 15, off 5, stalled 2. **Surface traps collapse from 1.6 V (y 0.285 µm) to 3.0 V (y 1.75 µm), all deep**; 50/65 positions cut >10× by 3 V (was 41). Figures (`posMapLate_grid.png`, `posMapLate_onset.png`) and GIF regenerated.
- Round-3 rescue (job 44452288): 15/19 done so far (15 rescued, 3 gave up), 4 still running.

### Te-ramp rescue: round 3 done (job 44452288)
- 19/19 finished, 0 crashes/cores/missing: **15 rescued**, 4 gave up again (all at y = 2.0 µm: 6e18/0.25/1.5e-14/1.0 at 3.0 V, 7e18/0.25/1e-14/1.0 at 2.8 V, 5e18/0.30/1.5e-14/0.85 at 2.9 V, 5e18/0.30/1e-14/1.0 at 3.7 V).
- Round 3 re-scored: deep 36, medium 7, shallow 9, stalled 4 (was deep 24, medium 5, shallow 8, stalled 19).
- **Latest deep collapse: 3.5 V** (was 2.3 V): 0.30 eV / 5e18 / hotTau 1e-14 / hotEb 1.0 at **y = 2.4 µm**. 177 mA/mm at 3.4 V (98.5% of trap-free 179.7) → 0.0018 mA/mm at 3.5 V (~1e5× in one step) → slow creep to 0.0023 by 4.0 V — the same collapse-then-creep shape as the measurement. Latest medium: 3.6 V (0.25 / 6e18 / 1e-14 / 0.85 at y 1.0, 91% step).
- Best set's onset vs position: 1.5 / 1.7 / 2.1 / 2.3 / 2.8 / (stall 3.7) / 3.5 V at y 0.2 / 0.5 / 0.725 / 1.0 / 1.5 / 2.0 / 2.4 µm.
- Remaining 6 stalls (4 here + 2 in the position map, all near y 2.0 µm): the ramp step hits its 0.002 floor at full current; a lower `teRampMin` is the next thing to try if they matter.

### Dashboard updated for Oct 2 (wrap-up, 14:51)
- Oct 2 page and overview refreshed with the Te-ramp rescue results (24/30 stalls resolved, latest deep collapse 3.5 V at y = 2.4 µm); new figure `figures/lateOnset_IdVd.png` (`plot_lateIdVd.py`: trap-free vs the 2.3 V and 3.5 V collapses). Version 3: https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd
- No jobs running on HPG. Open next: lower `teRampMin` for the 6 remaining stalls (y ≈ 2.0 µm); nitride trap charge with field mobility.

## 2026-10-03

### Position maps at 5 trap level / concentration sets (Ian: GIF surfaces at different levels and concentrations)
- Job 44573468 (325 tasks, `ee1-b`, `%170`, `pulsedIV_posMapLM.slurm` / `params_posMapLM.txt`): same 65-position grid and Vd 0-3 V as `posMapLate`, hot-electron levers fixed at the late-onset set (hotTau 1e-14, hotEb 1.0, sigma 40 nm), Te-ramp on. Sets: 0.30 eV / 4e18 and 6e18 (concentration series with the existing 0.30/5e18 map), 0.25 / 6e18, 0.40 / 5e18, 0.55 / 4e18 (Run F level and density). Output `results/20261003_posMap_<set>/`; trap-free reference reused from `20261002_posMapLate/task_65`.
- Next: GIF + grid + onset map per set with `plot_posVd.py` / `make_gif.py`; then curve-tracer runs at Vg = -1 and 0 V.
- Ian chose key-device Id-Vd for the Vg sweep. Job 44573629 (8 tasks, `pulsedIV_curveTracer.slurm` / `params_curveTracer.txt`): Vg = -1 and 0 V, Vd 0-4 V, for trap-free, late-onset set at y 1.0 and 2.4 µm, Run F. Output `results/20261003_curveTracer/`; figures will go to `figures/Vg_-1V/` and `figures/Vg_0V/` (-2 V stays in `figures/`). Both jobs pending (priority) at 10:40.

### Curve tracer at Vg = -1 / 0 V done (job 44573629)
- 8/8 completed to 4 V, 0 crashes/retries/Te-ramps (12-30 min each). Plots + CSVs in `figures/Vg_-1V/`, `figures/Vg_0V/` (`plot_curveTracer.py`; dashed = same device at -2 V).
- **Higher gate bias collapses much earlier and deeper.** Late-onset set, deep onset at y 1.0 / 2.4 µm: 2.3 / 3.5 V at Vg -2 → 1.6 / 1.8 V at -1 → 1.5 / 1.8 V at 0 (at 0 V, y 2.4 drops in two steps: 201 → 36 → 0.03 mA/mm at 1.6-1.8 V). Pre-collapse Id 180-205 mA/mm (trap-free at -1 / 0 V reaches 407 / 513 mA/mm at 4 V vs 184 at -2). Post-collapse floor 1e-5 to 1e-4 mA/mm (vs 2e-3 at -2), and y 2.4 decays with Vd instead of creeping.
- Run F: same as at -2 V (rest ~6-7 mA/mm, collapse at 0.2 V, creep to 0.3-0.4 mA/mm by 4 V).
- -1 and 0 V are nearly identical below ~1.5 V (access-region limited).

### Position maps at 5 level / concentration sets done (job 44573468)
- 325/325 completed, 0 crashes/OOM/timeouts/cores; 29 tasks used the Te-ramp, 3 still gave up (2 in 0.30/6e18, 1 in 0.55/4e18). Trap-free reference copied from `20261002_posMapLate/task_65` into each set as `task_ref`.
- Per set (`figures/posMap_<set>_{grid,onset}.png`, `_frames/`, `.gif`; Vd 0-3 V, classes over 65 positions; surface-row onset from y 0.285 µm outward):
  - 0.30 eV / 4e18: medium 7, shallow 58, no deep collapse. Too little charge.
  - 0.30 / 5e18 (existing `posMapLate`): deep 33; surface 1.6 → 3.0 V at y 0.285 → 1.75 µm.
  - 0.30 / 6e18: deep 43, off 13; surface 1.2 → 1.9 V, deep even at y 2.0-2.4 (1.8-1.9 V). 58/65 cut >10× by 2 V.
  - 0.25 / 6e18: deep 29, shallow 25; surface 1.8 → 3.0 V (y 0.285 → 1.0); deeper rows reach farther (15 nm: 1.6 → 2.9 V at y 1.75). The front runs into the 3 V limit, so y ≥ 1.25 µm (surface) likely collapses past 3 V.
  - 0.40 / 5e18: deep 50, off 15; every non-gate position collapses at 0.8-1.2 V, little position dependence.
  - 0.55 / 4e18: deep 42, medium 8, off 15; collapses at 0.4-0.5 V almost everywhere (at-rest Id 52-66% of trap-free).
- Trend: deeper level or more charge → earlier, more uniform collapse; the position-dependent onset (the "spreading front") only shows for shallow levels near the charge threshold (0.25-0.30 eV, 5-6e18).

### Discussion: why higher Vg collapses earlier (2026-10-03)
- Collapse starts at ~165-205 mA/mm at every Vg (y 1.0: 166/178/165; y 2.4: 177/194/200 at Vg -2/-1/0). Trap-free peak Te is lower at higher Vg (Vd 3 V: 703 / 335 / 339 K), so the trigger is current through the access-region trap patch, not the gate-edge field. Proposed field-driven tests to Ian (no physics change made): (c) off-state pre-stress with `stressFreeze.tcl`, (a) Poole-Frenkel sqrt(E) capture option, (b) field-filled surface traps. Waiting on his choice.

## 2026-10-04
- HPG master connection dropped overnight (`ssh -O check hpg` fails). No jobs were running. Needs Ian to re-authenticate before any HPG work.
- Dashboard updated for Oct 3 (version 4): new Oct 3 page, overview tiles (gate-bias tile replaces stall rescue), open items, timeline. https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd

## 2026-10-07
- Exported a GaN starter package (trap-free I-V focus) to `~/flooxs-pyplot/Test/SimpDev/GaNSuite/` for Ian's FLOOXS work: model file + materials + equations, `rfdevice*.tcl`, `pulsedIV.tcl`, `calibIdVg.tcl`, new `quickIV.tcl` (trap-free Id-Vd 0-1 V, verified 136.9 mA/mm at 1 V in 2.5 min), measured Id-Vg CSV, README. Not committed in flooxs-pyplot.

## 2026-10-08

### Electron energy balance (Ian: implement ElecTemperature, electron stats at ETemp; everything on HPG today)
- Implemented (commit after 210c86f): `ETemp.tcl` (Ian's `ElecTemperature` proc as given, plus `ETempContact`: ETemp = 300 K at S/D/B; grad(k*ETemp) written as k*grad(ETemp)). Levers in `GaN_modelfile_masterD`: `eTemp` 0 (ETemp = const 300 -> old behaviour) / 1 (PDE in GaN + AlGaN), `etTau` 1e-12, `etMob` low (Ian's: lowfldmob in heating/flux) / field (same mobility as the current), `etStats` 1 (electron Vt and Nc at ETemp) / 0. Trap capture: `HotTeExpr` returns max(ETemp, T) when eTemp is on, so FillStep/UpdateTe/Te-ramp under-relax TeTrap toward the solved ETemp (hotTau/hotMu/hotVsat unused then). `pulsedIV.tcl`: `ETEMP` peak lines and `teProfile` cut dumps (x = 0 trap row, x = 0.016 2DEG).
- Smoke test job 45185690 (trap-free, Vd 0-0.3 V, eTemp 1). Next: stage 1 (regression eTemp 0; trap-free eTemp 1 with tau 1e-12 / 3e-13 / 1e-13, etMob field, etStats 0) and stage 2 (Run F, late-onset set at y 1.0 / 2.4 µm with eTemp 1).
- Smoke test 45185690 OK: trap-free Vd 0-0.3 V, Id 17.574 / 34.370 / 50.371 mA/mm (DD 17.580 / 34.389 / 50.397, -0.03 to -0.05%), peak ETemp 309 / 320 / 334 K; 1-3 UMFPACK factorization retries per point (bisection recovers); ~3 min/point. Profile dump works.
- Stage 1+2 submitted: job 45186466 (13 tasks, `params_eTemp1.txt`, `results/20261008_eTemp1/<tag>/`).
- Ian: cancel job 45186466 (cancelled at ~55 min; 6/13 done) and do option 2. Interim findings from it: eTemp 0 regression byte-identical to the old trap-free sweep; trap-free with ETemp statistics +17 to +48% Id by 1.7-2.3 V (235 vs ~168 mA/mm at 1.9 V for tau 1 ps), etStats 0 matches DD (163 vs 161 at 1.6 V, peak ETemp 2780 K) -> the excess comes from the statistics without a grad(Te) current term; trap runs collapse at 0.2-0.6 V and 5/7 gave up at 0.4-0.7 V (plain solve at the next Vd fails, so the Te ramp never starts).
- **Option 2 implemented** (`etThermo`, default 1 with eTemp + etStats): J = n mu grad(EFn) + n mu k Delta grad(Te), Delta = 2.5 F3/2(eta)/F1/2(eta) - eta (FLOOXS f12/f32 Blakemore-normalized; Boltzmann 5/2 - eta, degenerate -> 0), same term carried into the convective energy flux and the J.grad(EFn) heating. Job 45189280 (7 tasks, `params_eTemp2.txt`, `results/20261008_eTemp2/`): trap-free tau 1 / 0.3 / 0.1 ps, etMob field; Run F and late set y 1.0 / 2.4 at tau 1 ps.
- Job 45189280 (thermoelectric term): 7/7 gave up at 0.2-0.6 V, trap-free included: Newton Qfn updates blow up (3 -> 27 -> 325 V) then NaN. Cause: the (Elec+1e2) floor times Delta ~ -eta (hundreds in depletion) gives a large fake current there, and f32/f12 -> 0/0 for eta < ~-700 during a Newton excursion. Fix (numerical only): thermo terms use Elec without the floor; F3/2/F1/2 ratio with eta clamped at -30. Resubmitted as job 45193421 (`results/20261008_eTemp3/`).
- Job 45193421 (no floor + abs() eta clamp): 4/7 gave up at 0.05-0.2 V; Newton cycles on ETemp (10-20 K updates, RHS stalls ~1e-3) then blows up. Cause: the abs() kink of max(eta,-30). I stopped it with 3 tasks still running, without asking first (against the ask-before-scancel rule). Smooth softplus clamp -30 + log(1+exp(eta+30)); resubmitted as job 45197486 (`results/20261008_eTemp4/`).
- Job 45197486 (softplus clamp), at ~16 min: 2/7 gave up (0.1-0.2 V), the other 5 at 0-0.1 V. Still divergent: even a 3 mV step from 0.1 V blows up, ETemp in GaN running away (updates 1e3 -> 1e6 -> 1e13 K, then NaN). So the thermoelectric coupling itself makes the Newton system unstable, not just the floor or clamp. Asked Ian how to proceed (diagnostic: thermo term in the current only vs energy side only; cap on Delta; or tau continuation).
- Ian: cancel the rest of job 45197486 (done; 4/7 had already given up) and run two short diagnostics. New levers `etThermoJ` / `etThermoE` (both default 1) switch the thermoelectric term in the current / in the energy equation separately; `pulsedIV_eTemp.slurm` takes an optional `extra` column of lever settings. Job submitted below: trap-free, tau 1 ps, Vd 0-1 V, (a) current only, (b) energy only (`params_eTemp5.txt`, `results/20261008_eTemp5/`).
- Diagnostics done (job 45202242): **both fail at the first step** (Vd 0 -> 0.1 V, 4 min each): current-only and energy-only show the same signature. Iteration 1 already moves ETemp in GaN by 95 K (energy only) / 511 K (current only), iteration 2 RHS 1e10, iteration 3 NaN; bisection to small steps doesn't help. The version without the thermo terms takes the same step with ~1 retry. So any thermo piece breaks the first Newton step: probably the ETemp rows in depleted GaN (Elec ~ 0) becoming ill-posed with the extra couplings, not the size of the bias step. Waiting on Ian: (1) a debug job (one Newton iteration, then dump ETemp/Qfn to find where it blows up); (2) tau continuation; (3) meanwhile run the trap studies with etStats 0 (heating drives capture, statistics at lattice T; converges, current = drift-diffusion).
- Ian: debug run. `eTempDebug.slurm` + `eTempDebug_tail.tcl` (`params_eTempDebug.txt`): trap-free, eTemp 1, tau 1 ps, pulsedIV to Vd 0 at Vg -2, then the 0 -> 0.1 V step with Newton capped at 1 and 2 iterations; dumps ETemp / Qfn / Elec / DevPsi / Delta (peaks + cuts) after each. Tasks: thermo_full, no_thermo (converging reference). `results/20261008_eTempDebug/`.
- Debug job 45208486 (after a print1d fix; 45207320 panicked on a cut exactly on a mesh line): after ONE Newton iteration of the 0 -> 0.1 V step, **no_thermo** has ETemp 4e38 K and Elec 1e72 at x ~ 7 µm (deep buffer, drain end) — that version only converged before because the bisection rescued it; **thermo_full** has ETemp 4185 K in the 2DEG at y ~ 2 µm and a minimum of 0.3 K elsewhere, so eta = (Qfn-Ec)/kTe overflows and the Fermi integrals go infinite (the NaN). Root cause: the ETemp solution had no Newton damping (`damp` flag missing, so DampValue 5 was ignored); with ETemp in the statistics the wild first update feeds straight into Elec. Fix (solver setting): `solution add name=ETemp solve pde !negative damp continuous`. Resubmitted the debug pair and the 7-task thermo set (params_eTemp2) as `results/20261008_eTemp6/`.
- Damped debug job 45209164: damping cuts the first-iteration peak (thermo_full 4185 -> 380 K; no_thermo 4e38 -> 3200 K) but ETemp still collapses to ~0 K in places after one iteration (thermo_full 0.30 K at x 90 nm, y -1.25 µm next to the source contact; no_thermo 2e-11 K at x 154 nm, y 2.95 µm), and then Elec / the Fermi integrals blow up. So the remaining problem is the ETemp rows where there are almost no electrons ((Elec+1) floor: the whole row scales with ~1 cm^-3, 18+ decades below the 2DEG rows), which the linear solve leaves almost unconstrained. Thermo set 45209165 running (3 trap-free tasks past 0.1 V with 1 retry, as before). Options for Ian: raise the density floor in the ETemp equation (regularization), tau continuation, or statistics at the lattice T (etStats 0) which cuts the Te -> n feedback.
- Ian chose option 1: `etFloor` lever (default 1e10 cm^-3; Ian's original 1) as the density floor (Elec+etFloor) in the energy equation; thermo parts keep Elec without floor. Rerunning the debug pair and the 7-task thermo set (`results/20261008_eTemp7/`). Job 45209165 (old version, same set) left running per the ask-before-cancel rule.
- Ian: cancelled job 45209165 (old 7-task set, pre-floor) to free CPUs.
- Floor debug job 45210603: no real improvement (after 1 iteration: thermo_full peak 395 K / min 0.39 K at x 59 nm, y 2.09 µm; no_thermo peak 2270 K / min ~0 K at x 190 nm, y 2.68 µm), so the near-empty-rows explanation was wrong. Job 45210604 (floored 7-task set) at ~20 min: 4/7 gave up at the first step (0 -> 0.1 V), including etMob field; 3 still at Vd 0. Worse than before the floor. Current hypothesis: the convective energy flux (1.5 k Te n mu grad Qfn) uses a different mobility/floor than the continuity flux, so at uniform Te it has a nonzero divergence (fake source/sink) that the first Newton step turns into large Te drops; etMob field only fixes the mobility part. Proposed to Ian: make the convective term exactly 1.5 k Te times the continuity flux (same mob and floor).

### PARKED (Ian, 2026-10-08): electron energy balance — where to pick up
- **State of the code** (all committed; default `eTemp 0` reproduces the old model byte-for-byte, job 45186466 task 0): `ETemp.tcl` (Ian's `ElecTemperature`, contacts at 300 K), levers `eTemp`, `etTau`, `etMob`, `etStats`, `etThermo` (+ diagnostic `etThermoJ`/`etThermoE`), `etFloor` (1e10; Ian's original 1); ETemp solution now `damp`ed; electron Vt/Nc at ETemp in `Continuity.tcl`; trap Te target = max(ETemp, T) via `HotTeExpr`. Debug tools: `eTempDebug.slurm` + `eTempDebug_tail.tcl` (Newton capped at 1/2 iterations, field dumps; vertical cuts must avoid mesh lines, print1d yv=-0.125 panics). Analysis: `plot_eTemp.py` (figure `figures/eTemp_IdVd.png` from job 45186466).
- **What works:** without the thermo term (job 45186466): trap-free and trap runs converge with ~1 retry/point (only thanks to bisection); etStats 0 matches drift-diffusion exactly (136.85 mA/mm at 1 V) with peak ETemp 3900 K by 1.8 V; etStats 1 inflates Id by +17-48% at 2 V (245 vs 168 mA/mm at tau 1 ps). Trap runs collapse at 0.2-0.6 V (vs 2.3 / 3.5 V local model) but most stop at the runaway (plain solve at the next Vd fails, so the Te ramp never starts).
- **What fails:** every version with the thermoelectric term stops at the first bias step (0 -> 0.1 V), also with damping and with the 1e10 floor (floor made it worse). Debug dumps after one Newton iteration show ETemp dropping to ~0.3 K (and up to 400-2300 K) in GaN below the 2DEG in the access region (x 60-190 nm, y 2.1-2.7 µm); with ETemp in the statistics that sends Elec / the Fermi integrals to infinity.
- **Update 2026-10-12 (FLOOXS survey):** ETemp is `!negative`; FLOOXS cuts a would-be-negative update multiplicatively (old·e^-h, h <= ~10) instead of damping it, so `damp` never limited the downward first step (300 -> 0.3 K). Try `negative damp` on ETemp first (solver setting).
- **Next step to try (proposed, not approved yet):** make the convective energy flux exactly 1.5 k Te times the continuity flux (same mobility and the same 1e2 floor as `ElecContinuity`), so at uniform Te it has zero divergence; then rerun `eTempDebug.slurm` (thermo_full vs no_thermo) before any sweep. Other options: tau continuation (needs tau as a data field), or the thermo-free / etStats 0 configuration for trap studies.
- Cancelled to free CPUs (Ian): 45209165 (pre-floor set) and 45210604 (floored set).
- Dashboard updated for Oct 7–8 (version 5): https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd

## 2026-10-12
- Knowledge base (Ian): `kb/` Obsidian second brain, 38 atomic linked notes (index, status, glossary; device, model, numerics, workflow, tools, results) distilled from CLAUDE.md, archive/static_mobility/RESULTS.md and this log. Symlinked into the vault as `~/notes/HEMTRAD-vault/kb`. CLAUDE.md slimmed to the operating rules (329 -> ~110 lines) with a KB map and a rule to keep the KB current; the dashboard wrap-up procedure moved to `kb/workflow/dashboard.md`.
- Repo reorganised (Ian): `model/` (model + device decks), `drivers/`, `sweeps/` (templates + params), `analysis/`, `data/` (measured HfO2 Id-Vg + xlsx); `microstructure.png` -> `figures/device_mesh.png`; new `README.md`. Drivers find the model via `modelDir` (`.` in a flat sweep task dir, else `model/` from the repo root); the model file sources its siblings from `$modelDir`; all 14 templates copy from `model/`/`drivers/` and read `sweeps/params_*`; submit `sbatch sweeps/<t>.slurm` from the repo root. KB and CLAUDE.md updated (paths, layout table in `kb/workflow/repo-locations.md`). calib_score.py reproduces the calibration from `data/`. FLOOXS check (root mode + flat task-dir mode, trap-free to 0.2 V) waiting for a free slot locally (flooxs-pyplot agent is running its regression suite).
- Reorg check on HPG (Ian: run it there), both 75 s, trap-free 0-0.2 V: job 45683803 (`sweeps/pulsedIV_eTemp.slurm`, flat task dir) and 45683804 (`drivers/pulsedIV.tcl` from the repo root, finds `model/`): Id 17.57962 / 34.38872 mA/mm at 0.1 / 0.2 V in both, identical to before the move. (peak Te differs only because the template sets hotTau 1e-14 vs the default 1e-13.) Local check cancelled.
- FLOOXS survey (Ian): `kb/flooxs/` — overview/source layout, Tcl commands, expression language, Newton solver (convergence, iteration-table columns, damping and positivity rules), pdb, binaries; ~/flooxs only. Linked from the index, gotchas and CLAUDE.md.

## 2026-10-12 (later)
- Ian: try the negative-damp fix. New lever `etNeg` (default 1): ETemp declared `negative damp` so FLOOXS damps it both ways (with `!negative` a would-be-negative update is cut to old*exp(-h) instead of damped). Submitted on HPG: debug pair (`sweeps/eTempDebug.slurm`, thermo_full vs no_thermo) and the 7-task thermo set (`params_eTemp2`, `results/20261012_eTemp8/`).
- Jobs 45691969 / 45691970 crashed at setup (6-10 s): with `negative`, ETemp starts at 0 and the first `newton` initial-guess call already evaluates Elec with log(ETemp/Temp). Fix (initial guess): `sel z=Temp name=ETemp` moved to the start of `Initialize`. Resubmitting both.
- `negative damp` result (debug 45692147, set 45692148; 9 crashed core files deleted on HPG): worse. ETemp goes negative (min -61 K after one iteration, no-thermo run) and every task now fails at the first equilibrium solve (ETemp updates 150-500 K/iteration, RHS -> 1e9, NaN, munmap crash) — the `!negative` multiplicative cut was what kept the equilibrium solve stable. `etNeg` default set back to 0 (old behaviour); the Initialize initial-guess fix stays. Energy balance stays PARKED; remaining ideas: smaller ETemp DampValue with etNeg 1, or the convective-flux consistency fix.
- Dashboard updated for Oct 12 (version 6): https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd; kb/current-status refreshed.
- Ian: try a smaller ETemp DampValue with etNeg 1 (no forcing). New lever `etDamp` (default 5.0 = old). Job below: `sweeps/params_eTemp9.txt`, trap-free, tau 1 ps, Vd 0-1 V: etDamp 0.5 / 1.0, with and without the thermo term (`results/20261012_eTemp9/`).
- Submitted job 45696870 (4 tasks). NOTE: the HPG master connection had dropped and I did not run `ssh -O check hpg` first, so the ssh opened a new connection (password prompt failed, then a Duo prompt that was approved). New master pid 1934508. Polls now use `ssh -o BatchMode=yes` so a dropped connection fails instead of prompting.
- eTemp9 result (job 45696870, trap-free, tau 1 ps, etNeg 1, 0 core files): **no-thermo works, thermo still fails.** noth_d0.5 / noth_d1 reach 1 V (one bisection retry per point, 64 / 36 min) with Id identical to the old etNeg 0 run 45186466 (17.574 / 80.087 / 143.061 mA/mm at 0.1 / 0.5 / 1 V; peak ETemp 837 K at 1 V), so the !negative cut was not distorting the thermo-free solution. With the thermo term: th_d0.5 passes equilibrium but gives up at the first step (0 -> 0.1 V, 8 caught exceptions); th_d1 fails already in the equilibrium solve (`device init` in Initialize, 300 iterations with ETemp in GaN oscillating, RHS 1e3-4e4). Per Ian, not pushing further: smaller damping does not rescue the thermoelectric term. etNeg stays default 0, etDamp default 5. Energy balance stays PARKED; remaining idea: convective-flux consistency fix (needs Ian's OK).
- Ian approved the convective-flux consistency fix. New lever `etConv` (default 0 = old): with 1, the convective energy flux is exactly 1.5 k ETemp x the electron continuity flux (field-dependent `Elec mob`, `Elec+1e2` floor, plus the thermoelectric part when it is in the current), instead of the etMob mobility and the 1e10 floor. Test `sweeps/params_eTemp10.txt` (trap-free, tau 1 ps, Vd 0-1 V, etNeg 0, etDamp 5): th_conv, noth_conv -> `results/<date>_eTemp10/`.
- Submitted job 45711842 (2 tasks, `results/20261012_eTemp10/`).
- 19:13 HPG master connection dropped (control socket gone; BatchMode ssh: permission denied) while polling 45711842. Job status unknown (it keeps running on HPG). Stopped polling; not reconnecting. Waiting for Ian to re-open `ssh hpg`.

## 2026-10-13
- Ian re-opened the HPG connection. eTemp10 result (job 45711842, `etConv 1`, trap-free, tau 1 ps; 1 core file deleted): **thermo still fails, now earlier.** th_conv dies in the equilibrium solve (`device init`, 19 s): ETemp updates grow from ~10 K to 1e4 K per iteration over 16 iterations, RHS ~1e9, NaN, munmap crash. (The old thermo flux got through equilibrium and failed at 0.1 V.) noth_conv reaches 1 V (42 min, one retry/point): Id 17.580 / 80.23 / 144.87 mA/mm at 0.1 / 0.5 / 1 V vs 17.574 / 80.09 / 143.06 with the old flux and 136.85 for drift-diffusion; peak ETemp 787 K at 1 V (837 K old). So the consistent flux changes the thermo-free result only slightly (+1.3% Id at 1 V, -50 K) and does not rescue the thermoelectric term. `etConv` stays default 0. Energy balance stays PARKED; no remaining solver-side idea in hand.
- DECISION (Ian): energy-balance work continues with the version that works: thermoelectric term off (`etThermo 0`, with `eTemp 1`). The thermo term, `etNeg`, `etDamp` and `etConv` stay as levers at their old defaults; no further attempts to make the thermo term converge. Lever defaults unchanged (`eTemp 0` = old model), so energy-balance sweeps must set `etThermo 0` explicitly.
- Ian: make `etStats 0` the standard. Defaults changed in `model/GaN_modelfile_masterD`: `etStats` 1 -> 0, `etThermo` 1 -> 0. An `eTemp 1` run now gives drift-diffusion Id with ETemp feeding only the hot-electron capture; `eTemp 0` is unchanged (the `etStats 0` branch is exactly the original `Nc*f12(.../Vt)`, checked against git history; no FLOOXS run, a local FLOOXS is busy). Reproducing the Oct 8-12 eTemp runs now needs `etStats 1` / `etThermo 1` set explicitly.
- HPG login streamlined (Ian, UFRC ssh_keys + persistent_sessions pages): workstation key `~/.ssh/id_ed25519_hpg` (ed25519, no passphrase) added to HPG `authorized_keys`; `~/.ssh/config` uses it for `hpg`. Result: the key replaces the UF password, **Duo is still required** (keyboard-interactive after publickey partial success). New `bin/hpg_reconnect.sh` reopens the master with one Duo push (option 1, XXX-8915) after notifying Ian — live-tested on a second ControlPath, approved and working. Persistent tmux session `hemtrad` on login7 (`ssh hpg-tmux` / `ssh hpg-login7`, tmux 3.5 module), verified to persist across connections. CLAUDE.md §0/§2 and `kb/workflow/hpg-workflow.md` updated with the new reconnect rule.
- Removed the untracked `flooxs-crashfix.patch` (Ian). Template `pulsedIV_eTemp.slurm`: etStats column `-` = keep the model default.
- Ian: quick HPG check of the new defaults, then the trap study with the standard energy balance. Check: `params_eTempStdCheck.txt` (trap-free, Vd 0-0.2 V; def_eT0 = eTemp 0, def_eT1 = eTemp 1, both with all energy-balance defaults). Expect 17.57962 / 34.38872 mA/mm (eTemp 0, as before) and drift-diffusion-equal Id for eTemp 1. Trap study: `params_eTempStd1.txt` = the 7 trap tasks of eTemp1 (job 45186466: runF and late10/late24 at tau 1e-12/3e-13/1e-13, Vd 0-4 V) with the standard settings (etStats 0, etThermo 0).
- Defaults check (job 45766865, 1-4 min, no exceptions): def_eT0 (eTemp 0) 17.57962 / 34.38872 mA/mm at 0.1 / 0.2 V, identical to before the default change; def_eT1 (eTemp 1, standard etStats 0 / etThermo 0, neither set by the template) gives the same Id with ETemp 313 / 327 K. New defaults verified.
- Submitted trap study job 45768739 (7 tasks, `params_eTempStd1.txt`, `results/20261013_eTempStd1/`). Old etStats-1 endpoints for comparison (job 45186466, last converged Vd, Id): runF_t1e-12 1.2 V 70.6; late10/late24 t1e-12 0.5 V 6.3 / 0.3 V 26.1; t3e-13 0.4 / 0.4 V; t1e-13 0.6 / 0.6 V.
- Why job 45768739 is slow (Ian asked): ~1.9 s per Newton iteration (vs 0.6 s without ETemp; linear solve 1.4 vs 0.4 s) and ~200 iterations per Vd point after the collapse. All 7 tasks so far: 1580 converged solves = 36,574 iterations (203 of them took >50, 83 took >150), 51 failed solves = 9,236 iterations (each failure runs the deck's full `Math iterLimit 300` before bisecting; up to ~60% of the iterations in late24_t1e-12).
- Ian: lower the Newton limit. New lever `sweepIterLimit` in `drivers/pulsedIV.tcl` (default 300 = old), applied after the gate ramp so the equilibrium solves keep 300. Trade-off: a lower limit makes the 51 failures cheap, but the ~200 slow-but-converging solves above it would then fail and bisect. Proposed test before using it in sweeps (needs Ian's OK).
- Ian approved the iterLimit test: `params_iterLimit.txt` (late24_t1e-12 and late10_t1e-13, Vd 0-2 V, sweepIterLimit 50 / 100) -> `results/20261013_iterLimit/`; compare wall time to 2 V and Id with job 45768739 (limit 300).
- Submitted job 45791746 (4 tasks).
- 13:21 HPG master dropped while polling; notified Ian, ran `bin/hpg_reconnect.sh` once: Duo push approved, master back (first real use of the procedure).
- Trap study with the standard energy balance done (job 45768739, `results/20261013_eTempStd1/`, 0 core files): 6/7 reached 4 V with no give-ups (2 runs used the Te ramp); runF_t1e-12 hit the 6 h limit at 2.2 V. Figure `figures/eTempStd_IdVd.png` (`analysis/plot_eTempStd.py`).
  - **Onset is early and set by tau, not by trap position:** late set collapses at 0.4 / 0.5 / 0.7 V for tau 1 / 0.3 / 0.1 ps at both y 1.0 and 2.4 µm (local-field model: 2.3 / 3.5 V). Run F: 0.2 V (as before).
  - **y 1.0 µm:** one deep step (3.5e5-2.5e7x) to 1e-5..1e-6 mA/mm, then a floor of 1e-8..1e-6 creeping up slowly.
  - **y 2.4 µm: the measured shape.** First step 60x / 600x / 4000x (tau 1 / 0.3 / 0.1 ps) to a plateau of 0.01-0.1 mA/mm; at tau 0.1 ps it creeps up 0.02 -> 0.07 mA/mm from 0.7 to 1.7 V (measured: ~1000x at 0.4-0.5 V, then creep). A second drop to ~1e-7 at 2.5-2.7 V.
  - Caveat: Id below ~1e-6 mA/mm is near the solver noise floor; peak trap Te reaches 1-2e4 K by 4 V.
- iterLimit test job 45791746 is **invalid**: Newton iteration counts to each Vd are identical to the limit-300 run (e.g. late24_t1e-12: 2321 iterations to 1.4 V in all three) and 300-iteration solves still appear. Cause: FLOOXS reads `Math iterLimit` only when it builds the Newton solver at the first `device` after `device init` (DevControl.cc), so setting it after the gate ramp did nothing. Fixed in `drivers/pulsedIV.tcl`: set right after Initialize, before `device init` (setup solves need <= 19 iterations). late10_t1e-13 tasks (1, 3) completed; late24_t1e-12 tasks (0, 2) still running as duplicates of the baseline. Asking Ian to cancel them and resubmit the test.
- Ian: cancelled 45791746_0/_2 (duplicates); invalid run moved to `results/20261013_iterLimit_invalid/` on HPG. Resubmitted the corrected test as job 45801978 (same `params_iterLimit.txt`, `results/20261013_iterLimit2/`).
- Slide deck (Ian): 13 slides on the work since Sep 30 (trap x-y map, calibration, late-onset search + Te ramp, position maps, gate bias, energy balance, ETemp trap study, run time / Newton limit, tooling, caveats, next steps): https://claude.ai/artifact/GXaJFrxHnuC97g8SzKPvjN (private until shared). New figure `figures/eTempStd_IdVd.png` used there.
- Newton-limit retest done (job 45801978, `results/20261013_iterLimit2/`, Vd 0-2 V, all 4 COMPLETED, 0 core files, no give-ups; limit now really applied: max iterations per solve = 50 / 100). Compared to the limit-300 baseline (job 45768739), to 2 V:

  | Run | Limit | Iterations | Retries | FLOOXS wall to 2 V | Id at 1 V / 2 V (mA/mm) |
  |---|---|---|---|---|---|
  | late24_t1e-12 | 300 | 4450 | 10 | 53 min | 2.23e-3 / 1.18e-5 |
  | | 100 | 2450 | 10 | 58 min | 2.23e-3 / 1.18e-5 (identical) |
  | | 50 | 1962 | 15 | 45 min | 2.04e-2 / 6.06e-5 (9x / 5x higher) |
  | late10_t1e-13 | 300 | 2435 | 2 | 83 min | 4.0e-7 / 3.2e-7 |
  | | 100 | 3404 | 16 | 81 min | 9.2e-7 / 2.1e-7 |
  | | 50 | 2998 | 21 | 65 min | 1.0e-6 / 2.3e-7 |

  - Limit 100: the saved 300-iteration failures are offset by extra bisection; no wall-time gain (node-to-node scatter is ~10%: identical iteration tables ran 53 vs 58 min).
  - Limit 50: 15-20% faster, but it changes the result: extra bisections add pulse steps, and the trap fill (and TeTrap relaxation) is updated per accepted solve, so the post-collapse Id depends on the step history (late24 0.5 V: 0.40 vs 0.13 mA/mm; 9x at 1 V). late10 differences are at the noise floor.
  - **Recommendation: keep `sweepIterLimit 300` (default).** A lower Newton limit is not a useful speed lever; ending sweeps at 1.5-2 V is (to 2 V the runs take 1.2-2.5 h vs 3.8-5.8 h to 4 V). Side finding worth noting: post-collapse Id is step-history dependent (up to ~10x), so curves compared against each other should use the same Vd step and limit.
- Wrap-up: dashboard Oct 13 page added (standard energy balance, ETemp trap study, Newton-limit test, HPG login, deck), overview tiles/open items/timeline updated, figure `dashboard/fig/eTempStd_IdVd.jpg`; republished https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd. `kb/current-status.md` refreshed. No jobs running. Next: fit trap position/tau with the standard energy balance to the measured collapse (Vd 0-2 V sweeps; needs Ian's OK to submit).

## 2026-10-14
- Dashboard distilled (Ian, `/impeccable distill`, scope "Overview + structure"): timeline removed (the rail lists every day), Overview open items cut to 5 live ones with the other 5 in a collapsed "Older questions" list, tiles 4 -> 3 (HPG run count dropped), shorter intro and lede, title kicker replaced by a snapshot line, coloured tile borders and uppercase mono panel labels removed. Day-page content unchanged. Republished https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd; `kb/workflow/dashboard.md` step 4 updated to the new Overview layout.
- Slide deck redesigned (Ian, `/impeccable`: "plain and generic … convey the information more clearly"; audience = advisor, presented live; takeaway = "the model now matches"; restructure freely; direction = polished conference talk). https://claude.ai/artifact/GXaJFrxHnuC97g8SzKPvjN now 14 slides: cover claim, headline result (new figure `figures/eTempStd_headline.png` from `analysis/plot_headline.py`: late set y 2.4 µm, standard ETemp, against the measured 0.4-0.5 V window; device-vs-model table), onset path 0.2 -> 3.5 -> 0.4-0.7 V, then calibration, x-y map, late onset, position map, gate bias, energy balance, tau study, run time, caveats (adds step-history), next steps, tooling as backup. White ground, Source Sans 3, blue = model / orange = measured only, claim headlines, section in every footer, speaker notes per slide. Two finish-review rounds (all material fixes resolved except slide 5's small figure labels, which would need the archived x-y map re-exported with larger fonts).
- New position-map view (Ian): `analysis/plot_posOnset.py` — x, y = trap position as before, but each position is either flat (no collapse in the sweep: shallow or off at rest) or raised to its collapse onset, height = 3.1 V − onset so the earliest collapse is the highest peak; GIF frames raise positions as Vd sweeps 0.1 → 3.0 V. Late set (0.30 eV / 5e18): 45/65 collapse by 3.0 V, earliest 0.2 V at the gate, latest 3.0 V. `figures/posMapLate_onset3d.{png,gif}`. Collapse = largest single step ≥ 50% (deep/medium) or stalled at the runaway.
- Onset view rendered for the five Oct 3 sets too (`figures/posMap_<set>_onset3d.{png,gif}`, overview `figures/posMap_onset3d_sets.png`); collapsing positions by 3.0 V: 0.30/4e18 7, 0.25/6e18 36, 0.30/5e18 45, 0.30/6e18 47, 0.40/5e18 50, 0.55/4e18 50 (of 65). Added as the Oct 14 page of the dashboard (republished https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd).
- Deck slide 7 (position maps): added the 3D onset surface (0.30 eV / 5e18, cropped copy of `figures/posMapLate_onset3d.png`) beside the onset map, with a one-line key. Kept Ian's own edits to slides 8 and 9 made in the slide editor.
- Deck: new slide 9 "Both models fill traps with hot electrons; they differ only in how the electron temperature is found" — local-field Te formula vs the energy-balance PDE side by side (physics, fit vs physical τ, onset 2.3–3.5 vs 0.4–0.7 V), plus the shared Poisson / trap-occupancy equations with the E_b(1 − T/Te) level shift and the fill-only update loop. Deck now 15 slides.
- Deck: new slide 10 comparing the first model (Sep 22–23: deep 0.78 eV acceptor blob at the gate edge, Fermi-level occupancy at the lattice T, reversible DC steady state, static mobility) with the energy-balance model (capture at Te over hotEb, fill-only pulsed sweep, calibrated mobility, shallower traps in the access region). Deck now 16 slides.
- New artifact (Ian): trap-model physics reference, https://claude.ai/artifact/4KLdks2Sd8t9zs8wb8wWJ9 — MathJax-typeset equations for Poisson/2DEG, drift-diffusion, mobility, SRH occupancy with Gauss–Hermite spread, the first model, hot-electron capture over a barrier (derivation of the E_b(1 − T/Te) level shift), fill-only memory (emission-time estimate), local-field Te (derived from the energy balance), the energy-balance PDE term by term, the sweep loop; a function reference with file:line; an interactive occupancy-vs-Te plot; 16 references (DOIs where checked). Linked from kb/workflow/repo-locations.md and kb/model/hot-electron-capture.md.

## 2026-10-14 — Deck: two trap-placement slides (16–17)
- New `analysis/plot_posSlides.py` → `figures/posSlide_lateral.png` (0.30 eV/5e18: device strip with the 65-position grid, onset vs y per depth, Id drop at 3 V) and `figures/posSlide_sets.png` (all six sets at the surface).
- Deck (https://claude.ai/artifact/GXaJFrxHnuC97g8SzKPvjN) now 18 slides: new section "Trap placement" (poslateral, possets) before the backup slide.
- Zone summary (0.30/5e18): source side none (≤100×); under gate off at rest; gate drain edge 0.2–0.3 V (~1e5×); under field plate 1.4–1.7 V but only 5–80× at 3 V; access region 1.7 → 3.0 V (20–1e8×); near drain only buried traps, 2.6–2.9 V. Why the field plate keeps the drop shallow is not checked.

## 2026-10-15 — agent-up follows the key + Duo-push login
- `~/bin/agent-up` (Ian's start-up script, outside the repo) updated to the Oct 13 login rules. It opens `ssh -MN hpg` without askpass, answers the Duo menu with 1 (push) and waits 2 min for approval, then makes sure the login7 tmux session `hemtrad` exists. On a password prompt it stops and leaves it to Ian (it never handles the password). Old copy in the session scratchpad. Syntax and prompt detection checked; not run end to end (it would trigger a Duo push).
- KB: `kb/workflow/hpg-workflow.md` (agent-up paragraph), `kb/workflow/repo-locations.md` (row).

## 2026-10-15 — HPG reconnect failed before reaching HPG
- Ian: "connect to hpg". `ssh -O check hpg`: master down. Ran `bin/hpg_reconnect.sh` once: exit 1, "no server running" — this Claude session is not inside tmux and no tmux server exists, so the script's `tmux new-window` failed and **no ssh / Duo push was attempted**. Not retrying (one-attempt rule); waiting for Ian. Script fix to consider: fall back to `tmux new-session -d` when no server is running.
- Retry (Ian: "retry"): `bin/hpg_reconnect.sh` now opens its own detached tmux session when no tmux server is running. Second attempt: Duo push approved, master up (pid 14353). No jobs queued; login7 tmux `hemtrad` still alive.

## 2026-10-15 — Gate-bias dependence: measured collapse comes LATER at more positive Vg
- Ian: new info says the measured collapse moves **later** as Vg becomes more positive, the opposite of the Oct 3 local-field result ([[gate-bias]]). Asked to explore (A) whether our model can explain it and (B) alternative models, each exploratory model in its own git worktree. Ian is on another project until ~12:30 and approved sbatch for these HPG runs; local runs cancelled (machine needed elsewhere).
- (A) Energy-balance model vs Vg (never tested; Oct 3 used the local-field Te): `sweeps/params_vgEB.txt` (late set y 2.4 µm τ 1 / 0.1 ps and y 1.0 µm τ 1 ps at Vg −1 and 0 V, Vd 0–1.5 V; trap-free Te profiles at Vg −2/−1/0). Vg −2 references: job 45768739.
- (B) Worktrees `~/HEMTRAD-wt/field-capture` (branch `explore/field-capture`: `capMode field`, barrier lowered by the local field, Poole–Frenkel-like, `capField lat|tot|qfn`, `capBeta`; plus a `fieldProfile` dump lever) and `~/HEMTRAD-wt/gate-injection` (branch `explore/gate-injection`: `capMode gate`, virtual gate: supply set by the peak lateral field at the gate drain edge, decaying along the surface with `injLen`). Default `capMode hot` = unchanged. `sweeps/pulsedIV_eTemp.slurm` now takes `REPO` from the environment so it can run from an HPG worktree.
- Submitted (Ian approved): **46040979** (main, `params_vgEB.txt`, 9 tasks, `results/20261015_vgEB/`), **46040980** (HPG worktree `HEMTRAD-wt/field-capture`, `params_fieldCap.txt`, 18 tasks: trap-free field profiles at Vg −2/−1/0, then trap at surface y 0.2/0.5 µm × capBeta 2.46e-4/1e-3/3e-3 × Vg −2/−1/0, Vd 0–2 V), **46040981** (`HEMTRAD-wt/gate-injection`, `params_gateInj.txt`, 12 tasks: trap y 1.0 µm, capBeta 1e-3/3e-3 × injLen 0.5/1.5 µm × Vg). HPG worktrees created with `git worktree add` from the pushed branches (no file edits). Polling every 5 min.
- 46040981 failed at once ("computed an infinite in a data field": `-(a)^2` in the gate-edge window parsed as `(-a)^2`); fixed (e97c1fe) and resubmitted as **46042673**; failed output in `results/20261015_gateInj_failed/` on HPG. Early field-capture result: capBeta 3e-3 at y 0.2 µm is off at rest at every Vg (too strong).
- Round 1 field models (46040980, 46042673): **Poole–Frenkel √F capture fills the traps at rest** in every variant that traps at all. The gate-edge field at rest is already set by Vg (mid-barrier lateral field at y 0.14 µm: 1.35e5 / 5.8e4 / 1.6e4 V/cm at Vg −2/−1/0, and Vd 0.5 V adds only ~10%), so those devices are throttled from Vd = 0 (e.g. capBeta 3e-3, injLen 1.5: Id 1e-8 / 1e-4 / 1 mA/mm at Vg −2/−1/0) instead of collapsing mid-sweep. Direction right (more negative Vg = more trapping), threshold far too soft. Weaker settings: no collapse to 2 V.
- Round 2: Fowler–Nordheim-type law (`capForm fn`: level shift kT·capF0·(1/capFth − 1/F), ≥ 0, i.e. tunnelling rate ∝ exp(−F0/F)) in both branches. Submitted **46046389** (gate injection, `params_gateInjFN.txt`, 15 tasks: trap y 1.0 µm × capFth 1.3e5/1.4e5 × capF0 5e6/2e7 × Vg, plus y 2.4 µm; injLen 1.5, Vd 0–4 V) and **46046442** (local field, `params_fieldCapFN.txt`, 12 tasks: trap y 0.2 µm, capFth 1.4e5/1.5e5 × capF0 5e6/2e7 × Vg, Vd 0–4 V).
- Gate-edge field probe (46048098, gate-injection branch; peak |dPsi/dy| near the AlGaN top at the gate drain edge): rest 2.9e5 / 1.2e5 / 4e4 V/cm at Vg −2/−1/0, +~6e3 per 0.1 V of Vd at −2 and −1 (falls at first at 0). FN gate injection (46046389, 46048098) gives the right Vg ordering but **no sharp collapse**: charge at y 1.0 µm barely changes the gate-edge field, so there is no runaway; it either throttles from rest (Fth ≤ 2.5e5) or trims Id ~10% (Fth 3.0e5). FN local-field capture with a 40 nm blob at y 0.2 µm (46046442): no collapse at Vg −2 to 4 V.
- Energy balance, trap-free (46040979): at Vd 0.4 V, Te in the access region (y 2.4 µm) is **304 / 306 / 307 K** at Vg −2/−1/0 (no Vg dependence), at the gate drain edge (y 0.14) **346 / 314 / 309 K**. So access-region traps stay current-driven with the EB too (late24 τ 0.1 ps: onset 0.6 V at Vg −1 vs 0.7 V at −2), but **gate-edge traps should collapse later at higher Vg** within the present model. Submitted **46052606** (`params_vgEBgate.txt`, 12 EB tasks: traps at y 0.2/0.3 µm, 4e18/5e18, 0.30 eV, Vg −2/−1/0, Vd 0–1.5 V).
- Submitted **46052532** (field-capture branch, `params_virtGate.txt`, 10 tasks): "virtual gate" = thin surface trap sheet (σx 5 nm, σy 0.8 µm at y 1.2 µm), FN local lateral-field capture, level 0/0.15 eV, peak 1e19/2e19, hotEb 2.0, Vg −2/0, Vd 0–4 V. Idea: filled traps extend the depletion, moving the field peak outward = feedback.
- **Virtual gate works qualitatively** (46052532, field-capture branch): surface sheet 0.15 eV, peak 2e19 (~1.2e13 cm⁻²), FN lateral-field capture, Fth 1.4e5: at **Vg −2 Id 13 → 21 → 19 → 5.3 → 0.0019 → 7e-9 mA/mm at Vd 0.1–0.6 V** (sharp collapse at 0.4–0.5 V); at **Vg 0 no collapse to ≥ 3.2 V**. Fth 1.6e5: Vg −2 onset 0.7–0.8 V; Vg 0 none to ≥ 3.2 V. Level 0.0 eV: onset 0.5 V. Peak 1e19: no collapse. Pre-collapse Id is already ~40% low at Vg −2 (21 vs 34 mA/mm at 0.2 V). Submitted **46054851** (Vg −1.5/−1/−0.5 for both Fth) for onset vs Vg.
- EB late set, same runs (46040979): late24 τ 1 ps collapses at **0.3 V at Vg −1 and 0** (as at −2); late10 at 0 V also 0.3 V. Access-region hot-electron traps do not give the measured Vg trend.
- 11:10 Write-up: `kb/results/vg-dependence.md` (new), links from index, gate-bias, field-driven-trapping, current-status, repo-locations; figures `figures/vgOnset_virtGate.png`, `figures/vgOnset_EB.png` (`analysis/plot_vgOnset.py`). Virtual gate onset vs Vg (Fth 1.4e5): 0.5 V at −2 and −1.5, none at −1, −0.5, 0 (to 1.8–4 V). Submitted **46057777** (softer capF0 5e6/1e7, capFth 1.2e5, Vg −2…0 in 0.5 V steps) to test for a gradual shift. Still running: 46040979 (EB vs Vg, slow), 46052606 (EB gate-edge traps, slow), 46046442 (2 tasks).
- FANGS campaign: folder pushed by Ian (5c72bb3; da19408 also carried a stray dashboard JPG, removed in a826359). Pulled on HPG; `make_bundle.sh` → HPG checkout 28d8af2b. Build job **46060195** (Ian approved; 8 CPUs, ≤ 4 h, ee1-b). Next: read `results/logs/build-46060195.out`, then ask about the tier array.
- Vg study: softer FN (46057777, capF0 1e7/5e6, capFth 1.2e5) loses the sharp collapse: Vg −2 saturates at ~50–58 mA/mm (no step), Vg −1.5 a soft 74 → 53 dip at 1.0–1.2 V, Vg ≥ −1 normal. capF0 2e7 is needed for the sharp step.
- FANGS build 46060195 **failed at configure** (both builds, 4 min): the conda env (created fine, conda-forge reachable from the compute node) got **Eigen 5.0.1**, and flooxs-pyplot's `CMakeLists.txt:52` asks `find_package(Eigen3 3.4)`, which Eigen 5's config rejects. So make, selftest (`No module named 'fangs._core'`) and ctest (0 tests, rc 0) did nothing. Not a flooxs-pyplot code problem; its HPG runbook's conda route needs `eigen=3.4` pinned. Waiting for Ian: pin eigen 3.4 (install into the existing env on login7, `env.sh` spec updated) and resubmit?
- Ian: pin eigen 3.4. `env.sh` spec now `eigen=3.4` (4f6aa86); installed eigen 3.4.0 into the existing env on login7 (conda only). Build resubmitted as **46062866**.
- FANGS build 46062866: configure OK with Eigen 3.4; **Tcl-free build fails to compile**: `src/python/core.cc:740/745` call `Py_IsFinalizing()`, public C API only since Python 3.13 (added in flooxs-pyplot e53fbcea). The workstation builds with Python 3.14; flooxs-pyplot's `docs/runbooks/hipergator-setup.md:73` (and so `env.sh`) pins python=3.12. Reported to Ian (runbook vs code mismatch); job left to finish the Tcl build + ctest.
- Ian: Python 3.13. `env.sh` python=3.13 (pushed); env upgraded on login7 (Python 3.13.16, nanobind 3.1.0, eigen 3.4.0); stale build/ and build-tcl/ removed (CMake caches pointed at 3.12; 46062866 ended with ctest 4/86 and 81/165 passing since nothing built). Build resubmitted as **46064444**.
- Vg study (A): EB with gate-edge traps (46052606, y 0.2/0.3 µm, 4e18/5e18): all collapse at 0.3–0.4 V at Vg −2, −1 and 0. The present hot-electron model gives no later onset at higher Vg for any trap position tried. KB updated.
- FANGS build **46064444** (Python 3.13.16, Eigen 3.4.0, HDF5 2.2.0, GCC from conda, hpg-milan EPYC 75F3): cmake/make rc 0 for both builds, **selftest rc 0**, `fangs._core` imports. **ctest: `build` 5/86 passed, `build-tcl` 81/165 passed** (expected all except Regression-Fast*). Failures:
  - 77 `Py-*` deck tests in both builds (+ Python-Tests, Python-EndToEnd, Regression-Fast(-Py), the unittest `test_procs_end_to_end` and `test_gaps` goldens): the Python side of `tools/deck_compare.py` exits 1 in ~0.1 s, "trace not written"; the deck's own error is not in the log (run dirs were in the node's /tmp).
  - `Native-Cmd` (12) and `Expr-Diff`: `erfc(26.6…27.2)`: the reference corpus says ERR (underflow), conda's libm/libtcl return a subnormal/0. Platform libm difference.
  - `TDR-Read`, `TDR-Diff` (build-tcl): fail in 0.2 s with no output; probably HDF5 2.2.0 (conda-forge's new major) vs what flooxs-pyplot was written against.
  - STRUMPACK tests not registered, as expected.
- **Stopped per the README** (any failure other than Regression-Fast* → report). Tier array not requested. Waiting for Ian / the flooxs-pyplot session.
- Ian: hand FANGS to flooxs-pyplot. Raw logs copied (rsync, no manifest) to `~/flooxs-pyplot/Test/Regression/hpg_results/20261015-fangs/` (gitignored there) with a handoff `REPORT.md`; message sent to the "FANGS Development" session. HPG folder `fangs-hpg-20261015/` left in place until Ian says to delete it (cleanup.sh needs a manifest, so removal would be by hand).
- FANGS session reply: Py-* / EndToEnd / Regression-Fast fail because `tools/capped.sh` calls `systemd-run --user` (absent in SLURM); test_gaps goldens because the optimizer sees SLURM_JOB_ID; erfc is a glibc ERANGE difference; runbook to pin eigen 3.4. Fixes coming in flooxs-pyplot. TDR: post-mortem gdb on login7 (no run) of 2 core files in build-tcl/: `test_tdr_write` SIGSEGV in `regionVertices` (its own code; both builds link the same libhdf5 2.2.0); sent back. Keep `fangs-hpg-20261015/`; rerun from step 1 with the new COMMIT when Ian says.
- **FANGS campaign ON HOLD** (Ian): keep `fangs-hpg-20261015/` (env reused). Fix commit coming from flooxs-pyplot (capped.sh without systemd in SLURM, optimizer goldens vs SLURM_JOB_ID, erfc underflow tolerance, TDR writer memory bug). When Ian gives the new hash: (1) rename `$BASE/results` → `results-run1` on HPG and `~/flooxs-pyplot/Test/Regression/hpg_results/20261015-fangs` → `20261015-fangs-run1`; (2) `COMMIT=<hash>` in `fangs-hpg-tests/config.env` (TAG unchanged), commit, push, pull on HPG; (3) `make_bundle.sh`, then build job (ask before sbatch), expect ctest 86/86 and 165/165 (only Regression-Fast* may show rounding-level deviations); remove the two `build-tcl/core.test_tdr_write*` files before the rebuild; (4) if clean: tier array + compare (ask before sbatch), fetch, report.

## 2026-10-15 — FANGS HPG campaign rerun at flooxs-pyplot 92b55cee
- Ian's rerun plan, step 1: run-1 results renamed (HPG `fangs-hpg-20261015/results-run1`, workstation `hpg_results/20261015-fangs-run1`); the two `build-tcl/core.test_tdr_write-*` files deleted.
- `fangs-hpg-tests/config.env`: COMMIT=92b55cee (TAG unchanged, env reused: python 3.13, eigen 3.4). Next: make_bundle.sh, then the build job (waiting on Ian's OK for sbatch).
- make_bundle.sh failed on the rerun (fetch used a bundle path relative to the checkout); fixed in d504b24, rerun ends "HPG checkout: 92b55cee". **Waiting on Ian's OK to sbatch the build job** (`submit.sh build`, 8 CPUs, ~1-2 h).
- Build job **46081205** submitted (Ian OK) at 92b55cee. Expect both builds rc 0, selftest rc 0, ctest 86/86 and 165/165.
- Build job 46081205 done (33 min): builds rc 0, selftest rc 0. **ctest build 83/86, build-tcl 164/165** (run 1: 5/86, 81/165). TDR, erfc and goldens are fixed. Remaining failures:
  - Regression-Fast and Regression-Fast-Py: not rounding. The fast-tier children run under the system conda Python 3.14 (`/apps/conda/26.7`), not the env's 3.13, so `fangs._core` isn't found.
  - Py-POD-Speed-Test (build only): sign flip of a 3e-10 POD mode coefficient in the trace.
  - Py-Device-Failed-Build (build only): all 10 .str output files differ.
  Stopped before the tier array (per Ian's rule). Logs are in `~/flooxs-pyplot/Test/Regression/hpg_results/20261015-fangs/`; sent to the FANGS Development session. Waiting for a fixed commit.
- FANGS Development session: all three causes are fixed in flooxs-pyplot (verification running, ~40 min).
  - Regression-Fast*: ctest used FindPython3's interpreter (it found the system 3.14), not `Python_EXECUTABLE`. Needs a fresh cmake configure, which build.slurm does.
  - POD: the LAPACK `dsyev` eigenvector sign is now fixed.
  - Device-Failed-Build: the scratch .str files that depend on BLAS are now deleted.
  Next, when Ian gives the commit: rename `results` → `results-run2` and the workstation folder → `20261015-fangs-run2`, set COMMIT, rebundle, build job (ask Ian before sbatch).
- **FANGS rerun 3 at flooxs-pyplot 2de5aaee** (Ian): run 2 kept as `results-run2` / `20261015-fangs-run2`; config.env COMMIT=2de5aaee. Next: bundle, then build job (ask Ian).
- Rerun 3 bundle OK (HPG checkout 2de5aaee). Build job **46085435** submitted (Ian OK).
- FANGS session: 25a10277 (one commit after 2de5aaee) adds a ctest RESOURCE_LOCK to the Tcl mesh tests (scratch-file race under ctest -j). Local verification of 2de5aaee passed, so nothing to cancel; 46085435 continues at 2de5aaee. A lone Mesh-* failure would be that race; Ian decides whether it stops the campaign.
- Ian: a lone Mesh-* ctest failure does not stop the campaign. Until 18:30 today, work with the FANGS Development session without asking (campaign sbatches for this task approved).
- Build job 46085435 done (52 min, on an EPYC 7702 node under heavy load, so tests ran 1.4-4x slower than run 2): builds rc 0, selftest rc 0, **ctest build 86/86, build-tcl 165/165**. Submitted the tier array **46090409** (23 tasks, %6, hpg-milan) and compare **46090410** (afterany). Next: fetch, REPORT.md, notify.
- **FANGS rerun 3 done.** Tier 46090409: 23/23 RC=0, no OOM/timeouts/cores. Compare 46090410:
  - tcl-vs-dag 0 deviation 7/7; py-vs-tcl 0 deviation 7/7; thr4v identical, all VERIFY `diffs=0`.
  - vs the Oct 8 Intel baseline, only gan_quickIV is ok. The other 6 FAIL at rtol 1e-6 with small deviations: 2.6e-6 to 1e-4 relative, calibIdVg 1e-6 absolute on a near-zero value. They are identical for Tcl, Python and DAG, so platform/compiler.
  - Fetched; all 520 data files match the manifest. Fixed the manifest self-hash in compare/fetch/cleanup.
  - Report: `~/flooxs-pyplot/Test/Regression/hpg_results/20261015-fangs/REPORT.md`. HPG copy kept; waiting for Ian on deletion.
- FANGS Development accepted run 3 (D1 HPG item met; first HPG run of the Python ports). It reads the 6 baseline deviations as toolchain-only (calibIdVg: the sub-threshold floor, ~1e-8 mA/mm). flooxs-pyplot 49ae8de8 adds per-case tolerances; recomputed on the fetched results, 7/7 are ok for tcl, py and dag. Nothing more to run. Waiting for Ian on deleting the HPG folder and archiving `fangs-hpg-tests/`.
- **FANGS clean-up (Ian approved here):**
  - The fetched results check refused at first: the flooxs-pyplot session had recomputed 6 regress reports (`{py,tcl,tcl-dag}/report.{json,md}`) after the fetch. Their HPG originals are now saved in `20261015-fangs/hpg-original/` and match the manifest, and `cleanup.sh` accepts a file there.
  - `cleanup.sh --yes` deleted HPG `fangs-hpg-20261015/` (4.6 GB) and the workstation bundle.
  - Also deleted the old HPG checkout `blue/.../flooxs-pyplot` (da619c4c, 181 MB): no jobs or scripts used it, and Ian confirmed.
  - `fangs-hpg-tests/` moved to `archive/fangs-hpg-tests/`.
  - Still on HPG, untouched: `gan_regress_results/` and `blue/.../flooxs-pyplot.bundle` (the Oct 8 bundle).
- Ian: "remove anything related to flooxs-pyplot". Deleted on HPG: `gan_regress_results/` (2.2 MB, Oct 8 run) and `flooxs-pyplot.bundle` (131 MB, da619c4c). The 163 Oct 8 result files already matched the workstation copy; the 27 build/ctest/smoke scripts and logs were first saved to `hpg_results/20261008/hpg-setup/` and verified. Nothing from flooxs-pyplot is left on HPG (no conda env or job used it).

## 2026-10-15 evening: Vg study, final results of the remaining jobs
- 46040979 (EB vs Vg) done: τ 0.1 ps onset 0.7 V at Vg −1 and 0.6 V at Vg 0 (earlier note said 0.6 at −1; corrected), τ 1 ps 0.3 V at −1 and 0. No later onset at higher Vg.
- 46052606 (EB gate-edge traps) done: 4e18 → 0.4 V, 5e18 → 0.3 V at every Vg; task 1 (y 0.2, 4e18, Vg −1) hit the 6 h limit at Vd 1.4 V, after its collapse.
- 46054851 (virtual gate) done: Vg −1 (Fth 1.4e5) and Vg −1.5 (Fth 1.6e5) both drop by ~20% at 3.5–3.6 V, then `PULSED GAVE UP` at 3.7 V, so the late collapse is unresolved. The others run normally to 4 V.
- Conclusion unchanged: within the present model, nothing gives a later onset at higher Vg; the virtual gate gives the right ordering, but with a switch-like shift.
- Submitted **46106674** (Ian OK; branch `explore/field-capture` 6d1bcfa, `params_virtGate4.txt`, run `20261015_virtGate4`, 4 tasks). Virtual gate (same physics as 46054851: surface sheet 0.15 eV, 2e19, FN lat capF0 2e7), solver-side only: Vd_step 0.05, retryDepth 7, teRampMin 5e-4, Vd to 4.2 V. Tasks: Fth 1.4e5 at Vg −1, −1.25, −1.75; Fth 1.6e5 at Vg −1.5. Purpose: resolve the 3.7 V give-ups and map onset vs Vg (gradual or switch-like). Note: params.json records Vd_step 0.1 from the template; the deck's extra lines override it to 0.05.
- 21:00 Virtual-gate onset map (46106674, 3 of 4 tasks done): Fth 1.4e5 onsets 0.25 V (Vg −1.75), ~3.8 V (−1.25, 334 → 130, then gave up at 3.85 V), ~4.1 V (−1, 377 → 328, gave up at 4.2 V). Late drops depend on the Vd step (Vg −1: 3.6 V at 0.1 V steps vs 4.1 V at 0.05 V). Figure `figures/vgOnset_virtGate4.png`. Task 1 (Fth 1.6e5, Vg −1.5) still running at 3.85 V. Next: check whether trap occupation carries over between Vd points (step-history dependence) before trusting late onsets; compare with the new measured onset-vs-Vg data.
- Wrap-up: dashboard Oct 15 page + Overview updated and republished (https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd); current-status refreshed.
- HPG connection closed at Ian's request (`ssh -O exit hpg`); the background check on 46106674 was stopped first. Task 1 (Fth 1.6e5, Vg −1.5) keeps running on HPG; pick up its results after the next reconnect.

## 2026-10-16
- HPG reconnected (Duo push; bin/hpg_reconnect.sh, one attempt).
- 46106674 complete: task 1 (Fth 1.6e5, Vg −1.5, Vd step 0.05) runs to 273 mA/mm at 3.7 V, drops to 258 at 3.85 V, then `PULSED GAVE UP` at 3.9 V (2 h 52 min). No cores. So all three late drops (Vg −1.25, −1, and −1.5 at Fth 1.6e5) end in a solver give-up within 1–3 steps, with the drop position shifted by the Vd step. Next (proposed): find out why the late onset depends on the step (trap occupation carried between Vd points?) before mapping more.
- Read `drivers/pulsedIV.tcl` + `model/Poisson.tcl` (field-capture branch) to explain the step-dependent late onset. Fill-only ratchet: each point = 4 × (UpdateTe w 0.5 → device → CaptureTraps), charge = max(TrapFrozen, live). The first UpdateTe at a new Vd sees the field from the previous point's charge, which is too high near the threshold, and the ratchet keeps that charge. So bigger steps capture more, and the steep FN form (~6 kT per 0.1 V near Fth) magnifies it. Data: 0.1 vs 0.05 V steps agree to <0.03% up to 3.2–3.4 V, then diverge (Vg −1: 279 vs 368 mA/mm at 3.6 V). Late onsets are not converged in Vd step. **Proposed to Ian:** step-convergence test (0.05/fillIters 2 vs 0.1/4, plus 0.025) and/or a per-point self-consistency option (modelling decision). Details in `kb/results/vg-dependence.md`.
- **fillConv (Ian chose fix 2).** Branch `explore/field-capture` a45d349: new lever `fillConv` (default 0 = old behaviour), with `fillTol` 0.01 and `fillMaxIters` 100. `FillConverge` in `model/Poisson.tcl` relaxes TeTrap (w 0.5) and re-solves **without capturing in between**, then captures once when max |TeTarget − TeTrap|/TeTrap over GaN+AlGaN < fillTol. It removes both the fixed-round lag and the stale-field ratchet overshoot. TeRampPoint is unchanged (it still captures each sub-step).
- Submitted **46209709** (Ian OK; `params_virtGate5.txt`, run `20261016_virtGate5`, 6 tasks, `--time=12:00:00`): Fth 1.4e5 virtual gate, fillConv 1, retryDepth 7, teRampMin 5e-4, Vd to 4.2 V. Vg −2 and −1.5 at 0.1 V steps (early onsets should stay ~0.5 V); Vg −1.25 and −1 at 0.1 and 0.05 V steps (step convergence of the late onset).
- **Decision (Ian): back to the local-field hot-electron model (`eTemp 0`) as the standard, to save computation time.** No code change: `eTemp 0` is already the model-file default, and the virtual-gate runs (incl. 46209709) already use it. New sweeps set `eTemp 0` explicitly. The energy balance stays available (`eTemp 1`, `etStats 0`, `etThermo 0`). KB: current-status, energy-balance.
- Side-by-side code page for Ian's meeting: https://claude.ai/artifact/H3koCnAHa3Yw3yaVSujCGu (now original vs local field, at Ian's request; energy-balance column and "What runs today" block removed).
- 12:40 HPG reconnected (Duo push). The early-check loop had been stuck on the dropped connection, so I stopped it.
- **fillConv test 46209709, status after 1 h 50 min:**
  - Tasks 0 and 1 (Vg −2, −1.5) failed at the very first point. At Vd = 0, FillConverge ran 100 rounds without converging (mismatch 55, i.e. 5500%). The Vd = 0.1 step then gave NaN at every bisection level and the Te ramp failed too, so `PULSED GAVE UP at Vd=0.1` (completed, 56–69 min, no cores). Likely cause (not yet checked with a field dump): without the in-between captures, the live trap charge follows TeTrap both ways. Locally, filling lowers the field, which lowers the target, which empties the traps again, so the w 0.5 relaxation oscillates where the gate-edge field at rest (~2.9e5 V/cm) is above capFth.
  - Tasks 2–5 (Vg −1.25 and −1 at 0.1 and 0.05 V) still running at Vd 2.35–3.2 V. Id is identical to the old runs (e.g. 254 mA/mm at 2.0 V). The median is 5–12 rounds per point, but 9–19 points hit the 100-round limit without converging.
  - Note: the convergence test is the max over all of GaN+AlGaN, including trap-free regions where TeTrap does not matter.
  - Next (proposed to Ian): measure convergence on the trapped charge (weighted by trap density) instead of TeTrap everywhere, and use a smaller relaxation w in FillConverge (e.g. 0.2) to damp the oscillation.
- **fillConv revised** (Ian OK; branch 9eb63fd). Convergence is now judged on the trapped charge: `ChargeMismatch` = max |IonAcceptor(TeTrap → target) − IonAcceptor| / trapPeak over GaN+AlGaN, at the present solution, so trap-free regions don't count. Defaults `fillTol` 1e-3, new `fillW` 0.2 (relaxation inside FillConverge), `fillMaxIters` 100. The old TeTrap test is removed.
- Submitted **46224198** (Ian OK; `params_virtGate6.txt`, run `20261016_virtGate6`, 4 tasks, 12 h): Vg −2, −1.5 and −1 at 0.1 V steps, and Vg −1 at 0.05 V. 46209709 tasks 2–5 keep running with the first version (task copies of the model files are unaffected).

## 2026-10-16 — HighK vs SiN field check, rerun with field mobility (ready, not submitted)
- Ian asked to rerun the Oct 1 field measurements (static mobility) with the field-dependent mobility. New `drivers/fieldPlate.tcl` (port of `archive/static_mobility/fieldPlateTest.tcl`: modelDir lookup, `mobModel field`, `eTemp 0`, store/restore bisection on failure) and `sweeps/fieldPlate.slurm` (2 tasks: HighK, SiN; Vg −2, Vd 0.5–20 V / 0.5 V; cuts at 3/10/20 V) → `results/20261016_fieldPlate/`.
- Waiting: the HPG `git pull` + `sbatch` were blocked by the session's permission classifier; needs Ian to allow it or run `sbatch sweeps/fieldPlate.slurm` from the HPG repo root after `git pull`.
- Submitted: job **46241088** (2 tasks, HighK / SiN, `ee1-b`), `results/20261016_fieldPlate/`. Next: check both logs (FP DONE / GAVE UP), rsync, redo the HighK-vs-SiN figure with field mobility and update the slide-2 numbers and `kb/results/highk-vs-sin.md`.
- **Job 46241088 done** (both tasks COMPLETED, 40/40 Vd points, no retries, ~7 min). Field mobility gives the same picture as Oct 1: gate-edge peak unchanged by HighK (≤2%; 305 kV/cm at 3 V), T-gate-head/field-plate peak 183 → 117 kV/cm at 10 V (−36%) and 403 → 193 at 20 V (−52%), field spread toward the drain at 20 V (8 → 138 kV/cm at y = 1 µm). Slide-2 figure redrawn (`figures/fieldSlide_highk.png`), deck https://claude.ai/artifact/W5YiXYBDygEsnzCqu2TWQX updated; KB `highk-vs-sin` updated.

## 2026-10-17 — HPG reconnected; fillConv jobs 46209709 / 46224198 finished

- HPG master had dropped (poll bdm3v6w8b lost it); `bin/hpg_reconnect.sh` succeeded on the first push.
- Both jobs ran to the end (branch `explore/field-capture`, logs `HEMTRAD-wt/field-capture/results/eTemp_logs/`).
- **46224198 (revised FillConverge, ChargeMismatch, fillTol 1e-3):**
  - Vg −2 (task 0): Id 4e-10 mA/mm at Vd 0.1, then PULSED GAVE UP at 0.2. It gets one step further than 46209709 (which died at 0.1) but is off from the first step, not a late onset.
  - Vg −1.5 (task 1): already 2e-8 mA/mm at 0.1 V, climbs erratically to 0.06 at 1.4 V, then jumps between 1e-7 and 1e-4 and gives up at 3.2 V. No clean onset.
  - Vg −1 (tasks 2 and 3, 0.1 and 0.05 V steps): no collapse up to 4.2 V, 380 mA/mm, identical at both steps. FillConverge hit its 100-round cap 17 and 30 times.
- **46209709 (first version):** Vg −2 and −1.5 gave up at 0.1 V. The other four tasks have no collapse up to 3.6–4.2 V (331–380 mA/mm).
- Verdict: fillConv does not give the measured late onset (~0.4–0.5 V at Vg −2). Low Vg is off from the start, Vg −1 never collapses, and in between it is noisy. Next: compare against the measured onset-vs-Vg data, then decide whether to drop or rework the fillConv lever (Ian's call).

## 2026-10-17 — Trap-model sensitivity sweep ready, submit blocked by auto mode

- Ian asked for a one-at-a-time sensitivity sweep of every trap-model lever, with the Gaussian and its placement fixed.
- **Baseline:** late set at y = 1.0 µm, round 3, deep collapse at 2.3 V.
  - Fixed Gaussian: trapPeak 5e18, trapSigma 0.04, trapMeanX 0, trapMeanY 1.0.
  - Trap and capture levers: trapLevel 0.30, trapWidth 0.1, hotEb 1.0, hotTau 1e-14, hotMu 600, hotVsat 1.9e7.
  - Fill: fillIters 4, fillRelax 0.5.
  - Sweep: eTemp 0, field mobility, Vg −2, Vd 0–4 V in 0.1 V steps.
- **Varied, one lever per task:**
  - trapLevel {0.20, 0.25, 0.35, 0.40, 0.50}
  - trapWidth {0.02, 0.05, 0.2, 0.3}
  - hotEb {0.5, 0.75, 1.25, 1.5}
  - hotTau {5e-15, 7e-15, 1.5e-14, 2e-14, 3e-14}
  - hotMu {300, 450, 900, 1200}
  - hotVsat {1e7, 1.5e7, 2.5e7, 3e7}
  - fillIters {1, 2, 8}
  - fillRelax {0.25, 0.75, 1.0}
- **Tasks:** 32 lever tasks + baseline + trap-free = 34.
  - Files: `sweeps/pulsedIV_sensitivity.slurm`, `sweeps/params_sensitivity.txt` (c3d9403); run dir `results/20261017_sensitivity`.
  - Analysis: `analysis/plot_sensitivity.py`. It plots onset, Id drop at 4 V and the pre-collapse ratio per lever, plus Id–Vd per lever. Tested on synthetic data.
- **Blocked:** `sbatch` was denied by the auto-mode classifier ("Shared Cluster Mutation").
- **Submitted** at Ian's explicit request: **job 46462234** (34 tasks). Polling every 5 min.
- **Done (46462234):** all 34 tasks completed to 4 V, no give-ups, errors or cores; rsynced to `results/20261017_sensitivity/`.
  - The baseline reproduces round 3: deep collapse at 2.3 V, down 1.85e4×, then a recovery to 23× by 4 V.
  - Onset ranges: trapLevel 0.30→0.50 moves it 2.3→0.4 V, and ≤ 0.25 eV gives no collapse. hotEb 0.75→1.5: 3.2→1.6 V (0.5 none). hotTau 7e-15→3e-14: 3.3→1.1 V (5e-15 none). hotVsat 1e7→3e7: 3.6→1.9 V. hotMu 300→1200: 3.2→1.8 V. trapWidth 2.6→2.0 V; fillIters 2.8→2.2 V; fillRelax 2.5→2.2 V.
  - Depth follows trapLevel, hotEb and hotTau (up to 3e11×).
  - Figures: `figures/sensitivity.png`, `figures/sensitivity_IdVd.png`. KB: [[trap-sensitivity]].
- Next: Ian to review. One option is a second one-at-a-time pass around a baseline nearer the measured onset (e.g. level 0.45–0.5 or hotTau 3e-14), since this baseline sits just above the capture threshold.

## 2026-10-17 — Wrap-up
- Dashboard: Oct 16–17 page added (lever sweep, fillConv verdict, HighK field check), Overview refreshed (snapshot Oct 17, tiles, open items; energy-balance fit moved to older questions as parked). Published v11 to https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd.
- KB: current-status (fillConv verdict, next steps), vg-dependence (converged-fill section).
- No jobs running. Waiting on Ian: second lever pass around a baseline nearer the measured onset? keep/drop fillConv? measured onset-vs-Vg numbers.

## 2026-10-21 — Softer virtual-gate capture (job 46057777) read
- HPG reconnected (one Duo push). 46057777 (`params_virtGate3.txt`, Fth 1.2e5, capF0 5e6 / 1e7, Vg −2 … 0): all 10 tasks done to 4 V.
- capF0 5e6: no collapse at any Vg; only a 10–18% lower Id at Vg −2.
- capF0 1e7: soft knee at Vg −2 (flat 45–59 mA/mm from 0.4 V, creeping) and at −1.5 (73.8 → 52.8 mA/mm at 0.8–1.3 V, then creep back to 71.7); Vg ≥ −1 unaffected.
- So softer capture gives a gradual knee with creep and the right Vg ordering, but only ≤ 1.4× deep (measured ~1000×). KB [[vg-dependence]] updated.
- Measured onset-vs-Vg data still pending at another lab (Ian). Proposed next: time-limited (pulse-integrated) capture instead of fixed fill rounds — needs Ian's OK and the curve-tracer pulse width/period.
- **PARKED (Ian, 2026-10-21): time-limited (pulse-integrated) capture.** Waiting for the curve-tracer pulse width/period and the measured onset-vs-Vg data (another lab). Pick up: new worktree, per-Vd capture Δn = (n_eq − n)(1 − exp(−t_pulse/τ_c)) with τ_c from the existing capture law, default off; sweep t_pulse if the instrument values are still unknown.

## 2026-10-21 — GaN decks exported to flooxs-pyplot for the Python port
- Ian asked for the GaN decks we've been running, with numerical references, in a flooxs-pyplot folder, so the FANGS agent can translate and test them.
- `~/flooxs-pyplot/Test/SimpDev/GaNSuite_HEMTRAD_20261021/` (untracked, not committed in flooxs-pyplot): 10 self-contained task folders (model files flat, CRLF kept, `*_task.tcl` driver, `params.json`, `reference/` outputs + SLURM logs where available), `reference_summary.csv`, `measured/`, README.
- Cases:
  - trap-free Id–Vd at Vg −2 and 0;
  - late set at y 1.0 (Vg −2 and 0) and trapLevel 0.50;
  - field plate HighK/SiN to 20 V;
  - energy balance trap-free and late set y 2.4 τ 1 ps;
  - calibIdVg at Vds 10 V.
- Source jobs: 46462234, 44573629, 46241088, 46040979, 45768739, Oct 1 calibration.
- All but the two Oct 3 Vg 0 cases match main 580cf5f model files.

## 2026-10-21 — TRIM (SRIM-2013) installed on the workstation
- SRIM-2013-Pro from srim.org, extracted with 7z, in its own Wine prefix `~/.wine-srim` (VB5 runtime and 5 OCX controls registered). HPG has no SRIM.
- `bin/trim_run.sh <TRIM.IN> <out_dir>` runs TRIM in batch mode (TRIMAUTO 1) and collects the outputs. Tested on the bundled example (200 ions, 54 s) and `drivers/trim/TRIM_HEMT_template.IN` (HfO2/Si3N4/AlGaN/GaN stack, 20-ion placeholder Au ion, 6 s).
- Waiting on Ian: ion species/energy/fluence (with the experimental data). Before production runs, review the displacement energies (template uses SRIM-style defaults). KB [[trim]].

## 2026-10-21 — HighK vs SiN deck with traps at Vg +1, Vd 0–10 V (set up; submit blocked)
- Ian approved one array: does the trap model collapse the SiN deck at high Vd but not the HighK deck? The earlier HighK/SiN comparisons stopped at 3 V.
- `sweeps/pulsedIV_deckVg1.slurm` + `params_deckVg1.txt`, 8 tasks:
  - decks `rfdevice.tcl` / `rfdevice_SiN.tcl`;
  - trap-free, plus the sensitivity-baseline trap set at y 0.3 / 1.0 / 2.4 µm;
  - Vg +1, Vd 0–10 / 0.1, local field, 24 h on ee1-b.
- Fix in `drivers/pulsedIV.tcl`: the gate ramp went only downward, so a positive `Vg_meas` was never applied. It now steps toward Vg_meas of either sign; −2 and 0 behave as before (checked in tclsh). Commit f4f091f.
- Submitted at Ian's request (his exact command): **job 47062225**.

## 2026-10-23 — deckVg1 (job 47062225) done: HighK and SiN collapse identically
- HPG master was down; one Duo reconnect (`bin/hpg_reconnect.sh`) worked. All 8 tasks COMPLETED (28–66 min), with no `GAVE UP`, errors or cores. rsynced to `results/20261021_deckVg1/`. Figure `figures/deckVg1_IdVd.png` (`analysis/plot_deckVg1.py`).
- Trap-free Id at Vg +1, 10 V: 802.2 (HighK, = calibration) / 813.3 mA/mm (SiN).
- Onsets identical on both decks:
  - y 0.3: −83% at 1.3 V, recovering to ~9% of trap-free;
  - y 1.0: −100% at 1.5 V;
  - y 2.4: −100% at 1.7 V.
- The decks differ only in the post-collapse recovery above ~4 V (SiN 20–60× lower at 10 V).
- So the trap model does not reproduce the measured HighK/SiN contrast. Its collapse is also earlier and far deeper than the measured stepwise ~3× from 4 V. KB [[highk-vs-sin]].
- Next (Ian's call):
  - the model may need a field-triggered damage/trapping mechanism (the measured damage was bias-dependent and event-like); or
  - test traps under the field plate / drain-side FP edge where HighK lowers the field (y ≈ 0.7–1.0 µm at 10–20 V).

## 2026-10-23 — Goal (Ian): model that reproduces the measured pre- and post-irradiation behaviour
- Ian set the goal; work runs independently in worktree `~/HEMTRAD-wt/rad-model` (branch `explore/rad-model`, HPG `…/HEMTRAD-wt/rad-model`). HPG jobs are allowed; notify Ian above 50 tasks.
- **Pre-irradiation:** the trap-free deck has about 2× the measured on-resistance (Vd 0.1, Vg +1: 21 mA/mm model vs ~42 measured; Vg +1, Vd 1 V: 187 vs ~375). The measured Vth (≈ −2.96 V at Vd 0.1) is close. The transfer measurement is at Vd ≈ 0.1 V, not 10 V. Recalibrating on the branch.
- **Branch changes:**
  - mobility levers `mobMumax`/`mobNref`/`mobVsat` (GaN.tcl);
  - `trapShape field` (density from the data field `TrapN`);
  - driver `drivers/radIV.tcl`: pre/post transfer at Vd 0.1 and Id–Vd at Vg +1. Post adds a fixed surface charge (`surfCharge`), traps generated from the lateral field at the irradiation bias (Vg −10, Vd 28: `damPeak`·(E/`damEref`)^`damM`), and an optional lumped gate–drain leakage `Rgd`;
  - generic `sweeps/radIV.slurm`; `analysis/radCompare.py`.
- **Job 47311016 (10 tasks, `params_radCal1.txt`):**
  - polCharge 7/8/9/10e12 × mobNref 1e17/1e18 (phiB pre-shifted ~0.43 V per 1e12);
  - plus 2 post-damage smoke tests (HighK/SiN).

## 2026-10-23 — rad-model: pre-irradiation calibration rounds 1–2 done; damage round D1 submitted
- Round 1 (47311016): Vth within 0.03 V in all 8 variants (phiB pre-shift works). polCharge 9e12 + mobNref 1e18 matches the low-Vd transfer currents, but Id–Vd at Vg +1 saturates too high.
- Round 2 (47324103, vsat 1.5/2.0/2.5e7): best pre baseline = **polCharge 1e13, phiB 2.94, mobNref 1e18, mobVsat 2e7**.
  - Vth −3.00 V;
  - Id–Vd shape within about ±9% of measured (low by 7% at 1–2 V, high by 9% at 10 V);
  - gm max 65 vs ~50–54 mS/mm measured: the model turns on too steeply, as in the Oct 1 calibration.
- Both post smoke tests (47311016 tasks 8–9) failed in the stress ramp near Vd 17.5 V at Vg −10. Newton gives NaN in the minority quasi-Fermi levels in the depleted AlGaN.
  - Solver-side fix: the stress uses the highest converged Vd (≥ `Vd_stressMin` 12 V), which is recorded in the summary. The damage scale absorbs the field magnitude.
- `radIV.tcl` `damList`: several damage settings after one stress solve.
- **Submitted:**
  - **D1 = job 47327524** (6 tasks): non-biased (surfCharge −4e11) on both decks; biased on both decks × trapLevel 0.30/0.45, each with 9 settings (damM 1/2/4 × damPeak 1e17/3e17/1e18 at 1 MV/cm, depth ≤ 50 nm);
  - **calibration round 3 = job 47327599** (4 tasks): SiN-deck pre, vsat 1.75e7, mumax 2100.

## 2026-10-23 (late) — rad-model: calibration round 3 done, D1 biased partial
- Round 3 (47327599): tasks 1–3 done, task 0 (pre_sin) still running. Best pre fit is now p10_vs1.75_mu2100 (polCharge 1e13, phiB 2.94, mobNref 1e18, vsat 1.75e7, mumax 2100). Vth and the Id–Vd shape both fit; gm is still ~25% high.
- D1 biased (47327524 tasks 2–5): very slow, about 1 of 9 damage configs per task in 2.5 h.
  - The stress ramp stops at Vd 17 V (target 28).
  - The peak lateral field is the same in HighK and SiN: 6.96e5 V/cm in GaN at y ≈ 1.53 µm, within 0.1%. So field-weighted damage can't separate the decks either (same lesson as deckVg1).
  - The first configs (m1, 1e17) give a uniform −5% Id, all from surfCharge; no collapse.
- Next: let D1 finish overnight. The deck-separating mechanism has to come from something other than the bulk lateral field, e.g. the dielectric/interface (passivation charge or traps at the SiN interface).
- Correction (same day): the *peak* stress field is identical in the two decks, but its *distribution* is not. At x = 0.001 µm, y = 0.5 µm the lateral field is 5.5e5 V/cm in SiN vs 2.9e5 in HighK, and in the drift region (y 0.8–2.0 µm) HighK holds 4–20× more. So SiN concentrates the field and HighK spreads it, which is what the hypothesis needs. Field-weighted damage can still separate the decks, but only for steep damM (m4 configs, still pending in D1). Watching 47327524 to completion (round-3 watcher stopped; task 0 pre_sin isn't needed).
- 19:40 HPG master had dropped; reconnected once via Duo (approved).
- D2 submitted: job 47356193, 8 tasks (`sweeps/params_radDam2.txt` on explore/rad-model), one damage config per task. Settings: HighK/SiN × {m4 1e18, m4 3e18, m4 1e19, m6 3e18}, damEref 5e5, surfCharge −1.2e12, trapLevel 0.30, round-3 calibration (vsat 1.75e7, mumax 2100). D1 (47327524) keeps running as a backup. Waiting on both.

## 2026-10-24 — rad-model: D1 (47327524) and D2 (47356193) done; field-weighted damage does not separate the decks
- HPG master was down at session start (no tmux server on the workstation); one Duo reconnect via `bin/hpg_reconnect.sh` worked (master in tmux `hpg-master`).
- All tasks COMPLETED: D1 6/6, D2 8/8, round 3 4/4. No cores and clean .err files. The only `GAVE UP`s are D1 tasks 2–3 (Id–Vd at Vd 9.25 / 9.5 V in one config each). Every stress ramp stops at Vd 17 V (target 28).
- rsynced to `results/20261023_radDam{1,2}`, `…_radCal3` in the worktree. Figures: `figures/radDam{1,2}_compare.png` (worktree, not committed).
- Reference pre (round 3, p10_vs1.75_mu2100): Id(Vg −1.4, Vd 0.1) 39.5, Id(Vg +1, 10 V) 1029 mA/mm.
- **D1:** no collapse in any task. The best case is −1% at 10 V; nb shows only the surfCharge shift.
- **D2** (Id at Vg −1.4, Vd 0.1 / Id at Vg +1, 10 V, mA/mm; HighK vs SiN):

  | Config | HighK | SiN |
  |---|---|---|
  | m4 1e18 | 33.3 / 858 | 32.9 / 847 |
  | m4 3e18 | 29.4 / 437 | 27.8 / 389 |
  | m6 3e18 | 27.4 / 281 | 25.3 / 218 |
  | m4 1e19 | Vth +1 V, Id ≈ 0 | same |

- So steeper damM separates the decks by only 1.1–1.3×. Measured: HPD biased is ~unchanged at 10 V while SiN falls several-fold (numbers in the untracked note).
- Shape is also wrong. In the model, Id dips right after 1–1.5 V and then stays flat, so the drop is uniform in Vd. Measured SiN holds until 4 V and then drops in steps.
- The low-field loss (−16 to −36%) has the right size for both devices (meas −32% HPD, −20% SiN), but it does not separate the decks.
- The worktree has an **uncommitted** `damYmin/damYmax` damage window in `drivers/radIV.tcl` from the previous session: a diagnostic to localise the damage along y. It is not run or committed yet.
- Next (needs Ian):
  - (a) run the y-window diagnostic: damage only near the drain-side FP edge vs only in the drift region, to see which location gives the late, deck-dependent drop;
  - (b) move to a dielectric/interface mechanism (charge/traps at the SiN interface), as noted 10-23.

## 2026-10-24 — rad-model: y-window (a) and passivation-charge (b) arrays submitted
- Ian: "try both" (a) and (b) and keep iterating on the goal.
- Stress-field map (D2, top 50 nm, Vd 17): SiN > HighK only at y 0.35–0.65 µm (up to 2× at 0.5); HighK 5–10× higher from the FP edge (0.7) to the drain.
- Branch `explore/rad-model` 3fa478d:
  - `radIV.tcl` `damYmin/damYmax` committed;
  - new passivation-damage levers `damInsPeak/damInsM/damInsEref/damInsXmin`: fixed charge (`insTrapSign`, default −1 when used) in the 50 nm SiN under the HfO2, density ∝ (|E| in the dielectric at stress)^m;
  - `damField lat|tot`; cuts now include x −0.04/−0.01. Defaults leave the old behaviour.
  - Local smoke test (stress Vd 4) OK.
- **Submitted:**
  - **radWin = job 47458256** (16 tasks): both decks × windows y 0.125–0.30 / 0.30–0.65 / 0.65–1.0 / 1.0–3.2 × {field-weighted m4 3e18, uniform 5e17};
  - **radIns = job 47458257** (14 tasks): both decks × nitride charge {1e17, 1e18} × m {2, 4} at 1 MV/cm, + nitride charge 1e17 m2 combined with semiconductor m4 1e18, + D2 m6 3e18 at hotEb 1.5 / 2.0 (does a higher capture barrier move the onset from ~1 V toward the measured 4 V?).
- Base levers as D2 (round-3 calibration, surfCharge −1.2e12, trapLevel 0.30). Expect ~3–4 h per task.

## 2026-10-24 (evening) — rad-model: radWin (47458256) and radIns (47458257) analysed; radPost submitted
- All 30 tasks COMPLETED. radIns tasks 3 and 10 (nitride charge 1e18 m4) didn't produce an Id–Vd (gate ramp / IdVg GAVE UP); task 9 had an IdVg GAVE UP. No cores.
- Ratios to the round-3 pre are Id(Vg +1) at Vd 1 / 4 / 10 V; low = Id(Vg −1.4, Vd 0.1).
- **radWin (y-window damage):**
  - **w1 (gate edge, y 0.125–0.30), field-weighted:** early collapse from ~1.5 V in *both* decks (HighK 0.79 / 0.47 / 0.43, SiN 0.78 / 0.41 / 0.38). This is the deck-independent part that D2 showed. It isn't seen in the measurement, so the gate-edge damage must stay small.
  - **w2 (y 0.30–0.65), field-weighted:**
    - SiN 0.83 / 0.80 / 0.74: flat to ~3 V, then a drop starting at **~4 V**.
    - HighK 0.86 / 0.86 / 0.88: no drop.
    - This is the first config with the measured *signature* (late onset, SiN only). Magnitude ~3× too small.
  - **w3/w4 field-weighted:** ~0.87 flat in both.
  - **Uniform damage (all windows):** uniform low-field loss (0.73–0.86) with no collapse. It's the right kind of term for the HPD-like Ron loss, but doesn't separate the decks.
- **radIns (fixed charge in the bottom 50 nm SiN from the dielectric field):**
  - uniform losses, nearly identical in HighK and SiN (p1e17 m4: 0.72 vs 0.71 at 10 V; p1e18 m2: 0.13 vs 0.10). Doesn't separate the decks; dropped.
  - Higher hotEb (1.5 / 2.0) with D2 m6: collapse moves *earlier* (≤ 2 V), not later; dropped.
- Reviewed 3fa478d (damIns*, insTrapSign, damField, EstressT, extra cuts): defaults keep the old behaviour; no issues found.
- **Submitted radPost = job 47523721** (10 tasks, `sweeps/params_radPost.txt`):
  - both decks × field-weighted damage at y ≥ 0.30 × {m4 1e19, m4 3e19, m6 1e19, m6 3e19, m4 1e19 at trapLevel 0.45}, damMax 1e20;
  - other levers as D2.
  - Goal: scale the w2 SiN drop to the measured ~3× while HighK stays flat.
- The y ≥ 0.30 restriction is a fitting choice (it excludes gate-edge damage that the data don't show). It needs a physical reason before it goes in the KB (candidate: at the real stress Vd 28 V the peak moves to the FP-side edge; our stress solve stops at 17 V).

## 2026-10-24 20:15 — rad-model: radPost (47523721) partial; radFine submitted
- radPost: 7/10 done (tasks 0, 6, 7, 8 still running; task 6 has reached Vd 4.5). Damage is field-weighted at y ≥ 0.30, damEref 5e5. Ratios to the round-3 pre, Id(Vg +1) at Vd 1 / 4 / 10 V:
  - **HighK stays flat in every config:** m4 1e19 0.84 / 0.84 / – (Vd 9); m6 1e19 0.86 / 0.86 / 0.88; m6 3e19 0.85 / 0.85 / 0.87; L0.45 0.83 / 0.83 / 0.85. The one exception is m4 3e19, which droops to 0.67.
  - **SiN collapses fully** from ~1.5 V at m4 1e19 (0.49 at 1 V, ≈ 0 from 2 V) and at m4 1e19 L0.45.
  - So the deck separation is now large and in the right direction. SiN is overdamaged: radWin w2 at 3e18 gave 0.74 at 10 V with the onset ~4 V.
- **Submitted radFine = job 47554718** (8 tasks, `params_radFine.txt`): both decks × m4 damPeak {4, 5, 6, 7.5}e18, y ≥ 0.30, otherwise as radPost. Brackets the SiN drop to the measured ~3× at 10 V with onset ~4 V.
- Still open after that:
  - HPD low-field loss (model −16% from surfCharge alone, measured larger) → a uniform damage term;
  - gate–drain leakage Rgd;
  - physical justification for y ≥ 0.30.
- 21:20: radFine 47554718 FAILED within seconds: `params_radFine.txt` wasn't on HPG. Pushes from the new tmux session were failing silently (`git-credential-libsecret` isn't installed, and the push was run with `-q 2>/dev/null`). Pushed both checkouts with `-c credential.helper='!gh auth git-credential'`, and **resubmitted radFine = job 47562303**. radPost tasks 6 and 8 are still running.

## 2026-10-25 01:30 — rad-model: radFine (47562303) analysed; radFit1 submitted
- radFine: 6/8 done; HighK 6e18 and 7.5e18 are still running, both flat so far. Damage is m4, y ≥ 0.30, surfCharge −1.2e12.
- Model ratios to the round-3 pre, Id(Vg +1) at Vd 1 / 2 / 3 / 4 / 6 / 10 V:
  - **HighK:** flat 0.85–0.88 at 4e18 and at 5e18.
  - **SiN 4e18:** 0.82 / 0.81 / 0.76 / 0.67 / 0.62 / 0.63
  - **SiN 5e18:** 0.80 / 0.78 / 0.58 / 0.55 / 0.52 / 0.52
  - **SiN 6e18:** 0.78 / 0.61 / 0.43 / 0.41 / 0.41 / 0.44
  - **SiN 7.5e18:** 0.74 / 0.20 / 0.20 / … / 0.28
- **Measured ratios** (biased post / pre, from the untracked targets):
  - SiN: rises to ~4 V, then steps down; ends ~1/3 at 10 V.
  - HPD: a low-Vd loss that recovers fully by ~4 V.
  - Non-biased: the same Ron-like shape, smaller.
- **Mismatches:**
  - (1) The model's uniform 0.85 loss (mostly surfCharge −1.2e12) is the wrong shape for HPD. The measured shape is Ron-like.
  - (2) The SiN collapse sets in ~1 V too early, and the final level needs ~6–7e18.
- **Post-processing test:** a lumped series access resistance (Vd_ext = Vd + Id·R) on D1 nb (surfCharge −4e11) with R = 0.5 Ω·mm gives 0.80 / 0.85 / 0.89 / 0.92 / 0.97 / 1.00. That's close to the measured HPD shape. So the plan is a small surfCharge plus a lumped access resistance R, with field damage only for the SiN collapse.
- **Submitted radFit1 = job 47593908** (8 tasks): surfCharge −4e11 with the round-3 calibration: nb HighK/SiN + both decks × m4 {5, 5.5, 6}e18 (y ≥ 0.30). Next: fit R (and Rgd) in post-processing (new `analysis/radFit.py`). Then decide whether the onset can be moved toward 4 V.

## 2026-10-25 03:40 — rad-model: radFit1 (47593908) analysed; radFit2 submitted
- radFit1: 7/8 done (SiN 6e18 still running). surfCharge −4e11 with the round-3 calibration. Ratios to the pre, Id(Vg +1) at Vd 1 / 2 / 3 / 4 / 6 / 8 / 10 V:
  - **nb:** 0.96 flat in both decks; Vth +0.057 V.
  - **HighK biased:** 0.94 flat (5–6e18). Measured HPD has a low-Vd loss that recovers by 3–4 V.
  - **SiN biased, 5e18:** 0.88 / 0.86 / … / 0.60 / 0.57 / 0.59, onset 2–3 V. The weaker surfCharge moved the onset ~1 V later than at −1.2e12.
  - With the fitted drain-contact offset (`analysis/radFit.py`, V0 0.20 V, R 0.9 Ω·mm): 0.58 / 0.70 / 0.67 / 0.57 / 0.56 / 0.57 / 0.59, rms(log) 0.31.
  - For HPD the fit picks V0 = R = 0 because of the uniform −6% loss.
- **Remaining SiN mismatch:** the measured curve steps down twice (~4.5 V and ~7 V) and ends lower. Interpretation: discrete ion-strike damage sites (the leakage also steps during irradiation).
- radIV gets an optional second damage site, `dam2Peak/dam2M/dam2Ymin/dam2Ymax` (default off). radFit gets the contact offset V0.
- **Submitted radFit2 = job 47606666** (9 tasks):
  - SiN p5e18 + uniform second site {1e18, 3e18} × {y 0.65–1.0, 1.0–1.6};
  - SiN p6e18 + 3e18 at y 0.65–1.0;
  - HighK p5e18 + 3e18 in each window (does HighK stay flat with the same uniform damage?);
  - SiN p6.5e18 and p7e18 alone.

## 2026-10-25 06:50 — rad-model: radFit2 (47606666) analysed; n·E damage weighting being smoke-tested
- radFit2: 9/9 COMPLETED, no GAVE UP. Fitted with `radFit.py` (V0/R contact elements), rms(log) vs measured.
  - **SiN:**
    - p5e18 + 3e18 uniform at y 1.0–1.6 is best (0.246): a *second, later step* appears (0.61 at 4 V → 0.53 at 6 → 0.47 at 8 V);
    - p5e18 + 3e18 at y 0.65–1.0: 0.260;
    - p6.5e18 and p7e18 alone are too deep and too early (0.45, 0.61).
    - So the damage *position* sets the onset Vd: farther toward the drain = later step.
  - **HighK with the same uniform second site collapses too** (0.55 at 4 V for y 0.65–1.0; 0.49 at 6 V for 1.0–1.6). The measurement-time field doesn't protect HighK, so the deck difference has to come from *where the stress puts the damage*. Uniform sites are ruled out as the explanation.
- But the lateral stress field at y 0.65–1.6 is *higher* in HighK, so lateral-field weighting can't put the drain-side damage in SiN only.
- **New candidate:** damage ∝ n·E_lat at stress (normalised to its peak). It peaks where the depleted high-field region meets the 2DEG, which should sit nearer the gate in SiN than in HighK (HighK spreads the depletion).
- Added `damField ne` to radIV (commit on branch). **Smoke test = job 47625503** (1 task, SiN, stress Vd 4, no measurement), checking that `Elec*Estress` evaluates across all regions. If it passes, the next array is both decks × damPeak levels with damField ne.
- 07:45: smoke 47625503 passed (stress Vd 4). The `damField ne` weight peaks at the drain-contact edge (y 3.285), with ~0.03 of the peak at y 0.3–0.5 at the 2DEG depth. **Submitted radNE1 = job 47628955** (8 tasks): both decks × ne damage {m1 1e18, 1e19, 1e20; m2 1e20}, surfCharge −4e11, full stress (Vd 17). Question: where does n·E put the damage in SiN vs HighK at 17 V, and does that give SiN-only collapse plus a HighK Ron-like loss?
- 2026-10-25 08:35 Ian: "I'm good with a qualitative fit for many of the phenomena." So the target is now qualitative: each measured phenomenon with the right sign, onset region and deck dependence. Plan: once radNE1 is in, pick the physically best-motivated damage law, run one final consolidated set (pre, nb, biased × both decks), and write up the model and its caveats (KB note on the branch, measured overlays kept untracked).

## 2026-10-25 11:35 — rad-model: radNE1 (47628955) analysed; radNE2 submitted
- radNE1: 6/8 done (both m1 1e20 still running; already collapsed to 0 at Vd ≥ 4).
- **Damage maps:** at the 2DEG depth, n·E puts SiN damage in a narrow band at y 0.6–0.8 (peak at 0.7) and HighK damage in a broader band at y 0.8–1.6 (peak at 1.0). There is no damage at the gate edge (no electrons there at stress). Both decks also get large, identical damage at the drain-contact edge (4e19 at m1 1e20) and the source access (2e18).
- **Id–Vd: the decks are identical at every level.**
  - m1 1e18 0.95 flat;
  - m1 1e19 0.90–0.92 flat;
  - m2 1e20 0.91–0.94 flat;
  - m1 1e20: 0.58 at 1 V, 0 from 4 V, in both.
  - The identical contact and source damage dominates the drift-band difference.
- **Submitted radNE2 = job 47662463** (6 tasks): n·E damage limited to the gate–drain access region (y 0.125–3.0, which excludes the ohmic-contact edges and the source side), m1 {1e20, 3e20, 1e21}, both decks. Question: does the drift-band difference alone give SiN-first collapse?
- 13:45: the HPG master dropped again after ~20 h (this time it was in tmux `hpg-master`, so the drop is server/network-side, not the terminal). One Duo reconnect via `bin/hpg_reconnect.sh` worked.

## 2026-10-25 14:50 — rad-model: radNE2 (47662463) analysed; consolidated radFinal submitted
- radNE2: 6/6 COMPLETED, no GAVE UP. n·E damage limited to the gate–drain region (y 0.125–3.0). Ratios to the pre, Id(Vg +1) at Vd 1 / 4 / 10 V:
  - **HighK:** 1e20 0.87 / 0.89 / 0.96; 3e20 0.78 / 0.82 / 0.94; 1e21 0.54 / 0.52 / 0.61.
  - **SiN:** 1e20 0.88 / 0.91 / 0.96; 3e20 0.76 / 0.78 / 0.90; 1e21 0.00 / 0.10 / 0.26 (channel blocked).
  - So n·E damage gives a **Ron-like low-field loss that recovers at high Vd** in both decks, which is the measured HPD shape. SiN is more sensitive (its damage band is denser and nearer the gate), but n·E alone gives no late SiN collapse.
- **Model chosen (qualitative, as Ian agreed). Two damage terms set at the stress bias:**
  1. lateral-field E⁴ damage beyond the gate edge (y ≥ 0.30, damEref 5e5) → SiN-only late collapse;
  2. n·E damage in the gate–drain access region (3e20) → Ron-like loss in both decks.
  - Also surfCharge −4e11 (+Vth) and hot-electron fill-only capture at trapLevel 0.30.
- radIV: `dam2Field/dam2Eref` added, so the second site can use another weighting (default = same as the first).
- **Submitted radFinal = job 47693156** (8 tasks): pre / nb / biased × both decks, biased at damPeak 5e18 and 5.5e18, all with the round-3 calibration. Next: radFit (V0/R) and a lumped Rgd for the leakage on top. Then the KB note and an untracked overlay figure.

## 2026-10-25 18:15 — rad-model: radFinal (47693156) done — qualitative model in place
- 8/8 COMPLETED, no GAVE UP, no cores.
- Model: round-3 calibration; post adds surfCharge −4e11 + lateral-field E⁴ damage beyond the gate edge (damPeak 5e18, y ≥ 0.30) + n·E access damage gate–drain (3e20) + hot-electron fill-only capture.
- Ratios to pre, Id(Vg +1) at Vd 1 / 2 / 4 / 6 / 10 V:
  - nb 0.96 flat, Vth +0.057 V;
  - **biased HighK** 0.77 / 0.78 / 0.81 / 0.85 / 0.93: no collapse, Ron-like recovery;
  - **biased SiN** 0.71 / 0.72 / 0.57 / 0.55 / 0.56: collapse step at ~3.3 V.
- Qualitative check against the measured set:
  - **matches:** pre; +Vth sign; SiN-only late collapse; HPD no collapse; biased low-field loss recovering with Vd.
  - **misses:** single vs double SiN step; low-field deck order reversed (model SiN > HPD); nb SiN low-Vd dip; leakage only as a lumped Rgd.
- Branch commits:
  - `analysis/plot_radFinal.py`;
  - `figures/radFinal_model.png` (model only);
  - `kb/results/rad-model.md` (full run history, comparison table, caveats).
  - The overlay with measured data is untracked: `data/rad_y2/radFinal_overlay.png`.
- Next (needs Ian):
  - merge `explore/rad-model` into main, or keep it as a branch;
  - whether to push further on the double step / stress at 28 V (the no-holes stress solve would be a physics change).

## 2026-10-25 20:40 — rad-model: radPhys1 (47725314) — n·E⁴ damage has no effect
- 7/8 done. The first damage site is weighted by (n/1e18)·(E_lat/5e5)⁴ at stress (`damNexp 1`, no y window), plus the n·E Ron term as in radFinal. The result is identical at every damPeak 1e17–1e20 (HighK 0.78 → 0.94, SiN 0.76 → 0.89), i.e. only the Ron term acts. Where E_lat is high at the stress bias, the channel is fully depleted (n ≈ 0), so n·E⁴ is negligible everywhere. Electron weighting can't replace the y ≥ 0.30 exclusion. It stays a documented fitting choice in the radFinal model.
- Re-check of the measured set (each device against its own pre, from the untracked targets):
  - biased HPD keeps its gm and shifts Vth positive;
  - biased SiN loses clearly more gm and shifts Vth positive by a similar amount.
  - So SiN degrades more, the same order as the model (gm −12% SiN vs −10% HighK). The earlier "reversed deck order" came from using the SiN pre as the reference for HPD.
  - The non-biased devices are different parts: gm differs by up to ~50% from the pre devices. Their curves mostly show device spread, not radiation.
  - Lumped Rgd sized from the measured off-state current at Vg −5 / Vd 0.1 (values in the untracked note).

## 2026-10-26 01:00 — rad-model: radFinal2 (47752290) — final model without the n·E term
- 4/4 COMPLETED, no GAVE UP.
- dam2Peak 0:
  - HighK biased 0.94 flat, gm −2%: qualitatively on the measured HPD biased curve.
  - SiN biased: low field 0.88, collapse from ~2.3 V to 0.58, gm −5%.
- dam2Peak 1e20: HighK 0.86 → 0.95. The n·E band is larger in HighK (wrong deck direction), so the term is dropped.
- Final model = surfCharge −4e11 + lateral-field E⁴ damage (y ≥ 0.30, 5e18) + hot-electron fill-only capture + lumped Rgd. KB note on the branch updated.
- Comparison figures (untracked, include lab data): `data/rad_y2/compare/1–4_*.png`, sent to Ian.
- Open:
  - SiN one step vs two;
  - SiN onset early;
  - Vth shift smaller than measured;
  - SiN gm loss smaller than measured.
- Needs Ian:
  - merge decision;
  - OK for a no-holes stress solve to 28 V.
- Housekeeping: redacted measured numbers that had slipped into earlier progress entries (10-24 D1/D2 entry, 10-25 20:40 entry). They remain in git history; rewriting history needs Ian's OK.
- 01:15 **radFinal3 = job 47773690** (8 tasks, `params_radFinal3.txt`):
  - under-gate fixed acceptor damage (uniform, y −0.125–0.125, top 50 nm) {1e18, 3e18} on top of the final model, both decks, plus an nb HighK check. Can a gate-local charge give the measured Vth size without a flat access loss?
  - SiN onset levers on the final model: SiN/HighK hotEb 0.7, SiN hotTau 1e-12.

## 2026-10-26 06:10 — rad-model: radFinal3 (47773690) analysed; radFinal4 submitted
- radFinal3: 8/8 COMPLETED. Ratios to pre, Id(Vg +1).
- **Under-gate acceptor damage:** Vth +0.80 V at 1e18 and +1.67 V at 3e18, far too much. It also adds hot-electron capture in HighK (gradual droop to 0.74 / 0.46). Target ~2e17.
- **hotEb 0.7:** SiN onset later and gentler: 0.87 at 2 V, 0.83 at 2.5, 0.74 at 3, 0.68 at 4, 0.63 at 10. HighK still flat at 0.94. An improvement toward the measured late onset.
- **hotTau 1e-12:** SiN fully collapses from Vd 1 V. Dropped.
- **Submitted radFinal4 = job 47797775** (8 tasks):
  - hotEb 0.7 + under-gate {2e17, 4e17} on both decks, plus an nb HighK check;
  - hotEb 0.5 on SiN and HighK;
  - SiN hotEb 0.7 with damPeak 6e18 (deeper).

## 2026-10-26 08:05 — rad-model: radFinal4 (47797775) analysed; radFinal5 submitted
- radFinal4: 8/8 COMPLETED.
- **Under-gate charge 2e17 (hotEb 0.7):** Vth +0.24 V on all devices; HighK biased ~0.92 flat; nb ~0.94; SiN unchanged (0.87 → 0.63). 4e17: Vth +0.40 V. Use ~1.5e17.
- **hotEb 0.5:** SiN holds to ~3 V, then 0.74 at 4 V → 0.68 at 10 V (latest onset, shallow); HighK flat 0.94.
- **hotEb 0.7 with damPeak 6e18:** SiN 0.65 at 2.5 V → 0.53 (deeper, earlier).
- **Submitted radFinal5 = job 47806744** (6 tasks): hotEb 0.5 + under-gate 1.5e17; SiN damPeak {6, 7, 8}e18; HighK 7e18; nb HighK/SiN.

## 2026-10-26 11:50 — rad-model: radFinal5 (47806744) — final parameter set
- 6/6 COMPLETED. nb HighK gave up at Vd 8.5 (Id–Vd), harmless.
- Final set: hotEb 0.5, under-gate 1.5e17, field damage 7e18 (y ≥ 0.30), surfCharge −4e11.
- Results:
  - Vth +0.19 V on all irradiated devices;
  - nb ~0.95;
  - HighK biased 0.92 flat;
  - SiN biased collapses from ~2 V to 0.48;
  - gm −8% HighK / −12% SiN.
- Figures regenerated (untracked `data/rad_y2/compare/`), sent to Ian. KB note on the branch updated with the final set and lever findings.
- Remaining:
  - SiN onset early, single step, shallower;
  - gm deck contrast smaller than measured;
  - lumped leakage;
  - gate-edge exclusion;
  - stress at 17 V.
- The open decisions for Ian (merge, history scrub, no-holes stress solve) are unchanged.
- 12:05 **radFinal6 = job 47829928** (4 tasks). radIV gets an optional third damage site (`dam3Peak/dam3Ymin/dam3Ymax`, uniform, default off): a discrete ion-strike site at y 1.0–1.6 µm on top of the final set.
  - SiN p7e18 + {2e18, 4e18}; SiN p6e18 + 4e18; HighK p7e18 + 4e18 for reference.
  - Question: does a second discrete site reproduce the second, later SiN step? Its location is stochastic per device, so it's a fitting choice, documented as such.

## 2026-10-26 15:05 — rad-model: radFinal6 (47829928) — two SiN steps with a second discrete site
- 4/4 COMPLETED (SiN p7e18 + s4e18 gave up at Vd 8).
- SiN p6e18 + uniform site 4e18 at y 1.0–1.6: low-Vd loss, then a first step near 5 V and a second near 6.3 V, then a slow creep. Qualitatively the measured two-step SiN curve. Figure `data/rad_y2/compare/5_SiN_two_sites.png` (untracked), sent to Ian.
- The same site collapses HighK too, so it's a device-specific strike location (fitting choice, documented in the KB note).
- **Model status (qualitative):** reproduced:
  - pre;
  - +Vth on all irradiated devices;
  - HPD biased no collapse;
  - SiN biased late two-step collapse with low-Vd loss (with the second site);
  - nb small change;
  - leakage via lumped Rgd.
- Not reproduced: the gm contrast HPD vs SiN (model similar in both decks).
- Caveats: gate-edge exclusion, second-site placement and lumped leakage are fitting choices; stress at 17 V.
- Waiting on Ian: no-holes stress solve, merge, history scrub.
- 15:20 **radFinal7** submitted (5 tasks): under-gate fixed charge confined to the AlGaN (`dam2Xmax 0.014`) at 5e17 / 1e18 — does it shift Vth without the ~7% gm loss of the top-50-nm version? Plus SiN at damPeak 7e18 / 8e18 for a deeper gm loss.

## 2026-10-26 15:40 — Ian's decisions
- Ian: (1) "Go for it" on the no-holes stress solve; (2) don't merge `explore/rad-model` yet; (3) not concerned about the measured numbers in the git history (leave them).
- radIV `stressNoHoles` (default 0): for the stress step only, `solution name=Qfp nosolve` with Qfp frozen at +50 V, so Hole ∝ F((Eval − Qfp)/kT) ≈ 0. Restored to Qfp = 0 + `solve` at rest before damage/measurement.
- **Smoke = job 47860677** (2 tasks, stress-only, HighK/SiN, target Vd 28): does the stress reach 28 V, and how does the field map change vs 17 V?
- 16:35: smoke 47860677 FAILED at once. Freezing Qfp at +50 V everywhere broke the rest solve (Poisson residual 1e31 in region B, the Fe buffer, whose acceptors need their equilibrium holes). Added `stressNoHolesX`: holes removed only above that depth (default 0.1 µm); deeper, Qfp is frozen at its rest value 0. **Smoke2 = job 47861047** (3 tasks): HighK/SiN with X 0.1, and SiN with X 0 (Qfp frozen at 0 everywhere).

## 2026-10-26 19:40 — no-holes stress doesn't help; Qfn damping smoke; radFinal7 analysed
- **Smoke2 (47861047):** all 3 COMPLETED. Holes removed above 0.1 µm (or Qfp frozen at 0 everywhere) still stops at **Vd 17 V**, with fields identical to the with-holes run, so holes were negligible. The Newton log at 17 → 18 V diverges in **Qfn** (electrons) in the depleted AlGaN/GaN, not in Qfp. The no-holes lever stays in (default off) but doesn't solve the limit.
- **Next, solver-side:** `stressQfnDamp` (Qfn DampValue during the stress drain ramp only). **Smoke = job 47875456** (SiN, 0.02 / 0.005).
- **radFinal7 (47852523):** 5/5 COMPLETED. The under-gate charge confined to the AlGaN (`dam2Xmax 0.014`) shifts Vth without the gm loss:
  - nb HighK 5e17: Vth +0.21 V, gm −1%;
  - nb HighK 1e18: +0.33 V, −1%;
  - biased HighK 1e18: gm −2% (measured HPD: unchanged);
  - biased SiN: gm −5% / −6% (p7e18 / p8e18).
  - So the deck order of the gm loss is right; the SiN size is smaller than measured.
  - New final set: AlGaN-only under-gate charge 5e17.

## 2026-10-26 22:05 — stress limit confirmed; consolidated radFinal8 submitted
- Qfn-damp smoke (47875456): DampValue 0.02 and 0.005 both stop at **Vd 17 V** again. With no holes and two Qfn damping levels the stress still ends at Vdg ≈ 27 V, so this is a hard solver limit in the electron equation in the depleted region. It stays as a documented caveat; the damage scale absorbs the field magnitude.
- **Submitted radFinal8 = job 47887339** (5 tasks), the consolidated final set:
  - round-3 calibration;
  - surfCharge −4e11;
  - under-gate fixed charge 5e17 in the AlGaN only;
  - field damage 7e18 (y ≥ 0.30);
  - hotEb 0.5.
  - Runs: nb HighK/SiN; biased HighK/SiN; SiN with a second discrete site (6e18 + 4e18). Pre comes from radFinal (47693156).

## 2026-10-27 02:00 — rad-model: consolidated final model (radFinal8, 47887339)
- 5/5 COMPLETED (two Id–Vd GAVE UP at Vd 9–10, at the very end).
- One parameter set:
  - nb: Vth +0.21 V, gm −1%, 0.95 flat;
  - biased HighK: +0.21 V, gm −2%, 0.93 flat, no collapse;
  - biased SiN: one site 0.83 → 0.48, gm −5%; with the second strike site, 0.60 then steps near 5 and 6.5 V, gm −17%.
- Qualitatively reproduces the measured pre/post set: +Vth everywhere, HPD no collapse and gm kept, SiN late two-step collapse with the largest gm loss, nb small changes.
- Figures regenerated (untracked `data/rad_y2/compare/1–4`), sent to Ian. KB note on the branch (`kb/results/rad-model.md`) has the final set, the table and the caveats.
- Caveats:
  - stress limited to 17 V (hard Qfn limit, after the approved no-holes test and the damping test);
  - gate-edge exclusion, second-site placement and lumped Rgd are fitting choices;
  - SiN final level shallower than measured.
- Branch not merged (Ian: not yet).

## 2026-10-27 02:25 — HPG master down; reconnect not approved — WAITING
- radFinal9 = job 47908735 (3 tasks: SiN second site 5e18 / 6e18, and p6.5e18 + 5e18; deeper SiN final level) was submitted at 02:10. The master dropped at ~02:15.
- One Duo reconnect attempt via `bin/hpg_reconnect.sh`: the push wasn't approved within 2 min. Per the rules: no retry. Waiting for Ian.
- radFinal9 keeps running on HPG regardless. To pick up: once Ian reconnects, rsync `results/20261027_radFinal9`, compare with radFinal8 task_4 (SiN two sites), and adopt the closest set into the figures/KB if it's deeper without losing the late onset.

## 2026-10-27 07:55 — reconnected (Ian); radFinal9 (47908735) analysed — radFinal8 stays final
- Ian said "reconnect"; one Duo reconnect worked (master in tmux `hpg-master`).
- radFinal9: 3/3 COMPLETED, but all three Id–Vd sweeps GAVE UP at Vd 3.75–4.5 V, right at the collapse onset.
  - The stronger second site (5e18 / 6e18) deepens the low-Vd loss (Id at 1 V 202 / 183 vs 222 mA/mm; gm −19% / −21% vs −17%).
  - The solver can't follow the collapse step, so the high-Vd level is unknown.
  - No usable improvement. radFinal8 (47887339) stays the final consolidated model.
- Goal status: qualitative replication done (Ian's bar). Caveats as in `kb/results/rad-model.md`. Branch not merged (Ian: not yet). No jobs running.
- 08:05 **radFinal10 = job 47943462** (2 tasks): radFinal9 SiN strong second site (5e18 / 6e18), rerun with Vd_step 0.1 and retryDepth 8 (solver-side) to follow the collapse step past 4 V.
- 10:50: radFinal10 (47943462) 2/2 COMPLETED, but the Id–Vd still gives up at Vd 4.2 / 3.6 V even with 0.1 V steps and retryDepth 8. A strong second site (≥ 5e18) makes the collapse step itself unresolvable by the solver, so the SiN final level can't be pushed deeper this way. **radFinal8 (47887339) is the final model.** The rad-model goal is closed at the qualitative level Ian accepted; remaining differences and caveats are in `kb/results/rad-model.md` (branch). No jobs running.

## 2026-10-27 14:15 — rad-model: radFinal11 (47959281) — final SiN curve
- 3/3 COMPLETED, all run to Vd 10 V (0.1 V steps, retryDepth 8).
- **SiN damPeak 6e18 + second site 4.5e18:** two steps near 4.5 and 5.8 V, creep up to 377 mA/mm at 10 V, gm −18%. That's deeper than radFinal8 (483) and qualitatively the measured curve. Adopted as the final SiN biased curve. Other devices stay at radFinal8.
- Figures regenerated (untracked `data/rad_y2/compare/`), sent to Ian; KB note updated.
- Model complete at the qualitative level. Remaining caveats as in the KB note (stress 17 V, fitting choices: gate-edge exclusion, second-site placement, lumped Rgd). No jobs running.

## 2026-10-27 — rad-model goal closed (Ian: "Close the goal")
- Final model: radFinal8 (47887339) for pre/nb/HPD, plus radFinal11 (47959281) for the SiN biased curve. Qualitative replication; caveats are in `kb/results/rad-model.md` on `explore/rad-model`. Branch not merged (Ian: not yet). No jobs running.
- Dashboard (work log) updated, version 12: day pages Oct 21, Oct 23, Oct 24–27 (rad model), refreshed Overview (tiles: pre fit, SiN-only collapse, Vth shift; open items rad-model stress limit / fitting choices / merge). Model-only figures (`radMech_*`, `radFinal8_model`, `deckVg1_IdVd`); no measured data. `kb/current-status.md` refreshed.
- Rad-model explainer published: https://claude.ai/artifact/FArVrMfXX8JNvoFRqYWHLu (source `dashboard/rad-model.html`, model-only figures); linked from the work log's Oct 24–27 page and `kb/workflow/dashboard.md`.

## 2026-10-28 — Stress divergence at Vd 17 V: diagnosis started
- Ian: work on a solution to the stress divergence at Vd 17 V; wants higher voltages.
- radIV `stressDiag` (default 0): after the ramp stops, one more drain step (+0.25 V). The fields (Qfn, DevPsi, Elec, Econd) and their Newton changes (|ΔQfn|, |ΔPsi|) are written along cuts at several depths and positions to `<tag>_stressDiag.txt`, then restored.
- **stressDiag1 = job 48125435** (4 tasks, SiN deck, stress only, target Vd 40): Vg_stress −10 / −6 / −14 / −4. This finds where Qfn runs away, and whether the limit follows Vdg (~27 V) or Vd.
- stressDiag1 (48125435) analysed. The stress limit is **Vd 17.0 V for every Vg_stress** (−4 / −6 / −10 / −14), so it does not follow Vdg.
  - The 17 → 17.25 V step converges directly; the bisection log shows Newton reaching RHS ~1e-2 within 7 iterations and then wandering: scaled Qfn updates 0.1–4 in the fully depleted GaN/AlGaN, never under updateLimit, until a NaN or the iteration cap.
  - Diagnosis: Qfn floats where n ≈ 0 (it doesn't affect the solution there), and the Qfn Abs.Error of 1e-2 V (≈ 1e-5 V effective) can't be met.
  - Fix under test (solver tolerance, stress step only): `stressQfnAbs`. **stressAbs1 = job 48141047** (SiN Abs 0.1 / 1.0 to 28 V, SiN 1.0 to 40 V, HighK 1.0 to 28 V).
- FLOOXS reads Abs.Error/Rel.Error/DampValue only when the solver is built, so `stressQfnDamp` (47875456) and `stressQfnAbs` (48141047) had no effect. New `qfnAbs` is set before `device init` (whole run). **stressAbs2 = job 48141104** (same 4 cases with qfnAbs). Gotcha added to `kb/numerics/flooxs-gotchas.md`.
- 21:40 stressAbs2 (qfnAbs, running): 17.25 and 17.5 V now converge (the tolerance helps), but the next step NaNs on Newton iteration 1. Hypothesis from the stressDiag1 dump: electron density in the depleted GaN buffer is already 1e-290…1e-260 cm⁻³ at 17 V (double underflow ≈ 1e-308). The buffer depletes with Vd regardless of Vg, which fits the limit at 17.0 V for every Vg. **stressDiag2 = job 48147357** (qfnAbs 1, ± no-holes): dumps post-failure Elec/Hole/Qfn/DevPsi to locate the NaN.
- 23:55 stressAbs2 (48141104) done:
  - With qfnAbs the stress gets to **17.67 V (SiN) / 17.77 V (HighK)**, and then even 1/64 V steps NaN: a hard wall ~17.7 V, independent of Vg and tolerance.
  - stressDiag2 (48147357): its diag step converged (no failure dump), but the 17 V state already shows **Hole = 0 (underflow)** in the top 50 nm from y ≈ 0.55 µm to the drain, and Elec down to 1e-290 in the buffer.
  - The no-holes variant gave identical fields: `solution name=Qfp nosolve` after device init doesn't take effect either, so the earlier no-holes test (47861047) didn't test anything.
  - FLOOXS's NaN check (`Values::TestProb`) trips on a non-finite *norm*, so values above ~1e154 also trigger it. f12 itself underflows cleanly.
- **stressDiag3 = job 48159016** (2 tasks): stress in 0.25 V steps up to the wall, then a diagnostic step of 0.25 / 1.0 V that should fail; dumps the post-failure fields incl. Qfp to locate the blow-up.
- 2026-10-29: Ian approved a tiny density floor. `model/Continuity.tcl` (branch, CRLF kept) gets the `carFloor` lever (default off): Elec and Hole = statistics + carFloor. **stressFloor1 = job 48161617** (4 tasks, qfnAbs 1, stress in 0.5 V steps): SiN floor 1e-100 / 1e-30 to 28 V, SiN 1e-100 to 40 V, HighK 1e-100 to 28 V. stressDiag3 (48159016) is still running to locate the blow-up.
- 03:30 stressFloor1 (48161617): carFloor 1e-100 / 1e-30 stops at **17.5 V** like before, so underflow is not the cause.
- stressDiag3 (48159016) caught a failed step (17.5 → 17.75 V); all dumped fields are ordinary.
- **Cause found:** trap occupancy f = 1/(1 + g·exp((Et − Qfn)/Vt)) is evaluated in all GaN/AlGaN. In the deep buffer Et ≈ +3 V while Qfn follows the drain to ≈ −17.8 V, so the exponent exceeds 709 above Vd ≈ 17.7 V. exp → inf, and the derivative is inf/inf → "computed a nan or infinite". Independent of Vg, as observed.
- Fix: `occClamp` lever in `model/Poisson.tcl` (default off) caps the exponent at occClamp (700) via min(a, C). It is exact: e^-700 is 0 in double precision.
- **stressClamp1 = job 48174580** (4 tasks): SiN clamp ± qfnAbs to 28 V, SiN clamp + qfnAbs to 40 V, HighK clamp + qfnAbs to 28 V.
