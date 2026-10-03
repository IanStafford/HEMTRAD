"""Curve-tracer Id-Vd at other gate voltages (job 44573629), one folder per Vg.

usage: python3 plot_curveTracer.py [run_dir]   (default results/20261003_curveTracer)
For each Vg in the run writes figures/Vg_<Vg>V/curveTracer_Vg<Vg>V.png (log and
linear Id-Vd of the four key devices, with the Vg = -2 V curve of each device as
a thin dashed line for reference) and copies the CSVs there. Vg = -2 V results
stay in figures/ (the default).
"""
import glob
import json
import os
import shutil
import sys

import matplotlib.pyplot as plt
import numpy as np

RUN = sys.argv[1] if len(sys.argv) > 1 else "results/20261003_curveTracer"
# Vg = -2 V counterparts (all 0-4 V)
SET = "pulsedIV_tp5.00e+18_tl0.30_ht1.00e-14_eb1.00_my"
R3 = "results/20261002_onsetField3"
M2 = {"notrap": f"{R3}/task_56/pulsedIV_notrap.csv",
      "late_y1.0": f"{R3}/task_17/{SET}1.000e+00.csv",
      "late_y2.4": f"{R3}RetryRamp/task_7/{SET}2.400e+00.csv",
      "runF": None}
DEV = [("notrap", "trap-free", "#8a8984"),
       ("late_y1.0", "late-onset set, y = 1.0 µm", "#86b6ef"),
       ("late_y2.4", "late-onset set, y = 2.4 µm", "#1c5cab"),
       ("runF", "Run F (4e18 / 0.55 eV, y = 0.2 µm)", "#d0752a")]
INK, MUTED = "#1a1a19", "#6b6a63"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.labelcolor": INK})

# Run F at Vg -2: the exact Run F set in late-onset round 1 (field mobility, 0-4 V)
for t in glob.glob("results/20261002_onsetField1/task_*"):
    p = json.load(open(f"{t}/params.json"))
    if (p["trapPeak"] == 4e18 and p["trapLevel"] == 0.55 and p["hotTau"] == 1.3e-13
            and p["hotEb"] == 0.5):
        M2["runF"] = glob.glob(f"{t}/pulsedIV_*.csv")[0]


def load(f):
    d = np.loadtxt(f, delimiter=",", ndmin=2)
    m = d[:, 0] > 0.05
    return d[m, 0], d[m, 1]


runs = {}
for t in sorted(glob.glob(f"{RUN}/Vg*_*")):
    p = json.load(open(f"{t}/params.json"))
    c = glob.glob(f"{t}/pulsedIV_*.csv")
    if c and os.path.getsize(c[0]) > 0:
        runs.setdefault(p["Vg_meas"], {})[p["devTag"]] = c[0]

for vg, devs in sorted(runs.items()):
    out = f"figures/Vg_{vg:g}V"
    os.makedirs(out, exist_ok=True)
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8), constrained_layout=True)
    for ax, log in zip(axs, (True, False)):
        for tag, lab, col in DEV:
            if M2.get(tag) and os.path.exists(M2[tag]):
                v, i = load(M2[tag])
                ax.plot(v, i, "--", color=col, lw=1, alpha=0.6)
            if tag in devs:
                v, i = load(devs[tag])
                ax.plot(v, i, "-", color=col, lw=2, marker="o" if tag != "notrap" else None,
                        ms=3, label=lab)
        if log:
            ax.set_yscale("log")
        ax.set_xlim(0, 4)
        ax.set_xlabel("Vd (V)")
        ax.set_ylabel("Id (mA/mm)")
        ax.grid(True, color="#e6e5df", lw=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axs[1].plot([], [], "--", color=MUTED, lw=1, label="same device at Vg = −2 V")
    axs[1].legend(frameon=False, fontsize=9, loc="upper left")
    fig.suptitle(f"Curve tracer, Vg = {vg:g} V (solid) vs −2 V (dashed); field mobility, "
                 "late-onset set = 0.30 eV / 5e18 / hotTau 1e-14 / hotEb 1.0", color=INK, fontsize=11)
    fig.savefig(f"{out}/curveTracer_Vg{vg:g}V.png", dpi=130)
    plt.close(fig)
    for tag, c in devs.items():
        shutil.copy(c, f"{out}/{os.path.basename(c)}")
    print(f"wrote {out}/curveTracer_Vg{vg:g}V.png ({len(devs)} devices)")
