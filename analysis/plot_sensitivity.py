"""One-at-a-time trap-model sensitivity (sweeps/pulsedIV_sensitivity.slurm).

Each task changes one lever from the baseline (late set at y = 1.0 um). For every
lever: collapse onset (classify_collapse in analysis/common.py, the rule of analyze_onset.py and
kb/results/collapse-classification.md, with two differences: a stalled run's onset is
Vd_last + Vd_step, and a shallow run has no onset), the deepest Id drop and the drop at
Vd 4 V (trap-free / trapped) and the pre-collapse current relative to trap-free.

usage: python3 analysis/plot_sensitivity.py [run_dir]
  default run_dir results/20261017_sensitivity
Writes figures/sensitivity_metrics.csv, figures/sensitivity.png (one row of
panels per lever) and figures/sensitivity_IdVd.png (Id-Vd per lever).
"""
import csv
import glob
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from common import BLUE, GRID_COOL, INK_COOL, MUTED_COOL, ORANGE, classify_collapse

RUN = sys.argv[1] if len(sys.argv) > 1 else "results/20261017_sensitivity"
LEVERS = ["trapLevel", "trapWidth", "hotEb", "hotTau", "hotMu", "hotVsat",
          "fillIters", "fillRelax"]
UNITS = {"trapLevel": "eV", "trapWidth": "eV", "hotEb": "eV", "hotTau": "s",
         "hotMu": "cm²/Vs", "hotVsat": "cm/s", "fillIters": "", "fillRelax": ""}
LOGX = {"hotTau", "hotMu", "hotVsat"}
INK, MUTED, GRID = INK_COOL, MUTED_COOL, GRID_COOL
VD_DROP = 4.0

ref, base, dev = None, None, []
for t in sorted(glob.glob(f"{RUN}/task_*"), key=lambda s: int(s.rsplit("_", 1)[1])):
    p = json.load(open(os.path.join(t, "params.json")))
    c = glob.glob(os.path.join(t, "pulsedIV_*.csv"))
    if not c or os.path.getsize(c[0]) == 0:
        print(f"no data: {t} ({p['label']})")
        continue
    d = np.loadtxt(c[0], delimiter=",", ndmin=2)
    if p["label"] == "notrap":
        ref = d
    elif p["label"] == "baseline":
        base = (d, p)
    else:
        dev.append((d, p))
if ref is None or base is None:
    raise SystemExit("trap-free reference or baseline missing")
iref = lambda v: np.interp(v, ref[:, 0], ref[:, 1])


def metrics(d, p):
    vd, idd = d[:, 0], d[:, 1]
    m = vd > 0.05
    v, i = vd[m], idd[m]
    # empty_ok: a curve with one point above 0.05 V is shallow with no onset
    c = classify_collapse(vd, idd, (ref[:, 0], ref[:, 1]), vd_max=p.get("Vd_max"),
                          stall_step=p.get("Vd_step"), empty_ok=True)
    cls, onset, maxloss, at_rest, j = c.cls, c.onset, c.maxloss, c.at_rest, c.j
    ipre = float(i[j])
    pre_ratio = ipre / float(iref(v[j]))
    if cls == "shallow":
        onset = np.nan                     # no collapse to speak of
    drop = float(iref(VD_DROP) / idd[-1]) if vd[-1] >= VD_DROP - 1e-6 else np.nan
    maxdrop = float(np.max(iref(v) / i))   # deepest point vs trap-free
    return dict(label=p["label"], cls=cls, onset=onset, maxloss=maxloss,
                maxdrop=maxdrop, drop4V=drop, pre_ratio=pre_ratio, at_rest=at_rest, last_vd=float(vd[-1]))


bm = metrics(*base)
rows = [dict(lever="baseline", value="", **bm)]
by_lever = {k: [] for k in LEVERS}
for d, p in dev:
    lev, val = p["label"].split("=")
    r = dict(lever=lev, value=float(val), **metrics(d, p))
    rows.append(r)
    by_lever[lev].append((r, d))
for lev in LEVERS:                           # add the baseline point to every lever
    by_lever[lev].append((dict(lever=lev, value=float(base[1][lev]), **bm), base[0]))
    by_lever[lev].sort(key=lambda x: x[0]["value"])

