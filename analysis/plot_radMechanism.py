"""Illustrative model-only figures for the rad model (no measured data).

usage: python3 analysis/plot_radMechanism.py
Writes
- figures/radMech_damage.png: lateral stress field at the stress bias and the
  resulting damage traps along the channel, HighK vs SiN (radFinal8 cuts);
- figures/radMech_SiN_IdVd.png: Id-Vd at Vg +1 for both decks, pre and biased post,
  with the SiN one-site and two-site (radFinal11) curves.
"""
import glob
import os
import re

import matplotlib.pyplot as plt
import numpy as np

INK, MUTED, GRID = "#14171F", "#646B78", "#E2E4E9"
COL = {"highk": "#1B4F9C", "sin": "#C2410C"}
NAME = {"highk": "HighK (HPD)", "sin": "SiN"}
R8, R11, R0 = "results/20261026_radFinal8", "results/20261027_radFinal11", "results/20261025_radFinal"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})


def cut(f, name, xc):
    blk = open(f).read().split(f"# {name} along y at x = {xc}")[1].split("#")[0]
    rows = [l.strip("{} \n").split() for l in blk.splitlines() if re.match(r"\{\s*-?\d", l)]
    return np.array([[float(a[0]), float(a[1])] for a in rows])


def style(ax):
    ax.grid(color=GRID, lw=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def marks(ax):
    for y, lab in ((-0.125, "gate"), (0.125, ""), (0.725, "FP edge")):
        ax.axvline(y, color=MUTED, lw=0.7, ls=":")
    ax.axvspan(-0.125, 0.125, color=GRID, alpha=0.6, lw=0)


fig, axs = plt.subplots(1, 2, figsize=(12, 4.3))
for deck in ("highk", "sin"):
    f = glob.glob(f"{R8}/task_*/b_{deck}_cuts.txt")[0]
    e, n = cut(f, "Estress", "0.001"), cut(f, "TrapN", "0.016")
    axs[0].semilogy(e[:, 0], e[:, 1], color=COL[deck], lw=2, label=NAME[deck])
    axs[1].semilogy(n[:, 0], np.maximum(n[:, 1], 1e12), color=COL[deck], lw=2, label=NAME[deck])
for ax in axs:
    marks(ax); style(ax); ax.set_xlim(-0.4, 2.0)
    ax.set_xlabel("position along the channel y (µm); gate shaded, field-plate edge dotted")
    ax.legend(frameon=False, fontsize=9)
axs[0].set_ylim(1e3, 2e6); axs[0].set_ylabel("lateral field (V/cm)")
axs[0].set_title("1  Stress field at Vg −10 V, Vd 17 V (AlGaN top)", color=INK, fontsize=11, loc="left")
axs[0].annotate("SiN peak 2× HighK\nunder the T-gate overhang", xy=(0.5, 5.5e5), xytext=(0.85, 8e5),
                fontsize=8, color=INK, arrowprops=dict(arrowstyle="->", color=MUTED))
axs[1].set_ylim(1e14, 3e19); axs[1].set_ylabel("damage trap density (cm⁻³)")
axs[1].set_title("2  Damage traps ∝ E⁴ (2DEG depth, y ≥ 0.30 µm)", color=INK, fontsize=11, loc="left")
fig.tight_layout()
fig.savefig("figures/radMech_damage.png", dpi=150)

pre = {d: np.loadtxt(f"{R0}/task_{i}/pre_{d}_IdVd.csv", delimiter=",") for d, i in (("highk", 0), ("sin", 1))}
bh = np.loadtxt(glob.glob(f"{R8}/task_2/*_IdVd.csv")[0], delimiter=",")
bs1 = np.loadtxt(glob.glob(f"{R8}/task_3/*_IdVd.csv")[0], delimiter=",")
bs2 = np.loadtxt(glob.glob(f"{R11}/task_2/*_IdVd.csv")[0], delimiter=",")
fig, axs = plt.subplots(1, 2, figsize=(12, 4.3), sharey=True)
axs[0].plot(pre["highk"][:, 0], pre["highk"][:, 2], ":", color=COL["highk"], lw=2, label="pre")
axs[0].plot(bh[:, 0], bh[:, 2], "-", color=COL["highk"], lw=2, label="biased post")
axs[0].set_title("HighK (HPD): no collapse, ~7% lower", color=INK, fontsize=11, loc="left")
axs[1].plot(pre["sin"][:, 0], pre["sin"][:, 2], ":", color=COL["sin"], lw=2, label="pre")
axs[1].plot(bs1[:, 0], bs1[:, 2], "-", color="#E8A27C", lw=1.6, label="biased post, one damage site")
axs[1].plot(bs2[:, 0], bs2[:, 2], "-", color=COL["sin"], lw=2.2, label="biased post, + second strike site")
axs[1].set_title("SiN: collapse above the knee, two steps", color=INK, fontsize=11, loc="left")
for ax in axs:
    style(ax); ax.set_xlabel("Vd (V)"); ax.legend(frameon=False, fontsize=9, loc="lower right")
axs[0].set_ylabel("Id at Vg +1 V (mA/mm)")
fig.tight_layout()
fig.savefig("figures/radMech_SiN_IdVd.png", dpi=150)
print("wrote figures/radMech_damage.png figures/radMech_SiN_IdVd.png")
