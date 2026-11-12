"""Final set vs deeper trap levels and a smaller damage scale, SiN biased (radExp1). usage: python3 analysis/plot_radExp1.py <out.png>"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load(p):
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(glob.glob(p)[0]) if l.strip()])


fig, ax = plt.subplots(1, 2, figsize=(11, 3.9), sharey=True)
pre = load("results/20261104_radMap1/task_*/sin_ref_IdVd.csv")
for a in ax:
    a.plot(pre[:, 0], pre[:, 1], color="0.65", lw=1.5, label="pre-irradiation")
    f = load("results/20261109_radEB1/task_*/sin_b_eb1_IdVd.csv"); a.plot(f[:, 0], f[:, 1], color="#c2410c", lw=2, label="final model (0.30 eV, 7e18)")
for lab, p, c in (("0.40 eV", "results/20261111_radExp1c/task_*/sin_L0.4_os_IdVd.csv", "#2a78d6"), ("0.50 eV", "results/20261111_radExp1c/task_*/sin_L0.5_os_IdVd.csv", "#14325c")):
    d = load(p); ax[0].plot(d[:, 0], d[:, 1], color=c, lw=1.7, label=lab)
for lab, p, c in (("4.5e18", "sin_p4.5e+18", "#9ec5ee"), ("3e18", "sin_p3e+18", "#5a9be0"), ("2e18", "sin_p2e+18", "#14325c")):
    d = load(f"results/20261111_radExp1/task_*/{p}_IdVd.csv"); ax[1].plot(d[:, 0], d[:, 1], color=c, lw=1.7, label=f"scale {lab}")
ax[0].set_title("SiN biased: deeper trap level", fontsize=11); ax[1].set_title("SiN biased: smaller damage scale", fontsize=11)
for a in ax:
    a.set_xlabel("Vd (V)"); a.grid(alpha=0.3); a.legend(fontsize=8)
ax[0].set_ylabel("Id (mA/mm), Vg +1 V")
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=130); print("wrote", sys.argv[1])
