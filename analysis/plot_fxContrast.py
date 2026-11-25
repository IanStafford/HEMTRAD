"""SiN vs HighK step counts against strike density on the corrected geometry (28 V stress, damage scale 6e17, library mesh,
plain strikes sigma 40 nm, trap level 0.30 and 0.40 eV): number of drops (table rule, hyst >= 8 mA/mm) and the size of the
largest drop (per cent of the peak before it). Runs: fxRadStepA, B, C, E, F, G, K and fxRad28strikeL. Model output only.
usage: python3 analysis/plot_fxContrast.py [out.png]"""
import glob
import json
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "analysis")
from common import DROP_MIN_TABLE, drop_episodes, read_csv  # noqa: E402

SKIP = re.compile(r"p1\.[678]|p1\.15|p2\.|p2e|p1e|p1\.0|_N0$|tau|x0\.|vs2|vs3|dv05|ko\d|near|fp_|hyb|band|depth|fm\d|nofm|old|y0\.|lev0\.(35|45)|s0\.|_hk_n4e18|m2p5|m5fix|m10|^fx_[MD]_|D5|fam|dam")


def largest(d):
    v, i = d[:, 0], d[:, 1]
    k = big = 0
    while k < len(i) - 1:
        if i[k + 1] < i[k] - 1e-9:
            j = k
            while j < len(i) - 1 and i[j + 1] < i[j]:
                j += 1
            if i[k] - i[j] >= DROP_MIN_TABLE:
                big = max(big, 100 * (i[k] - i[j]) / i[k])
            k = j
        else:
            k += 1
    return big


def table():
    out = {}
    for f in glob.glob("results/20261124_fx*/task_*/params.json"):
        l = json.load(open(f))["label"]
        g = glob.glob(os.path.dirname(f) + "/*_IdVd.csv")
        m, n = re.search(r"_N(\d)$", l), re.search(r"n(\d(?:\.\d)?)e\+?18", l)
        if not g or not m or not n or (SKIP.search(l) and not re.search(r"hk_n4e18", l)):
            continue
        d = read_csv(g[0])
        if d is None or len(d) < 5:
            continue
        deck = "hk" if "_hk" in l or l.startswith("fx_hk") else "sin"
        tl = 0.40 if "lev0.4" in l else 0.30
        out[(tl, float(n.group(1)), deck, int(m.group(1)))] = (len(drop_episodes(d[:, 0], d[:, 1], DROP_MIN_TABLE, "hyst")), largest(d))
    for f in glob.glob("results/20261124_fxRad28strikeL/task_*/params.json"):
        l = json.load(open(f))["label"]
        if not l.startswith(("fx_sin28_p1.5", "fx_hk28_p1.5")) or "_N0" in l:
            continue
        d = read_csv(glob.glob(os.path.dirname(f) + "/*_IdVd.csv")[0])
        out[(0.30, 3.0, "hk" if "hk28" in l else "sin", int(l[-1]))] = (len(drop_episodes(d[:, 0], d[:, 1], DROP_MIN_TABLE, "hyst")), largest(d))
    return out


def main(out="figures/rad/fpfix/contrast_density.png"):
    T = table()
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.6), sharey=True)
    for ax, tl in zip(axs, (0.30, 0.40)):
        for deck, col in (("sin", "#C2410C"), ("hk", "#1B4F9C")):
            for N, ls, mk in ((1, "-", "o"), (2, "--", "s"), (3, ":", "^")):
                p = sorted((n, v) for (t, n, d, k), v in T.items() if t == tl and d == deck and k == N)
                if p:
                    ax.plot([x for x, _ in p], [v[1] for _, v in p], ls=ls, marker=mk, color=col, lw=1.4, label=f"{'SiN' if deck == 'sin' else 'HighK'}, {N} strike{'s' if N > 1 else ''}")
        ax.set_title(f"trap level {tl:.2f} eV", fontsize=11, loc="left")
        ax.set_xlabel("strike density (1e18 cm$^{-3}$)")
        ax.grid(color="#e3e5e8", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, fontsize=8, ncol=2)
    axs[0].set_ylabel("largest drop (% of the current before it)")
    fig.suptitle("Plain strikes on the corrected contact: largest drop, SiN and HighK (library mesh)", x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print("wrote", out)
    for k in sorted(T):
        print(k, T[k][0], f"{T[k][1]:.0f}%")


if __name__ == "__main__":
    main(*sys.argv[1:])
