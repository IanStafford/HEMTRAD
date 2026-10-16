"""Figures for the Oct 16 two-slide deck (strike placement, HighK vs SiN).

usage: HEADLINE_FONT_DIR=<folder of Source Sans 3 TTFs> python3 analysis/plot_strikeSlides.py
Writes:
  figures/strikeSlide_IV.png         trap-free vs gate-drain-edge strike (mid-barrier), Id-Vd log
  figures/strikeSlide_placement.png  mid-barrier (7.5 nm) row of 20261002_posMapLate: strip,
                                     onset Vd vs y, Id drop at 3 V vs y with its definition
  figures/fieldSlide_highk.png       lateral field along the 2DEG, HighK vs SiN, Vd 3/10/20 V
                                     (archive/static_mobility/figures/fieldPlate_cuts.csv)
"""
import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Rectangle

INK, BODY, MUTED, GRID = "#14171F", "#394150", "#646B78", "#E2E4E9"
BLUE, ORANGE, PALE = "#1B4F9C", "#C2410C", "#B9CBE6"
GATE, FP = (-0.125, 0.125), (0.285, 0.725)
RUN, DEPTH = "results/20261002_posMapLate", 0.0075   # mid AlGaN barrier (15 nm)
OFF_ROW, NONE_ROW = -0.35, 3.45

FONT_DIR = os.environ.get("HEADLINE_FONT_DIR")
if FONT_DIR:
    for f in glob.glob(os.path.join(FONT_DIR, "**", "*.ttf"), recursive=True):
        font_manager.fontManager.addfont(f)
    plt.rcParams["font.family"] = "Source Sans 3"
plt.rcParams.update({"font.size": 17, "xtick.labelsize": 16, "ytick.labelsize": 16,
                     "axes.labelsize": 17, "axes.edgecolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.labelcolor": INK, "mathtext.fontset": "cm"})


def style(ax, xlim=(-0.6, 2.65)):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)
    ax.set_xlim(*xlim)


def zones(ax):
    for (lo, hi) in (GATE, FP):
        ax.axvspan(lo, hi, color="#EEF1F6", lw=0, zorder=0)


def load_run():
    ref, dev = None, {}
    for t in glob.glob(f"{RUN}/task_*") + glob.glob(f"{RUN}Retry*/task_*"):
        p = json.load(open(os.path.join(t, "params.json")))
        c = glob.glob(os.path.join(t, "pulsedIV_*.csv"))
        if not c or os.path.getsize(c[0]) == 0:
            continue
        d = np.loadtxt(c[0], delimiter=",", ndmin=2)
        if p["trapPeak"] < 1e12:
            ref = d
        elif abs(p["trapMeanX"] - DEPTH) < 1e-6:
            y = p["trapMeanY"]
            if y not in dev or d[-1, 0] > dev[y][-1, 0]:   # a retry that got further wins
                dev[y] = d
    return ref, dev


def classify(d, ref):
    """(class, onset, log10 drop at the last Vd) as in plot_posSlides.py."""
    vd, idd = d[:, 0], d[:, 1]
    m = vd > 0.05
    v, i = vd[m], idd[m]
    drop = min(8.0, np.log10(np.interp(vd[-1], ref[:, 0], ref[:, 1]) / max(idd[-1], 1e-30)))
    if i[0] / np.interp(v[0], ref[:, 0], ref[:, 1]) < 0.1:
        return "off", np.nan, drop
    loss = 1.0 - i[1:] / i[:-1]
    if loss.max() < 0.5:
        return "none", np.nan, drop
    thr = 0.95 if loss.max() > 0.95 else 0.5   # deep: first >95% step; medium: first >50%
    return "collapse", float(v[1 + np.nonzero(loss >= thr - 1e-12)[0][0]]), drop


ref, dev = load_run()
ys = sorted(dev)
pts = {y: classify(dev[y], ref) for y in ys}
for y in ys:
    print(f"y={y:6.3f}  {pts[y][0]:8s} onset={pts[y][1]}  drop=10^{pts[y][2]:.2f}")

