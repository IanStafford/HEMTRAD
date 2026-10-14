"""Talk figures on trap placement, from the six position maps (65 positions each).

usage: python3 analysis/plot_posSlides.py
Set HEADLINE_FONT_DIR to a folder of Source Sans 3 TTFs to match the slides.
Classes and onsets as in plot_posVd.py / plot_posOnset.py (CLAUDE.md §10.0 rule).
Writes (sized to be shown ~1100 px wide):
  figures/posSlide_lateral.png  0.30 eV / 5e18: device strip with the trap grid, onset Vd
                                vs lateral y per depth, suppression at Vd = 3 V vs y
  figures/posSlide_sets.png     all six sets at the AlGaN surface (depth 0): onset Vd and
                                suppression at 3 V vs y, ordered from weakest to strongest
Prints the per-position table it plotted.
"""
import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Rectangle

INK, BODY, MUTED, GRID = "#14171F", "#394150", "#646B78", "#E2E4E9"
GATE, FP, LGD_DRAIN = (-0.125, 0.125), (0.285, 0.725), 3.285
FLOOR = 8.0                     # log10 suppression cap (~1e-8 mA/mm noise floor)
NONE_ROW, OFF_ROW = 3.45, -0.3  # where "no collapse by 3 V" / "off at rest" sit on the onset axis
SETS = [  # weakest -> strongest trapping (onset falls monotonically down the list)
    ("20261003_posMap_tl0.30_tp4e18", "0.30 eV, 4e18"),
    ("20261003_posMap_tl0.25_tp6e18", "0.25 eV, 6e18"),
    ("20261002_posMapLate", "0.30 eV, 5e18"),
    ("20261003_posMap_tl0.30_tp6e18", "0.30 eV, 6e18"),
    ("20261003_posMap_tl0.40_tp5e18", "0.40 eV, 5e18"),
    ("20261003_posMap_tl0.55_tp4e18", "0.55 eV, 4e18"),
]
RAMP6 = ["#B9CBE6", "#8FB0DD", "#5E8BCB", "#1B4F9C", "#123D7C", "#0B2447"]
RAMP5 = ["#9DB9E2", "#6E9BD8", "#3F73BD", "#1B4F9C", "#0B2E5E"]

FONT_DIR = os.environ.get("HEADLINE_FONT_DIR")
if FONT_DIR:
    for f in os.listdir(FONT_DIR):
        if f.endswith(".ttf"):
            font_manager.fontManager.addfont(os.path.join(FONT_DIR, f))
    plt.rcParams["font.family"] = "Source Sans 3"
plt.rcParams.update({"font.size": 16, "xtick.labelsize": 15, "ytick.labelsize": 15,
                     "axes.labelsize": 16, "axes.edgecolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.labelcolor": INK})


def load(run):
    ref, dev, vmax = None, {}, 0.0
    for t in glob.glob(f"results/{run}/task_*") + glob.glob(f"results/{run}Retry*/task_*"):
        p = json.load(open(os.path.join(t, "params.json")))
        c = glob.glob(os.path.join(t, "pulsedIV_*.csv"))
        if not c or os.path.getsize(c[0]) == 0:
            continue
        d = np.loadtxt(c[0], delimiter=",", ndmin=2)
        if p["trapPeak"] < 1e12:
            ref = (d[:, 0], d[:, 1])
            continue
        vmax = max(vmax, p.get("Vd_max", d[-1, 0]))
        k = (round(p["trapMeanX"] * 1e3, 2), p["trapMeanY"])
        if k not in dev or d[-1, 0] > dev[k][0][-1]:
            dev[k] = (d[:, 0], d[:, 1])
    if ref is None:
        raise SystemExit(f"{run}: trap-free reference missing")
    vr, ir = ref
    out = {}
    for k, (vd, idd) in dev.items():
        m = vd > 0.05
        v, i = vd[m], idd[m]
        sup = min(FLOOR, np.log10(np.interp(vd[-1], vr, ir) / max(idd[-1], 1e-30)))
        if i[0] / np.interp(v[0], vr, ir) < 0.1:
            out[k] = ("off", np.nan, sup)
            continue
        loss = 1.0 - i[1:] / i[:-1]
        mx = loss.max()
        cls = "deep" if mx > 0.95 else "medium" if mx >= 0.5 else "shallow"
        if cls == "shallow" and vd[-1] < vmax - 1e-6:
            out[k] = ("stalled", float(vd[-1] + 0.1), np.nan)
            continue
        if cls == "shallow":
            out[k] = ("shallow", np.nan, sup)
            continue
        thr = 0.95 if cls == "deep" else 0.5
        out[k] = (cls, float(v[1 + np.nonzero(loss >= thr - 1e-12)[0][0]]), sup)
    return out


