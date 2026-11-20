"""0-3 strike series on several meshes (2026-11-19, goal follow-up: do the steps survive mesh refinement?).
One row per strike setting, one column per mesh (library = 15 nm at y 0.8; m10 = 10 nm uniform; m5fix = 5 nm over
y 0.64-0.96, otherwise the library mesh). Curves: SiN, 28 V stress (scale 1.5e18) + 0-3 strikes, Vg +1 V. Prints
the drops (falling Id of at least 8 mA/mm) of every curve. Runs: radStep A-F (library), meshChkLoad_m10/m5fix,
radStepM 52044406.
usage: python3 analysis/plot_meshSeries.py [out.png] [set key ...]"""
import glob
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# setting key -> (title, {strikes: library label})
SETS = {
    "lev40_n6": ("trap 0.40 eV, 6e18 strikes", {0: "F_lev0.4_N0", 1: "E_lev0.4_n6e18_N1", 2: "E_lev0.4_n6e18_N2", 3: "E_lev0.4_n6e18_N3"}),
    "lev40_n5": ("trap 0.40 eV, 5e18 strikes", {0: "F_lev0.4_N0", 1: "F_lev0.4_n5e+18_N1", 2: "F_lev0.4_n5e+18_N2", 3: "F_lev0.4_n5e+18_N3"}),
    "lev40_n7": ("trap 0.40 eV, 7e18 strikes", {0: "F_lev0.4_N0", 1: "F_lev0.4_n7e+18_N1", 2: "F_lev0.4_n7e+18_N2", 3: "F_lev0.4_n7e+18_N3"}),
    "lev30_n6": ("trap 0.30 eV, 6e18 strikes (row A)", {0: "C_p1.5_N0", 1: "A_p1.5e+18_n6e+18_N1", 2: "B_n6e18_N2", 3: "A_p1.5e+18_n6e+18_N3"}),
    "lev30_n7": ("trap 0.30 eV, 7e18 strikes", {0: "C_p1.5_N0", 1: "C_p1.5_n7e18_N1", 2: "C_p1.5_n7e18_N2", 3: "C_p1.5_n7e18_N3"}),
    "lev30_n8": ("trap 0.30 eV, 8e18 strikes", {0: "C_p1.5_N0", 1: "A_p1.5e+18_n8e+18_N1", 2: "C_p1.5_n8e18_N2", 3: "A_p1.5e+18_n8e+18_N3"}),
}
MESHES = [("library (15 nm at y 0.8)", ("",)), ("10 nm uniform", ("M_m10_", "m10_", "D5_m10_")),
          ("2.5 nm at the strikes", ("M_m2p5_",)),
          ("5 nm at y 0.8", ("M_m5fix_", "m5fix_", "D5_m5fix_"))]
COL = ["#9aa0a8", "#e0a060", "#c8641e", "#7a2e05"]


def index():
    idx = {}
    pats = ["results/2026111*_radStep[A-F]/task_*", "results/20261118_meshChkLoad_*/task_*", "results/20261119_radStepM/task_*",
            "results/20261120_radStepM2/task_*", "results/2026112*_radStepM3/task_*"]
    for pat in pats:
        for t in glob.glob(pat):
            try:
                lab = json.load(open(f"{t}/params.json"))["label"]
                f = glob.glob(f"{t}/*_IdVd.csv")[0]
            except (OSError, ValueError, IndexError):
                continue
            idx.setdefault(lab, f)
    return idx


def load(f):
    d = np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(f) if l.strip()])
    return d[:, :2] if d.ndim == 2 and len(d) > 2 else None


def drops(d, thr=8.0):
    v, i = d[:, 0], d[:, 1]
    out, k = [], 0
    while k < len(v) - 1:
        if i[k + 1] < i[k] - 1.0:
            s = k
            while k < len(v) - 1 and i[k + 1] < i[k] - 0.5:
                k += 1
            if i[s] - i[k] >= thr:
                out.append((v[s], v[k], i[s], i[k]))
        k += 1
    return out


def find(idx, prefixes, lab):
    for p in prefixes:
        if p + lab in idx:
            return idx[p + lab]
    return None


def main(out="figures/rad/step28/mesh_series.png", *keys):
    keys = keys or tuple(SETS)
    idx = index()
    fig, axs = plt.subplots(len(keys), len(MESHES), figsize=(4.3 * len(MESHES), 3.2 * len(keys)), squeeze=False,
                            sharex=True)
    for r, key in enumerate(keys):
        title, labs = SETS[key]
        print(f"== {title}")
        for c, (mname, prefixes) in enumerate(MESHES):
            ax = axs[r][c]
            for n in range(4):
                f = find(idx, prefixes, labs[n])
                d = load(f) if f else None
                if d is None:
                    continue
                ax.plot(d[:, 0], d[:, 1], color=COL[n], lw=2.0 if n else 1.5, ls="-" if n else "--",
                        label=f"{n} strike{'s' if n != 1 else ''}")
                ds = drops(d)
                txt = "; ".join(f"{a:.1f}-{b:.1f} V {x:.0f}->{y:.0f}" for a, b, x, y in ds)
                print(f"   {mname:26s} N{n}: {len(ds)} drops  {txt}   (to {d[-1, 0]:.1f} V)")
            ax.set_xlim(0, 12)
            ax.grid(alpha=0.25)
            if r == 0:
                ax.set_title(mname, fontsize=11)
            if c == 0:
                ax.set_ylabel(f"{title}\nId (mA/mm), Vg +1 V", fontsize=9)
            if r == len(keys) - 1:
                ax.set_xlabel("Vd (V)")
        axs[r][0].legend(loc="lower right", fontsize=8, frameon=False)
    fig.suptitle("SiN, 28 V stress damage + 0-3 strikes (y 0.8 / 1.6 / 2.4 µm) on three meshes", fontsize=12, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
