"""Full x-y trap sensitivity map (job: see progress.md, 2026-10-01).

Gaussian trap blob (Run F levels) centred from the top of the HighK (x=-0.275
um) to 0.5 um into the GaN (x=0.515), across the channel (y=-0.4..2.5 um).
Insulator parts of the blob are static charge: sign -1 (filled, -q*N) at every
position, +1 (fixed positive) at insulator-centred positions.

Per device: r_rest = Id/Id_no-trap at Vd=0.1 V, r_3V = Id/Id_no-trap at 3 V,
r_worst = min over Vd of Id/Id_no-trap, collapse onset / depth vs trap-free
(only for devices conducting at rest), regime.

Writes figures/trapXYMap_metrics.csv, figures/trapXYMap_3d.png (3D surfaces,
sign -1), figures/trapXYMap_map.png (2D maps over the device cross-section)
and figures/trapXYMap_sign.png (-1 vs +1 at insulator positions).
"""
import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Rectangle

RUN = "results/20261001_trapXYMap"
VD_END = 3.0
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
SEQ = LinearSegmentedColormap.from_list(
    "blue_seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
# diverging: orange = current raised, grey = no change, blue = current cut
DIV = LinearSegmentedColormap.from_list(
    "div", ["#b4441b", "#eb6834", "#f6c3a6", "#f2f1ee", "#a9c9f2", "#3987e5", "#0d366b"])
METALS = [((-0.125, 0.125), (-0.05, -0.005), "gate"),
          ((-0.325, 0.485), (-0.20, -0.05), "T-gate"),
          ((0.285, 0.725), (-0.57, -0.30), "field plate")]
LAYERS = [(-0.30, "HighK top"), (-0.20, ""), (-0.05, "Nitride"), (0.0, "AlGaN"),
          (0.015, "2DEG / GaN")]


def load(p):
    d = np.loadtxt(p, delimiter=",", ndmin=2)
    return d[:, 0], d[:, 1]


ref, dev = None, {}
for t in glob.glob(f"{RUN}/task_*") + glob.glob(f"{RUN}Retry/task_*"):
    p = json.load(open(os.path.join(t, "params.json")))
    c = glob.glob(os.path.join(t, "pulsedIV_*.csv"))
    if not c or os.path.getsize(c[0]) == 0:
        continue
    vd, idd = load(c[0])
    if p["trapPeak"] < 1e12:
        ref = (vd, idd)
        continue
    k = (p["insTrapSign"], p["trapMeanX"], p["trapMeanY"])
    if k not in dev or vd[-1] > dev[k][0][-1]:
        dev[k] = (vd, idd)
if ref is None:
    raise SystemExit("trap-free reference missing")
vr, ir = ref
iref = lambda v: np.interp(v, vr, ir)

rows = []
for (sg, x, y), (vd, idd) in sorted(dev.items()):
    done = abs(vd[-1] - VD_END) < 1e-6
    m = vd > 0.05
    ratio = idd[m] / iref(vd[m])
    ipk = int(np.argmax(idd))
    pk = idd[ipk]
    post = idd[ipk:]
    imin = ipk + int(np.argmin(post))
    r_rest = float(ratio[0])
    below = np.nonzero(post < pk / 10)[0]
    onset = vd[ipk + below[0]] if below.size else np.nan
    depth = iref(vd[imin]) / idd[imin]
    if r_rest < 0.1:
        regime, onset, depth = "off at rest", np.nan, np.nan
    elif np.isfinite(onset):
        regime = "collapse"
    else:
        regime = "no collapse" if done else "incomplete"
        if not done:
            depth = np.nan
    rows.append(dict(insTrapSign=sg, trapMeanX=x, trapMeanY=y, regime=regime,
                     complete=int(done), last_Vd=vd[-1], r_rest=r_rest,
                     r_3V=float(idd[-1] / iref(VD_END)) if done else np.nan,
                     r_worst=float(ratio.min()), onset_Vd=onset,
                     collapse_depth_vs_ref=depth))

os.makedirs("figures", exist_ok=True)
cols = list(rows[0])
with open("figures/trapXYMap_metrics.csv", "w") as f:
    f.write(",".join(cols) + "\n")
    for r in rows:
        f.write(",".join(r[c] if isinstance(r[c], str) else f"{r[c]:.6g}"
                         for c in cols) + "\n")
print(f"{len(rows)} devices, {sum(r['complete'] for r in rows)} complete; "
      f"ref Id(3V) = {iref(VD_END):.4g} mA/mm")
for sg in (-1, 1):
    rs = [r for r in rows if r["insTrapSign"] == sg]
    reg = {}
    for r in rs:
        reg[r["regime"]] = reg.get(r["regime"], 0) + 1
    print(f"  sign {sg:+d}: {len(rs)} devices: " +
          ", ".join(f"{k} {v}" for k, v in sorted(reg.items())))

plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})


def grid(sg, key, transform):
    xs = sorted({r["trapMeanX"] for r in rows if r["insTrapSign"] == sg})
    ys = sorted({r["trapMeanY"] for r in rows if r["insTrapSign"] == sg})
    Z = np.full((len(xs), len(ys)), np.nan)
    for r in rows:
        if r["insTrapSign"] == sg and np.isfinite(r[key]) and r[key] > 0:
            Z[xs.index(r["trapMeanX"]), ys.index(r["trapMeanY"])] = transform(r[key])
    return np.array(xs), np.array(ys), Z


