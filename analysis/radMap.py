"""Damage-region maps from radIV runs with uniform sites (damSites).

usage: python3 analysis/radMap.py <run_dir>... --csv out.csv [--plot out.png] [--xlabel TEXT]
Per task: Vth, gm, Ron, Id at 1/4/10 V (Vg +1), the largest step in Id-Vd and any give-up
Vd. Each deck's task with no damage (label *_ref) is the reference for the changes.
Site position is the mean y of the task's damSites; several sites are listed in the CSV.
"""
import csv
import glob
import json
import os
import re
import sys

import numpy as np

from radMetrics import ron_step, vth_gm

args = sys.argv[1:]
def opt(name):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]
        return v
    return None
out, plot, xlabel = opt("--csv"), opt("--plot"), opt("--xlabel") or "Site centre y (um)"
COLS = ["dVth", "gm_ratio", "Ron_ratio", "Id1_ratio", "Id4_ratio", "Id10_ratio", "drop_mAmm", "dropVd", "lastVd"]


def task_metrics(t):
    m = {}
    f = glob.glob(os.path.join(t, "*_IdVg.csv"))
    if f and os.path.getsize(f[0]) > 0:
        d = np.loadtxt(f[0], delimiter=",", ndmin=2)
        if len(d) > 5:
            m["Vth"], m["gm"] = vth_gm(d[:, 0], d[:, 1])
            m["Ioff"] = float(d[np.argmin(d[:, 0]), 2])
    f = glob.glob(os.path.join(t, "*_IdVd.csv"))
    if f and os.path.getsize(f[0]) > 0:
        d = np.loadtxt(f[0], delimiter=",", ndmin=2)
        m["Ron"], m["drop_mAmm"], m["dropVd"] = ron_step(d)
        for v in (1.0, 4.0, 10.0):
            m[f"Id{v:g}"] = float(np.interp(v, d[:, 0], d[:, 2])) if d[-1, 0] >= v - 1e-6 else np.nan
        m["lastVd"] = float(d[-1, 0])
    return m


def sites(p):
    return [[float(x) for x in s.split()] for s in re.findall(r"\{([^{}]+)\}", p.get("damSites", ""))]


rows = []
for a in args:
    for t in sorted(glob.glob(f"{a}/task_*"), key=lambda s: int(s.rsplit("_", 1)[1])):
        p = json.load(open(os.path.join(t, "params.json")))
        s = sites(p)
        rows.append(dict(label=p["label"], deck="SiN" if "SiN" in p.get("deviceDeck", "") else "HighK",
                         y=np.mean([(q[0] + q[1]) / 2 for q in s]) if s else np.nan,
                         N=s[0][4] if s else 0.0, nsites=len(s), sites=p.get("damSites", ""),
                         **task_metrics(t)))
refs = {r["deck"]: r for r in rows if r["label"].endswith("_ref")}
for r in rows:
    b = refs.get(r["deck"], {})
    r["dVth"] = r.get("Vth", np.nan) - b.get("Vth", np.nan)
    for k, n in (("gm", "gm_ratio"), ("Ron", "Ron_ratio"), ("Id1", "Id1_ratio"), ("Id4", "Id4_ratio"), ("Id10", "Id10_ratio")):
        r[n] = r.get(k, np.nan) / b.get(k, np.nan)
keys = ["label", "deck", "y", "N", "nsites"] + COLS + ["Vth", "gm", "Ron", "Id1", "Id4", "Id10", "Ioff", "sites"]
if out:
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, keys, extrasaction="ignore", restval="")
        w.writeheader()
        w.writerows(rows)
    print("wrote", out)
print(f"{'label':<28}" + "".join(f"{c:>11}" for c in COLS))
for r in rows:
    print(f"{r['label']:<28}" + "".join(f"{r.get(c, np.nan):>11.3g}" for c in COLS))

if plot:
    import matplotlib.pyplot as plt
    C = {"HighK": "#2a78d6", "SiN": "#e0732b"}
    STY = ["-", "--", ":"]
    fig, axs = plt.subplots(2, 3, figsize=(13, 6.5), sharex=True)
    panels = [("dVth", "Vth change (V)"), ("gm_ratio", "gm / reference"), ("Ron_ratio", "Ron / reference"),
              ("Id4_ratio", "Id at Vd 4 V / reference"), ("Id10_ratio", "Id at Vd 10 V / reference"), ("dropVd", "Vd of largest step (V)")]
    dens = sorted({r["N"] for r in rows if r["nsites"] == 1})
    for ax, (k, title) in zip(axs.flat, panels):
        for deck in C:
            for i, n in enumerate(dens):
                q = sorted((r for r in rows if r["deck"] == deck and r["N"] == n and r["nsites"] == 1), key=lambda r: r["y"])
                if q:
                    ax.plot([r["y"] for r in q], [r.get(k, np.nan) for r in q], STY[i % 3], color=C[deck], lw=2, marker="o", ms=4,
                            label=f"{deck}, {n:g} cm$^{{-3}}$")
        ax.axvspan(-0.125, 0.125, color="0.9", zorder=0)
        ax.set_title(title, fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.2)
    for ax in axs[1]:
        ax.set_xlabel(xlabel)
    axs[0, 0].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(plot, dpi=150)
    print("wrote", plot)
