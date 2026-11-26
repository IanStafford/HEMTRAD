"""Field-scaled strikes on a weak stress band (fxFieldStrike1 52761027, 72 runs): SiN against HighK, 1-3 strikes, for each
stress-band scale (rows) and strike base density (columns). 28 V stress, corrected contact, Vg +1 V, library mesh with 10 nm
at the strikes. Dotted grey: the stress band alone (fpFixScale28; none at 4.5e17). Drops marked by the table rule
(common.drop_episodes, hyst, 8 mA/mm). Model output only.
usage: python3 analysis/plot_fxFieldStrike1.py [out.png]"""
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "analysis")
from common import DROP_MIN_TABLE, STRIKE_SIN_28, drop_episodes, read_csv  # noqa: E402

ROWS = (("2e17", ""), ("3e17", ""), ("4.5e17", ""), ("3e17", "_lev0.4"))
COLS = ("2e17", "4e17", "8e17")
COL = STRIKE_SIN_28[1:]      # 1, 2, 3 strikes


def curves():
    out = {}
    for run in ("20261125_fxFieldStrike1", "20261122_fpFixScale28"):
        for f in glob.glob(f"results/{run}/task_*/params.json"):
            g = glob.glob(os.path.dirname(f) + "/*_IdVd.csv")
            if g:
                d = read_csv(g[0])
                if d is not None and len(d) > 4:
                    out[json.load(open(f))["label"]] = d
    return out


def ndrops(d):
    return len(drop_episodes(d[:, 0], d[:, 1], DROP_MIN_TABLE, "hyst"))


def main(out="figures/rad/fpfix/fieldstrike1.png"):
    C = curves()
    fig, axs = plt.subplots(len(ROWS), len(COLS), figsize=(15.5, 15), sharex=True, sharey=True)
    for r, (n0, lev) in enumerate(ROWS):
        for c, b in enumerate(COLS):
            ax = axs[r][c]
            for deck, ls in (("sin", "-"), ("hk", "--")):
                ref = C.get(f"fpscale28_{deck}_d{n0}") if not lev else None
                if ref is not None:
                    ax.plot(ref[:, 0], ref[:, 1], color="#9aa0a8", lw=1.2, ls=":" if deck == "sin" else (0, (1, 3)))
                for k in (1, 2, 3):
                    d = C.get(f"fx_fs1_{deck}_d{n0}_b{b}{lev}_N{k}")
                    if d is None:
                        continue
                    name = "SiN" if deck == "sin" else "HighK"
                    ax.plot(d[:, 0], d[:, 1], color=COL[k - 1], lw=1.8 if deck == "sin" else 1.3, ls=ls,
                            label=f"{name} {k} strike{'s' if k > 1 else ''}: {ndrops(d)} drop{'s' if ndrops(d) != 1 else ''}")
            trap = "0.40" if lev else "0.30"
            ax.set_title(f"band {n0}, strikes {b} cm$^{{-3}}$ at 5e5 V/cm, trap {trap} eV", fontsize=10.5, loc="left")
            ax.set_xlim(0, 12)
            ax.set_ylim(0, 1000)
            ax.grid(color="#e3e5e8", lw=0.8)
            ax.spines[["top", "right"]].set_visible(False)
            ax.legend(frameon=False, fontsize=8, loc="lower right", ncol=2)
        axs[r][0].set_ylabel("Id (mA/mm)")
    for ax in axs[-1]:
        ax.set_xlabel("Vd (V)")
    fig.suptitle("Field-scaled strikes (E$^4$, sigma 30 nm, y 0.55 / 0.50+0.60 / 0.47+0.56+0.65 um) on a weak 28 V stress band: "
                 "SiN solid, HighK dashed, band alone dotted grey", x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
