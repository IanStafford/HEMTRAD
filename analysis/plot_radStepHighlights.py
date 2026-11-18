"""Highlights of the stepped-collapse search (2026-11-17): selected SiN curves with several drops, one panel each,
with every drop (>= 10 mA/mm) marked, the pre-irradiation curve and the Nov 11 model for reference.
usage: python3 analysis/plot_radStepHighlights.py <out.png>"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, "analysis")
from plot_radStep import drops  # noqa: E402

R = "results/20261117_"
PICK = [
    ("radStepA", "A_p1.5e+18_n6e+18_N1", "1 strike, 6e18 at y 0.8; scale 1.5e18"),
    ("radStepE", "E_lev0.4_n6e18_N3", "3 strikes, 6e18; trap level 0.40 eV"),
    ("radStepE", "E_lev0.4_n6e18_N2", "2 strikes, 6e18; trap level 0.40 eV"),
    ("radStepA", "A_p1.5e+18_n8e+18_N3", "3 strikes, 8e18; scale 1.5e18"),
    ("radStepC", "C_p1.5_n7e18_N3", "3 strikes, 7e18; scale 1.5e18"),
    ("radStepC", "C_p1.5_n8e18_N2", "2 strikes, 8e18; scale 1.5e18"),
    ("radStepE", "E_fp_n6e18_N2", "2 strikes, 6e18 at the field-plate edges (0.9, 0.3)"),
    ("radStepF", "F_lev0.4_n5e+18_N2", "2 strikes, 5e18; trap level 0.40 eV"),
    ("radStepE", "E_s0.06_n6e18_N2", "2 strikes, 6e18, sigma 60 nm"),
]


def load(p):
    f = glob.glob(p)
    if not f:
        return None
    d = np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(f[0]) if l.strip()])
    return d if d.ndim == 2 and len(d) >= 3 else None


BEST = [PICK[0], PICK[2], PICK[5]]


def best(out):
    """One row: the three curves the deck shows."""
    pre = load("results/20261104_radMap1/task_*/sin_ref_IdVd.csv")
    nov = load("results/20261109_radEB1/task_*/sin_b_eb1_IdVd.csv")
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    for a, (run, lab, title) in zip(axs, BEST):
        d = load(f"{R}{run}/task_*/{lab}_IdVd.csv")
        a.plot(pre[:, 0], pre[:, 1], color="#c5c9ce", lw=1.2, ls="--", label="pre-irradiation")
        a.plot(nov[:, 0], nov[:, 1], color="#7a808a", lw=1.2, ls=":", label="Nov 11 model")
        a.plot(d[:, 0], d[:, 1], color="#b8460f", lw=2.4, label="28 V stress + strikes")
        for k, s in enumerate(drops(d[:, 0], d[:, 1], 10.0), 1):
            a.annotate("", xy=(s[1], s[3]), xytext=(s[0], s[2]),
                       arrowprops=dict(arrowstyle="-|>", color="#1d5fa8", lw=1.5, shrinkA=0, shrinkB=0))
            a.text(s[1] + 0.15, s[3] - 22, f"{k}", color="#1d5fa8", fontsize=11, fontweight="bold")
        a.set_title(title, fontsize=11.5, loc="left")
        a.set_xlim(0, 12.2)
        a.set_ylim(0, 1080)
        a.set_xlabel("Vd (V)")
        a.grid(color="#e3e5e8", lw=0.8)
        a.spines[["top", "right"]].set_visible(False)
    axs[0].set_ylabel("Id (mA/mm), Vg +1 V")
    axs[0].legend(frameon=False, fontsize=10, loc="upper left")
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    print("wrote", out)


def main(out):
    pre = load("results/20261104_radMap1/task_*/sin_ref_IdVd.csv")
    nov = load("results/20261109_radEB1/task_*/sin_b_eb1_IdVd.csv")
    fig, axs = plt.subplots(3, 3, figsize=(14, 11), sharex=True, sharey=True)
    for a, (run, lab, title) in zip(axs.flat, PICK):
        d = load(f"{R}{run}/task_*/{lab}_IdVd.csv")
        a.plot(pre[:, 0], pre[:, 1], color="#c5c9ce", lw=1.2, ls="--", label="pre-irradiation")
        a.plot(nov[:, 0], nov[:, 1], color="#7a808a", lw=1.1, ls=":", label="Nov 11 model")
        if d is not None:
            a.plot(d[:, 0], d[:, 1], color="#b8460f", lw=2.2, label="28 V stress + strikes")
            for k, s in enumerate(drops(d[:, 0], d[:, 1], 10.0), 1):
                a.annotate("", xy=(s[1], s[3]), xytext=(s[0], s[2]),
                           arrowprops=dict(arrowstyle="-|>", color="#1d5fa8", lw=1.4, shrinkA=0, shrinkB=0))
                a.text(s[1] + 0.15, s[3] - 18, f"{k}", color="#1d5fa8", fontsize=9, fontweight="bold")
        a.set_title(f"SiN: {title}", fontsize=10, loc="left")
        a.set_xlim(0, 12.2)
        a.set_ylim(0, 1080)
        a.grid(color="#e3e5e8", lw=0.8)
        a.spines[["top", "right"]].set_visible(False)
    axs[0][0].legend(frameon=False, fontsize=8.5, loc="upper left")
    for a in axs[-1]:
        a.set_xlabel("Vd (V)")
    for a in axs[:, 0]:
        a.set_ylabel("Id (mA/mm), Vg +1 V")
    fig.suptitle("Stepped SiN Id-Vd after a 28 V off-state stress (Vg -10 V) plus strike damage; numbered arrows mark each drop of 10 mA/mm or more",
                 fontsize=11.5, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print("wrote", out)


if __name__ == "__main__":
    (best if len(sys.argv) > 2 and sys.argv[2] == "best" else main)(sys.argv[1])
