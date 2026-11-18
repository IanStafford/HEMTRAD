"""Round H (field-scaled strikes, 2026-11-18): SiN and HighK side by side at the 28 V stress, scale 1.5e18.
No strike (round C), one 3e18 strike at y 0.5 um without field scaling, and with gaussFieldM 4 at 3e18 and 2e18.

usage: python3 analysis/plot_radStepH.py [out.png]
"""
import glob
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RUNS = ("results/20261117_radStepC", "results/20261118_radStepH")
DECKS = (("SiN", "#c2410c", {"none": "C_p1.5_N0", "nofm": "H_sin_nofm_n3e18_N1",
                              "fm3": "H_sin_fm4_n3e18_N1", "fm2": "H_sin_fm4_n2e18_N1"}),
         ("HighK", "#1b4f9c", {"none": "C_hk_p1.5_n6e18_N0", "nofm": "H_hk_nofm_n3e18_N1",
                               "fm3": "H_hk_fm4_n3e18_N1", "fm2": "H_hk_fm4_n2e18_N1"}))
STY = {"none": ("no strike", "#9aa0a8", "--", 2.0), "nofm": ("3e18 strike, unscaled", None, ":", 2.4),
       "fm3": ("3e18 strike, × (E/E_ref)^4", None, "-", 2.6), "fm2": ("2e18 strike, × (E/E_ref)^4", None, "-", 1.6)}


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


def main(out="figures/rad/step28/fieldstrike_H.png"):
    c = curves()
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=True)
    for ax, (deck, col, labs) in zip(axs, DECKS):
        for key in ("none", "nofm", "fm2", "fm3"):
            d = c.get(labs[key])
            if d is None:
                continue
            name, cc, ls, lw = STY[key]
            m = d[:, 0] <= 12.0
            ax.plot(d[m, 0], d[m, 1], ls, color=cc or col, lw=lw, alpha=0.75 if key == "fm2" else 1.0, label=name)
        ax.set_title(f"{deck}: strike at y 0.5 µm (T-gate head edge)", fontsize=12)
        ax.set_xlabel("Vd (V)")
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 1100)
        ax.grid(alpha=0.25)
    axs[0].annotate("field-scaled: falls to 5e-6 to 4e-3 mA/mm", xy=(1.0, 4), xytext=(2.6, 130), fontsize=10,
                    color="#5a1d04", arrowprops=dict(arrowstyle="->", color="#5a1d04", lw=1))
    axs[0].set_ylabel("Id (mA/mm), Vg +1 V")
    axs[1].legend(loc="lower right", fontsize=9.5, frameon=False)
    fig.tight_layout()
    fig.savefig(out, dpi=170)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
