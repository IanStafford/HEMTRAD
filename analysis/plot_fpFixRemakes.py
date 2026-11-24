"""Nov 11 model with the fixed FP contact box against the old box (2026-11-24): the figures that the Nov 11-based
remakes replace. Damage scale 1.5e18 (fixed box) against 7e18 (old box). nov11_IdVd: 17.66 V stress; the strike
and high-Vd runs use the true 17.0 V stress. Model output only.
  nov11_IdVd.png       pre, non-biased and biased Id-Vd at Vg +1, both decks
  strikeN_IdVd.png     0-3 strikes (fxRadStrikeN 52357003, radStrikeN 51174895), old row over fixed row
  strike2_radHV.png    second-strike position (fxRadStrike2 52357002) and the Vd 28 V sweep (fxRadHV 52357001)
usage: python3 analysis/plot_fpFixRemakes.py [out dir]"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "analysis")
from common import BLUE, ORANGE, STRIKE_HK_28, STRIKE_SIN_28, read_glob  # noqa: E402

NEW = "results/20261122_fxRadStrikeN/task_*/fx_{}_N{}_IdVd.csv"
OLD = "results/20261113_radStrikeN/task_*/{}_N{}_IdVd.csv"
HV_NEW = "results/20261122_fxRadHV/task_*/fx_{}_IdVd.csv"
HV_OLD = "results/20261112_radHV/task_*/{}_IdVd.csv"
S2_NEW = "results/20261122_fxRadStrike2/task_*/fx_sin_{}_IdVd.csv"
DECKS = (("hk", "HighK (HPD)", BLUE), ("sin", "SiN", ORANGE))
RAMP = {"hk": STRIKE_HK_28, "sin": STRIKE_SIN_28}
plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Sans"})


def finish(ax, title, xmax, ymax=None):
    ax.set_title(title, fontsize=11, loc="left")
    ax.set_xlabel("Vd (V)")
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.grid(color="#e3e5e8", lw=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def nov11(out):
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, (d, name, col) in zip(axs, DECKS):
        pre = read_glob(f"results/20261120_fpFixPre/task_*/fpfix_{d}_ref_IdVd.csv")
        nbn = {"hk": "nb_highk_eb1", "sin": "nb_sin_eb1"}[d]
        nb = read_glob(f"results/20261120_fpFixEB1/task_*/fpfix_{nbn}_IdVd.csv")
        bn = read_glob(f"results/20261121_fpFixScaleEB1/task_*/fpscale_{d}_b_eb1_d1.5e18_IdVd.csv")
        bo = read_glob(f"results/20261109_radEB1/task_*/{d}_b_eb1_IdVd.csv")
        ax.plot(pre[:, 0], pre[:, 1], color="0.6", lw=1.6, label="pre-irradiation")
        ax.plot(nb[:, 0], nb[:, 1], color=col, lw=1.4, ls="--", label="non-biased")
        ax.plot(bn[:, 0], bn[:, 1], color=col, lw=2.2, label="biased, fixed box, 1.5e18")
        ax.plot(bo[:, 0], bo[:, 1], color="#222", lw=1.4, ls=":", label="biased, old box, 7e18")
        finish(ax, f"{name}, Vg +1 V", 10.2, 1100)
        ax.legend(frameon=False, fontsize=9, loc="lower right")
    axs[0].set_ylabel("Id (mA/mm)")
    fig.tight_layout()
    fig.savefig(f"{out}/nov11_IdVd.png", dpi=160)
    plt.close(fig)


def strike_n(out):
    fig, axs = plt.subplots(2, 2, figsize=(11, 8.4), sharey="col", sharex=True)
    for r, (pat, lab) in enumerate(((OLD, "old box, 7e18"), (NEW, "fixed box, 1.5e18"))):
        for ax, (d, name, _) in zip(axs[r], DECKS):
            for n in range(4):
                c = read_glob(pat.format(d, n))
                if c is not None:
                    ax.plot(c[:, 0], c[:, 1], color=RAMP[d][n], lw=1.9, label=f"{n} strike{'s' if n != 1 else ''}")
            finish(ax, f"{name}, {lab}", 10.2)
            ax.legend(frameon=False, fontsize=9, loc="lower right")
        axs[r][0].set_ylabel("Id (mA/mm)")
    fig.tight_layout()
    fig.savefig(f"{out}/strikeN_IdVd.png", dpi=160)
    plt.close(fig)


def strike2_hv(out):
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.6))
    ax = axs[0]
    cols = ["#222", "#f2a66b", "#e0782f", "#b8460f", "#8a3409", "#5a2206", "#2c0f02"]
    for (tag, lab), col in zip((("cut1", "no second strike"), ("s2_y0.8", "y 0.8"), ("s2_y1.2", "y 1.2"), ("s2_y2", "y 2.0"),
                                ("s2_y2.4", "y 2.4"), ("s2_y2.8", "y 2.8"), ("s2_y3.1", "y 3.1")), cols):
        c = read_glob(S2_NEW.format(tag))
        ax.plot(c[:, 0], c[:, 1], color=col, lw=2.4 if tag == "cut1" else 1.4,
                ls="-" if tag != "cut1" else (0, (5, 3)), label=lab)
    finish(ax, "SiN biased, second strike (3e18), fixed box", 10.2)
    ax.set_ylabel("Id (mA/mm)")
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax = axs[1]
    for d, name, col in DECKS:
        for pat, ls, lab in ((HV_OLD, ":", "old box"), (HV_NEW, "-", "fixed box")):
            c = read_glob(pat.format(f"{d}_b_eb1_hv"))
            ax.plot(c[:, 0], c[:, 1], color=col, lw=1.8, ls=ls, label=f"{name} biased, {lab}")
    finish(ax, "Nov 11 model to Vd 28 V (early ends: solver gave up)", 28.5)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(f"{out}/strike2_radHV.png", dpi=160)
    plt.close(fig)


def main(out="figures/rad/fpfix"):
    os.makedirs(out, exist_ok=True)
    nov11(out)
    strike_n(out)
    strike2_hv(out)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
