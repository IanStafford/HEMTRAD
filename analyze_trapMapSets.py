"""3D trap maps at several trap concentrations/levels (job 43513462).

Per device: collapse depth vs trap-free (Id_no-trap / Id at the post-collapse
minimum - the plotted collapse metric), collapse ratio (pre-collapse peak /
post-peak min, kept for reference; it inflates late collapses), suppression
(Id_no-trap / Id at Vd=3 V), at-rest fraction (Id / Id_no-trap at 0.1 V),
regime, and the number of solver retries pulsedIV.tcl needed.

Collapse metrics are only meaningful for devices that conduct at rest; devices
that are off at rest (at-rest fraction < 0.1) are left as holes in the
collapse surface and marked on the floor.

Writes figures/trapMapSets_metrics.csv, one figure per set
(figures/trapMapSets_tp<peak>_tl<level>.png) and two overviews
(figures/trapMapSets_overview_{depth,suppression}.png).
"""
import glob
import json
import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# usage: python3 analyze_trapMapSets.py [run_dir [tag]]  (default: the 10n field-mobility
# Run F map; the static 10f run is results/archive_static_mobility/20260927_trapMapSets)
RUN = sys.argv[1] if len(sys.argv) > 1 else "results/20261001_trapMapF_field"
TAG = sys.argv[2] if len(sys.argv) > 2 else "trapMapF_field"
VD_END = 3.0
SEQ = LinearSegmentedColormap.from_list(
    "blue_seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
INK, MUTED, OFF = "#1a1a19", "#6b6a63", "#eb6834"
GATE, FP = (-0.125, 0.125), (0.285, 0.725)


def load(path):
    d = np.loadtxt(path, delimiter=",", ndmin=2)
    return d[:, 0], d[:, 1]


ref, dev = None, {}
# The solver-side retry run supersedes the main run wherever it got further.
for task in glob.glob(f"{RUN}/task_*") + glob.glob(f"{RUN}Retry/task_*"):
    p = json.load(open(os.path.join(task, "params.json")))
    csvs = glob.glob(os.path.join(task, "pulsedIV_*.csv"))
    if not csvs or os.path.getsize(csvs[0]) == 0:
        continue
    vd, idd = load(csvs[0])
    if p["trapPeak"] < 1e12:
        ref = (vd, idd)
        continue
    tid = int(task.rsplit("_", 1)[1])
    out = glob.glob(f"{os.path.dirname(task)}/slurm_*_{tid}.out")
    retries = 0
    if out:
        m = re.findall(r"retries=(\d+)", open(out[0], errors="ignore").read())
        retries = int(m[-1]) if m else 0
    key = (p["trapPeak"], p["trapLevel"], p["trapMeanX"], p["trapMeanY"])
    if key not in dev or vd[-1] > dev[key][0][-1]:
        dev[key] = (vd, idd, retries)
if ref is None:
    raise SystemExit("trap-free reference missing")
vd_ref, id_ref = ref
iref = lambda v: np.interp(v, vd_ref, id_ref)

rows = []
for (tp, tl, mx, my), (vd, idd, nre) in sorted(dev.items()):
    done = abs(vd[-1] - VD_END) < 1e-6
    ipk = int(np.argmax(idd))
    pk = idd[ipk]
    post = idd[ipk:]
    at_rest = idd[1] / iref(vd[1]) if len(vd) > 1 else np.nan
    imin = ipk + int(np.argmin(post))
    # Collapse depth vs a trap-free device at the same Vd, taken at the
    # post-collapse minimum. Unlike peak/min it doesn't reward late onsets
    # (whose pre-collapse peak is higher only because Id rises with Vd).
    depth = iref(vd[imin]) / idd[imin]
    below = np.nonzero(post < pk / 10)[0]
    onset = vd[ipk + below[0]] if below.size else np.nan
    if at_rest < 0.1:
        regime, ratio, onset, depth = "off at rest", np.nan, np.nan, np.nan
    else:
        ratio = pk / post.min()
        regime = "collapse" if np.isfinite(onset) else (
            "no collapse" if done else "incomplete")
        if regime == "incomplete":  # stopped before its collapse resolved
            ratio = depth = np.nan
    supp = iref(VD_END) / idd[-1] if done else np.nan
    rows.append(dict(trapPeak=tp, trapLevel=tl, trapMeanX=mx, trapMeanY=my,
                     regime=regime, complete=int(done), last_Vd=vd[-1],
                     retries=nre, peak_mA_mm=pk, onset_Vd=onset,
                     collapse_ratio=ratio, collapse_depth_vs_ref=depth,
                     min_Vd=vd[imin], at_rest_frac=at_rest,
                     suppression_3V=supp))

os.makedirs("figures", exist_ok=True)
cols = list(rows[0])
with open(f"figures/{TAG}_metrics.csv", "w") as f:
    f.write(",".join(cols) + "\n")
    for r in rows:
        f.write(",".join(r[c] if isinstance(r[c], str) else f"{r[c]:.6g}"
                         for c in cols) + "\n")

sets = sorted({(r["trapPeak"], r["trapLevel"]) for r in rows})
xs = sorted({r["trapMeanX"] for r in rows})
ys = sorted({r["trapMeanY"] for r in rows})
Y, X = np.meshgrid(ys, np.array(xs) * 1e3)  # depth in nm
print(f"{len(rows)} devices, {sum(r['complete'] for r in rows)} complete, "
      f"{sum(r['retries'] > 0 for r in rows)} needed retries; "
      f"ref Id(3V)={iref(VD_END):.4g} mA/mm")


def grid(tp, tl, key):
    Z = np.full((len(xs), len(ys)), np.nan)
    off = np.zeros_like(Z, dtype=bool)
    inc = np.zeros_like(Z, dtype=bool)
    for r in rows:
        if (r["trapPeak"], r["trapLevel"]) != (tp, tl):
            continue
        i, j = xs.index(r["trapMeanX"]), ys.index(r["trapMeanY"])
        off[i, j] = r["regime"] == "off at rest"
        inc[i, j] = r["regime"] == "incomplete"
        v = r[key]
        if np.isfinite(v) and v > 0:
            Z[i, j] = np.log10(v)
    return Z, off, inc


def panel(ax, Z, off, inc, zlim, zlabel, title):
    ok = np.isfinite(Z)
    if ok.sum() >= 4:
        ax.plot_surface(Y, X, Z, cmap=SEQ, vmin=zlim[0], vmax=zlim[1],
                        edgecolor="white", linewidth=0.5, alpha=0.92)
    ax.scatter(Y[ok], X[ok], Z[ok], color=INK, s=9, depthshade=False)
    floor = zlim[0]
    if off.any() and "minimum" in zlabel:
        ax.scatter(Y[off], X[off], np.full(off.sum(), floor), marker="x",
                   color=OFF, s=30, depthshade=False, label="off at rest")
    if inc.any():
        ax.scatter(Y[inc], X[inc], np.full(inc.sum(), floor), marker="^",
                   color=MUTED, s=28, depthshade=False,
                   label="did not converge at collapse")
    if (off.any() and "minimum" in zlabel) or inc.any():
        ax.legend(loc="upper left", frameon=False, fontsize=8)
    for lo, hi in (GATE, FP):
        ax.plot([lo, hi, hi, lo, lo], [0, 0, 15, 15, 0], [floor] * 5,
                color=INK, lw=1.1)
    ax.set_zlim(*zlim)
    ax.set_ylim(-1, 15)
    ax.set_xlabel("trapMeanY (µm)\nsource → drain", fontsize=8, labelpad=4)
    ax.set_ylabel("depth (nm)\nsurface → 2DEG", fontsize=8, labelpad=4)
    ax.set_zlabel(zlabel, fontsize=8, labelpad=4)
    ax.tick_params(labelsize=7)
    ax.view_init(elev=26, azim=-62)
    ax.set_title(title, color=INK, fontsize=10)


def zrange(key):
    v = [np.log10(r[key]) for r in rows if np.isfinite(r[key]) and r[key] > 0]
    return (min(v) - 0.3, max(v) + 0.3) if v else (0, 1)


ZR, ZS = zrange("collapse_depth_vs_ref"), zrange("suppression_3V")
RL = "log10(Id_no-trap / Id) at the\npost-collapse minimum"
SL = "log10(Id_no-trap / Id)\nat Vd = 3 V"

for tp, tl in sets:
    fig = plt.figure(figsize=(14, 6.2))
    for k, (key, zl, lab, zr) in enumerate(
            (("collapse_depth_vs_ref", RL,
              "Collapse depth vs trap-free (at the collapse)", ZR),
             ("suppression_3V", SL, "Suppression vs trap-free", ZS))):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        Z, off, inc = grid(tp, tl, key)
        panel(ax, Z, off, inc, zr, zl, lab)
    fig.suptitle(f"trapPeak = {tp:.0e} cm⁻³, trapLevel = {tl} eV "
                 "(Run F hot-electron levers, Vg = -2 V, Vd 0-3 V)"
                 "  -  gate and field plate outlined on the floor",
                 color=INK, fontsize=11)
    fig.tight_layout()
    out = f"figures/{TAG}_tp{tp:.0e}_tl{tl}.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print("wrote", out)

for key, zl, zr, name in ((("collapse_depth_vs_ref", RL, ZR, "depth"),
                           ("suppression_3V", SL, ZS, "suppression")) if len(sets) > 1 else ()):
    ncol = 3
    nrow = (len(sets) + ncol - 1) // ncol
    fig = plt.figure(figsize=(6.2 * ncol, 5.4 * nrow))
    for k, (tp, tl) in enumerate(sets):
        ax = fig.add_subplot(nrow, ncol, k + 1, projection="3d")
        Z, off, inc = grid(tp, tl, key)
        panel(ax, Z, off, inc, zr, zl, f"{tp:.0e} cm⁻³, {tl} eV")
    fig.suptitle(f"{'Collapse depth vs trap-free, at the post-collapse minimum' if name == 'depth' else 'Suppression vs trap-free at Vd = 3 V'}"
                 " by trap location, for each trap concentration / level"
                 " (shared z-scale)", color=INK, fontsize=12)
    fig.tight_layout()
    out = f"figures/{TAG}_overview_{name}.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print("wrote", out)

from collections import Counter
for tp, tl in sets:
    c = Counter(r["regime"] for r in rows if (r["trapPeak"], r["trapLevel"]) == (tp, tl))
    print(f"  {tp:.0e} {tl}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
