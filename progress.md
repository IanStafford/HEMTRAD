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
