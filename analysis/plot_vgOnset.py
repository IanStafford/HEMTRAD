"""Collapse onset vs gate bias: Id-Vd (log) for one model at several Vg.

usage: python3 analysis/plot_vgOnset.py out.png "title" label=csv [label=csv ...]
Each csv is a pulsedIV output (Vd, Id mA/mm, peak Te). Onset = Vd of the first
single 0.1 V step that loses >= 95% (deep) or, failing that, >= 50% (medium); otherwise
"none". This is a simpler rule than classify_collapse in analysis/common.py: no "off at
rest" or "stalled" class, and >= 95% rather than > 95% for deep.
Prints one line per curve: label, onset, Id before and after.
"""
import sys

import matplotlib.pyplot as plt
import numpy as np

from common import GRID_COOL, INK_COOL

INK, GRID = INK_COOL, GRID_COOL
COLS = ["#0B2E5E", "#1B4F9C", "#6E9BD8", "#A9BEDF"]


def onset(v, i):
    m = v > 0.05
    v, i = v[m], i[m]
    loss = 1.0 - i[1:] / np.maximum(i[:-1], 1e-30)
    for thr, cls in ((0.95, "deep"), (0.5, "medium")):
        k = np.nonzero(loss >= thr)[0]
        if len(k):
            return cls, v[k[0] + 1], i[k[0]], i[k[0] + 1]
    return "none", np.nan, np.nan, np.nan


out, title, pairs = sys.argv[1], sys.argv[2], sys.argv[3:]
fig, ax = plt.subplots(figsize=(7.5, 4.8))
for n, p in enumerate(pairs):
    lab, f = p.split("=", 1)
    d = np.loadtxt(f, delimiter=",", ndmin=2)
    v, i = d[:, 0], np.abs(d[:, 1])
    cls, o, ib, ia = onset(v, i)
    m = v > 0.05
    ax.semilogy(v[m], i[m], "-o", ms=3.5, lw=1.8, color=COLS[n % 4], label=f"{lab}: {cls} at {o:.1f} V" if cls != "none" else f"{lab}: no collapse")
    print(f"{lab}: {cls} onset {o:.2f} V, Id {ib:.3g} -> {ia:.3g} mA/mm; last Vd {v[-1]:.2f}")
ax.axvspan(0.4, 0.5, color="#F6E1D7", lw=0, label="measured onset at Vg = −2 V")
ax.set_xlabel("Vd (V)")
ax.set_ylabel("Id (mA/mm)")
ax.set_title(title, color=INK, fontsize=11)
ax.grid(color=GRID)
ax.legend(frameon=False, fontsize=8)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(out, dpi=150)
