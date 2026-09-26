"""Trap concentration x level x position sweep (job 43373001).

Per device: peak Id, onset Vd (first Vd after the peak where Id < peak/10),
collapse ratio (peak / post-peak min), at-rest fraction (Id / Id_ref at
Vd=0.1 V) and suppression (Id_ref / Id at Vd=3.0 V).

Writes figures/trapConcLevel_metrics.csv, figures/trapConcLevel_IdVd.png
(small multiples, level x concentration) and figures/trapConcLevel_summary.png.
"""
import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

RUN = "results/20260926_trapConcLevel"
VD_END = 3.0
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
LEVEL_COLORS = {0.35: "#2a78d6", 0.55: "#eb6834", 0.75: "#1baf7a"}
# Ordinal single-hue ramp for lateral position (source side light -> drain dark).
POS = LinearSegmentedColormap.from_list(
    "pos", ["#b7d3f6", "#5598e7", "#256abf", "#0d366b"])
GATE = (-0.125, 0.125)
FP = (0.285, 0.725)


def load(path):
    d = np.loadtxt(path, delimiter=",")
    return d[:, 0], d[:, 1]


ref, dev = None, {}
# The retry run (finer Vd step) supersedes the main run wherever it got further.
for run in (RUN, RUN + "Retry"):
    for task in glob.glob(f"{run}/task_*"):
        p = json.load(open(os.path.join(task, "params.json")))
        csvs = glob.glob(os.path.join(task, "pulsedIV_*.csv"))
        if not csvs:
            continue
        vd, idd = load(csvs[0])
        if p["trapPeak"] < 1e12:
            ref = (vd, idd)
            continue
        key = (p["trapPeak"], p["trapLevel"], p["trapMeanY"])
        if key not in dev or vd[-1] > dev[key][0][-1]:
            dev[key] = (vd, idd)
if ref is None:
    raise SystemExit("trap-free reference missing")
vd_ref, id_ref = ref
iref = lambda v: np.interp(v, vd_ref, id_ref)

peaks = sorted({k[0] for k in dev})
levels = sorted({k[1] for k in dev})
ys = sorted({k[2] for k in dev})

rows = []
for (tp, tl, y), (vd, idd) in sorted(dev.items()):
    done = abs(vd[-1] - VD_END) < 1e-6
    ipk = int(np.argmax(idd))
    pk = idd[ipk]
    post = idd[ipk:]
    ratio = pk / post.min()
    below = np.nonzero(post < pk / 10)[0]
    onset = vd[ipk + below[0]] if below.size else np.nan
    at_rest = idd[1] / iref(vd[1])
    supp = iref(VD_END) / idd[-1] if done else np.nan
    # Regime: off at rest (static depletion), hot-electron collapse
    # (conducts at rest, then drops >10x), or unaffected/mild.
    if at_rest < 0.1:
        regime = "off at rest"
        onset = np.nan
    elif np.isfinite(onset):
        regime = "collapse"
    else:
        regime = "no collapse" if done else "incomplete"
    rows.append(dict(regime=regime, trapPeak=tp, trapLevel=tl, trapMeanY=y, complete=int(done),
                     last_Vd=vd[-1], peak_mA_mm=pk, peak_Vd=vd[ipk],
                     onset_Vd=onset, collapse_ratio=ratio,
                     at_rest_frac=at_rest, suppression_3V=supp))

os.makedirs("figures", exist_ok=True)
cols = list(rows[0])
with open("figures/trapConcLevel_metrics.csv", "w") as f:
    f.write(",".join(cols) + "\n")
    for r in rows:
        f.write(",".join(r[c] if isinstance(r[c], str) else f"{r[c]:.6g}"
                         for c in cols) + "\n")
print(f"{len(rows)} devices, {sum(r['complete'] for r in rows)} complete; "
      f"ref Id(3V)={iref(VD_END):.4g} mA/mm")

plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})


def style(ax):
    ax.grid(True, color=GRID, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1) Id-Vd small multiples: rows = level, cols = concentration.
fig, axs = plt.subplots(len(levels), len(peaks), figsize=(13, 10),
                        sharex=True, sharey=True, constrained_layout=True)
