"""3D onset surface: does each trap position collapse during the sweep, and at what Vd.

Same trap-position grid as plot_posVd.py (trapMeanX depth × trapMeanY lateral),
but z is no longer the suppression at one Vd. Each position is classed once
(CLAUDE.md §10.0 rule, as in plot_posVd.py): it collapses if its largest single
0.1 V step loses >= 50% (deep or medium), or if it stalled at the runaway (collapse
probably at the stall Vd). Shallow and off-at-rest positions do not collapse in
the sweep and sit flat on the floor. Height = Vd_max + 0.1 - onset, so the
earliest collapse is the highest peak; the z ticks are labelled in onset Vd.

usage: python3 analysis/plot_posOnset.py run_dir tag
Writes figures/<tag>_onset3d.png (final state) and figures/<tag>_onset3d_frames/Vd_<v>.png,
one frame per 0.1 V in which positions rise as they collapse (GIF via make_gif.py).
"""
import glob
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

RUN, TAG = sys.argv[1], sys.argv[2]
INK, MUTED, FLOORC = "#1a1a19", "#6b6a63", "#e9e8e3"
SEQ = LinearSegmentedColormap.from_list(
    "blue_seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
GATE, FP = (-0.125, 0.125), (0.285, 0.725)
STALL, OFF = "#eb6834", "#6b6a63"

ref, dev, setdesc, VMAX = None, {}, "", 0.0
for t in glob.glob(f"{RUN}/task_*") + glob.glob(f"{RUN}Retry*/task_*"):
    p = json.load(open(os.path.join(t, "params.json")))
    c = glob.glob(os.path.join(t, "pulsedIV_*.csv"))
    if not c or os.path.getsize(c[0]) == 0:
        continue
    d = np.loadtxt(c[0], delimiter=",", ndmin=2)
    if p["trapPeak"] < 1e12:
        ref = (d[:, 0], d[:, 1])
        continue
    VMAX = max(VMAX, p.get("Vd_max", d[-1, 0]))
    setdesc = (f"{p['trapPeak']:.0e} cm⁻³, {p['trapLevel']} eV, hotTau {p['hotTau']:g} s, "
               f"hotEb {p['hotEb']} eV")
    k = (p["trapMeanX"], p["trapMeanY"])
    if k not in dev or d[-1, 0] > dev[k][0][-1]:
        dev[k] = (d[:, 0], d[:, 1])
if ref is None:
    raise SystemExit("trap-free reference missing")
vr, ir = ref
xs = sorted({k[0] for k in dev})
ys = sorted({k[1] for k in dev})
Y, X = np.meshgrid(ys, np.array(xs) * 1e3)


def onset(vd, idd, vmax):
    """(class, onset Vd), identical to plot_posVd.py."""
    m = vd > 0.05
    v, i = vd[m], idd[m]
    if i[0] / np.interp(v[0], vr, ir) < 0.1:
        return "off at rest", np.nan
    loss = 1.0 - i[1:] / i[:-1]
    mx = loss.max()
    cls = "deep" if mx > 0.95 else "medium" if mx >= 0.5 else "shallow"
    if cls == "shallow" and vd[-1] < vmax - 1e-6:
        return "stalled", float(vd[-1] + 0.1)
    thr = 0.95 if cls == "deep" else 0.5 if cls == "medium" else mx
    return cls, float(v[1 + np.nonzero(loss >= thr - 1e-12)[0][0]])


ONS = np.full(X.shape, np.nan)
CLS = np.empty(X.shape, dtype=object)
for (x, y), (vd, idd) in dev.items():
    i, j = xs.index(x), ys.index(y)
    CLS[i, j], o = onset(vd, idd, VMAX)
    if CLS[i, j] in ("deep", "medium", "stalled"):
        ONS[i, j] = o
TOP = VMAX + 0.1                       # height of a collapse at Vd = 0
n_col = int(np.isfinite(ONS).sum())
n_tot = int(sum(c is not None for c in CLS.flat))
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})


