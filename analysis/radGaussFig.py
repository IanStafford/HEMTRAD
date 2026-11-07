"""Gaussian traps at y 1.0 um, standard mesh against 5 nm, log scale. usage: python3 analysis/radGaussFig.py <out.png>"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load(p):
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(glob.glob(p)[0]) if l.strip()])


G = "results/20261107_radGauss/task_*/pulsedIV_{}.csv"
O = "results/20261021_deckVg1/task_*/pulsedIV_{}.csv"
fig, ax = plt.subplots(1, 3, figsize=(13, 3.9), sharey=True)
nt = load(O.format("highk_notrap"))
P = [("HighK, 0.30 eV, 5e18", O.format("highk_y1.0"), G.format("hk_y1_L0.3_m05")),
     ("SiN, 0.30 eV, 5e18", O.format("sin_y1.0"), G.format("sin_y1_L0.3_m05")),
     ("HighK, 0.55 eV, 4e18", G.format("hk_y1_L0.55"), G.format("hk_y1_L0.55_m05"))]
for a, (t, c, f) in zip(ax, P):
    a.semilogy(nt[1:, 0], nt[1:, 1], color="0.65", lw=1.5, label="no traps")
    d = load(c); a.semilogy(d[1:, 0], np.maximum(d[1:, 1], 1e-6), color="#e0732b", lw=1.6, label="standard mesh")
    d = load(f); a.semilogy(d[1:, 0], np.maximum(d[1:, 1], 1e-6), color="#14325c", lw=1.6, label="5 nm around the trap")
    a.set_title(t, fontsize=11); a.set_xlabel("Vd (V)"); a.grid(alpha=0.3); a.set_ylim(1e-4, 2e3)
ax[0].set_ylabel("Id (mA/mm), Vg +1 V, hotEb 1.0"); ax[0].legend(fontsize=8)
fig.suptitle("Gaussian trap at y 1.0 µm, σ 40 nm", fontsize=12)
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=130); print("wrote", sys.argv[1])
