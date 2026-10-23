"""HighK vs SiN deck with traps at Vg +1 V, Vd 0-10 V (sweeps/pulsedIV_deckVg1.slurm).

usage: python3 analysis/plot_deckVg1.py [run_dir]
  default run_dir results/20261021_deckVg1
Writes figures/deckVg1_IdVd.png: one panel per trap position, HighK solid, SiN
dashed, trap-free references grey.
"""
import glob
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

RUN = sys.argv[1] if len(sys.argv) > 1 else "results/20261021_deckVg1"
INK, MUTED, GRID, BLUE, ORANGE = "#14171F", "#646B78", "#E2E4E9", "#1B4F9C", "#C2410C"

D = {}
for t in glob.glob(f"{RUN}/task_*"):
    p = json.load(open(os.path.join(t, "params.json")))
    d = np.loadtxt(glob.glob(os.path.join(t, "pulsedIV_*.csv"))[0], delimiter=",", ndmin=2)
    D[p["label"]] = d[d[:, 0] > 0.05]       # drop Vd = 0 (Id 0 on a log axis)

plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})
fig, axs = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
for ax, y in zip(axs, ["0.3", "1.0", "2.4"]):
    for deck, col, ls in [("highk", BLUE, "-"), ("sin", ORANGE, "--")]:
        ref, d = D[f"{deck}_notrap"], D[f"{deck}_y{y}"]
        ax.semilogy(ref[:, 0], ref[:, 1], color=MUTED, lw=1.2, ls=ls)
        ax.semilogy(d[:, 0], d[:, 1], color=col, lw=2, ls=ls,
                    label="HighK" if deck == "highk" else "SiN")
    ax.set_title(f"trap at y = {y} µm", color=INK, fontsize=11)
    ax.set_xlabel("Vd (V)")
    ax.grid(color=GRID, lw=0.8)
    ax.spines[["top", "right"]].set_visible(False)
axs[0].set_ylabel("Id (mA/mm)")
axs[0].legend(frameon=False, loc="lower left", title="grey = trap-free")
fig.suptitle("HighK vs SiN passivation, Vg +1 V, trap set 5e18 / 0.30 eV / hotEb 1.0 / hotTau 1e-14 "
             "(job 47062225)", color=INK, fontsize=11)
fig.tight_layout()
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/deckVg1_IdVd.png", dpi=150)
print("wrote figures/deckVg1_IdVd.png")
