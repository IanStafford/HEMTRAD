"""Id-Vd of damaged sections on the standard and fine meshes (radMesh).
usage: python3 analysis/radMeshFig.py <radMap1_dir> <radMesh_dir> <out.png>
"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

mp, ms, out = sys.argv[1:4]


def load(run, tag):
    g = glob.glob(f"{run}/task_*/{tag}_IdVd.csv")
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(g[0]) if l.strip()])


P = [("0.3 µm at y 3.0 µm, 4e18", (mp, "hk_y3.00_n4e+18"), "hk_y3.00_m10", "hk_y3.00_m05"),
     ("0.3 µm at y −0.9 µm, 4e18", (mp, "hk_y-0.90_n4e+18"), "hk_y-0.90_m10", "hk_y-0.90_m05"),
     ("0.1 µm at y 1.5 µm, 1.2e19", (ms, "hk_w0.1"), "hk_w0.1_m10", "hk_w0.1_m05")]
ref = load(mp, "hk_ref")
fig, axes = plt.subplots(1, 3, figsize=(12, 3.9), sharey=True)
for ax, (t, c, m10, m05) in zip(axes, P):
    ax.plot(ref[:, 0], ref[:, 1], color="0.65", lw=1.5, label="undamaged")
    d = load(*c); ax.plot(d[:, 0], d[:, 1], color="#e0732b", lw=1.8, label="standard mesh")
    d = load(ms, m10); ax.plot(d[:, 0], d[:, 1], color="#2a78d6", lw=1.8, label="10 nm in the site")
    d = load(ms, m05); ax.plot(d[:, 0], d[:, 1], color="#14325c", lw=1.8, ls="--", label="5 nm in the site")
    ax.set_title(t, fontsize=11); ax.set_xlabel("Vd (V)"); ax.grid(alpha=0.3)
axes[0].set_ylabel("Id (mA/mm), HighK, Vg +1 V")
axes[0].legend(fontsize=8)
fig.tight_layout(); fig.savefig(out, dpi=130); print("wrote", out)