norm = plt.Normalize(0, len(ys) - 1)
for i, tl in enumerate(levels):
    for j, tp in enumerate(peaks):
        ax = axs[i, j]
        ax.plot(vd_ref[1:], id_ref[1:], color=MUTED, ls="--", lw=1.8,
                label="no traps")
        for k, y in enumerate(ys):
            if (tp, tl, y) not in dev:
                continue
            vd, idd = dev[(tp, tl, y)]
            ax.plot(vd[1:], idd[1:], color=POS(norm(k)), lw=1.6,
                    label=f"y = {y:g} µm")
        ax.set_yscale("log")
        ax.set_ylim(1e-9, 300)
        style(ax)
        if i == 0:
            ax.set_title(f"trapPeak = {tp:.0e} cm⁻³", color=INK)
        if j == 0:
            ax.set_ylabel(f"trapLevel = {tl} eV\nId (mA/mm)")
        if i == len(levels) - 1:
            ax.set_xlabel("Vd (V)")
h, l = axs[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc="outside right center", frameon=False,
           title="trap position\n(source → drain)", fontsize=8)
fig.suptitle("Id-Vd by trap concentration (columns), level (rows) and "
             "lateral position (shade) - x = 0, Vg = -2 V\n",
             color=INK, fontsize=11, x=0.01, ha="left")
fig.savefig("figures/trapConcLevel_IdVd.png", dpi=140)
plt.close(fig)

# 2) Summary vs position: onset, log suppression, at-rest fraction.
metrics = [("onset_Vd", "collapse onset Vd (V)\n(only devices that conduct at rest)", False),
           ("suppression_3V", "Id_no-trap / Id at 3 V", True),
           ("at_rest_frac", "Id / Id_no-trap at Vd = 0.1 V", True)]
fig, axs = plt.subplots(len(metrics), len(peaks), figsize=(13, 9.5),
                        sharex=True, sharey="row", constrained_layout=True)
for j, tp in enumerate(peaks):
    for i, (key, lab, logy) in enumerate(metrics):
        ax = axs[i, j]
        for lo, hi in (GATE, FP):
            ax.axvspan(lo, hi, color=GRID, alpha=0.6, lw=0)
        for tl in levels:
            pts = [(r["trapMeanY"], r[key]) for r in rows
                   if r["trapPeak"] == tp and r["trapLevel"] == tl]
            x, v = zip(*sorted(pts))
            ax.plot(x, v, color=LEVEL_COLORS[tl], lw=2, marker="o", ms=5,
                    mec="white", mew=0.8, label=f"{tl} eV")
        if logy:
            ax.set_yscale("log")
        style(ax)
        if i == 0:
            ax.set_title(f"trapPeak = {tp:.0e} cm⁻³", color=INK)
            ax.text(0, 0.97, "gate", transform=ax.get_xaxis_transform(),
                    ha="center", va="top", color=MUTED, fontsize=8)
            ax.text(np.mean(FP), 0.97, "field\nplate",
                    transform=ax.get_xaxis_transform(), ha="center",
                    va="top", color=MUTED, fontsize=8)
        if j == 0:
            ax.set_ylabel(lab)
        if i == len(metrics) - 1:
            ax.set_xlabel("trap position trapMeanY (µm), source → drain")
h, l = axs[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc="outside lower center", ncol=3, frameon=False,
           title="trapLevel (below Ec)")
fig.suptitle("Collapse metrics vs trap position, by concentration and level"
             " (x = 0, Vg = -2 V, Vd 0-3 V)\n", color=INK, fontsize=11,
             x=0.01, ha="left")
fig.savefig("figures/trapConcLevel_summary.png", dpi=140)
plt.close(fig)
print("wrote figures/trapConcLevel_{metrics.csv,IdVd.png,summary.png}")
from collections import Counter
for tp in peaks:
    for tl in levels:
        c = Counter(r["regime"] for r in rows
                    if r["trapPeak"] == tp and r["trapLevel"] == tl)
        print(f"  {tp:.0e} {tl}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