# ------------------------------------------------------------ IV: before vs after the strike
edge = dev[0.125]
fig, ax = plt.subplots(figsize=(7.4, 6.6))
m = ref[:, 0] > 0
ax.semilogy(ref[m, 0], ref[m, 1], color=INK, lw=2.6)
m = edge[:, 0] > 0
ax.semilogy(edge[m, 0], edge[m, 1], color=BLUE, lw=2.6, marker="o", ms=6, mec="white", mew=1.2)
ax.text(1.55, 260, "pre-irradiation", color=INK, fontsize=18, ha="center", va="bottom")
ax.text(1.55, 6e-5, "after a strike at the\ngate drain edge", color=BLUE, fontsize=18,
        ha="center", va="top", linespacing=1.15)
i0, i1 = ref[-1, 1], edge[-1, 1]
ax.annotate("", (2.92, i1), (2.92, i0), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.4))
mant, ex = f"{i0 / i1:.0e}".split("e+")
sup = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
ax.text(2.85, np.sqrt(i0 * i1), f"Id drop\n≈ {mant}×10{str(int(ex)).translate(sup)}",
        color=INK, fontsize=17, ha="right", va="center", linespacing=1.15)
style(ax, (0, 3.05))
ax.set_ylim(1e-5, 2e3)
ax.set_yticks([1e-4, 1e-2, 1, 1e2])
ax.set_yticklabels(["10⁻⁴", "10⁻²", "1", "10²"])
ax.set_xlabel("Vd (V)")
ax.set_ylabel("Id (mA/mm)")
fig.subplots_adjust(left=0.15, right=0.98, top=0.97, bottom=0.12)
fig.savefig("figures/strikeSlide_IV.png", dpi=200)
plt.close(fig)

# ------------------------------------------------------------ placement: mid-barrier row only
fig = plt.figure(figsize=(9.6, 7.6))
gs = fig.add_gridspec(3, 1, height_ratios=[0.8, 2.0, 2.0], hspace=0.14)
a0, a1, a2 = (fig.add_subplot(gs[i]) for i in range(3))

a0.set_xlim(-0.6, 2.65)
a0.set_ylim(22, -24)
a0.add_patch(Rectangle((-0.6, 0), 3.25, 15, color="#F3EEE4", lw=0))
a0.axhline(15, color=BLUE, lw=2.5)
a0.text(2.63, 17.5, "2DEG", ha="right", va="top", color=BLUE, fontsize=15)
a0.text(-0.63, 7.5, "AlGaN\n15 nm", ha="right", va="center", color=MUTED, fontsize=14)
a0.add_patch(Rectangle((GATE[0], -14), GATE[1] - GATE[0], 14, color=INK, lw=0))
a0.add_patch(Rectangle((FP[0], -14), FP[1] - FP[0], 6, color="#8A909C", lw=0))
a0.text(0, -15, "gate", ha="center", va="bottom", color=INK, fontsize=15)
a0.text(sum(FP) / 2, -15, "field plate", ha="center", va="bottom", color=MUTED, fontsize=15)
a0.text(-0.58, -15, "← source", ha="left", va="bottom", color=MUTED, fontsize=15)
a0.text(2.63, -15, "drain →", ha="right", va="bottom", color=MUTED, fontsize=15)
a0.scatter(ys, [7.5] * len(ys), s=40, color=BLUE, edgecolor="white", lw=1, zorder=3)
a0.axis("off")

on = np.array([pts[y][1] for y in ys])
a1.plot(ys, on, color=BLUE, lw=2.4, zorder=3)
for y in ys:
    c, o, _ = pts[y]
    if c == "collapse":
        a1.plot(y, o, "o", ms=9, color=BLUE, mec="white", mew=1.5, zorder=4)
    elif c == "none":
        a1.plot(y, NONE_ROW, "o", ms=7, color=PALE, zorder=3)
    else:
        a1.plot(y, OFF_ROW, "s", ms=7, color=PALE, zorder=3)
