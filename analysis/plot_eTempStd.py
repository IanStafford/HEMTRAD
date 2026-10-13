"""Trap study with the standard energy balance (eTemp 1, etStats 0, etThermo 0).

usage: python3 analysis/plot_eTempStd.py [run_dir]   (default results/20261013_eTempStd1)
Writes figures/eTempStd_IdVd.png: one panel per trap set (Run F, late set at
y 1.0 and 2.4 µm), Id-Vd for tau 1 / 0.3 / 0.1 ps against the old local-field
model (dashed) and the Oct 8 etStats-1 run at tau 1 ps (dotted). Prints onset,
collapse depth and the post-collapse trend per run.
"""
import glob
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
RUN = sys.argv[1] if len(sys.argv) > 1 else "results/20261013_eTempStd1"
OLDE = "results/20261008_eTemp1"
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
SET = "pulsedIV_tp5.00e+18_tl0.30_ht1.00e-14_eb1.00_my"
R3 = "results/20261002_onsetField3"
OLD = {"late10": f"{R3}/task_17/{SET}1.000e+00.csv",
       "late24": f"{R3}RetryRamp/task_7/{SET}2.400e+00.csv"}
for t in glob.glob("results/20261002_onsetField1/task_*"):
    p = json.load(open(f"{t}/params.json"))
    if p["trapPeak"] == 4e18 and p["trapLevel"] == 0.55 and p["hotTau"] == 1.3e-13 and p["hotEb"] == 0.5:
        OLD["runF"] = glob.glob(f"{t}/pulsedIV_*.csv")[0]
TITLE = {"runF": "Run F (4e18, 0.55 eV, y 0.2 µm)",
         "late10": "Late set at y = 1.0 µm (5e18, 0.30 eV)",
         "late24": "Late set at y = 2.4 µm (5e18, 0.30 eV)"}
TAUS = [("1e-12", "τ 1 ps", "#0d366b"), ("3e-13", "τ 0.3 ps", "#3987e5"), ("1e-13", "τ 0.1 ps", "#86b6ef")]


def load(f):
    if not f or not os.path.exists(f) or os.path.getsize(f) == 0:
        return None
    d = np.loadtxt(f, delimiter=",", ndmin=2)
    m = d[:, 0] > 0.05
    return d[m, 0], d[m, 1]


def onset(v, i):
    """First step losing >95% (deep), else the largest step; depth = pre / min after."""
    loss = 1 - i[1:] / i[:-1]
    k = np.nonzero(loss > 0.95)[0]
    k = k[0] if len(k) else int(np.argmax(loss))
    pre = i[k]
    after = i[k + 1:]
    return v[k + 1], pre, pre / after.min(), after


print(f"{'run':16s} {'lastVd':>6s} {'onset':>6s} {'Id pre':>8s} {'1st step':>9s} {'depth':>9s}  Id at 1 / 2 / 4 V")
fig, axs = plt.subplots(1, 3, figsize=(14, 4.6), constrained_layout=True, sharey=True)
plt.rcParams.update({"font.size": 9.5})
for ax, base in zip(axs, ("runF", "late10", "late24")):
    o = load(OLD.get(base))
    if o:
        ax.semilogy(o[0], o[1], "--", color=MUTED, lw=1.2, label="local-field model (Oct 2)")
    e = load(f"{OLDE}/{base}_t1e-12/pulsedIV_{base}_t1e-12.csv")
    if e:
        ax.semilogy(e[0], e[1], ":", color=MUTED, lw=1.6, label="ETemp, etStats 1 (Oct 8, τ 1 ps)")
    for tau, lab, c in TAUS:
        tag = f"{base}_t{tau}"
        r = load(f"{RUN}/{tag}/pulsedIV_{tag}.csv")
        if not r:
            continue
        v, i = r
        ax.semilogy(v, i, "-", color=c, lw=2, label=lab)
        ov, pre, depth, after = onset(v, i)
        step = pre / after[0]
        g = lambda x: f"{np.interp(x, v, i):.2e}" if v[-1] >= x - 1e-6 else "-"
        print(f"{tag:16s} {v[-1]:6.1f} {ov:6.1f} {pre:8.2f} {step:9.1e} {depth:9.1e}  {g(1)} / {g(2)} / {g(4)}")
    ax.set_title(TITLE[base], color=INK, fontsize=10)
    ax.set_xlabel("Vd (V)")
    ax.set_xlim(0, 4)
    ax.set_ylim(1e-9, 400)
    ax.grid(True, color=GRID, lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axs[0].set_ylabel("Id (mA/mm)")
axs[1].legend(frameon=False, fontsize=8, loc="center right")
fig.suptitle("Trap study with the standard energy balance (eTemp 1, etStats 0, etThermo 0), Vg = −2 V",
             color=INK)
fig.savefig("figures/eTempStd_IdVd.png", dpi=130)
print("wrote figures/eTempStd_IdVd.png")
