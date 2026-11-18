"""Field-scaled strikes at the 28 V stress (rounds H/I, 2026-11-18): two figures.

1. <out>_series.png: 0-3 field-scaled strikes over y 0.65 / 0.6 / 0.55 um (round I band b: base 2e18 / 6e17 / 2e17,
   gaussFieldM 4), SiN and HighK, each curve a full-width 2D run. 0 strikes = the 28 V stress damage alone (round C).
2. <out>_segments.png: a WHAT-IF, not a simulation. If each strike collapsed only its own share f of the gate width
   and the columns carried current independently (no spreading between them), the device current would be
   Id = (1 - k f) Id_0 + f sum_i Id_i for k strikes, with Id_i the full-width 2D curve of strike i. Strikes here are
   single field-scaled strikes at y 0.5 um of different density (round I: 3e17, 6e17, 1e18), whose drops start at
   different Vd. Whether one strike can switch that much width is the open 3D question (kb/model/3d-plan.md).

usage: python3 analysis/plot_radStepFS.py [out prefix] [f]
"""
import glob
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RUNS = ("results/20261117_radStepC", "results/20261118_radStepI")
COL = {"sin": ["#9aa0a8", "#e0782f", "#b8460f", "#5a1d04"], "hk": ["#9aa0a8", "#6f9fd8", "#2f62a8", "#12305e"]}
N0 = {"sin": "C_p1.5_N0", "hk": "C_hk_p1.5_n6e18_N0"}


def curves():
    out = {}
    for run in RUNS:
        for t in glob.glob(f"{run}/task_*"):
            try:
                lab = json.load(open(f"{t}/params.json"))["label"]
                f = glob.glob(f"{t}/*_IdVd.csv")[0]
            except (OSError, ValueError, IndexError):
                continue
            d = np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(f) if l.strip()])
            if d.ndim == 2 and len(d) > 2:
                out[lab] = d
    return out


def series(c, out):
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=True)
    for ax, deck, name in zip(axs, ("sin", "hk"), ("SiN", "HighK")):
        for k in range(4):
            lab = N0[deck] if k == 0 else f"I_{deck}_bandb_N{k}"
            d = c.get(lab)
            if d is None:
                continue
            m = d[:, 0] <= 12.0
            ax.plot(d[m, 0], d[m, 1], color=COL[deck][k], lw=2.4 if k else 1.8, ls="-" if k else "--",
                    label=f"{k} strike{'s' if k != 1 else ''}")
        ax.set_title(f"{name}: field-scaled strikes near the gate", fontsize=12)
        ax.set_xlabel("Vd (V)")
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 1050)
        ax.grid(alpha=0.25)
        ax.legend(loc="lower right", fontsize=9.5, frameon=False)
    axs[0].set_ylabel("Id (mA/mm), Vg +1 V")
    fig.tight_layout()
    fig.savefig(out, dpi=170)
    print("wrote", out)


def segments(c, out, f):
    v = np.linspace(0.0, 12.0, 241)
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=True)
    for ax, deck, name in zip(axs, ("sin", "hk"), ("SiN", "HighK")):
        base = c[N0[deck]]
        i0 = np.interp(v, base[:, 0], base[:, 1])
        parts = []
        for n in ("1e+18", "6e+17", "3e+17"):
            d = c[f"I_{deck}_y0.5_n{n}_N1"]
            parts.append(np.interp(v, d[:, 0], d[:, 1]))
        for k in range(4):
            tot = (1.0 - k * f) * i0 + f * sum(parts[:k])
            ax.plot(v, tot, color=COL[deck][k], lw=2.4 if k else 1.8, ls="-" if k else "--",
                    label=f"{k} strike{'s' if k != 1 else ''}")
        ax.set_title(f"{name}: what-if, each strike switches {f:.0%} of the width", fontsize=11.5)
        ax.set_xlabel("Vd (V)")
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 1050)
        ax.grid(alpha=0.25)
        ax.legend(loc="lower right", fontsize=9.5, frameon=False)
    axs[0].set_ylabel("Id (mA/mm), Vg +1 V")
    fig.text(0.5, -0.01, "Not a simulation: weighted sum of full-width 2D curves (strikes 1e18, 6e17, 3e17 at y 0.5 µm, "
             "field-scaled), assuming independent columns.", ha="center", fontsize=9, color="#555")
    fig.tight_layout()
    fig.savefig(out, dpi=170, bbox_inches="tight")
    print("wrote", out)


def main(prefix="figures/rad/step28/fieldscaled", f="0.25"):
    c = curves()
    series(c, f"{prefix}_series.png")
    segments(c, f"{prefix}_segments.png", float(f))


if __name__ == "__main__":
    main(*sys.argv[1:])
