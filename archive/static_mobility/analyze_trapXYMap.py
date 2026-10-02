"""Full x-y trap sensitivity map (job: see progress.md, 2026-10-01).

Gaussian trap blob (Run F levels) centred from the top of the HighK (x=-0.275
um) to 0.5 um into the GaN (x=0.515), across the channel (y=-0.4..2.5 um).
Insulator parts of the blob are static charge: sign -1 (filled, -q*N) at every
position, +1 (fixed positive) at insulator-centred positions.

Per device: r_rest = Id/Id_no-trap at Vd=0.1 V, r_3V = Id/Id_no-trap at 3 V,
r_worst = min over Vd of Id/Id_no-trap, collapse onset / depth vs trap-free
(only for devices conducting at rest), regime.

Writes figures/trapXYMap_metrics.csv, figures/trapXYMap_3d.png (3D surfaces,
sign -1), figures/trapXYMap_map.png and _map_plus.png (2D maps over the
device cross-section, sign -1 / +1)
and figures/trapXYMap_sign.png (-1 vs +1 at insulator positions) and
figures/trapXYMap_neutral.png (companion run results/20261001_trapXYMap0:
insulator traps neutral, sign 0, x -30..80 nm, side by side with -1 / +1)
and figures/trapXYMap_3d_neutral.png (its 3D surfaces).
"""
import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Rectangle

RUN = "results/archive_static_mobility/20261001_trapXYMap"
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
for t in (glob.glob(f"{RUN}/task_*") + glob.glob(f"{RUN}Retry/task_*")
          + glob.glob(f"{RUN}0/task_*")):
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
for sg in (-1, 0, 1):
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


FLOOR = 8.0   # |log10| beyond ~8 is the numerical noise floor (Id ~1e-8 mA/mm)


def layer(x):
    return ("HighK" if x < -0.05 else "Nitride" if x < 0 else
            "AlGaN" if x < 0.015 else "GaN")


def in_metal(x, y):
    return any(y0 < y < y1 and x0 < x < x1 for (y0, y1), (x0, x1), _ in METALS)


def xlabels(xs):
    return [f"{x * 1e3:g} {layer(x)}" for x in xs]


# 1) 3D surfaces, depth on evenly spaced rows (the action is in a ~70 nm band
#    that a linear axis would squash)
PANELS = {"r_rest": "suppression at rest, Vd = 0.1 V",
          "r_3V": "suppression at Vd = 3 V",
          "r_worst": "worst suppression, Vd 0.1-3 V"}


