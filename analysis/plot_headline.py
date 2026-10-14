"""Headline figure for talks: the late set at y = 2.4 µm with the standard energy
balance, against the measured collapse window.

usage: python3 analysis/plot_headline.py [run_dir]   (default results/20261013_eTempStd1)
Writes figures/eTempStd_headline.png: Id-Vd for tau 1 / 0.3 / 0.1 ps (job 45768739),
the old local-field model (dashed, Oct 2) and the measured onset window
(0.4-0.5 V, ~1000x drop on the pulsed curve tracer) as a shaded band.
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

RUN = sys.argv[1] if len(sys.argv) > 1 else "results/20261013_eTempStd1"
OLD = ("results/20261002_onsetField3RetryRamp/task_7/"
       "pulsedIV_tp5.00e+18_tl0.30_ht1.00e-14_eb1.00_my2.400e+00.csv")
INK, MUTED, GRID, MEAS = "#14171F", "#646B78", "#E2E4E9", "#C2410C"
TAUS = [("1e-12", "τ 1 ps", "#0B2E5E"), ("3e-13", "τ 0.3 ps", "#1B4F9C"), ("1e-13", "τ 0.1 ps", "#6E9BD8")]


def load(f):
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        return None
    d = np.loadtxt(f, delimiter=",", ndmin=2)
    m = d[:, 0] > 0.05
    return d[m, 0], d[m, 1]


plt.rcParams.update({"font.size": 15, "axes.edgecolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.labelcolor": INK})
fig, ax = plt.subplots(figsize=(10.4, 6.6), constrained_layout=True)
ax.axvspan(0.4, 0.5, color=MEAS, alpha=0.16, lw=0)
ax.text(0.55, 3e-5, "measured collapse\n0.4–0.5 V, ~1000×", color=MEAS, fontsize=15,
        va="center", ha="left", fontweight="semibold")
o = load(OLD)
if o:
    ax.semilogy(o[0], o[1], "--", color=MUTED, lw=1.6)
    ax.text(0.95, 1.9e2, "local-field model (Oct 2): no collapse until 3.5 V", color=MUTED,
            fontsize=13, ha="left", va="bottom")
for tau, lab, c in TAUS:
    tag = f"late24_t{tau}"
    r = load(f"{RUN}/{tag}/pulsedIV_{tag}.csv")
    if r:
        v, i = r
        k = v <= 2.0
        ax.semilogy(v[k], i[k], "-", color=c, lw=2.6)
        j = np.argmin(abs(v - 1.9))
        ax.text(2.04, i[j], lab, color=c, fontsize=14, va="center", ha="left", fontweight="semibold")
ax.set_xlim(0, 2.45)
ax.set_ylim(1e-6, 600)
ax.set_xlabel("Vd (V)")
ax.set_ylabel("Id (mA/mm)")
ax.grid(True, color=GRID, lw=0.8)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.savefig("figures/eTempStd_headline.png", dpi=150)
print("wrote figures/eTempStd_headline.png")