a1.annotate("0.2 V", (0.125, pts[0.125][1]), xytext=(0.32, 0.3), color=INK, fontsize=16,
            va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
style(a1)
zones(a1)
a1.axhspan(3.15, 3.75, color="#F4F5F7", lw=0, zorder=0)
a1.set_ylim(-0.6, 3.75)
a1.set_yticks([OFF_ROW, 0, 1, 2, 3, NONE_ROW])
a1.set_yticklabels(["off at rest", "0", "1", "2", "3", "none"])
a1.set_ylabel("onset Vd (V)")
a1.set_xticklabels([])

yd = [y for y in ys if pts[y][0] != "off"]
dr = [pts[y][2] for y in yd]
a2.plot(yd, dr, color=BLUE, lw=2.4, marker="o", ms=8, mec="white", mew=1.4, zorder=3)
fpd = [pts[y][2] for y in yd if FP[0] - 1e-6 <= y <= FP[1] + 1e-6 and y < 0.6]
a2.text(0.505, max(fpd) + 1.4, f"{10 ** min(fpd):.0f}–{10 ** max(fpd):.0f}×", color=INK,
        fontsize=16, ha="center", va="bottom")
style(a2)
zones(a2)
a2.set_ylim(-0.3, 11.2)
a2.set_yticks([0, 2, 4, 6, 8])
a2.set_yticklabels(["1×", "10²", "10⁴", "10⁶", "10⁸"])
a2.set_ylabel("Id drop at 3 V")
a2.set_xlabel("strike position y (µm), gate centre = 0")
a2.text(1.95, 9.9, r"$\mathrm{I_D\ drop}=\dfrac{I_D^{\,\mathrm{pre}}(V_D=3\ \mathrm{V})}"
        r"{I_D^{\,\mathrm{post}}(V_D=3\ \mathrm{V})}$", color=INK, fontsize=21,
        ha="center", va="center")
fig.subplots_adjust(left=0.15, right=0.985, top=0.99, bottom=0.09)
fig.align_ylabels([a1, a2])
fig.savefig("figures/strikeSlide_placement.png", dpi=200)
plt.close(fig)

# ------------------------------------------------------------ HighK vs SiN lateral field
cuts = np.genfromtxt("archive/static_mobility/figures/fieldPlate_cuts.csv", delimiter=",",
                     names=True)
fig, axs = plt.subplots(1, 3, figsize=(16.8, 5.6), sharey=True)
for ax, v in zip(axs, (3, 10, 20)):
    m = (cuts["Vd"] == v) & (cuts["y_um"] > -0.5) & (cuts["y_um"] < 2.1)
    y = cuts["y_um"][m]
    ax.plot(y, cuts["E_sin_Vcm"][m] / 1e3, color=ORANGE, lw=2.4)
    ax.plot(y, cuts["E_highk_Vcm"][m] / 1e3, color=BLUE, lw=2.4)
    style(ax, (-0.45, 2.05))
    zones(ax)
    ax.set_title(f"Vd = {v} V", color=INK, fontsize=20, loc="left", fontweight="semibold")
    ax.set_xlabel("y (µm), gate centre = 0")
    ax.text(0, 575, "gate", ha="center", color=MUTED, fontsize=15)
    ax.text(sum(FP) / 2, 575, "field plate", ha="center", color=MUTED, fontsize=15)
axs[0].set_ylim(0, 620)
axs[0].set_ylabel("lateral field along the 2DEG (kV/cm)")
axs[0].text(0.5, 330, "curves overlap", color=MUTED, fontsize=16)
axs[0].text(1.1, 120, "HighK (εr 35)", color=BLUE, fontsize=17)
axs[0].text(1.1, 70, "SiN (εr 6.3)", color=ORANGE, fontsize=17)
a = axs[2]
a.annotate("416 → 202\n−51%", (0.53, 416), xytext=(0.95, 450), color=INK, fontsize=16,
           va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
a.annotate("9 → 116", (1.0, 116), xytext=(1.3, 230), color=INK, fontsize=16, va="center",
           arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
axs[1].annotate("140 → 98\n−30%", (0.49, 140), xytext=(0.95, 300), color=INK, fontsize=16,
                va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
fig.subplots_adjust(left=0.06, right=0.995, top=0.92, bottom=0.14, wspace=0.08)
fig.savefig("figures/fieldSlide_highk.png", dpi=200)
plt.close(fig)
print("wrote figures/strikeSlide_IV.png, strikeSlide_placement.png, fieldSlide_highk.png")