def onset_axis(ax, label=True):
    ax.axhspan(3.15, 3.75, color="#F4F5F7", lw=0, zorder=0)
    ax.set_ylim(-0.55, 3.75)
    ax.set_yticks([OFF_ROW, 0, 1, 2, 3, NONE_ROW])
    ax.set_yticklabels(["off at rest", "0", "1", "2", "3", "none by 3 V"])
    if label:
        ax.set_ylabel("collapse onset Vd (V)")


def zones(ax, lab=False, top=None):
    for (lo, hi), name in ((GATE, "gate"), (FP, "field plate")):
        ax.axvspan(lo, hi, color="#EEF1F6", lw=0, zorder=0)
        if lab:
            ax.text((lo + hi) / 2, top, name, ha="center", va="bottom", color=MUTED, fontsize=14)


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)
    ax.set_xlim(-0.6, 2.65)


def series(ax, ys, pts, col, z=3):
    """pts: list of (cls, onset, sup) per y; draws onset line + class markers."""
    yv = np.array([o if c in ("deep", "medium") else np.nan for c, o, _ in pts])
    ax.plot(ys, yv, color=col, lw=2.2, zorder=z)
    for y, (c, o, _) in zip(ys, pts):
        if c == "deep":
            ax.plot(y, o, "o", ms=8, color=col, mec="white", mew=1.5, zorder=z + 1)
        elif c == "medium":
            ax.plot(y, o, "o", ms=8, mfc="white", mec=col, mew=2, zorder=z + 1)
        elif c == "stalled":
            ax.plot(y, o, "x", ms=9, color=col, mew=2.2, zorder=z + 1)
        elif c == "shallow":
            ax.plot(y, NONE_ROW, "o", ms=5, color=col, alpha=0.8, zorder=z)
        elif c == "off":
            ax.plot(y, OFF_ROW, "s", ms=6, color=col, zorder=z)


def sup_series(ax, ys, pts, col, z=3):
    s = np.array([p[2] for p in pts])
    ax.plot(ys, s, color=col, lw=2.2, zorder=z, marker="o", ms=6, mec="white", mew=1.2)


def legend_classes(ax, x, y, loc="upper left", ncol=4):
    items = [("o", dict(color=MUTED, mec="white")), ("o", dict(mfc="white", mec=MUTED, mew=2)),
             ("x", dict(color=MUTED, mew=2)), ("s", dict(color=MUTED))]
    names = ["deep (>95% drop)", "medium (50–95%)", "stalled", "off at rest"]
    h = [plt.Line2D([], [], marker=m, ls="", ms=8, **kw) for m, kw in items]
    ax.legend(h, names, loc=loc, bbox_to_anchor=(x, y), frameon=False, fontsize=14,
              ncol=ncol, handletextpad=0.3, columnspacing=1.2)


# ---------------------------------------------------------------- figure 1: lateral, one set
late = load("20261002_posMapLate")
ys = sorted({k[1] for k in late})
depths = sorted({k[0] for k in late})
fig = plt.figure(figsize=(11.0, 7.9))
gs = fig.add_gridspec(3, 1, height_ratios=[0.9, 2.3, 1.5], hspace=0.12)
a0, a1, a2 = (fig.add_subplot(gs[i]) for i in range(3))

# device strip: AlGaN barrier with the trap grid, gate and field plate above, 2DEG below
a0.set_xlim(-0.6, 2.65)
a0.set_ylim(24, -25)
a0.add_patch(Rectangle((-0.6, 0), 3.25, 15, color="#F3EEE4", lw=0))
a0.axhline(15, color="#1B4F9C", lw=2.5)
a0.text(2.63, 18.5, "2DEG", ha="right", va="top", color="#1B4F9C", fontsize=14)
a0.text(-0.63, 7.5, "AlGaN\n15 nm", ha="right", va="center", color=MUTED, fontsize=13)
a0.add_patch(Rectangle((GATE[0], -14), GATE[1] - GATE[0], 14, color=INK, lw=0))
a0.add_patch(Rectangle((FP[0], -14), FP[1] - FP[0], 6, color="#8A909C", lw=0))
a0.text(0, -15, "gate", ha="center", va="bottom", color=INK, fontsize=14)
a0.text(sum(FP) / 2, -15, "field plate", ha="center", va="bottom", color=MUTED, fontsize=14)
a0.text(-0.58, -15, "← source (−1.13)", ha="left", va="bottom", color=MUTED, fontsize=14)
a0.text(2.63, -15, "drain (3.29) →", ha="right", va="bottom", color=MUTED, fontsize=14)
for di, d in enumerate(depths):
    a0.scatter(ys, [d] * len(ys), s=26, color=RAMP5[di], edgecolor="white", lw=0.8, zorder=3)
a0.axis("off")

