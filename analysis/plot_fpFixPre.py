"""Pre-irradiation device, old FP contact box against the fixed box (2026-11-24): change in drain current with Vg
(Id-Vg at Vd 0.1 V, radMap1 49570571 against fpFixPre 52134553) and with Vd (Id-Vd at Vg +1 V, and at Vg 0 V from
radHV 51027334 against fxRadHV 52357001). At Vg 0 the gate and field plate are both at 0 V, so the contact box
cannot matter. Model output only.
usage: python3 analysis/plot_fpFixPre.py [out.png]"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, "analysis")
from common import BLUE, ORANGE, read_glob  # noqa: E402

DECKS = (("sin", "SiN", ORANGE, "pre_sin_hv"), ("hk", "HighK (HPD)", BLUE, "pre_highk_hv"))


def change(old, new):
    """(x, percent change of new against old) at the x values both curves have."""
    o = {round(x, 6): i for x, i in old[:, :2]}
    p = [(x, 100 * (i / o[round(x, 6)] - 1)) for x, i in new[:, :2] if round(x, 6) in o and abs(o[round(x, 6)]) > 1.0]
    p.sort()
    return np.array(p)


def main(out="figures/rad/fpfix/pre_contact.png"):
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    for d, name, col, hv in DECKS:
        c = change(read_glob(f"results/20261104_radMap1/task_*/{d}_ref_IdVg.csv"),
                   read_glob(f"results/20261120_fpFixPre/task_*/fpfix_{d}_ref_IdVg.csv"))
        axs[0].plot(c[:, 0], c[:, 1], color=col, lw=2, label=name)
        for sfx, ls, vg in (("IdVd", "-", "+1 V"), ("IdVdG0", "--", "0 V")):
            c = change(read_glob(f"results/20261112_radHV/task_*/{hv}_{sfx}.csv"),
                       read_glob(f"results/20261122_fxRadHV/task_*/fx_{hv}_{sfx}.csv"))
            axs[1].plot(c[:, 0], c[:, 1], color=col, lw=2, ls=ls, label=f"{name}, Vg {vg}")
    axs[0].set_title("Id-Vg at Vd 0.1 V (above 1 mA/mm)", fontsize=11, loc="left")
    axs[0].set_xlabel("Vg (V)")
    axs[1].set_title("Id-Vd", fontsize=11, loc="left")
    axs[1].set_xlabel("Vd (V)")
    axs[0].set_ylabel("change in Id, fixed box vs old (%)")
    for ax in axs:
        ax.axhline(0, color="0.4", lw=0.8)
        ax.grid(color="#e3e5e8", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
