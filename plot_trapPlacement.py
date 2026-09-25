"""Plot the trap-placement study (job 43366825) against radPlot1.

One panel per trap depth (trapMeanX); one line per lateral position
(trapMeanY). Reads results/20260925_trapPlacement/task_*/ on the workstation.
"""
import glob
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

RUN = "results/20260925_trapPlacement"
OUT = sys.argv[1] if len(sys.argv) > 1 else "figures/trapPlacement.png"

# Reference categorical palette, slots 1-5 in fixed order (dataviz skill).
Y_COLORS = {0.125: "#2a78d6", 0.20: "#eb6834", 0.285: "#1baf7a",
            0.725: "#eda100", 2.0: "#e87ba4"}
Y_LABELS = {0.125: "gate edge (0.125)", 0.20: "0.20 (Run F)",
            0.285: "FP left (0.285)", 0.725: "FP right (0.725)",
            2.0: "access (2.0)"}
X_TITLES = {0.0: "AlGaN surface (x=0)", 0.0075: "mid-AlGaN (x=0.0075)",
            0.015: "2DEG interface (x=0.015)"}
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"


def load(path):
    d = np.loadtxt(path, delimiter=",")
    return d[:, 0], d[:, 1]


runs = {}
for task in sorted(glob.glob(f"{RUN}/task_*")):
    p = json.load(open(os.path.join(task, "params.json")))
    csv = glob.glob(os.path.join(task, "pulsedIV_*.csv"))[0]
    runs[(p["trapMeanX"], p["trapMeanY"])] = load(csv)

vd_t, id_t = load("figures/radPlot1.csv")

plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})
fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), sharey=True,
                         constrained_layout=True)

for ax, mx in zip(axes, sorted(X_TITLES)):
    ax.plot(vd_t[1:], id_t[1:], color=MUTED, lw=2, ls="--",
            label="radPlot1 (target)", zorder=1)
    for my in sorted(Y_COLORS):
        vd, idd = runs[(mx, my)]
        ax.plot(vd[1:], idd[1:], color=Y_COLORS[my], lw=2, marker="o",
                ms=4, mec="white", mew=0.8, label=Y_LABELS[my], zorder=2)
    ax.set_yscale("log")
    ax.set_ylim(1e-5, 100)
    ax.set_xlim(0, 1.65)
    ax.set_title(X_TITLES[mx], color=INK, fontsize=11, loc="left")
    ax.set_xlabel("Vd (V)")
    ax.grid(True, which="major", color=GRID, lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

axes[0].set_ylabel("Id (mA/mm)")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="outside lower center", ncol=6,
           frameon=False, title="trapMeanY (µm)", title_fontsize=9)
fig.suptitle("Trap placement vs. collapse (Run F levers, Vg = -2 V)",
             color=INK, fontsize=12, x=0.01, ha="left")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=150)
print(f"wrote {OUT}")