os.makedirs("figures", exist_ok=True)
with open("figures/sensitivity_metrics.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(f"{r['lever']:>10} {str(r['value']):>8}  {r['cls']:<11} onset {r['onset']:<5.2g} "
          f"maxdrop {r['maxdrop']:.3g}  drop@4V {r['drop4V']:.3g}  pre {r['pre_ratio']:.2f}  last {r['last_vd']}")

plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})

# --- metrics per lever: onset / drop / pre-collapse ratio --------------------
fig, axs = plt.subplots(3, len(LEVERS), figsize=(2.3 * len(LEVERS), 7), sharey="row")
for c, lev in enumerate(LEVERS):
    pts = by_lever[lev]
    x = np.array([r["value"] for r, _ in pts])
    bx = float(base[1][lev])
    for rr, (key, lab, logy) in enumerate([("onset", "onset Vd (V)", False),
                                           ("maxdrop", "Id drop: deepest (—), at 4 V (--)", True),
                                           ("pre_ratio", "Id before / trap-free", False)]):
        ax = axs[rr, c]
        y = np.array([r[key] for r, _ in pts], float)
        ax.plot(x, y, "-", color=BLUE, lw=2, zorder=2)
        ax.plot(x, y, "o", ms=6, color=BLUE, mec="white", mew=1.5, zorder=3)
        if key == "maxdrop":
            y4 = np.array([r["drop4V"] for r, _ in pts], float)
            ax.plot(x, y4, "--", color=MUTED, lw=1.5, zorder=1)
            ax.plot(x, y4, "o", ms=4, color=MUTED, zorder=1)
        bi = int(np.argmin(abs(x - bx)))
        ax.plot(x[bi], y[bi], "o", ms=8, color=ORANGE, mec="white", mew=1.5, zorder=4)
        for xi, (r, _) in zip(x, pts):       # mark points with no onset
            if key == "onset" and np.isnan(r["onset"]):   # open marker = no collapse to 4 V
                ax.plot(xi, 0.12, "o", ms=6, mfc="white", mec=BLUE, mew=1.5, clip_on=False, zorder=3)
        if lev in LOGX:
            ax.set_xscale("log")
            ax.xaxis.set_minor_formatter(plt.NullFormatter())
            ax.set_xticks(x[::2], [f"{v:.2g}" for v in x[::2]], fontsize=8)
        if logy:
            ax.set_yscale("log")
        if key == "onset":
            ax.set_ylim(0, 4.2)
            pad = 0.05 * (x.max() - x.min())
            if lev not in LOGX:
                ax.set_xlim(x.min() - pad, x.max() + pad)
            else:
                ax.set_xlim(x.min() / 1.15, x.max() * 1.15)
        ax.grid(color=GRID, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        if c == 0:
            ax.set_ylabel(lab)
        if rr == 2:
            ax.set_xlabel(f"{lev} ({UNITS[lev]})" if UNITS[lev] else lev)
fig.suptitle("Trap-model sensitivity, one lever at a time (orange = baseline: "
             "0.30 eV, 5e18, hotEb 1.0, hotTau 1e-14, y 1.0 µm, Vg −2 V; open = no collapse to 4 V)", color=INK, fontsize=11)
fig.tight_layout()
fig.savefig("figures/sensitivity.png", dpi=150)

# --- Id-Vd per lever --------------------------------------------------------
fig, axs = plt.subplots(2, 4, figsize=(15, 7), sharex=True, sharey=True)
for ax, lev in zip(axs.flat, LEVERS):
    ax.semilogy(ref[:, 0], ref[:, 1], color=MUTED, lw=1.5, ls="--", label="trap-free")
    pts = by_lever[lev]
    shades = plt.cm.Blues(np.linspace(0.35, 1.0, len(pts)))
    for (r, d), col in zip(pts, shades):
        isb = r["label"] == "baseline"
        ax.semilogy(d[:, 0], d[:, 1], color=ORANGE if isb else col, lw=2,
                    label=f"{r['value']:g}" + (" (base)" if isb else ""))
    ax.set_title(lev, color=INK, fontsize=11)
    ax.grid(color=GRID, lw=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=7, frameon=False, loc="lower left")
for ax in axs[1]:
    ax.set_xlabel("Vd (V)")
for ax in axs[:, 0]:
    ax.set_ylabel("Id (mA/mm)")
fig.tight_layout()
fig.savefig("figures/sensitivity_IdVd.png", dpi=150)
print("wrote figures/sensitivity.png, figures/sensitivity_IdVd.png, figures/sensitivity_metrics.csv")
