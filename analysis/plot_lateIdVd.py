"""Id-Vd of the latest deep collapses (round 3 + Te-ramp rescue) vs trap-free.

usage: python3 analysis/plot_lateIdVd.py  ->  figures/lateOnset_IdVd.png
"""
import matplotlib.pyplot as plt
import numpy as np

from common import GRID_WARM, INK_WARM, MUTED_WARM, REF

# onsetField3 (job 44435511) and its Te-ramp rescue onsetField3RetryRamp (job 44452288)
CURVES = [
    (REF["onset3_notrap"], "trap-free", "#8a8984", "--"),
    (REF["late_y1.0"], "traps at y = 1.0 µm (deep, 2.3 V)", "#86b6ef", "-"),
    (REF["late_y2.4"], "traps at y = 2.4 µm (deep, 3.5 V; Te-ramp rescue)", "#1c5cab", "-"),
]
INK, MUTED = INK_WARM, MUTED_WARM
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
ax.grid(True, which="major", color=GRID_WARM, lw=0.6)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, fontsize=9, loc="center left")
ax.set_title("Latest deep collapses: 0.30 eV / 5e18 cm⁻³ / hotTau 1e-14 / hotEb 1.0, σ 40 nm, Vg = −2 V",
             fontsize=10, color=INK)
fig.savefig("figures/lateOnset_IdVd.png", dpi=130)
print("wrote figures/lateOnset_IdVd.png")
