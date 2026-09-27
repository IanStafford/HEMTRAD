"""Cone vs Gaussian trap shape at 2e18 cm^-3 / 0.75 eV (job 43536494).

Compares the cone sweep (5 geometries x 10 apex positions, apex at the AlGaN
surface) against the Gaussian 2e18/0.75 x=0 row of the trap-map sets run
(job 43513462: same Vd range, damping and retry driver).

Per device: at-rest fraction (Id / Id_no-trap at Vd=0.1 V), regime, collapse
onset, collapse depth vs trap-free at the post-collapse minimum, and
suppression at Vd=3 V (same definitions as analyze_trapMapSets.py).

Writes figures/trapCone_metrics.csv, figures/trapCone_shapes.png,
figures/trapCone_vs_position.png and figures/trapCone_IdVd.png.
"""
import glob
import json
import math
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scipy.special import erf

CONE = "results/20260927_trapCone"
GAUSS = "results/20260927_trapMapSets"
VD_END = 3.0
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
SEQ = LinearSegmentedColormap.from_list(
    "blue_seq", ["#ffffff", "#cde2fb", "#86b6ef", "#3987e5", "#0d366b"])
GATE, FP = (-0.125, 0.125), (0.285, 0.725)
PEAK, SIGMA, W0, EDGE = 2e18, 0.04, 0.01, 0.01


def load(path):
    d = np.loadtxt(path, delimiter=",", ndmin=2)
    return d[:, 0], d[:, 1]


def tasks(run):
    for t in glob.glob(f"{run}/task_*") + glob.glob(f"{run}Retry/task_*"):
        p = json.load(open(os.path.join(t, "params.json")))
        c = glob.glob(os.path.join(t, "pulsedIV_*.csv"))
        if c and os.path.getsize(c[0]) > 0:
            yield p, load(c[0])


ref, curves = None, {}
for p, (vd, idd) in tasks(CONE):
    if p["trapPeak"] < 1e12:
        ref = (vd, idd)
        continue
    key = (f"cone {p['coneLen']:g} µm / {p['coneAngle']:g}°", p["trapMeanY"])
    if key not in curves or vd[-1] > curves[key][0][-1]:
        curves[key] = (vd, idd)
for p, (vd, idd) in tasks(GAUSS):
    if p["trapPeak"] < 1e12 and ref is None:
        ref = (vd, idd)
    if (p["trapPeak"], p["trapLevel"], p["trapMeanX"]) == (2e18, 0.75, 0.0):
        key = ("gaussian (σ 0.04 µm)", p["trapMeanY"])
        if key not in curves or vd[-1] > curves[key][0][-1]:
            curves[key] = (vd, idd)
if ref is None:
    raise SystemExit("trap-free reference missing")
vd_ref, id_ref = ref
iref = lambda v: np.interp(v, vd_ref, id_ref)


def geom_key(name):
    if name.startswith("gaussian"):
        return (0, 0, 0)
    L, a = name.split()[1], name.split("/ ")[1].rstrip("°")
    return (1, float(L), float(a))


shapes = sorted({k[0] for k in curves}, key=geom_key)
ys = sorted({k[1] for k in curves})

rows = []
for (shape, y), (vd, idd) in sorted(curves.items(), key=lambda kv: (geom_key(kv[0][0]), kv[0][1])):
    done = abs(vd[-1] - VD_END) < 1e-6
    ipk = int(np.argmax(idd))
    pk = idd[ipk]
    post = idd[ipk:]
    imin = ipk + int(np.argmin(post))
    at_rest = idd[1] / iref(vd[1])
    below = np.nonzero(post < pk / 10)[0]
    onset = vd[ipk + below[0]] if below.size else np.nan
    depth = iref(vd[imin]) / idd[imin]
    if at_rest < 0.1:
        regime, onset, depth = "off at rest", np.nan, np.nan
    else:
        regime = "collapse" if np.isfinite(onset) else (
            "no collapse" if done else "incomplete")
        if regime == "incomplete":
            depth = np.nan
    supp = iref(VD_END) / idd[-1] if done else np.nan
    rows.append(dict(shape=shape, trapMeanY=y, regime=regime, complete=int(done),
                     last_Vd=vd[-1], at_rest_frac=at_rest, onset_Vd=onset,
                     collapse_depth_vs_ref=depth, suppression_3V=supp))

