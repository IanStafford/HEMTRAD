"""Id-Vd curves of a position map, one panel per deck.
usage: python3 analysis/radCurves.py <run_dir> <out.png>   (radMap1-style labels)
Line colour runs with site position; solid is the higher density, dotted the lower.
"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

run, out = sys.argv[1], sys.argv[2]
YS = ["-0.90", "-0.30", "0.00", "0.30", "0.90", "1.80", "3.00"]


def load(tag):
    g = glob.glob(f"{run}/task_*/{tag}_IdVd.csv")
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(g[0]) if l.strip()])


fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
cm = plt.get_cmap("viridis")
for ax, (d, name) in zip(axes, (("hk", "HighK"), ("sin", "SiN"))):
    r = load(f"{d}_ref")
    ax.plot(r[:, 0], r[:, 1], color="k", lw=2, label="reference")
    for i, y in enumerate(YS):
        c = cm(i / (len(YS) - 1))
        x = load(f"{d}_y{y}_n1e+18")
        ax.plot(x[:, 0], x[:, 1], color=c, lw=1, ls=":")
        x = load(f"{d}_y{y}_n4e+18")
        ax.plot(x[:, 0], x[:, 1], color=c, lw=1.6, label=f"y {y} um")
    ax.set_title(f"{name}: Id-Vd at Vg +1 V (solid 4e18, dotted 1e18 cm$^{{-3}}$)", fontsize=11)
    ax.set_xlabel("Vd (V)")
    ax.grid(alpha=0.3)
axes[0].set_ylabel("Id (mA/mm)")
axes[0].legend(fontsize=8)
fig.tight_layout()
fig.savefig(out, dpi=130)
print("wrote", out)
