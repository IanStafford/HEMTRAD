"""Strike transients on the fixed contact (fxStrikeField28 52605291 and fxSeeMap28 52357004): lateral field on the 2DEG
row before and during a strike. (a) DC field, biased (Vg -10 / Vd 28 V) against gate-only (Vg -10 / Vd 0), both decks.
(b) peak field under the T-gate head (y 0.3-0.725) and at the drain end (y >= 3.0) against time for the biased strikes at
y 0.2, 0.53 and 0.8 and the gate-only case. The unbiased HighK run stopped at 0.14 ns. Model output only.
usage: ~/venvs/render/bin/python analysis/plot_seeFieldPositions.py [out.png]"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, "analysis")
import plot_seeField as p  # noqa: E402

B = "results/20261124_fxStrikeField28/task_{}/{}"
RUNS = {"SiN": {"0.2": p.PRE["SiN"], "0.53": B.format(1, "fx_sin_y0.53_map"), "0.8": B.format(2, "fx_sin_y0.8_map"), "unb": B.format(0, "fx_sin_unb_y0.2_map")},
        "HighK": {"0.2": p.PRE["HighK"], "0.53": B.format(5, "fx_hk_y0.53_map"), "0.8": B.format(6, "fx_hk_y0.8_map"), "unb": B.format(4, "fx_hk_unb_y0.2_map")}}
COL = {"SiN": "#C2410C", "HighK": "#1B4F9C"}
LS = {"0.2": "-", "0.53": "--", "0.8": ":", "unb": "-."}


def tms(lab):
    return 0.0 if lab == "DC" else float(lab.split()[0])


def main(out="figures/see/strike_field_bias.png"):
    fig, axs = plt.subplots(1, 3, figsize=(16.5, 4.6))
    for d in ("SiN", "HighK"):
        for key, lab in (("0.2", "biased"), ("unb", "gate-only (Vd 0)")):
            y, e = p.efield(RUNS[d][key] + "_map_dc.vtk")
            axs[0].semilogy(y, np.maximum(e, 1e2), color=COL[d], ls="-" if key == "0.2" else "--", lw=1.6, label=f"{d}, {lab}")
    axs[0].set_title("(a) before the strike, DC", fontsize=11, loc="left")
    axs[0].set_xlabel("y along the channel (um)"); axs[0].set_ylabel("|Ey| on the 2DEG row (V/cm)"); axs[0].set_xlim(-0.5, 3.4); axs[0].set_ylim(1e2, 2e6)
    axs[0].legend(frameon=False, fontsize=8.5)
    for ax, (zone, sel, title) in zip(axs[1:], (("head", lambda y: (y > 0.3) & (y < 0.725), "(b) peak under the T-gate head"), ("drain", lambda y: y >= 3.0, "(c) peak near the drain (y >= 3.0)"))):
        for d in ("SiN", "HighK"):
            for key in ("0.2", "0.53", "0.8", "unb"):
                t, v = [], []
                for lab, f in p.snaps(RUNS[d][key]):
                    y, e = p.efield(f); t.append(max(tms(lab), 0.5)); v.append(e[sel(y)].max())
                ax.loglog(t, v, color=COL[d], ls=LS[key], lw=1.5, marker="o", ms=3, label=f"{d}, strike y {key}" if key != "unb" else f"{d}, gate-only, y 0.2")
        ax.set_title(title, fontsize=11, loc="left"); ax.set_xlabel("time after the strike starts (ps; 0.5 = DC)"); ax.set_ylim(1e3, 2e6)
    axs[1].set_ylabel("V/cm"); axs[1].legend(frameon=False, fontsize=7.5, ncol=2, loc="lower left")
    for ax in axs:
        ax.grid(color="#e3e5e8", lw=0.8); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(out, dpi=140); print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