# 1) 3D surfaces, sign -1: suppression at 3 V and worst-case over the sweep
fig = plt.figure(figsize=(16, 7.2))
for k, (key, lab) in enumerate((("r_3V", "log10 suppression at Vd = 3 V"),
                                ("r_worst", "log10 worst suppression, Vd 0.1-3 V"))):
    xs, ys, Z = grid(-1, key, lambda v: -np.log10(v))
    Y, X = np.meshgrid(ys, xs * 1e3)
    ax = fig.add_subplot(1, 2, k + 1, projection="3d")
    ax.plot_surface(Y, X, Z, cmap=SEQ, edgecolor="white", linewidth=0.4,
                    alpha=0.93, vmin=np.nanmin(Z), vmax=np.nanmax(Z))
    ok = np.isfinite(Z)
    ax.scatter(Y[ok], X[ok], Z[ok], color=INK, s=6, depthshade=False)
    ax.set_xlabel("y, lateral (µm)\nsource → drain", labelpad=8)
    ax.set_ylabel("x, depth (nm)\nHighK top → GaN", labelpad=8)
    ax.set_zlabel(lab, labelpad=6)
    ax.view_init(elev=28, azim=-55)
    ax.set_title(lab, color=INK, fontsize=11)
fig.suptitle("Trap-blob sensitivity across the device (Run F levels; insulator "
             "parts fully filled, -q·N; holes = inside metal)", color=INK,
             fontsize=12)
fig.tight_layout()
fig.savefig("figures/trapXYMap_3d.png", dpi=140)
plt.close(fig)


# 2) 2D maps over the cross-section (depth down, as in the device)
def outline(ax):
    for (y0, y1), (x0, x1), name in METALS:
        ax.add_patch(Rectangle((y0, x0 * 1e3), y1 - y0, (x1 - x0) * 1e3,
                               fill=False, edgecolor=INK, lw=1.2, hatch="//"))
        if x0 > -0.35:
            ax.text((y0 + y1) / 2, (x0 + x1) / 2 * 1e3, name, ha="center",
                    va="center", fontsize=8, color=INK,
                    bbox=dict(fc="white", ec="none", alpha=0.7, pad=1))
    for xl, name in LAYERS:
        ax.axhline(xl * 1e3, color=MUTED, lw=0.7, ls=":")
        if name:
            ax.text(2.62, xl * 1e3, name, fontsize=8, color=MUTED, va="bottom",
                    ha="right")


fig, axs = plt.subplots(1, 2, figsize=(16, 6.4), constrained_layout=True)
for ax, (key, lab) in zip(axs, (("r_rest", "Id / Id_no-trap at rest (Vd = 0.1 V)"),
                                ("r_3V", "Id / Id_no-trap at Vd = 3 V"))):
    xs, ys, Z = grid(-1, key, np.log10)
    lim = max(1.0, np.nanmax(np.abs(Z)))
    pc = ax.pcolormesh(ys, xs * 1e3, Z, cmap=DIV, shading="nearest",
                       norm=TwoSlopeNorm(vmin=-lim, vcenter=0.0, vmax=max(lim * 0.05, 0.05)))
    outline(ax)
    ax.set_ylim(530, -310)
    ax.set_xlim(-0.45, 2.65)
    ax.set_xlabel("y, lateral position of the trap blob (µm), source → drain")
    ax.set_ylabel("x, depth (nm), surface stack at top")
    ax.set_title(lab + " - log10, blue = current cut", color=INK, fontsize=11)
    fig.colorbar(pc, ax=ax, shrink=0.9, label="log10(Id / Id_no-trap)")
fig.suptitle("Where a trap blob hurts the device (Run F levels, insulator parts "
             "-q·N); hatched = metal", color=INK, fontsize=12)
fig.savefig("figures/trapXYMap_map.png", dpi=140)
plt.close(fig)

# 3) Sign comparison at insulator-centred positions
ins = sorted({(r["trapMeanX"], r["trapMeanY"]) for r in rows
              if r["insTrapSign"] == 1})
if ins:
    fig, axs = plt.subplots(1, 2, figsize=(15, 5.6), constrained_layout=True,
                            sharey=True)
    xs_i = sorted({x for x, _ in ins})
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
    for ax, sg in zip(axs, (-1, 1)):
        for c, x in zip(colors, xs_i):
            pts = sorted((r["trapMeanY"], np.log10(r["r_3V"])) for r in rows
                         if r["insTrapSign"] == sg and r["trapMeanX"] == x
                         and np.isfinite(r["r_3V"]))
            if pts:
                yy, vv = zip(*pts)
                ax.plot(yy, vv, color=c, lw=2, marker="o", ms=5, mec="white",
                        label=f"x = {x * 1e3:g} nm")
        ax.axhline(0, color=MUTED, lw=1)
        ax.axvspan(-0.125, 0.125, color=GRID, alpha=0.7, lw=0)
        ax.axvspan(0.285, 0.725, color=GRID, alpha=0.4, lw=0)
        ax.grid(True, color=GRID, lw=0.8)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
        ax.set_title(f"insulator charge {'-q·N (filled)' if sg < 0 else '+q·N (positive)'}",
                     color=INK)
        ax.set_xlabel("y (µm), source → drain")
    axs[0].set_ylabel("log10(Id / Id_no-trap) at Vd = 3 V\n(below 0 = current cut)")
    axs[1].legend(frameon=False, fontsize=9, loc="lower right")
    fig.suptitle("Traps centred in the insulators: sign of the trapped charge "
                 "(shaded: gate, field plate)", color=INK, fontsize=12)
    fig.savefig("figures/trapXYMap_sign.png", dpi=140)
    plt.close(fig)
print("wrote figures/trapXYMap_{metrics.csv,3d.png,map.png,sign.png}")