os.makedirs("figures", exist_ok=True)
cols = list(rows[0])
with open("figures/trapCone_metrics.csv", "w") as f:
    f.write(",".join(cols) + "\n")
    for r in rows:
        f.write(",".join(r[c] if isinstance(r[c], str) else f"{r[c]:.6g}"
                         for c in cols) + "\n")
print(f"{len(rows)} devices, {sum(r['complete'] for r in rows)} complete")
for s in shapes:
    rs = [r for r in rows if r["shape"] == s]
    reg = {}
    for r in rs:
        reg[r["regime"]] = reg.get(r["regime"], 0) + 1
    print(f"  {s:24s}: " + ", ".join(f"{k} {v}" for k, v in sorted(reg.items())))

color = {s: (INK if s.startswith("gaussian") else CAT[i - 1])
         for i, s in enumerate(shapes)}
dash = {s: ("--" if s.startswith("gaussian") else "-") for s in shapes}
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})


def style(ax):
    ax.grid(True, color=GRID, lw=0.8)
    for sd in ("top", "right"):
        ax.spines[sd].set_visible(False)


# 1) What the shapes look like (same formulas as TrapConc_* in the model).
def dens(shape, X, Y):
    if shape.startswith("gaussian"):
        return PEAK * np.exp(-(X ** 2 + Y ** 2) / (2 * SIGMA ** 2))
    L = float(shape.split()[1])
    a = float(shape.split("/ ")[1].rstrip("°"))
    w = W0 + math.tan(math.radians(a)) * X
    return (PEAK * 0.5 * (1 + erf((w - np.abs(Y)) / EDGE))
            * 0.5 * (1 + erf((X + 2 * EDGE) / EDGE))
            * 0.5 * (1 + erf((L - X) / EDGE)))


x = np.linspace(0, 0.25, 300)
y = np.linspace(-0.2, 0.2, 320)
Y, X = np.meshgrid(y, x)
fig, axs = plt.subplots(1, len(shapes), figsize=(3.0 * len(shapes), 3.4),
                        sharey=True, constrained_layout=True)
for ax, s in zip(axs, shapes):
    D = dens(s, X, Y)
    area = D.sum() * (x[1] - x[0]) * (y[1] - y[0]) / PEAK
    im = ax.pcolormesh(Y, X * 1e3, D, cmap=SEQ, vmin=0, vmax=PEAK,
                       shading="auto")
    ax.axhline(15, color=MUTED, lw=1, ls=":")
    ax.text(0.19, 13, "2DEG", color=MUTED, fontsize=7, ha="right", va="bottom")
    ax.set_title(f"{s}\narea {area:.4f} µm²", color=INK, fontsize=9)
    ax.set_xlabel("y from centre/apex (µm)")
    ax.invert_yaxis()
axs[0].set_ylabel("depth x (nm), surface at top")
fig.colorbar(im, ax=axs, shrink=0.85, label="trap density (cm⁻³)")
fig.suptitle("Trap distributions compared (2e18 cm⁻³ peak; area = in-material "
             "cross-section ∝ charge per gate width)", color=INK, fontsize=10)
fig.savefig("figures/trapCone_shapes.png", dpi=150)
plt.close(fig)

# 2) Metrics vs apex position.
metrics = [("at_rest_frac", "Id / Id_no-trap at Vd = 0.1 V\n(at rest)"),
           ("suppression_3V", "Id_no-trap / Id at Vd = 3 V")]
