"""Helpers shared by the analysis scripts (clean-up stage 3a, kb/workflow/cleanup-plan.md; findings AN-1, -3, -5,
-6, -7, -10, -14, -15, -20).

Each helper reproduces the copies it replaces. Where the copies differ, a keyword argument selects the old variant,
so a script that switches to the helper keeps its output by passing its old settings (the docstrings name the
variant each script used). The equivalence tests were run on the runs in results/ (2026-11-21).

Import: a script in analysis/ writes `from common import ...` with no sys.path line, because python3 puts the
script's own folder first on sys.path. A script elsewhere (archive/), run from the repo root, first does
`sys.path.insert(0, "analysis")`. matplotlib is imported only inside seq_cmap and use_slide_fonts, so importing this
module does not pick a matplotlib backend.

Contents:
  CSV files         IDVD, IDVG, PULSED (column numbers), read_csv, read_glob
  task index        label_index
  drops             DROP_MIN_FIG, DROP_MIN_TABLE, drop_episodes, drop_values
  collapse class    classify_loss, classify_collapse, Collapse
  reference curves  REF, pre_ref, LATE_SET, RUN_F, run_f_curve
  radIV metrics     vth_gm, ron_step, PRIVATE_DIRS, guard_private_output, load_pre_scalars (the same code as
                    radMetrics.py, which can then re-export them from here)
  style             grey palettes, BLUE / ORANGE / DECK_COL, SEQ_COLORS / seq_cmap, GATE / FP / LGD_DRAIN,
                    strike colour ramps, use_slide_fonts
"""
import glob
import json
import os
import re
import sys
from collections import namedtuple

import numpy as np

# ============================================================================ CSV files
# Column numbers of the driver outputs (drivers/radIV.tcl header "Outputs"; drivers/pulsedIV.tcl ivCSV).
# Id_dev and Id_ext are equal while Rgd = 0 (the radIV default; no sweeps/params_*.txt line sets Rgd).
# ron_step, radCompare, radMap, radFit, plot_radFinal and plot_radMechanism read Id_ext; the step and strike
# figures read Id_dev.
IDVD = dict(vd=0, id_dev=1, id_ext=2, te=3)   # radIV <tag>_IdVd.csv, <tag>_IdVdG<Vg>.csv: Vd, Id_dev, Id_ext, peak Te
IDVG = dict(vg=0, id_dev=1, id_ext=2)         # radIV <tag>_IdVg.csv: Vg, Id_dev, Id_ext
PULSED = dict(vd=0, id=1, te=2)               # pulsedIV pulsedIV_*.csv: Vd, Id, peak Te
                                              # (V, mA/mm, K)


def read_csv(path, min_rows=None, ncols=None):
    """Numbers of a comma-separated file as an array (the reader copied into 23 scripts).

    Blank lines and empty fields are skipped, so a trailing comma does no harm. A file with one row gives a 2D
    array of one row; an empty file gives a 1D empty array. A missing file raises FileNotFoundError and rows of
    different lengths raise ValueError.
    min_rows: return None unless the array is 2D with at least min_rows rows ("len(d) > 2" in the copies is
    min_rows=3). ncols: keep the first ncols columns, after the min_rows check (plot_meshSeries.load is
    read_csv(f, min_rows=3, ncols=2)).
    """
    with open(path) as fh:
        d = np.array([[float(v) for v in l.split(",") if v.strip()] for l in fh if l.strip()])
    if min_rows is not None and not (d.ndim == 2 and len(d) >= min_rows):
        return None
    return d[:, :ncols] if ncols is not None else d


