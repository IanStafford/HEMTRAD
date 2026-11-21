"""28 V stress damage-scale refit (rad28fit, radExp3, rad28fitB; 2026-11-12/14): Id-Vd at Vg +1 V for SiN and
HighK against the damage scale. usage: python3 archive/analysis_dayfigs/plot_rad28fit.py <out.png>"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SIN = [("1e18", "results/20261112_rad28fit/task_*/sin_s28_p1e+18_IdVd.csv"),
       ("1.5e18", "results/20261112_radExp3/task_*/sin_s28_p1.5e+18_IdVd.csv"),
       ("2e18", "results/20261113_rad28fitB/task_*/sin_s28_p2e+18_IdVd.csv"),
       ("3e18", "results/20261113_rad28fitB/task_*/sin_s28_p3e+18_IdVd.csv")]
HK = [("1.5e18", "results/20261112_rad28fit/task_*/hk_s28_p1.5e+18_IdVd.csv"),
      ("2.5e18", "results/20261112_radExp3/task_*/hk_s28_p2.5e+18_IdVd.csv"),
      ("4e18", "results/20261112_rad28fit/task_*/hk_s28_p4e+18_IdVd.csv")]
SC = ["#f2a66b", "#e0782f", "#b8460f", "#5a1d04"]
HC = ["#93bde6", "#3f7fc4", "#0d376b"]


def load(p):
    f = glob.glob(p)
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(f[0]) if l.strip()]) if f else None


def main(out):
    plt.rcParams.update({"font.size": 12})
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    for a, (name, rows, cols, pre) in zip(axs, (("SiN", SIN, SC, "sin"), ("HighK", HK, HC, "hk"))):
        p = load(f"results/20261104_radMap1/task_*/{pre}_ref_IdVd.csv")
        a.plot(p[:, 0], p[:, 1], color="#c5c9ce", lw=1.5, ls="--", label="pre-irradiation")
        for (lab, path), c in zip(rows, cols):
            d = load(path)
            if d is not None:
                a.plot(d[:, 0], d[:, 1], color=c, lw=2.2, label=f"damage scale {lab}")
        a.set_title(f"{name}, 28 V off-state stress", loc="left", fontsize=12)
        a.set_xlabel("Vd (V)")
        a.set_xlim(0, 10.2)
        a.set_ylim(0, None)
        a.grid(color="#e3e5e8")
        a.spines[["top", "right"]].set_visible(False)
        a.legend(frameon=False, fontsize=10.5, loc="upper left")
    axs[0].set_ylabel("Id (mA/mm) at Vg +1 V")
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1])
