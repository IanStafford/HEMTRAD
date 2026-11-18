"""3D slice after the brick-gradient fix (2026-11-18): left, a full-width ion track along the gate width in 3D
against the same strike in 2D, before and after the fix; right, current lost to a track against the fraction of
the width it covers. Data: data/rad3d_fangs (FANGS port runs), results/20261112_rad3dSolve task_6 (undamaged 2D
slice, same coarsening). usage: python3 analysis/plot_rad3dFix.py <out.png>"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

D = "data/rad3d_fangs"


def load(p):
    f = glob.glob(p)
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(f[0]) if l.strip()]) if f else None


def main(out):
    ref, bef, aft = load(f"{D}/ref2d.csv"), load(f"{D}/before_full.csv"), load(f"{D}/after_full.csv")
    half, quar = load(f"{D}/after_half.csv"), load(f"{D}/after_quarter.csv")
    pre = load("results/20261112_rad3dSolve/task_6/*_IdVd.csv")
    plt.rcParams.update({"font.size": 12})
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})
    a.plot(ref[:, 0], ref[:, 1], color="#172230", lw=2.6, label="2D strike (reference)")
    a.plot(bef[:, 0], bef[:, 1], color="#c2410c", lw=2.0, ls="--", label="3D, before the fix")
    a.plot(aft[:, 0], aft[:, 1], color="#1b4f9c", lw=2.0, ls=(0, (1, 1.5)), label="3D, after the fix")
    for v in (3.0, 6.0):
        r0, rb, ra = (np.interp(v, d[:, 0], d[:, 1]) for d in (ref, bef, aft))
        a.annotate(f"{rb / r0:.2f}", (v, rb), xytext=(4, -16), textcoords="offset points", color="#c2410c", fontsize=11)
        a.annotate(f"{ra / r0:.3f}", (v, ra), xytext=(4, 6), textcoords="offset points", color="#1b4f9c", fontsize=11)
    a.set_xlabel("Vd (V)")
    a.set_ylabel("Id (mA/mm) at Vg +1 V")
    a.set_title("Full-width track: 3D vs 2D (numbers: 3D / 2D)", loc="left", fontsize=12)
    a.set_xlim(0, 6.3)
    a.set_ylim(0, None)
    a.grid(color="#e3e5e8")
    a.spines[["top", "right"]].set_visible(False)
    a.legend(frameon=False, fontsize=10.5, loc="lower right")
    p0 = np.interp(1.0, pre[:, 0], pre[:, 1])
    fr = [0.0, 0.25, 0.5, 1.0]
    ids = [p0, np.interp(1.0, quar[:, 0], quar[:, 1]), np.interp(1.0, half[:, 0], half[:, 1]), np.interp(1.0, aft[:, 0], aft[:, 1])]
    loss = [100 * (p0 - i) / p0 for i in ids]
    b.plot([0, 1], [0, loss[-1]], color="#9aa0a8", lw=1.4, ls="--", label="in proportion to width")
    b.plot(fr, loss, color="#1b4f9c", lw=2.2, marker="o", ms=9, mec="#f4f5f1", mew=2, label="3D slice (fixed)")
    for f, l in zip(fr, loss):
        b.annotate(f"{l:.1f}%", (f, l), xytext=(8, -4), textcoords="offset points", fontsize=11, color="#172230")
    b.set_xlabel("fraction of the slice width the track covers")
    b.set_ylabel("Id lost at Vd 1 V (%)")
    b.set_title("Partial-width tracks (3e18, sigma 40 nm, y 0.8 um)", loc="left", fontsize=12)
    b.set_xlim(-0.05, 1.15)
    b.set_ylim(0, None)
    b.grid(color="#e3e5e8")
    b.spines[["top", "right"]].set_visible(False)
    b.legend(frameon=False, fontsize=10.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    print("wrote", out, "loss", [round(x, 2) for x in loss])


if __name__ == "__main__":
    main(sys.argv[1])
