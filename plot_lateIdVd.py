"""Id-Vd of the latest deep collapses (round 3 + Te-ramp rescue) vs trap-free.

usage: python3 plot_lateIdVd.py  ->  figures/lateOnset_IdVd.png
"""
import matplotlib.pyplot as plt
import numpy as np

R = "results/20261002_onsetField3"
SET = "pulsedIV_tp5.00e+18_tl0.30_ht1.00e-14_eb1.00_my"
CURVES = [
    (f"{R}/task_56/pulsedIV_notrap.csv", "trap-free", "#8a8984", "--"),
    (f"{R}/task_17/{SET}1.000e+00.csv", "traps at y = 1.0 µm (deep, 2.3 V)", "#86b6ef", "-"),
    (f"{R}RetryRamp/task_7/{SET}2.400e+00.csv", "traps at y = 2.4 µm (deep, 3.5 V; Te-ramp rescue)", "#1c5cab", "-"),
]
INK, MUTED = "#1a1a19", "#6b6a63"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.labelcolor": INK})
fig, ax = plt.subplots(figsize=(7.5, 4.6), constrained_layout=True)
for f, lab, c, ls in CURVES:
    d = np.loadtxt(f, delimiter=",", ndmin=2)
    m = d[:, 0] > 0.05
    ax.semilogy(d[m, 0], d[m, 1], ls, color=c, lw=2, marker="o" if ls == "-" else None,
                ms=3, label=lab)
ax.set_xlabel("Vd (V)")
ax.set_ylabel("Id (mA/mm)")
ax.set_xlim(0, 4)
ax.grid(True, which="major", color="#e6e5df", lw=0.6)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, fontsize=9, loc="center left")
ax.set_title("Latest deep collapses: 0.30 eV / 5e18 cm⁻³ / hotTau 1e-14 / hotEb 1.0, σ 40 nm, Vg = −2 V",
             fontsize=10, color=INK)
fig.savefig("figures/lateOnset_IdVd.png", dpi=130)
print("wrote figures/lateOnset_IdVd.png")