def panel(ax, upto):
    """Surface with every position that has collapsed by Vd = upto raised to its height."""
    up = np.isfinite(ONS) & (ONS <= upto + 1e-6)
    h = np.where(up, TOP - np.nan_to_num(ONS), 0.0)
    fc = np.empty(X.shape + (4,))
    fc[:] = plt.matplotlib.colors.to_rgba(FLOORC)
    fc[up] = SEQ(h[up] / TOP)
    ax.plot_surface(Y, X, h, facecolors=fc, edgecolor="white", linewidth=0.4, shade=False)
    ax.scatter(Y[up], X[up], h[up], color=INK, s=6, depthshade=False)
    st = up & (CLS == "stalled")
    if st.any():
        ax.scatter(Y[st], X[st], h[st], marker="x", color=STALL, s=40, depthshade=False)
    off = CLS == "off at rest"
    if off.any():
        ax.scatter(Y[off], X[off], np.zeros(off.sum()), marker="s", color=OFF, s=14, depthshade=False)
    for lo, hi in (GATE, FP):
        ax.plot([lo, hi, hi, lo, lo], [0, 0, 15, 15, 0], [0] * 5, color=INK, lw=1.0)
    ax.set_zlim(0, TOP)
    ticks = [v for v in np.arange(0.5, VMAX + 1e-6, 0.5)]
    ax.set_zticks([TOP - v for v in ticks])
    ax.set_zticklabels([f"{v:.1f}" for v in ticks])
    ax.set_ylim(-1, 16)
    ax.set_xlabel("trap y (µm)\nsource → drain", fontsize=8, labelpad=3)
    ax.set_ylabel("depth (nm)\nsurface → 2DEG", fontsize=8, labelpad=3)
    ax.set_zlabel("collapse onset Vd (V)\nhigher = earlier", fontsize=8, labelpad=4)
    ax.tick_params(labelsize=7)
    ax.view_init(elev=24, azim=-60)
    leg = [Line2D([], [], marker="s", ls="", color=FLOORC, markeredgecolor=MUTED, ms=7,
                  label="no collapse in the sweep (flat)")]
    if (CLS == "stalled").any():
        leg.append(Line2D([], [], marker="x", ls="", color=STALL, ms=7, label="stalled at the runaway"))
    if off.any():
        leg.append(Line2D([], [], marker="s", ls="", color=OFF, ms=5, label="off at rest"))
    ax.legend(handles=leg, loc="upper left", frameon=False, fontsize=7)


for final in (True, False):
    steps = [VMAX] if final else [round(0.1 * k, 1) for k in range(1, int(round(VMAX * 10)) + 1)]
    if not final:
        os.makedirs(f"figures/{TAG}_onset3d_frames", exist_ok=True)
    for v in steps:
        fig = plt.figure(figsize=(7.5, 6.2))
        ax = fig.add_subplot(1, 1, 1, projection="3d")
        panel(ax, v)
        k = int(np.sum(np.isfinite(ONS) & (ONS <= v + 1e-6)))
        ax.set_title(f"Collapsed by Vd = {v:.1f} V: {k}/{n_tot} positions" if not final else
                     f"Collapse onset by trap position: {n_col}/{n_tot} collapse by {VMAX:.1f} V",
                     color=INK, fontsize=10)
        fig.suptitle(setdesc + ", σ 40 nm, Vg = −2 V; outlines: gate, field plate", color=MUTED, fontsize=8)
        fig.tight_layout()
        out = f"figures/{TAG}_onset3d.png" if final else f"figures/{TAG}_onset3d_frames/Vd_{v:.1f}.png"
        fig.savefig(out, dpi=130 if final else 120)
        plt.close(fig)
print(f"{n_tot} positions, {n_col} collapse by {VMAX} V; earliest {np.nanmin(ONS):.1f} V, "
      f"latest {np.nanmax(ONS):.1f} V; wrote figures/{TAG}_onset3d.png and {TAG}_onset3d_frames/")
