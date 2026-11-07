"""What strike placement does on a fine mesh: Id-Vd by position per deck, the current level and Vd/Id against y.
usage: python3 analysis/radPlacementFig.py <out.png> <title> <run> <label pattern with {d} and {y}> y1 y2 ...
"""
import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

out, title, run, pat = sys.argv[1:5]
Y = sys.argv[5:]


def load(r, tag):
    g = glob.glob(f"{r}/task_*/{tag}_IdVd.csv")
    if not g or os.path.getsize(g[0]) == 0:
        return None
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(g[0]) if l.strip()])


EXTRA = {"-0.9": ("results/20261105_radFine", "hk_y-0.9_w0.1_n1.2e19"), "1.5": ("results/20261104_radMesh", "hk_w0.1_m05"),
         "3": ("results/20261105_radFine", "hk_y3.0_w0.1_n1.2e19")}
fig, ax = plt.subplots(1, 4, figsize=(16, 3.9))
cm = plt.get_cmap("viridis")
ys = [float(y) for y in Y]
stats = {}
for a, (d, name) in zip(ax[:2], (("hk", "HighK"), ("sin", "SiN"))):
    r = load("results/20261104_radMap1", f"{d}_ref")
    a.plot(r[:, 0], r[:, 1], color="0.65", lw=1.5, label="undamaged")
    for i, y in enumerate(Y):
        x = load(run, pat.format(d=d, y=y))
        if x is None and d == "hk" and y in EXTRA:
            x = load(*EXTRA[y])  # the same HighK sites were run earlier, under other labels
        if x is None:
            continue
        a.plot(x[:, 0], x[:, 1], color=cm(i / max(1, len(Y) - 1)), lw=1.3, label=f"y {y}" if i % 3 == 0 else None)
        s = x[x[:, 0] >= 3]
        stats[(d, y)] = (s[:, 1].mean() if len(s) else np.nan, x[1, 0] / x[1, 1] * 1e3)
    a.set_title(f"{name}, Vg +1 V", fontsize=11); a.set_xlabel("Vd (V)"); a.set_ylabel("Id (mA/mm)"); a.set_ylim(0, 1080); a.legend(fontsize=7)
for j, (a, t, u) in enumerate(((ax[2], "Current level, 3–10 V mean", "Id (mA/mm)"), (ax[3], "Vd/Id at 0.25 V", "Ω·mm"))):
    for d, c, name, m in (("hk", "#2a78d6", "HighK", "o"), ("sin", "#eb6834", "SiN", "s")):
        v = [stats.get((d, y), (np.nan, np.nan))[j] for y in Y]
        a.plot(ys, v, color=c, marker=m, ms=5, lw=1.5, label=name)
    a.axvspan(-0.125, 0.125, color="0.88", zorder=0); a.set_title(t, fontsize=11); a.set_xlabel("Site centre y (µm), grey = gate"); a.set_ylabel(u); a.legend(fontsize=8); a.set_ylim(bottom=0)
for a in ax:
    a.grid(alpha=0.3)
fig.suptitle(title, fontsize=12, y=1.0)
fig.tight_layout(); fig.savefig(out, dpi=130); print("wrote", out)
for k in sorted(stats, key=lambda k: (k[0], float(k[1]))):
    print(k, "level %.0f  Vd/Id %.2f" % stats[k])
