"""Mesh check of the 28 V strike steps (2026-11-19): each case on the library mesh (15 nm at y 0.8), m10 (10 nm
uniform 0.3-2.6 um) and m5fix (library mesh with a true 5 nm at y 0.8). Runs: radStep A-E (library),
meshChkLoad_m10 51939191, meshChkLoad_m5fix 51939192. The label index searches every results/2026111*_radStep* run
and both meshChkLoad runs; a repeated label keeps the first task found. All six cases are also in
plot_meshSeries.SETS, which covers more meshes.
usage: python3 analysis/plot_meshChkSteps.py [out.png]"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import label_index, read_csv

CASES = [("C_p1.5_N0", "stress only"), ("A_p1.5e+18_n6e+18_N1", "1 strike (y 0.8)"),
         ("B_n6e18_N2", "2 strikes (0.8, 1.6)"), ("A_p1.5e+18_n6e+18_N3", "3 strikes (0.8, 1.6, 2.4)"),
         ("E_lev0.4_n6e18_N2", "2 strikes, trap 0.40 eV"), ("C_p1.5_n8e18_N2", "2 strikes, 8e18")]
MESH = [("", "library (15 nm at 0.8)", "#9aa0a8"), ("m10_", "10 nm uniform", "#2f62a8"), ("m5fix_", "5 nm at 0.8", "#b8460f")]

idx = label_index(["results/2026111*_radStep*/task_*", "results/20261118_meshChkLoad_*/task_*"], min_rows=None)

fig, axs = plt.subplots(2, 3, figsize=(14, 7.4), sharex=True)
for ax, (lab, title) in zip(axs.ravel(), CASES):
    for pre, name, col in MESH:
        f = idx.get(pre + lab)
        if not f:
            continue
        d = read_csv(f)
        ax.plot(d[:, 0], d[:, 1], color=col, lw=2.0, label=name)
    ax.set_title(title, fontsize=11)
    ax.set_xlim(0, 12)
    ax.grid(alpha=0.25)
for ax in axs[1]:
    ax.set_xlabel("Vd (V)")
for ax in axs[:, 0]:
    ax.set_ylabel("Id (mA/mm), Vg +1 V")
axs[0, 0].legend(loc="lower right", fontsize=9, frameon=False)
fig.suptitle("SiN, 28 V stress damage (1.5e18) + 6e18 strikes: the same cases on three meshes", fontsize=12)
fig.tight_layout()
out = sys.argv[1] if len(sys.argv) > 1 else "figures/rad/step28/meshchk_steps.png"
fig.savefig(out, dpi=150)
print("wrote", out)
