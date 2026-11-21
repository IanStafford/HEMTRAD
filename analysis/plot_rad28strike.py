"""Strike count at the 28 V stress (rad28strikeL, 2026-11-17): final model, Vg -10 / Vd 28 V stress loaded from the
stress library, damage scale P, plus 0-3 Gaussian strikes (3e18, sigma 40 nm) at y 0.8 / 1.6 / 2.4 um. Id-Vd at
Vg +1 V, SiN and HighK side by side, the 3-strike curve drawn heavier.

usage: python3 analysis/plot_rad28strike.py <run dir> <P, e.g. 2e+18> <out.png>
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import STRIKE_HK_28, STRIKE_SIN_28, pre_ref, read_glob

DECKS = (("sin", "SiN passivation", STRIKE_SIN_28),     # colour ramps by number of strikes
         ("hk", "HighK passivation", STRIKE_HK_28))
plt.rcParams.update({"font.size": 12, "axes.edgecolor": "#8a8f98", "axes.labelcolor": "#2b2f36",
                     "xtick.color": "#4a4f58", "ytick.color": "#4a4f58"})


def load(p):
    """The first file matching the glob p (any number of rows), or None if there is none."""
    return read_glob(p, min_rows=None)


def main(run, p, out):
    fig, axs = plt.subplots(1, 2, figsize=(12.0, 4.8), sharey=True)
    for a, (d, name, ramp) in zip(axs, DECKS):
        pre = load(pre_ref(d))
        a.plot(pre[:, 0], pre[:, 1], color="#9aa0a8", lw=1.8, ls=(0, (5, 3)), label="pre-irradiation")
        for n in range(4):
            c = load(f"{run}/task_*/{d}28_p{p}_N{n}_IdVd.csv")
            if c is None:
                continue
            a.plot(c[:, 0], c[:, 1], color=ramp[n], lw=3.2 if n == 3 else 1.6,
                   label=f"{n} strike{'s' if n != 1 else ''}", zorder=3 if n == 3 else 2)
        a.set_title(name, fontsize=13, loc="left")
        a.set_xlabel("Vd (V)")
        a.set_xlim(0, 10.2)
        a.set_ylim(0, None)
        a.grid(color="#e3e5e8", lw=0.8)
        a.spines[["top", "right"]].set_visible(False)
        # legend where the curves aren't: lower right, unless the 0-strike curve is below 300 mA/mm at 8 V
        # (a hard SiN collapse)
        c0 = load(f"{run}/task_*/{d}28_p{p}_N0_IdVd.csv")
        low = c0 is not None and np.interp(8.0, c0[:, 0], c0[:, 1]) < 300.0
        a.legend(frameon=False, fontsize=10.5, loc="center right" if low else "lower right")
    axs[0].set_ylabel("Id (mA/mm) at Vg +1 V")
    fig.suptitle(f"After biased irradiation: Vg −10 V / Vd 28 V stress, damage scale {float(p):.1e} cm⁻³, "
                 "strikes at y 0.8, 1.6, 2.4 µm", fontsize=12, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
