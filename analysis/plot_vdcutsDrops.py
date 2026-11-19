"""Channel profiles before and after each drop of an Id-Vd curve run with vdCuts=1 (drivers/radIV.tcl): electron
density 1 nm below the AlGaN/GaN interface, lateral field and hot-electron temperature (and, if present, the filled
traps mid-barrier), one column per drop. Drops are runs of falling Id of at least 8 mA/mm.
usage: python3 analysis/plot_vdcutsDrops.py <task dir> <out.png> [title]"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, "analysis")
import vdcuts  # noqa: E402


def drops(v, i, thr=8.0):
    out, k = [], 0
    while k < len(v) - 1:
        if i[k + 1] < i[k] - 1.0:
            s = k
            while k < len(v) - 1 and i[k + 1] < i[k] - 0.5:
                k += 1
            if i[s] - i[k] >= thr:
                out.append((s, k))
        k += 1
    return out


def main(task, out, title=""):
    c = vdcuts.load(glob.glob(f"{task}/*_vdcuts.txt")[0])
    iv = np.loadtxt(glob.glob(f"{task}/*_IdVd.csv")[0], delimiter=",", usecols=(0, 1))
    v, i = iv[:, 0], iv[:, 1]
    ds = drops(v, i)
    rows = [("Elec", "electrons, 2DEG (cm⁻³)", True), ("Ey", "lateral field (V/cm)", True),
            ("TeTrap", "electron temp. (K)", False)]
    if any("IonAcceptor_x0.008" in c[k] for k in c):
        rows.append(("IonAcceptor_x0.008", "filled traps, AlGaN (cm⁻³)", True))
    fig, axs = plt.subplots(len(rows) + 1, max(len(ds), 1), figsize=(4.6 * max(len(ds), 1), 2.3 * (len(rows) + 1)),
                            squeeze=False, sharex="row")
    for col, (s, k) in enumerate(ds):
        a, b = round(v[s], 3), round(v[k], 3)
        ax = axs[0][col]
        ax.plot(v, i, color="#555", lw=1.5)
        ax.axvspan(a, b, color="#e0782f", alpha=0.3)
        ax.set_title(f"drop {a:g}-{b:g} V: {i[s]:.0f} -> {i[k]:.0f} mA/mm", fontsize=10)
        ax.set_xlabel("Vd (V)")
        for r, (lab, name, lg) in enumerate(rows, start=1):
            ax = axs[r][col]
            for vd, col2, ls in ((a, "#2f62a8", "-"), (b, "#b8460f", "-")):
                y, val = c[vd][lab]
                m = (y > 0.2) & (y < 2.8)
                ax.plot(y[m], np.abs(val[m]), color=col2, ls=ls, lw=1.6, label=f"Vd {vd:g} V")
            if lg:
                ax.set_yscale("log")
            if col == 0:
                ax.set_ylabel(name, fontsize=9)
            ax.grid(alpha=0.25)
            if r == len(rows):
                ax.set_xlabel("y along the channel (µm), gate at 0")
        axs[1][col].legend(fontsize=8, frameon=False)
    if title:
        fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
