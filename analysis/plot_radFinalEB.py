"""Final rad model as of 2026-11-11 (the "Nov 11 model"): hotEb 1.0, 10 nm from y 0.3 to 2.0 um. Id-Vd at Vg +1 V
per deck: pre-irradiation (radMap1, job 49570571), non-biased and biased (radEB1, job 50411481). Both runs used the
old field-plate contact box (kb/results/fp-contact-fix.md).
usage: python3 analysis/plot_radFinalEB.py <out.png>"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import BLUE, ORANGE, pre_ref, read_csv


def load(p):
    """The first file matching the glob p; IndexError if there is none."""
    return read_csv(glob.glob(p)[0])


fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.9), sharey=True)
for a, (d, name, col, nb) in zip(ax, (("hk", "HighK (HPD)", BLUE, "nb_highk_eb1"), ("sin", "SiN", ORANGE, "nb_sin_eb1"))):
    p = load(pre_ref(d)); a.plot(p[:, 0], p[:, 1], color="0.6", lw=1.6, label="pre-irradiation")
    n = load(f"results/20261109_radEB1/task_*/{nb}_IdVd.csv"); a.plot(n[:, 0], n[:, 1], color=col, lw=1.4, ls="--", label="non-biased")
    b = load(f"results/20261109_radEB1/task_*/{d}_b_eb1_IdVd.csv"); a.plot(b[:, 0], b[:, 1], color=col, lw=2.0, label="biased")
    a.set_title(f"{name}, Vg +1 V", fontsize=11); a.set_xlabel("Vd (V)"); a.grid(alpha=0.3)
ax[0].set_ylabel("Id (mA/mm)"); ax[1].legend(fontsize=9)
fig.suptitle("Final model: capture barrier 1.0 eV, 10 nm mesh from y 0.3 to 2.0 µm", fontsize=12)
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=130); print("wrote", sys.argv[1])