def read_glob(pattern, min_rows=3, skip_empty=False, ncols=None):
    """read_csv of the first file that matches the glob pattern (glob.glob order), or None if none matches.

    min_rows=3: plot_radStepSeries.load. min_rows=None (no check): the "... if f else None" loaders of
    plot_rad28strike and plot_radStrikeN. skip_empty=True also gives None for a file of size 0: with
    min_rows=None this is radPlacementFig.load. The loaders that crash on a missing file (radCurves, radMeshFig,
    radPartialWidth, plot_radFinalEB) are read_csv(glob.glob(pattern)[0]). The day-figure scripts moved to
    archive/analysis_dayfigs/ have the same loaders: plot_radStepHighlights (min_rows=3); plot_nov12,
    plot_rad28fit, plot_rad3dFix (min_rows=None); radFineFig (min_rows=None, skip_empty=True); plot_radExp1,
    radEBFig, radGaussFig, plot_gaussFine (read_csv(glob.glob(pattern)[0])).
    """
    f = glob.glob(pattern)
    if not f or (skip_empty and os.path.getsize(f[0]) == 0):
        return None
    return read_csv(f[0], min_rows=min_rows, ncols=ncols)


# ============================================================================ task index
def label_index(patterns, csv="*_IdVd.csv", min_rows=3, keep="first", sort=False, match=None, warn=True):
    """{label: file} over the task directories matching patterns (a glob or a list of globs), the label being the
    "label" of each task's params.json.

    Tasks are visited pattern by pattern in glob.glob order; sort=True sorts each pattern's matches first
    (plot_radStep). The value is the first match of <task>/<csv>, and a task without one is skipped; with
    csv=None the value is the task directory itself. match: a regex; a task whose label it does not re.search is
    skipped before its file is read (plot_radStep's group regex). min_rows: a task whose file is not 2D with at
    least min_rows rows (read_csv) is skipped; None (or csv=None) reads no file. A params.json that is missing or
    is not valid JSON is skipped; one without a "label" key raises KeyError.
    keep: which task a label keeps when it occurs twice. 'first' is plot_meshSeries.index and plot_meshChkSteps
    (setdefault); 'last' is plot_radStep, plot_radStepFS/H.curves, plot_deckVg1 and plot_radFinal (dict
    assignment). A later task replaces an earlier one only if it passes the csv and min_rows checks, as in those
    scripts. warn: print each repeated label to stderr (no label repeats in results/ today).

    The scripts' copies read the label before or after looking for the csv file, and some catch fewer errors;
    the result is the same wherever a copy ran without an exception. Calls that reproduce each script:
      plot_meshSeries.index    label_index(pats, min_rows=None)
      plot_meshChkSteps        label_index(["results/2026111*_radStep*/task_*",
                                            "results/20261118_meshChkLoad_*/task_*"], min_rows=None)
      plot_radStepFS/H.curves  label_index([f"{r}/task_*" for r in RUNS], keep="last"), then read_csv of each file
      plot_radStep.main        label_index(f"{run}/task_*", keep="last", sort=True, match=rx), then read_csv
      plot_deckVg1             label_index(f"{RUN}/task_*", csv="pulsedIV_*.csv", min_rows=None, keep="last")
      plot_radFinal            label_index(task globs of run and pre_run, csv=None, keep="last") -> {label: task dir}
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', not {keep!r}")
    rx = re.compile(match) if match is not None else None
    out = {}
    for pat in ([patterns] if isinstance(patterns, str) else patterns):
        tasks = glob.glob(pat)
        if sort:
            tasks = sorted(tasks)
        for t in tasks:
            if csv is None:
                f = t
            else:
                g = glob.glob(f"{t}/{csv}")
                if not g:
                    continue
                f = g[0]
            try:
                with open(f"{t}/params.json") as fh:
                    lab = json.load(fh)["label"]
            except (OSError, ValueError):
                continue
            if rx is not None and not rx.search(lab):
                continue
            if csv is not None and min_rows is not None and read_csv(f, min_rows=min_rows) is None:
                continue
            if lab in out:
                if warn:
                    print(f"label_index: label {lab!r} in {out[lab]} and {f}; keeping the {keep}", file=sys.stderr)
                if keep == "first":
                    continue
            out[lab] = f
    return out


# ============================================================================ drops
# Two drop rules are in use (AN-1). They give different counts on 3 of the 66 curves of plot_meshSeries' sets, so
# each script keeps its own mode and threshold until Ian picks one rule:
DROP_MIN_FIG = 10.0     # mA/mm, mode 'any': arrows and marks in the figures and the register (plot_radStep,
                        # plot_radStepSeries, plot_meshDeliverable, testRegister; the archived
                        # archive/analysis_dayfigs/plot_radStepHighlights)
DROP_MIN_TABLE = 8.0    # mA/mm, mode 'hyst': the counts in the KB tables (plot_meshSeries, plot_pocketVolts,
                        # plot_vdcutsDrops, vdcutsDropTable; kb/results/step-search-28v.md, step-mechanism.md)
HYST_START = 1.0        # mA/mm: mode 'hyst' starts an episode at a step that falls by more than this
HYST_CONT = 0.5         # mA/mm: ... and continues it while each step falls by more than this


def drop_episodes(v, i, min_drop, mode):
    """Episodes of falling current in an Id-Vd curve, as (start, end) index pairs with i[start] - i[end] >= min_drop.

    mode 'any' (plot_radStep.drops): an episode is a run of strictly falling points.
    mode 'hyst' (the drops() of plot_meshSeries, plot_pocketVolts, plot_vdcutsDrops and vdcutsDropTable): an
    episode starts at a step that falls by more than HYST_START and continues while each step falls by more than
    HYST_CONT. The three index-returning copies are drop_episodes(v, i, DROP_MIN_TABLE, "hyst").
    """
    out = []
    if mode == "any":
        k = 1
        while k < len(i):
            if i[k] < i[k - 1]:
                a = k - 1
                while k < len(i) and i[k] < i[k - 1]:
                    k += 1
                if i[a] - i[k - 1] >= min_drop:
                    out.append((a, k - 1))
            else:
                k += 1
    elif mode == "hyst":
        k = 0
        while k < len(v) - 1:
            if i[k + 1] < i[k] - HYST_START:
                s = k
                while k < len(v) - 1 and i[k + 1] < i[k] - HYST_CONT:
                    k += 1
                if i[s] - i[k] >= min_drop:
                    out.append((s, k))
            k += 1
    else:
        raise ValueError(f"mode must be 'any' or 'hyst', not {mode!r}")
    return out


def drop_values(v, i, min_drop, mode):
    """drop_episodes as (Vd start, Vd end, Id before, Id after) floats.

    drop_values(v, i, min_drop, "any") is plot_radStep.drops(v, i, min_drop); drop_values(d[:, 0], d[:, 1],
    DROP_MIN_TABLE, "hyst") is plot_meshSeries.drops(d) (which returned numpy floats of the same values).
    """
    return [(float(v[s]), float(v[e]), float(i[s]), float(i[e])) for s, e in drop_episodes(v, i, min_drop, mode)]


# ============================================================================ collapse class
# The 2026-10-01 rule (kb/results/collapse-classification.md), for pulsedIV Id-Vd curves at Vg -2 V.
Collapse = namedtuple("Collapse", "cls onset j at_rest maxloss")


def classify_loss(maxloss):
    """Class from the largest single-step loss: > 95% deep, 50-95% medium, < 50% shallow."""
    return "deep" if maxloss > 0.95 else "medium" if maxloss >= 0.5 else "shallow"


def classify_collapse(vd, idd, ref, vd_max=None, stall_step=0.1, empty_ok=False):
    """Collapse class and onset of one Id-Vd curve, by analyze_onset.py's rule. Returns Collapse(cls, onset, j,
    at_rest, maxloss).

    Points at Vd <= 0.05 V are dropped (the masked curve is v, i). The step losses are 1 - i[n+1]/i[n]; maxloss is
    the largest and sets the class (classify_loss). The onset is v[j+1], where j is the first step whose loss
    reaches the class threshold (0.95 deep, 0.5 medium, maxloss itself for shallow). Then:
    - at_rest = i[0] / Id_ref at v[0], with ref = (Vd, Id) of the trap-free device; below 0.1 the class is
      "off at rest" and the onset NaN;
    - a shallow curve that ends before vd_max - 1e-6 is "stalled" (it gave up at the runaway), with the onset at
      the Vd it could not reach, vd[-1] + stall_step. vd_max=None never stalls.
    j, at_rest and maxloss are returned for every class.

    The policies of the copies:
      analyze_onset     vd_max=p.get("Vd_max", vd[-1]) (so a task without Vd_max never stalls), stall_step 0.1
      plot_posVd, plot_posOnset, plot_posSlides
                        vd_max = the largest Vd_max of the run, stall_step 0.1; plot_posSlides then reports
                        shallow with a NaN onset and calls "off at rest" "off"
      plot_sensitivity  vd_max=p.get("Vd_max"), stall_step=p.get("Vd_step"), empty_ok=True (a curve with one
                        point above 0.05 V is shallow with j 0, maxloss 0 and a NaN onset); it then sets a shallow
                        onset to NaN. Its copy reads p["Vd_max"] and p["Vd_step"] only for a shallow curve, so .get
                        gives the same result wherever the copy ran
      plot_strikeSlides vd_max=None (no stalled class); deep or medium is its "collapse", shallow its "none"
    plot_vgOnset, plot_eTempStd and the archived plot_eTemp use simpler rules of their own and are not covered.
    The pos* and strikeSlides copies test "off at rest" before the step losses; they give the same result except
    on a curve whose losses cannot be computed (one point above 0.05 V, or 0/0 steps), where this function raises
    as analyze_onset does. No curve in results/ is such a curve.
    """
    vr, ir = ref
    m = vd > 0.05
    v, i = vd[m], idd[m]
    at_rest = float(i[0] / np.interp(v[0], vr, ir))
    loss = 1.0 - i[1:] / i[:-1]
    if empty_ok and not len(loss):
        maxloss, cls, j, onset = 0.0, "shallow", 0, np.nan
    else:
        maxloss = float(loss.max())
        cls = classify_loss(maxloss)
        thr = 0.95 if cls == "deep" else 0.5 if cls == "medium" else maxloss
        j = int(np.nonzero(loss >= thr - 1e-12)[0][0])
        onset = float(v[j + 1])
    if at_rest < 0.1:
        cls, onset = "off at rest", np.nan
    elif cls == "shallow" and vd_max is not None and vd[-1] < vd_max - 1e-6:
        cls, onset = "stalled", float(vd[-1] + stall_step)
    return Collapse(cls, onset, j, at_rest, maxloss)


# ============================================================================ reference curves
# Paths as the scripts write them, relative to the repo root (glob patterns where the scripts glob). All of these
# runs used the old field-plate contact box (kb/results/fp-contact-fix.md); the fixed-box reruns are fpFixPre
# (job 52134553) and fpFixEB1 (job 52134554).
LATE_SET = "pulsedIV_tp5.00e+18_tl0.30_ht1.00e-14_eb1.00_my"   # file-name stem of the late-onset set (5e18, 0.30 eV,
                                                               # hotTau 1e-14, hotEb 1.0); the trap y follows


def pre_ref(deck, kind="IdVd"):
    """Pre-irradiation model curve, deck 'sin' or 'hk', kind 'IdVd' or 'IdVg': radMap1 (job 49570571), labels
    sin_ref (task 1) and hk_ref (task 0). The PRE pattern of plot_rad28strike and plot_radStrikeN."""
    return f"results/20261104_radMap1/task_*/{deck}_ref_{kind}.csv"


REF = {
    # pre-irradiation, radMap1 job 49570571 (radIV, Vg +1 V)
    "pre_sin": pre_ref("sin"),
    "pre_hk": pre_ref("hk"),
    "pre_sin_IdVg": pre_ref("sin", "IdVg"),
    "pre_hk_IdVg": pre_ref("hk", "IdVg"),
    # "Nov 11 model": SiN biased, stressed at 17.66 V; radEB1 job 50411481, task 1, label sin_b_eb1
    "nov11_sin": "results/20261109_radEB1/task_*/sin_b_eb1_IdVd.csv",
    # late-onset search round 3 (pulsedIV, field mobility, Vg -2 V): onsetField3 job 44435511 and its Te-ramp
    # rescue onsetField3RetryRamp job 44452288. These params.json files have no label, so the task numbers stay.
    "onset3_notrap": "results/20261002_onsetField3/task_56/pulsedIV_notrap.csv",       # trap-free (trapPeak 1e10)
    "late_y1.0": f"results/20261002_onsetField3/task_17/{LATE_SET}1.000e+00.csv",          # y 1.0 um, deep at 2.3 V
    "late_y2.4": f"results/20261002_onsetField3RetryRamp/task_7/{LATE_SET}2.400e+00.csv",  # y 2.4 um, deep at 3.5 V
    # Oct 27 final SiN biased curve (two steps near 4.5 and 5.8 V on the standard mesh): radFinal11 job 47959281,
    # task 2, label b_sin_p6_s4.5e18 (damPeak 6e18 + dam3Peak 4.5e18). It is plot_radMechanism's bs2 and, by the
    # descriptions in progress.md (2026-10-27, 2026-11-05) and kb/results/rad-model.md, the "standard mesh" curve
    # that radFineFig.py (now archive/analysis_dayfigs/) read from $FINAL_REF; which file that variable named is
    # not recorded. The run is on HPG only (not in the workstation's results/), so this entry is not checked
    # against dashboard/fig/radFine.jpg.
    "radfinal11_sin": "results/20261027_radFinal11/task_2/*_IdVd.csv",
}

# Run F trap set (kb/results/run-F.md) as it appears in late-onset round 1 (field mobility, y 0.2 um)
RUN_F = dict(trapPeak=4e18, trapLevel=0.55, hotTau=1.3e-13, hotEb=0.5)


def run_f_curve(run="results/20261002_onsetField1"):
    """Path of the Run F curve in onsetField1 (job 44359813; task_70): the pulsedIV CSV of the task whose
    params.json matches RUN_F. The loop copied in plot_curveTracer, plot_eTempStd and the archived
    archive/energy_balance/plot_eTemp: tasks in glob.glob order, the last match wins; None if no task matches."""
    f = None
    for t in glob.glob(f"{run}/task_*"):
        with open(f"{t}/params.json") as fh:
            p = json.load(fh)
        if all(p[k] == v for k, v in RUN_F.items()):
            f = glob.glob(f"{t}/pulsedIV_*.csv")[0]
    return f


# ============================================================================ radIV metrics
# The same code as radMetrics.py (whose users are radCompare, radMap, radFit, plot_radFinal and plot_radStrikeN),
# kept here so radMetrics.py can become a re-export of these names.
def vth_gm(vg, idd):
    """Threshold voltage by linear extrapolation at the peak transconductance, and that peak (Id in mA/mm gives
    gm in mS/mm)."""
    o = np.argsort(vg)
    vg, idd = vg[o], idd[o]
    gm = np.gradient(idd, vg)
    k = int(np.argmax(gm))
    return vg[k] - idd[k] / gm[k], gm[k]


def ron_step(d, vmax=0.5):
    """From an Id-Vd array (Vd, Id, Id_ext, ... in V, mA/mm): Ron (ohm*mm) from the slope
    for 0 < Vd <= vmax, then the largest drop between neighbouring points and its Vd."""
    v, i = d[:, IDVD["vd"]], d[:, IDVD["id_ext"]]
    m = (v > 0) & (v <= vmax)
    ron = 1.0e3 / np.polyfit(v[m], i[m], 1)[0] if m.sum() >= 2 else np.nan
    di = np.diff(i)
    k = int(np.argmin(di)) if len(di) else 0
    drop = float(-di[k]) if len(di) and di[k] < 0 else 0.0
    return ron, drop, float(v[k + 1]) if drop > 0 else np.nan


# ---- measured-data guards (2026-11-20, Ian: measured numbers stay out of tracked files of this public repo)
PRIVATE_DIRS = ("figures", "dashboard")


def guard_private_output(path, have_measured):
    """Refuse to write a figure that contains measured data into a tracked folder (figures/, dashboard/)."""
    if not (have_measured and path):
        return
    rel = os.path.relpath(os.path.abspath(path), os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if rel.split(os.sep)[0] in PRIVATE_DIRS:
        raise SystemExit(f"refusing to write measured data to {path}: tracked folder ({rel.split(os.sep)[0]}/) of a public "
                         "repo; write it outside the repo or under data/rad_y2/ (gitignored)")


def load_pre_scalars(targets_path):
    """Measured pre-irradiation scalars (Vth, gm, Ioff) from pre_scalars.csv next to the targets file (untracked)."""
    import csv
    f = os.path.join(os.path.dirname(targets_path), "pre_scalars.csv")
    if not os.path.exists(f):
        return {}
    rows = [r for r in csv.reader(l for l in open(f) if not l.startswith("#")) if r and r[0] != "key"]
    return {k: float(v) for k, v in rows}


# ============================================================================ style
# Each script keeps the palette it has, so its figures do not change. Two sets of greys are in use (V1 and V2 in
# the clean-up plan):
# warm greys, the October trap-map and position-map figures: analyze_onset, analyze_trapMapSets, plot_calib,
# plot_curveTracer, plot_eTempStd, plot_lateIdVd, plot_posOnset, plot_posVd (and the archived plot_eTemp and
# analyze_mobCompare)
INK_WARM, MUTED_WARM, GRID_WARM = "#1a1a19", "#6b6a63", "#e6e5df"
# cool greys, the slide figures and the rad model: plot_deckVg1, plot_headline, plot_posSlides, plot_radFinal,
# plot_radMechanism, plot_sensitivity, plot_strikeSlides, plot_vgOnset
INK_COOL, BODY_COOL, MUTED_COOL, GRID_COOL = "#14171F", "#394150", "#646B78", "#E2E4E9"
BLUE, ORANGE, PALE = "#1B4F9C", "#C2410C", "#B9CBE6"   # with the cool greys: HighK, SiN, a pale blue
DECK_COL = {"highk": BLUE, "sin": ORANGE}              # plot_radFinal and plot_radMechanism COL
STALL_COL = "#eb6834"                                  # stalled / off markers: plot_posVd, plot_posOnset STALL,
                                                       # analyze_trapMapSets OFF
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]   # categorical, plot_calib

# one-hue sequential blue ramp for magnitudes (onset Vd, suppression): analyze_onset, analyze_trapMapSets,
# plot_posVd, plot_posOnset (and the archived analyze_mobCompare)
SEQ_COLORS = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]


def seq_cmap(name="blue_seq"):
    """The SEQ colormap. The name is only a label; analyze_onset calls it "onset", the others "blue_seq"."""
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list(name, SEQ_COLORS)


# lateral spans (y, um) shaded or outlined as gate and field plate in the position-map figures, and the drain edge
GATE, FP = (-0.125, 0.125), (0.285, 0.725)
LGD_DRAIN = 3.285

# 0-3 strike colour ramps (index = number of strikes). There are about six slightly different ramps; these three
# are each used by two scripts. Unifying the ramps changes figures and needs Ian's OK (AN-14).
STRIKE_SIN_28 = ["#f2a66b", "#e0782f", "#b8460f", "#6e2606"]     # plot_rad28strike, plot_radStrikeN: SiN
STRIKE_HK_28 = ["#93bde6", "#4f8ccc", "#245fa3", "#0d376b"]      # plot_rad28strike, plot_radStrikeN: HighK
STRIKE_SIN_STEP = ["#9aa0a8", "#e0782f", "#b8460f", "#5a1d04"]   # plot_radStep RAMP (a dict), plot_radStepFS COL["sin"]


def use_slide_fonts(recursive=True):
    """If HEADLINE_FONT_DIR is set, register its .ttf files with matplotlib and make "Source Sans 3" the font
    family; returns the folder (None if the variable is unset or empty). recursive=False takes only the files
    directly in the folder (os.listdir: plot_headline, plot_posSlides); recursive=True also takes subfolders
    (glob "**/*.ttf": plot_strikeSlides)."""
    d = os.environ.get("HEADLINE_FONT_DIR")
    if not d:
        return None
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    if recursive:
        files = glob.glob(os.path.join(d, "**", "*.ttf"), recursive=True)
    else:
        files = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".ttf")]
    for f in files:
        font_manager.fontManager.addfont(f)
    plt.rcParams["font.family"] = "Source Sans 3"
    return d