# collapse depth is only shown if some device actually collapses
if any(r["regime"] == "collapse" for r in rows):
    metrics.append(("collapse_depth_vs_ref",
                    "collapse depth vs trap-free\n(at post-collapse min)"))
fig, axs = plt.subplots(len(metrics), 1, figsize=(10, 3.4 * len(metrics) + 0.8),
                        sharex=True, constrained_layout=True)
for ax, (key, lab) in zip(axs, metrics):
    for lo, hi in (GATE, FP):
        ax.axvspan(lo, hi, color=GRID, alpha=0.7, lw=0)
    for s in shapes:
        pts = sorted((r["trapMeanY"], r[key]) for r in rows if r["shape"] == s)
        xv, v = zip(*pts)
        ax.plot(xv, v, color=color[s], ls=dash[s], lw=2, marker="o", ms=5,
                mec="white", mew=0.8, label=s)
    ax.set_yscale("log")
    ax.set_ylabel(lab)
    style(ax)
axs[0].text(0, 0.03, "gate", transform=axs[0].get_xaxis_transform(),
            ha="center", color=MUTED, fontsize=8)
axs[0].text(np.mean(FP), 0.03, "field plate",
            transform=axs[0].get_xaxis_transform(), ha="center",
            color=MUTED, fontsize=8)
axs[-1].set_xlabel("trap position trapMeanY (µm) - Gaussian centre / cone apex, "
                   "source → drain")
axs[1].legend(loc="upper right", ncol=2, frameon=False, fontsize=8)
same = [s for s in shapes if s.endswith("/ 30°")]
if len(same) > 1:
    axs[1].text(0.45, 0.30, "the three 30° cones (0.05, 0.1, 0.2 µm long)\n"
                "overlap exactly: depth beyond ~50 nm has no effect",
                transform=axs[1].transAxes, color=INK, fontsize=8)
note = ("" if any(r["regime"] == "collapse" for r in rows)
        else " - no hot-electron collapse for any shape or position")
fig.suptitle("Cone vs Gaussian trap shape, 2e18 cm⁻³ / 0.75 eV, at the AlGaN "
             "surface" + note, color=INK, fontsize=11, x=0.01, ha="left")
fig.savefig("figures/trapCone_vs_position.png", dpi=140)
plt.close(fig)

# 3) Id-Vd per apex position.
ncol = 5
nrow = math.ceil(len(ys) / ncol)
fig, axs = plt.subplots(nrow, ncol, figsize=(3.2 * ncol, 3.0 * nrow),
                        sharex=True, sharey=True, constrained_layout=True)
for ax, yy in zip(axs.flat, ys):
    ax.plot(vd_ref[1:], id_ref[1:], color=MUTED, lw=1.5, ls=":",
            label="no traps")
    for s in shapes:
        if (s, yy) in curves:
            vd, idd = curves[(s, yy)]
            ax.plot(vd[1:], idd[1:], color=color[s], ls=dash[s], lw=1.6,
                    label=s)
    ax.set_yscale("log")
    ax.set_ylim(1e-7, 300)
    ax.set_title(f"y = {yy:g} µm", color=INK, fontsize=9)
    style(ax)
for ax in axs[-1]:
    ax.set_xlabel("Vd (V)")
for ax in axs[:, 0]:
    ax.set_ylabel("Id (mA/mm)")
h, l = axs.flat[0].get_legend_handles_labels()
fig.legend(h, l, loc="outside lower center", ncol=len(l), frameon=False,
           fontsize=8)
fig.suptitle("Id-Vd by trap position: cone geometries vs Gaussian "
             "(2e18 cm⁻³ / 0.75 eV, surface)", color=INK, fontsize=11,
             x=0.01, ha="left")
fig.savefig("figures/trapCone_IdVd.png", dpi=130)
plt.close(fig)
print("wrote figures/trapCone_{metrics.csv,shapes.png,vs_position.png,IdVd.png}")
