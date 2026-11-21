"""Why the strike curves step (2026-11-19): voltage across each damaged spot ("pocket") of the 2DEG against Vd, from
the per-Vd lateral-field cuts of vdCuts runs (drivers/radIV.tcl vdCuts=1, cut 1 nm below the AlGaN/GaN interface).
The voltage across a pocket is the integral of |Ey| over its y range. Top row: Id-Vd with each drop marked and
labelled by the pocket that switches (drops: mode 'hyst' of common.drop_episodes, at least 8 mA/mm). Bottom row:
the pocket voltages; a pocket switches (its barrier traps fill with hot electrons) when about 0.5 V sits across it.
usage: python3 analysis/plot_pocketVolts.py <out.png> <title>=<task dir> [<title>=<task dir> ...]
The title's leading digit is the number of strikes (0-3): only the stress band and the first that many strike
spots are drawn, so an undamaged stretch of channel is not shown as a pocket."""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import vdcuts
from common import DROP_MIN_TABLE, drop_episodes

# y ranges (um) and Okabe-Ito colours, fixed order
POCKETS = [("stress band (y 0.45-0.72)", (0.45, 0.72), "#4d4d4d"),
           ("strike at y 0.8", (0.72, 1.1), "#E69F00"),
           ("strike at y 1.6", (1.45, 1.85), "#0072B2"),
           ("strike at y 2.4", (2.25, 2.65), "#009E73")]
THR = 0.5


def pocket_volts(c):
    vds = sorted(c)
    out = np.zeros((len(vds), len(POCKETS)))
    for r, vd in enumerate(vds):
        y, e = c[vd]["Ey"]
        o = np.argsort(y)
        y, e = y[o], e[o]
        for k, (_, (a, b), _) in enumerate(POCKETS):
            m = (y >= a) & (y < b)
            out[r, k] = np.trapezoid(e[m], y[m]) * 1.0e-4
    return np.array(vds), out


def main(out, *cols):
    cols = [a.split("=", 1) for a in cols]
    fig, axs = plt.subplots(2, len(cols), figsize=(3.6 * len(cols) + 0.6, 7.0), sharex=True,
                            gridspec_kw=dict(height_ratios=[1.0, 1.15]))
    axs = np.atleast_2d(axs).reshape(2, len(cols))
    for j, (title, task) in enumerate(cols):
        c = vdcuts.load(glob.glob(f"{task}/*_vdcuts.txt")[0])
        iv = np.loadtxt(glob.glob(f"{task}/*_IdVd.csv")[0], delimiter=",", usecols=(0, 1))
        v, i = iv[:, 0], iv[:, 1]
        vds, pv = pocket_volts(c)
        nstr = int(title.strip()[0]) if title.strip()[0].isdigit() else 3
        have = list(range(1 + nstr))                 # stress band + strikes 1..nstr
        ax = axs[0, j]
        ax.plot(v, i, color="#222", lw=1.8)
        for s, k in drop_episodes(v, i, DROP_MIN_TABLE, "hyst"):
            a, b = v[s], v[k]
            r = int(np.argmin(np.abs(vds - b)))
            r0 = int(np.argmin(np.abs(vds - a)))
            who = have[int(np.argmax((pv[r] - pv[r0])[have]))]   # the pocket whose voltage jumps across the drop
            ax.axvspan(a, b, color=POCKETS[who][2], alpha=0.35, lw=0)
        ax.set_title(title, fontsize=10.5)
        ax.set_ylim(0, 450)
        ax.grid(alpha=0.25)
        ax = axs[1, j]
        for k, (lab, _, col) in enumerate(POCKETS):
            if k not in have:
                continue
            ax.plot(vds, pv[:, k], color=col, lw=2.0, label=lab)
        ax.axhline(THR, color="#c0392b", lw=1.0, ls="--")
        ax.set_yscale("log")
        ax.set_ylim(0.03, 12)
        ax.set_xlim(0, 12)
        ax.set_xlabel("Vd (V)")
        ax.grid(alpha=0.25, which="both")
    axs[0, 0].set_ylabel("Id (mA/mm), Vg +1 V")
    axs[1, 0].set_ylabel("voltage across each damaged spot (V)")
    axs[1, 0].text(0.2, THR * 1.12, "≈0.5 V: the spot switches", color="#c0392b", fontsize=8.5)
    h, l = [], []
    for ax in axs[1]:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l:
                h.append(hh)
                l.append(ll)
    fig.legend(h, l, loc="lower center", ncol=len(l), frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, -0.01))
    fig.text(0.5, 0.995, "SiN, 28 V stress damage + 6e18 strikes: shaded = drop, coloured by the spot that switches",
             ha="center", va="top", fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(out, dpi=150)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
