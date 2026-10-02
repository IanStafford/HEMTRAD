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
