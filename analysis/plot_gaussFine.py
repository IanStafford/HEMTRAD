"""Oct 29 deck trap set (Gaussian, 0.30 eV, 5e18, hotEb 1.0) on 5 nm, both decks, y 1.0 and 2.4 um.
usage: python3 analysis/plot_gaussFine.py <out.png>"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load(p):
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(glob.glob(p)[0]) if l.strip()])


fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.9), sharey=True)
for a, y in zip(ax, ("1", "2.4")):
    for d, name, col in (("highk", "HighK", "#1b4f9c"), ("sin", "SiN", "#c2410c")):
        n = load(f"results/20261021_deckVg1/task_*/pulsedIV_{d}_notrap.csv")
        a.plot(n[1:, 0], n[1:, 1], color=col, lw=1.0, ls=":", label=f"{name}, no traps")
    for d, name, col in (("hk", "HighK", "#1b4f9c"), ("sin", "SiN", "#c2410c")):
        t = load(f"results/20261107_radGauss/task_*/pulsedIV_{d}_y{y}_L0.3_m05.csv")
        a.plot(t[1:, 0], t[1:, 1], color=col, lw=1.8, label=f"{name}, trap")
    a.set_title(f"Trap at y = {y} µm, Vg +1 V", fontsize=11); a.set_xlabel("Vd (V)"); a.grid(alpha=0.3)
ax[0].set_ylabel("Id (mA/mm)"); ax[0].legend(fontsize=8)
fig.suptitle("Same trap set on a 5 nm mesh", fontsize=12)
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=130); print("wrote", sys.argv[1])
