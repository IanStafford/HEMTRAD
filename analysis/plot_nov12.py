"""Dashboard figures for Nov 12-13: high-Vd curves (radHV) and second-strike position (radStrike2).
usage: python3 analysis/plot_nov12.py <out dir>"""
import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.size": 11})
HV = "results/20261112_radHV/task_*/{}.csv"
ST = "results/20261112_radStrike2/task_*/{}_IdVd.csv"


def load(p):
    f = glob.glob(p)
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(f[0]) if l.strip()]) if f else None


def main(out):
    os.makedirs(out, exist_ok=True)
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.0), sharey=True)
    for a, (d, pre, b, name, col) in zip(axs, (("hk", "pre_highk_hv", "hk_b_eb1_hv", "HighK (HPD)", "#1b4f9c"),
                                               ("sin", "pre_sin_hv", "sin_b_eb1_hv", "SiN", "#c2410c"))):
        for sfx, ls, vg in (("IdVd", "-", "+1"), ("IdVdG0", "--", "0")):
            p = load(HV.format(f"{pre}_{sfx}"))
            c = load(HV.format(f"{b}_{sfx}"))
            if p is not None:
                a.plot(p[:, 0], p[:, 1], color="0.6", lw=1.5, ls=ls, label=f"pre, Vg {vg} V")
            if c is not None:
                a.plot(c[:, 0], c[:, 1], color=col, lw=2.0, ls=ls, label=f"biased, Vg {vg} V")
        a.set_title(f"{name}: final model to Vd 28 V", fontsize=11, loc="left")
        a.set_xlabel("Vd (V)")
        a.grid(alpha=0.3)
        a.legend(fontsize=8.5, frameon=False, loc="lower right")
    axs[0].set_ylabel("Id (mA/mm)")
    fig.tight_layout()
    fig.savefig(f"{out}/radHV_28V.png", dpi=150)
    plt.close(fig)

    fig, a = plt.subplots(figsize=(6.8, 4.2))
    c = load(ST.format("sin_cut1"))
    a.plot(c[:, 0], c[:, 1], color="0.35", lw=2.2, label="final set, no second strike")
    cols = ["#f2a66b", "#e0782f", "#b8460f", "#8a3409", "#5a2206"]
    for y, cc in zip((0.8, 1.2, 2.0, 2.4, 2.8), cols):
        s = load(ST.format(f"sin_s2_y{y:g}"))
        if s is not None:
            a.plot(s[:, 0], s[:, 1], color=cc, lw=1.5, label=f"+ strike at y {y:g} um")
    a.set_xlabel("Vd (V)")
    a.set_ylabel("Id (mA/mm)")
    a.set_title("SiN biased, second Gaussian strike (3e18, 40 nm)", fontsize=11, loc="left")
    a.grid(alpha=0.3)
    a.legend(fontsize=8.5, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(f"{out}/radStrike2_pos.png", dpi=150)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1])
