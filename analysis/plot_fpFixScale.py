"""FP contact fix, damage-scale refit of the Nov 11 model (2026-11-22): SiN and HighK biased Id-Vd at Vg +1 after the
17.66 V stress, old FP box at damPeak 7e18 (radEB1, job 50411481) against the fixed box at damPeak 7e17-3e18
(fpFixScaleEB1, job 52223190), with the pre-irradiation curves (fixed box, fpFixPre 52134553). Model output only.
usage: python3 analysis/plot_fpFixScale.py [out.png]"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "analysis")
from common import read_glob  # noqa: E402

SCALES = ("7e17", "1e18", "1.5e18", "2e18", "3e18")
RAMP = {"sin": ["#f2c7a5", "#e9995f", "#c8641e", "#8f3a0b", "#4d1a02"],
        "hk": ["#c9dcf2", "#93b9e3", "#4f84c4", "#25528f", "#0f2a52"]}


def main(out="figures/rad/fpfix_scale_eb1.png"):
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 6.0), sharey=True)
    for ax, deck, name, old in ((axs[0], "sin", "SiN biased", "sin_b_eb1"), (axs[1], "hk", "HighK biased", "hk_b_eb1")):
        pre = read_glob(f"results/20261120_fpFixPre/task_*/fpfix_{deck}_ref_IdVd.csv")
        if pre is not None:
            ax.plot(pre[:, 0], pre[:, 1], color="#c5c9ce", lw=1.4, ls="--", label="pre-irradiation (fixed box)")
        o = read_glob(f"results/20261109_radEB1/task_*/{old}_IdVd.csv")
        ax.plot(o[:, 0], o[:, 1], color="#222", lw=1.6, ls=":", label="Nov 11 model, old FP box, scale 7e18")
        for k, dp in enumerate(SCALES):
            d = read_glob(f"results/20261121_fpFixScaleEB1/task_*/fpscale_{deck}_b_eb1_d{dp}_IdVd.csv")
            if d is None:
                continue
            ax.plot(d[:, 0], d[:, 1], color=RAMP[deck][k], lw=2.6 if dp == "1.5e18" else 1.6,
                    label=f"fixed box, scale {dp}" + ("  (refit)" if dp == "1.5e18" else ""))
        ax.set_title(f"{name}, 17.66 V stress, Vg +1 V", fontsize=11.5, loc="left")
        ax.set_xlabel("Vd (V)")
        ax.set_xlim(0, 10.2)
        ax.set_ylim(0, 1100)
        ax.grid(color="#e3e5e8", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    axs[0].set_ylabel("Id (mA/mm)")
    fig.suptitle("FP contact fix: damage scale 1.5e18 with the fixed box reproduces the Nov 11 model (old box, 7e18)",
                 fontsize=11.5, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
