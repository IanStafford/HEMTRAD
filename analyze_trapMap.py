"""Trap map (job 43369760): collapse ratio vs trap location, 3D surface.

For each device: collapse ratio = pre-collapse peak Id / minimum Id after
the peak (Ian's definition). Also computes suppression vs the trap-free
reference device (Id_ref / Id_trap at Vd = 1.6 V), which captures
locations that pinch the channel at rest - there peak/min stays small
even though the device is essentially off from the start.

Writes figures/trapMap_ratios.csv and figures/trapMap_3d.png.
"""
import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

RUN = "results/20260926_trapMap"
CSV_OUT = "figures/trapMap_ratios.csv"
PNG_OUT = "figures/trapMap_3d.png"

# Single-hue sequential ramp (dataviz reference blue, light -> dark).
SEQ = LinearSegmentedColormap.from_list(
    "blue_seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
INK, MUTED = "#1a1a19", "#6b6a63"


def load(path):
    d = np.loadtxt(path, delimiter=",")
    return d[:, 0], d[:, 1]


ref = None
devices = {}
# Retry run (finer Vd step) supersedes the main run where it completed.
for run in (RUN, RUN + "Retry"):
    for task in glob.glob(f"{run}/task_*"):
        p = json.load(open(os.path.join(task, "params.json")))
        csvs = glob.glob(os.path.join(task, "pulsedIV_*.csv"))
        if not csvs:
            continue
        vd, idd = load(csvs[0])
        if p["trapPeak"] < 1e12:
            ref = (vd, idd)
            continue
        key = (p["trapMeanX"], p["trapMeanY"])
        done = abs(vd[-1] - 1.6) < 1e-6
        if key not in devices or done:
            devices[key] = (vd, idd)
rows = [(k[0], k[1], v[0], v[1]) for k, v in devices.items()]

if ref is None:
    raise SystemExit("reference (trap-free) device missing")
vd_ref, id_ref = ref

table = []
for mx, my, vd, idd in rows:
    complete = abs(vd[-1] - 1.6) < 1e-6
    i_pk = int(np.argmax(idd))
    peak = idd[i_pk]
    i_min = i_pk + int(np.argmin(idd[i_pk:]))
    ratio = peak / idd[i_min]
    supp = id_ref[-1] / idd[-1] if complete else np.nan
    table.append((mx, my, peak, vd[i_pk], idd[i_min], vd[i_min], ratio,
                  supp, int(complete)))

table.sort(key=lambda r: (r[0], r[1]))
os.makedirs("figures", exist_ok=True)
with open(CSV_OUT, "w") as f:
    f.write("trapMeanX_um,trapMeanY_um,peak_mA_mm,peak_Vd,min_mA_mm,min_Vd,"
            "collapse_ratio,suppression_vs_ref_1p6V,complete\n")
    for r in table:
        f.write(",".join(f"{v:.6g}" for v in r) + "\n")
print(f"wrote {CSV_OUT} ({len(table)} devices); "
      f"reference Id(1.6V) = {id_ref[-1]:.4g} mA/mm")

# One 3D surface per metric on the (trapMeanY, trapMeanX) grid.
xs = sorted({r[0] for r in table})
ys = sorted({r[1] for r in table})
Y, X = np.meshgrid(ys, np.array(xs) * 1e3)  # depth in nm


def surface(col, zlabel, title, out):
    Z = np.full((len(xs), len(ys)), np.nan)
    for r in table:
        if r[8] and np.isfinite(r[col]):  # non-converged sweeps leave a hole
            Z[xs.index(r[0]), ys.index(r[1])] = np.log10(r[col])
    fig = plt.figure(figsize=(11, 7.5))
    ax = fig.add_subplot(projection="3d")
    ax.plot_surface(Y, X, Z, cmap=SEQ, edgecolor="white", linewidth=0.6,
                    alpha=0.92, vmin=np.nanmin(Z), vmax=np.nanmax(Z))
    ok = np.isfinite(Z)
    ax.scatter(Y[ok], X[ok], Z[ok], color=INK, s=12, depthshade=False)
    bad = ~ok
    if bad.any():
        zfloor = np.nanmin(Z) - 0.5
        ax.scatter(Y[bad], X[bad], np.full(bad.sum(), zfloor), marker="x",
                   color=MUTED, s=40, depthshade=False,
                   label="did not converge")
        ax.legend(loc="upper left", frameon=False, fontsize=9)
    zmin = np.nanmin(Z) - 0.5
    for lo, hi, name, dx in ((-0.125, 0.125, "gate", -0.35),
                             (0.285, 0.725, "field plate", 0.35)):
        ax.plot([lo, hi, hi, lo, lo], [0, 0, 15, 15, 0], [zmin] * 5,
                color=INK, lw=1.4)
        ax.text((lo + hi) / 2 + dx, -3.5, zmin, name, color=INK,
                fontsize=9, ha="center")
    ax.set_xlabel("lateral position trapMeanY (µm)\nsource  \u2192  drain",
                  color=INK, labelpad=10)
    ax.set_ylabel("depth trapMeanX (nm)\nsurface  \u2192  2DEG", color=INK,
                  labelpad=10)
    ax.set_zlabel(zlabel, color=INK, labelpad=8)
    ax.set_zlim(zmin, np.nanmax(Z) + 0.3)
    ax.set_ylim(-4, 15)
    ax.view_init(elev=26, azim=-62)
    ax.set_title(title, color=INK, fontsize=11)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"wrote {out}")


surface(6, "log10(collapse ratio)",
        "Collapse ratio (pre-collapse peak / post-peak min) vs trap location"
        "\nRun F levers, Vg = -2 V, Vd 0-1.6 V", PNG_OUT)
surface(7, "log10(Id_no-trap / Id_trap) at Vd=1.6 V",
        "Current suppression vs trap-free device, by trap location"
        "\nRun F levers, Vg = -2 V", PNG_OUT.replace(".png", "_suppression.png"))
