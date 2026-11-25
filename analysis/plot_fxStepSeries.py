"""Stepped 1/2/3-strike series on the corrected geometry (28 V stress, fixed FP contact, damage scale 6e17), SiN, on the
5 nm (m5fix) and 2.5 nm (m2p5) meshes: trap level 0.40 eV / 7e18 strikes and 0.30 eV / 8e18 strikes. Model output only.
Drops marked by the table rule (common.drop_episodes, hyst, 8 mA/mm). Runs: fxRadStepM 52610363, fxRadStepM3 52610365,
fxRadStepF 52610353, fxRadStepA 52610348, fxMeshChkLoad_m5fix 52610360, fxRadStepC 52610350.
usage: python3 analysis/plot_fxStepSeries.py [out.png]"""
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "analysis")
from common import DROP_MIN_TABLE, STRIKE_SIN_28, drop_episodes, read_csv  # noqa: E402

RAMP = ["#9aa0a8"] + STRIKE_SIN_28[1:]      # 0, 1, 2, 3 strikes
LAB = {"0.40": ("trap 0.40 eV, 7e18 cm$^{-3}$ strikes", [("fx_F_lev0.4_N0", "fx_M_m5fix_F_lev0.4_N0", "fx_M_m2p5_F_lev0.4_N0")] +
                [(f"fx_F_lev0.4_n7e+18_N{k}", f"fx_M_m5fix_F_lev0.4_n7e+18_N{k}", f"fx_M_m2p5_F_lev0.4_n7e+18_N{k}") for k in (1, 2, 3)]),
       "0.30": ("trap 0.30 eV, 8e18 cm$^{-3}$ strikes", [("fx_C_p1.5_N0", "fx_m5fix_C_p1.5_N0", "fx_M_m2p5_C_p1.5_N0"),
                ("fx_A_p1.5e+18_n8e+18_N1", "fx_M_m5fix_A_p1.5e+18_n8e+18_N1", "fx_M_m2p5_A_p1.5e+18_n8e+18_N1"),
                ("fx_C_p1.5_n8e18_N2", "fx_m5fix_C_p1.5_n8e18_N2", "fx_M_m2p5_C_p1.5_n8e18_N2"),
                ("fx_A_p1.5e+18_n8e+18_N3", "fx_M_m5fix_A_p1.5e+18_n8e+18_N3", "fx_M_m2p5_A_p1.5e+18_n8e+18_N3")])}
MESH = ("library (9.5-17 nm)", "5 nm (m5fix)", "2.5 nm (m2p5)")


def curves():
    out = {}
    for f in glob.glob("results/20261124_fx*/task_*/params.json"):
        g = glob.glob(os.path.dirname(f) + "/*_IdVd.csv")
        if g:
            d = read_csv(g[0])
            if d is not None and len(d) > 4:
                out[json.load(open(f))["label"]] = d
    return out


def main(out="figures/rad/fpfix/step_series_fixed.png"):
    C = curves()
    fig, axs = plt.subplots(2, 3, figsize=(15.5, 8.6), sharey="row", sharex=True)
    for r, (key, (title, sets)) in enumerate(LAB.items()):
        for c in range(3):
            ax = axs[r][c]
            for n, labs in enumerate(sets):
                d = C.get(labs[c])
                if d is None:
                    continue
                e = drop_episodes(d[:, 0], d[:, 1], DROP_MIN_TABLE, "hyst")
                ax.plot(d[:, 0], d[:, 1], color=RAMP[n], lw=1.8, label=f"{n} strike{'s' if n != 1 else ''}: {len(e)} drop{'s' if len(e) != 1 else ''}")
            ax.set_title(f"{title}, {MESH[c]}", fontsize=10.5, loc="left")
            ax.set_xlabel("Vd (V)")
            ax.set_xlim(0, 12)
            ax.grid(color="#e3e5e8", lw=0.8)
            ax.spines[["top", "right"]].set_visible(False)
            ax.legend(frameon=False, fontsize=9, loc="lower right")
        axs[r][0].set_ylabel("Id (mA/mm)")
    fig.suptitle("SiN, 28 V stress, corrected contact, damage scale 6e17, Vg +1 V: drops at least 8 mA/mm (table rule)", x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
