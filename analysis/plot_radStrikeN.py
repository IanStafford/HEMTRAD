"""Strike-count comparison (radStrikeN, 2026-11-13): final model (biased, 17 V stress, hotEb 1.0) plus 0-3
Gaussian strikes at y 0.8 / 1.6 / 2.4 um, SiN and HighK decks. Id-Vd at Vg +1 V, Id-Vg at Vd (driver default).

usage: python3 analysis/plot_radStrikeN.py <run dir> <out dir>
  <run dir> holds task_*/{sin,hk}_N{0..3}_IdVd.csv (and _IdVg.csv); a missing case is left out.
Writes <out dir>/{sin,hk}_IdVd.png, summary.png and metrics.json.
"""
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from radMetrics import vth_gm  # noqa: E402

PRE = "results/20261104_radMap1/task_*/{d}_ref_{k}.csv"
DECKS = {"sin": ("SiN", ["#f2a66b", "#e0782f", "#b8460f", "#6e2606"]),
         "hk": ("HighK (HPD)", ["#93bde6", "#4f8ccc", "#245fa3", "#0d376b"])}
YS = (0.8, 1.6, 2.4)
plt.rcParams.update({"font.size": 13, "axes.edgecolor": "#8a8f98", "axes.labelcolor": "#2b2f36",
                     "xtick.color": "#4a4f58", "ytick.color": "#4a4f58", "font.family": "DejaVu Sans"})


def load(p):
    f = glob.glob(p)
    if not f:
        return None
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(f[0]) if l.strip()])


def at(d, v):
    return float(np.interp(v, d[:, 0], d[:, 1]))


def main(run, out):
    os.makedirs(out, exist_ok=True)
    met = {}
    for d, (name, ramp) in DECKS.items():
        pre, preg = load(PRE.format(d=d, k="IdVd")), load(PRE.format(d=d, k="IdVg"))
        vth0, gm0 = vth_gm(preg[:, 0], preg[:, 1])
        met[d] = {"pre": {"Id1": at(pre, 1.0), "Id5": at(pre, 5.0), "Id10": at(pre, 10.0), "Vth": vth0, "gm": gm0}}
        fig, ax = plt.subplots(figsize=(7.4, 5.0))
        ax.plot(pre[:, 0], pre[:, 1], color="#9aa0a8", lw=2.0, ls=(0, (5, 3)), label="pre-irradiation")
        ax.annotate("pre", (pre[-1, 0], pre[-1, 1]), xytext=(6, 0), textcoords="offset points",
                    va="center", color="#5b616b", fontsize=12)
        for n in range(4):
            c = load(f"{run}/task_*/{d}_N{n}_IdVd.csv")
            if c is None:
                continue
            ax.plot(c[:, 0], c[:, 1], color=ramp[n], lw=2.0, label=f"{n} strike{'s' if n != 1 else ''}")
            ax.annotate(f"N={n}", (c[-1, 0], c[-1, 1]), xytext=(6, 0), textcoords="offset points",
                        va="center", color="#2b2f36", fontsize=12)
            g = load(f"{run}/task_*/{d}_N{n}_IdVg.csv")
            m = {"Id1": at(c, 1.0), "Id5": at(c, 5.0), "Id10": at(c, 10.0), "Vdmax": float(c[-1, 0])}
            if g is not None:
                v, gmax = vth_gm(g[:, 0], g[:, 1])
                m.update({"Vth": v, "dVth": v - vth0, "gm": gmax, "gm_rel": gmax / gm0})
            dI = np.diff(c[:, 1])
            k = int(np.argmin(dI))
            m.update({"maxdrop": float(-dI[k]) if dI[k] < 0 else 0.0, "Vd_maxdrop": float(c[k + 1, 0])})
            met[d][f"N{n}"] = m
        ax.set_xlim(0, 11.2)
        ax.set_ylim(0, None)
        ax.set_xlabel("Vd (V)")
        ax.set_ylabel("Id (mA/mm)")
        ax.grid(color="#e3e5e8", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, fontsize=12, loc="lower right")
        fig.tight_layout()
        fig.savefig(f"{out}/{d}_IdVd.png", dpi=220)
        plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.6), sharey=True)
    for a, (key, lab) in zip(axs, (("Id1", "Vd 1 V"), ("Id10", "Vd 10 V"))):
        for d, (name, ramp) in DECKS.items():
            ns = [n for n in range(4) if f"N{n}" in met[d]]
            r = [met[d][f"N{n}"][key] / met[d]["pre"][key] for n in ns]
            if ns:
                a.plot(ns, r, color=ramp[2], lw=2.0, marker="o", ms=9, mec="#fbfbf8", mew=2)
                a.annotate(name.split(" ")[0], (ns[-1], r[-1]), xytext=(10, 0), textcoords="offset points",
                           va="center", color="#2b2f36", fontsize=12)
        a.set_title(f"Id / pre-irradiation at {lab}, Vg +1 V", fontsize=13, loc="left")
        a.set_xticks(range(4))
        a.set_xlim(-0.2, 3.6)
        a.set_xlabel("number of strikes")
        a.grid(color="#e3e5e8", lw=0.8)
        a.spines[["top", "right"]].set_visible(False)
    axs[0].set_ylim(0, 1.05)
    fig.tight_layout()
    fig.savefig(f"{out}/summary.png", dpi=220)
    json.dump(met, open(f"{out}/metrics.json", "w"), indent=1)
    for d in met:
        for k, v in met[d].items():
            print(d, k, {a: round(b, 3) for a, b in v.items()})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
