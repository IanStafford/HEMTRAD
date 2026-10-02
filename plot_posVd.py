"""Per-Vd 3D surfaces: how trap position sets the collapse onset.

One trap set, a grid of positions (trapMeanX depth × trapMeanY lateral). For
each chosen Vd, a surface of suppression vs the trap-free device,
log10(Id_no-trap / Id), capped at the ~1e-8 mA/mm noise floor. A shared z-scale
across all panels makes the frames comparable (and GIF-ready). Each point is
also coloured on the floor by its collapse class / onset (CLAUDE.md §10.0).

usage: python3 plot_posVd.py run_dir tag [Vd list, comma-separated]
  default Vd: 0.3,0.6,...,3.0
Writes figures/<tag>_grid.png (all panels), figures/<tag>_frames/Vd_<v>.png
(one per Vd, for a GIF) and figures/<tag>_onset.png (onset Vd vs position).
"""
import glob
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

RUN, TAG = sys.argv[1], sys.argv[2]
VDS = ([float(v) for v in sys.argv[3].split(",")] if len(sys.argv) > 3
       else [round(0.3 * k, 1) for k in range(1, 11)])
FLOOR = 8.0
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
SEQ = LinearSegmentedColormap.from_list(
    "blue_seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
GATE, FP = (-0.125, 0.125), (0.285, 0.725)
STALL = "#eb6834"

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


def supp_at(vd, idd, v):
    """log10(Id_ref/Id) at Vd=v; NaN if the run stopped before v."""
    if v > vd[-1] + 1e-6:
        return np.nan
    i = np.interp(v, vd, idd)
    return float(np.clip(np.log10(np.interp(v, vr, ir) / max(i, 1e-30)), 0.0, FLOOR))


def onset(vd, idd, vmax):
    """(class, onset Vd) by the §10.0 rule: largest single-step loss sets the
    class; onset = first step reaching the class threshold. A run that gave up
    before vmax without a recorded collapse is "stalled" at the unreached Vd."""
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


Z = {v: np.full(X.shape, np.nan) for v in VDS}
ONS = np.full(X.shape, np.nan)
CLS = np.empty(X.shape, dtype=object)
for (x, y), (vd, idd) in dev.items():
    i, j = xs.index(x), ys.index(y)
    for v in VDS:
        Z[v][i, j] = supp_at(vd, idd, v)
    CLS[i, j], o = onset(vd, idd, VMAX)
    if CLS[i, j] in ("deep", "medium", "stalled"):
        ONS[i, j] = o

plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})


def panel(ax, v):
    z = Z[v]
    ax.plot_surface(Y, X, z, cmap=SEQ, vmin=0, vmax=FLOOR, edgecolor="white",
                    linewidth=0.4, alpha=0.95)
    ok = np.isfinite(z)
    ax.scatter(Y[ok], X[ok], z[ok], color=INK, s=5, depthshade=False)
    if (~ok).any():
        ax.scatter(Y[~ok], X[~ok], np.zeros((~ok).sum()), marker="x", color=STALL, s=28,
                   depthshade=False, label="run stalled before this Vd\n(collapse not resolved)")
        ax.legend(loc="upper left", frameon=False, fontsize=7)
    for lo, hi in (GATE, FP):
        ax.plot([lo, hi, hi, lo, lo], [0, 0, 15, 15, 0], [0] * 5, color=INK, lw=1.0)
    ax.set_zlim(0, FLOOR)
    ax.set_ylim(-1, 16)
    ax.set_xlabel("trap y (µm)\nsource → drain", fontsize=8, labelpad=3)
    ax.set_ylabel("depth (nm)\nsurface → 2DEG", fontsize=8, labelpad=3)
    ax.set_zlabel("log10(Id_no-trap / Id)", fontsize=8, labelpad=2)
    ax.tick_params(labelsize=7)
    ax.view_init(elev=24, azim=-60)
    n = int(np.nansum(z > 1.0))
    ax.set_title(f"Vd = {v:.1f} V   ({n}/{z.size} positions cut >10×)", color=INK, fontsize=10)


title = (f"Collapse spreading across trap positions as Vd rises ({setdesc}, σ 40 nm, "
         "Vg = −2 V, field mobility); outlines: gate, field plate")
ncol = 5
nrow = (len(VDS) + ncol - 1) // ncol
fig = plt.figure(figsize=(4.4 * ncol, 4.2 * nrow))
for k, v in enumerate(VDS):
    panel(fig.add_subplot(nrow, ncol, k + 1, projection="3d"), v)
fig.suptitle(title, color=INK, fontsize=12)
fig.tight_layout()
fig.savefig(f"figures/{TAG}_grid.png", dpi=130)
plt.close(fig)

os.makedirs(f"figures/{TAG}_frames", exist_ok=True)
for v in VDS:
    fig = plt.figure(figsize=(7.5, 6.2))
    panel(fig.add_subplot(1, 1, 1, projection="3d"), v)
    fig.suptitle(setdesc + ", σ 40 nm, Vg = −2 V", color=MUTED, fontsize=9)
    fig.tight_layout()
    fig.savefig(f"figures/{TAG}_frames/Vd_{v:.1f}.png", dpi=120)
    plt.close(fig)

# summary: onset Vd over position (deep/medium), class letters
fig, ax = plt.subplots(figsize=(11, 4.2), constrained_layout=True)
pc = ax.pcolormesh(np.arange(len(ys) + 1) - 0.5, np.arange(len(xs) + 1) - 0.5, ONS,
                   cmap=SEQ, vmin=0, vmax=max(VDS))
lab = {"deep": "D", "medium": "M", "shallow": "S", "off at rest": "off", "stalled": "stall"}
for i in range(len(xs)):
    for j in range(len(ys)):
        c = CLS[i, j]
        if c is None:
            continue
        t = lab[c] + (f"\n{ONS[i, j]:.1f}" if np.isfinite(ONS[i, j]) else "")
        dark = np.isfinite(ONS[i, j]) and ONS[i, j] > 0.6 * max(VDS)
        ax.text(j, i, t, ha="center", va="center", fontsize=8, color="white" if dark else INK)
ax.set_xticks(range(len(ys)))
ax.set_xticklabels([f"{y:g}" for y in ys])
ax.set_yticks(range(len(xs)))
ax.set_yticklabels([f"{x * 1e3:g}" for x in xs])
ax.invert_yaxis()
ax.set_xlabel("trap y (µm), source → drain")
ax.set_ylabel("trap depth (nm)")
ax.set_title(f"Collapse onset Vd by trap position (D deep >95%, M medium, S shallow, off = off at rest,\n"
             f"stall = run stopped at the runaway, collapse probably at that Vd); {setdesc}",
             color=INK, fontsize=10)
fig.colorbar(pc, ax=ax, label="onset Vd (V)")
fig.savefig(f"figures/{TAG}_onset.png", dpi=130)
print(f"{len(dev)} positions; wrote figures/{TAG}_grid.png, {TAG}_frames/, {TAG}_onset.png")
for v in VDS:
    print(f"  Vd {v:.1f}: {int(np.nansum(Z[v] > 1))} positions cut >10x, "
          f"{int(np.isnan(Z[v]).sum())} not reached")