def surf3d(sg, keys, title, out, azim=-128):
    fig = plt.figure(figsize=(8 * len(keys), 7.4))
    for k, key in enumerate(keys):
        lab = PANELS[key]
        xs, ys, Z = grid(sg, key, lambda v: min(-np.log10(v), FLOOR))
        Y, X = np.meshgrid(ys, np.arange(len(xs)))
        ax = fig.add_subplot(1, len(keys), k + 1, projection="3d")
        ax.plot_surface(Y, X, np.where(np.isfinite(Z), Z, np.nan), cmap=SEQ,
                        edgecolor="white", linewidth=0.4, alpha=0.93, vmin=0, vmax=FLOOR)
        ok = np.isfinite(Z)
        ax.scatter(Y[ok], X[ok], Z[ok], color=INK, s=6, depthshade=False)
        ax.set_yticks(np.arange(len(xs)))
        ax.set_yticklabels(xlabels(xs), fontsize=7)
        ax.set_xlabel("y, lateral (µm)\nsource → drain", labelpad=8)
        ax.set_ylabel("trap centre depth (nm)", labelpad=22)
        ax.set_zlabel(f"log10 {lab}", labelpad=6)
        ax.set_zlim(0, FLOOR)
        ax.view_init(elev=32, azim=azim)
        ax.set_title(lab, color=INK, fontsize=11)
    fig.suptitle(title, color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


surf3d(-1, ("r_3V", "r_worst"),
       "Trap-blob sensitivity across the device (Run F levels; insulator parts fully "
       f"filled, -q·N; capped at 1e{FLOOR:g} = noise floor; holes = metal)",
       "figures/trapXYMap_3d.png")
if any(r["insTrapSign"] == 0 for r in rows):
    surf3d(0, ("r_rest", "r_3V", "r_worst"),
           "Neutral insulator traps (sign 0): Run F blob, x -30…80 nm. At rest only the gate "
           "region is off; under bias the access region collapses "
           f"(capped at 1e{FLOOR:g}; hole = metal)",
           "figures/trapXYMap_3d_neutral.png")

# 2) 2D maps over the cross-section, rows = sampled depths (top = HighK top)
DIVR = DIV.reversed()   # blue = current cut, orange = current raised
for sg in (-1, 1):
    fig, axs = plt.subplots(1, 2, figsize=(16, 6.4 if sg < 0 else 3.6),
                            constrained_layout=True)
    for ax, (key, lab) in zip(axs, (("r_rest", "Id / Id_no-trap at rest (Vd = 0.1 V)"),
                                    ("r_3V", "Id / Id_no-trap at Vd = 3 V"))):
        xs, ys, Z = grid(sg, key, lambda v: max(np.log10(v), -FLOOR))
        pc = ax.pcolormesh(np.arange(len(ys) + 1) - 0.5, np.arange(len(xs) + 1) - 0.5, Z,
                           cmap=DIVR, norm=TwoSlopeNorm(vmin=-FLOOR, vcenter=0, vmax=1))
        for i, x in enumerate(xs):
            for j, y in enumerate(ys):
                if in_metal(x, y):
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                           hatch="//", ec=MUTED, lw=0))
                elif not np.isfinite(Z[i, j]):
                    ax.text(j, i, "?", ha="center", va="center", color=INK, fontsize=8)
        for i in range(1, len(xs)):
            if layer(xs[i]) != layer(xs[i - 1]):
                ax.axhline(i - 0.5, color=INK, lw=0.8)
        ax.set_yticks(np.arange(len(xs)))
        ax.set_yticklabels(xlabels(xs), fontsize=8)
        ax.set_xticks(np.arange(len(ys)))
        ax.set_xticklabels([f"{y:g}" for y in ys], fontsize=8)
        ax.invert_yaxis()
        for j, y in enumerate(ys):
            if -0.125 <= y <= 0.125:
                ax.axvspan(j - 0.5, j + 0.5, ymin=0, ymax=0.012, color=INK)
        ax.set_xlabel("y, lateral trap position (µm), source → drain (black tick = under gate)")
        ax.set_ylabel("trap centre depth (nm), layer")
        ax.set_title(lab, color=INK, fontsize=11)
        fig.colorbar(pc, ax=ax, shrink=0.9, label=f"log10(Id / Id_no-trap), floor -{FLOOR:g}")
    fig.suptitle(f"Where a trap blob hurts the device (Run F levels, insulator parts "
                 f"{'-q·N, fully filled' if sg < 0 else '+q·N'}); blue = current cut, "
                 "hatched = metal, ? = did not finish", color=INK, fontsize=12)
    fig.savefig(f"figures/trapXYMap_map{'' if sg < 0 else '_plus'}.png", dpi=140)
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
            pts = sorted((r["trapMeanY"], max(np.log10(r["r_3V"]), -FLOOR)) for r in rows
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
    axs[0].set_ylabel(f"log10(Id / Id_no-trap) at Vd = 3 V\n(below 0 = current cut; floor -{FLOOR:g})")
    axs[1].legend(frameon=False, fontsize=9, loc="lower right")
    fig.suptitle("Traps centred in the insulators: sign of the trapped charge "
                 "(shaded: gate, field plate)", color=INK, fontsize=12)
    fig.savefig("figures/trapXYMap_sign.png", dpi=140)
    plt.close(fig)

# 4) Neutral vs filled vs positive insulator charge at the shared near-surface rows
if any(r["insTrapSign"] == 0 for r in rows):
    xs0 = sorted({r["trapMeanX"] for r in rows if r["insTrapSign"] == 0})
    ys0 = sorted({r["trapMeanY"] for r in rows if r["insTrapSign"] == 0})
    look = {(r["insTrapSign"], r["trapMeanX"], r["trapMeanY"]): r for r in rows}
    fig, axs = plt.subplots(2, 3, figsize=(18, 7.4), constrained_layout=True,
                            sharex=True, sharey=True)
    for c, (sg, name) in enumerate(((0, "neutral (sign 0)"), (-1, "filled, -q·N (sign -1)"),
                                    (1, "positive, +q·N (sign +1)"))):
        for rr, (key, lab) in enumerate((("r_rest", "at rest, Vd = 0.1 V"),
                                         ("r_3V", "Vd = 3 V"))):
            ax = axs[rr, c]
            Z = np.full((len(xs0), len(ys0)), np.nan)
            for i, x in enumerate(xs0):
                for j, y in enumerate(ys0):
                    r = look.get((sg, x, y))
                    if r is not None and np.isfinite(r[key]) and r[key] > 0:
                        Z[i, j] = max(np.log10(r[key]), -FLOOR)
            pc = ax.pcolormesh(np.arange(len(ys0) + 1) - 0.5, np.arange(len(xs0) + 1) - 0.5,
                               Z, cmap=DIVR, norm=TwoSlopeNorm(vmin=-FLOOR, vcenter=0, vmax=1))
            for i, x in enumerate(xs0):
                for j, y in enumerate(ys0):
                    if in_metal(x, y):
                        ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                               hatch="//", ec=MUTED, lw=0))
                    elif not np.isfinite(Z[i, j]) and (sg, x, y) in look:
                        ax.text(j, i, "?", ha="center", va="center", color=INK, fontsize=8)
                    elif (sg, x, y) not in look:
                        ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fc="white", ec=GRID, lw=0.5))
                    r = look.get((sg, x, y))
                    if r is not None and r["regime"] == "collapse":
                        ax.text(j, i, "C", ha="center", va="center", color="white",
                                fontsize=8, fontweight="bold")
            for i in range(1, len(xs0)):
                if layer(xs0[i]) != layer(xs0[i - 1]):
                    ax.axhline(i - 0.5, color=INK, lw=0.8)
            ax.set_yticks(np.arange(len(xs0)))
            ax.set_yticklabels(xlabels(xs0), fontsize=8)
            ax.set_xticks(np.arange(len(ys0)))
            ax.set_xticklabels([f"{y:g}" for y in ys0], fontsize=8)
            ax.set_title(f"{name}: {lab}", color=INK, fontsize=10)
            if rr == 1:
                ax.set_xlabel("y (µm), source → drain")
        axs[0, 0].invert_yaxis()
    for rr in range(2):
        axs[rr, 0].set_ylabel("trap centre depth (nm)")
    fig.colorbar(pc, ax=axs, shrink=0.8, label=f"log10(Id / Id_no-trap), floor -{FLOOR:g}")
    fig.suptitle("Insulator trap charge: neutral vs filled vs positive (Run F blob; C = hot-electron "
                 "collapse, white = not run, hatched = metal)", color=INK, fontsize=12)
    fig.savefig("figures/trapXYMap_neutral.png", dpi=140)
    plt.close(fig)
print("wrote figures/trapXYMap_{metrics.csv,3d.png,3d_neutral.png,map.png,map_plus.png,sign.png,neutral.png}")
