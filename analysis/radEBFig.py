"""Final parameter set at hotEb 0.5 and 1.0 on the 10 nm mesh. usage: python3 analysis/radEBFig.py <out.png>"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load(p):
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(glob.glob(p)[0]) if l.strip()])


P = [("HighK, biased", "results/20261104_radMap1/task_*/hk_ref", "results/20261107_radChk2/task_*/hk_b_m10", "results/20261109_radEB1/task_*/hk_b_eb1", None),
     ("SiN, biased, one site", "results/20261104_radMap1/task_*/sin_ref", "results/20261107_radChk2/task_*/sin_b_m10", "results/20261109_radEB1/task_*/sin_b_eb1", "results/20261109_radEB1/task_*/sin_b_eb0.75"),
     ("SiN, biased, two sites", "results/20261104_radMap1/task_*/sin_ref", "results/20261105_radFine/task_*/sin_final_m10", "results/20261109_radEB1/task_*/sin_final_eb1", None)]
fig, ax = plt.subplots(1, 3, figsize=(13, 3.9), sharey=True)
for a, (t, pre, e5, e1, e75) in zip(ax, P):
    for p, c, ls, lab in ((pre, "0.65", "-", "pre-irradiation"), (e5, "#2a78d6", "-", "hotEb 0.5 (final model)"),
                          (e75, "#9ec5ee", "--", "hotEb 0.75"), (e1, "#eb6834", "-", "hotEb 1.0")):
        if p:
            d = load(p + "_IdVd.csv"); a.plot(d[:, 0], d[:, 1], color=c, ls=ls, lw=1.7, label=lab)
    m5 = {"SiN, biased, one site": "sin_b_eb1_m05", "SiN, biased, two sites": "sin_final_eb1_m05"}.get(t)
    if m5:
        d = load(f"results/20261109_radEB2/task_*/{m5}_IdVd.csv"); a.plot(d[:, 0], d[:, 1], color="#7a2e0e", ls=":", lw=1.7, label="hotEb 1.0, 5 nm")
    a.set_title(t, fontsize=11); a.set_xlabel("Vd (V)"); a.grid(alpha=0.3)
ax[0].set_ylabel("Id (mA/mm), Vg +1 V"); ax[1].legend(fontsize=8)
fig.suptitle("Final parameter set, 10 nm mesh from y 0.3 to 2.0 µm (dotted: 5 nm)", fontsize=12)
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=130); print("wrote", sys.argv[1])