# onset vs y, one line per depth
for di, d in enumerate(depths):
    series(a1, ys, [late[(d, y)] for y in ys], RAMP5[di], z=3 + di)
style(a1)
zones(a1)
onset_axis(a1)
a1.set_xticklabels([])
lab = {0.0: "0 nm (surface)", 7.5: "7.5 nm", 15.0: "15 nm (at 2DEG)"}
for di, d in enumerate(depths):
    if d in lab:
        o = late[(d, 1.75)][1]
        col = RAMP5[di] if di > 1 else "#5E7FB0"
        if d == 0.0:  # above its line, clear of the stalled marks at y = 2.0
            a1.text(0.78, 2.68, lab[d], color=col, fontsize=14, va="center")
            continue
        a1.annotate(lab[d], (1.75, o), xytext=(1.86, {7.5: 2.36, 15.0: 1.72}[d]),
                    color=col, fontsize=14, va="center",
                    arrowprops=dict(arrowstyle="-", color=GRID, lw=1))
legend_classes(a1, 1.0, 0.0, loc="lower right", ncol=2)

# suppression at 3 V
for di, d in enumerate(depths):
    sup_series(a2, ys, [late[(d, y)] for y in ys], RAMP5[di], z=3 + di)
style(a2)
zones(a2)
a2.set_ylim(-0.3, 8.6)
a2.set_yticks([0, 2, 4, 6, 8])
a2.set_yticklabels(["1×", "10²", "10⁴", "10⁶", "10⁸"])
a2.set_ylabel("Id drop at 3 V")
a2.set_xlabel("trap lateral position y (µm), gate centre = 0")
fig.subplots_adjust(left=0.13, right=0.985, top=0.985, bottom=0.085)
fig.savefig("figures/posSlide_lateral.png", dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- figure 2: six sets at the surface
fig, (b1, b2) = plt.subplots(2, 1, figsize=(11.0, 7.9), gridspec_kw=dict(height_ratios=[2.3, 1.5], hspace=0.1))
tab = {}
for si, (run, name) in enumerate(SETS):
    m = load(run)
    tab[name] = m
    pts = [m[(0.0, y)] for y in ys]
    series(b1, ys, pts, RAMP6[si], z=3 + si)
    sup_series(b2, ys, pts, RAMP6[si], z=3 + si)
style(b1)
zones(b1)
onset_axis(b1)
b1.set_xticklabels([])
# direct labels at the right end of each collapsing line
ends = {"0.25 eV, 6e18": (1.05, 3.0, 1.0), "0.30 eV, 5e18": (1.75, 3.0, 1.75), "0.30 eV, 6e18": (2.4, 1.8, 2.4),
        "0.40 eV, 5e18": (2.4, 1.1, 2.4), "0.55 eV, 4e18": (2.4, 0.5, 2.4)}
txty = {"0.25 eV, 6e18": (0.3, 2.75), "0.30 eV, 5e18": (1.86, 3.0), "0.30 eV, 6e18": (2.43, 1.9),
        "0.40 eV, 5e18": (2.43, 1.18), "0.55 eV, 4e18": (2.43, 0.5)}
for si, (run, name) in enumerate(SETS):
    if name in txty:
        b1.text(*txty[name], name, color=RAMP6[si] if si > 1 else "#5E7FB0", fontsize=14, va="center",
                ha="left" if name != "0.25 eV, 6e18" else "left")
b1.text(0.85, 0.12, "0.30 eV, 4e18: only the gate edge\n(medium, 0.4 V)", color="#7F97BF", fontsize=14, va="center")
legend_classes(b1, 0.0, 1.0, loc="lower left")
style(b2)
zones(b2, lab=True, top=8.0)
b2.set_ylim(-0.3, 8.6)
b2.set_yticks([0, 2, 4, 6, 8])
b2.set_yticklabels(["1×", "10²", "10⁴", "10⁶", "10⁸"])
b2.set_ylabel("Id drop at 3 V")
b2.set_xlabel("trap lateral position y (µm), gate centre = 0; traps at the AlGaN surface")
fig.subplots_adjust(left=0.13, right=0.985, top=0.94, bottom=0.085)
for ax in (b1, b2):
    ax.set_xlim(-0.6, 3.1)
fig.savefig("figures/posSlide_sets.png", dpi=200)
plt.close(fig)

for name, m in tab.items():
    ncol = sum(c in ("deep", "medium", "stalled") for c, _, _ in m.values())
    surf = [f"{m[(0.0, y)][1]:.1f}" if m[(0.0, y)][0] in ("deep", "medium") else m[(0.0, y)][0][:3] for y in ys]
    print(f"{name}: {ncol}/65 collapse; surface onset by y {ys}: {surf}")
print("wrote figures/posSlide_lateral.png, figures/posSlide_sets.png")
