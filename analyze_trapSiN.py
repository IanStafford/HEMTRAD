"""HighK vs SiN passivation: the 10f 2e18 cm^-3 / 0.75 eV trap map on both devices.

HighK device: job 43513462 (+ retry 43515232), results/20260927_trapMapSets*.
SiN device (rfdevice_SiN.tcl, every HighK region -> Nitride): job in
progress.md (2026-10-01), results/20261001_trapSiN. Each device is normalised to
its own trap-free reference.

Per device: r_rest = Id/Id_no-trap at Vd=0.1 V, r_3V at 3 V, r_worst = min over
Vd, collapse onset (first Vd where Id < running max / 10, for devices that
conduct at rest), collapse depth vs trap-free at the post-onset minimum, regime.

Writes figures/trapSiN_metrics.csv, figures/trapSiN_3d.png (suppression
surfaces, HighK vs SiN, shared scale) and figures/trapSiN_compare.png (trap-free
Id-Vd of both devices, suppression vs position per depth, Id-Vd at the gate,
and the HighK/SiN suppression ratio per position).
"""
import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

RUNS = {"HighK": ["results/20260927_trapMapSets", "results/20260927_trapMapSetsRetry"],
        "SiN": ["results/20261001_trapSiN", "results/20261001_trapSiNRetry"]}
TP, TL = 2e18, 0.75
VD_END = 3.0
SEQ = LinearSegmentedColormap.from_list(
    "blue_seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
DEV_C = {"HighK": "#2a78d6", "SiN": "#eb6834"}
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
GATE, FP = (-0.125, 0.125), (0.285, 0.725)


def load(p):
    d = np.loadtxt(p, delimiter=",", ndmin=2)
    return d[:, 0], d[:, 1]


refs, dev = {}, {}
for name, runs in RUNS.items():
    for run in runs:
        for t in glob.glob(f"{run}/task_*"):
            p = json.load(open(os.path.join(t, "params.json")))
            c = glob.glob(os.path.join(t, "pulsedIV_*.csv"))
            if not c or os.path.getsize(c[0]) == 0:
                continue
            vd, idd = load(c[0])
            if p["trapPeak"] < 1e12:
                if name not in refs or vd[-1] > refs[name][0][-1]:
                    refs[name] = (vd, idd)
                continue
            if (p["trapPeak"], p["trapLevel"]) != (TP, TL):
                continue
            k = (name, p["trapMeanX"], p["trapMeanY"])
            if k not in dev or vd[-1] > dev[k][0][-1]:
                dev[k] = (vd, idd)
for name in RUNS:
    if name not in refs:
        raise SystemExit(f"trap-free reference missing for {name}")
iref = {n: (lambda v, n=n: np.interp(v, refs[n][0], refs[n][1])) for n in refs}

rows = []
for (name, x, y), (vd, idd) in sorted(dev.items()):
    done = abs(vd[-1] - VD_END) < 1e-6
    m = vd > 0.05
    ratio = idd[m] / iref[name](vd[m])
    runmax = np.maximum.accumulate(idd)
    below = np.nonzero(idd < runmax / 10)[0]
    onset = vd[below[0]] if below.size else np.nan
    imin = (below[0] + int(np.argmin(idd[below[0]:]))) if below.size else 0
    r_rest = float(ratio[0])
    depth = iref[name](vd[imin]) / idd[imin] if below.size else np.nan
    if r_rest < 0.1:
        regime, onset, depth = "off at rest", np.nan, np.nan
    elif below.size:
        regime = "collapse"
    else:
        regime = "no collapse" if done else "incomplete"
    rows.append(dict(device=name, trapMeanX=x, trapMeanY=y, regime=regime,
                     complete=int(done), last_Vd=vd[-1], r_rest=r_rest,
                     r_3V=float(idd[-1] / iref[name](VD_END)) if done else np.nan,
                     r_worst=float(ratio.min()), onset_Vd=onset,
                     collapse_depth_vs_ref=depth))

os.makedirs("figures", exist_ok=True)
cols = list(rows[0])
with open("figures/trapSiN_metrics.csv", "w") as f:
    f.write(",".join(cols) + "\n")
    for r in rows:
        f.write(",".join(r[c] if isinstance(r[c], str) else f"{r[c]:.6g}"
                         for c in cols) + "\n")
for name in RUNS:
    vr, ir = refs[name]
    print(f"{name}: trap-free Id(0.1/1/3 V) = {iref[name](0.1):.4g} / "
          f"{iref[name](1.0):.4g} / {iref[name](3.0):.4g} mA/mm")
    rs = [r for r in rows if r["device"] == name]
    reg = {}
    for r in rs:
        reg[r["regime"]] = reg.get(r["regime"], 0) + 1
    print(f"  {len(rs)} devices: " + ", ".join(f"{k} {v}" for k, v in sorted(reg.items())))

xs = sorted({r["trapMeanX"] for r in rows})
ys = sorted({r["trapMeanY"] for r in rows})
Y, X = np.meshgrid(ys, np.array(xs) * 1e3)


def grid(name, key):
    Z = np.full((len(xs), len(ys)), np.nan)
    for r in rows:
        if r["device"] == name and np.isfinite(r[key]) and r[key] > 0:
            Z[xs.index(r["trapMeanX"]), ys.index(r["trapMeanY"])] = -np.log10(r[key])
    return Z


plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})

# 1) suppression surfaces, HighK vs SiN, shared z-scale
keys = (("r_3V", "log10 suppression at Vd = 3 V"),
        ("r_worst", "log10 worst suppression, Vd 0.1-3 V"))
fig = plt.figure(figsize=(15, 12))
for rr, (key, zlab) in enumerate(keys):
    Zs = {n: grid(n, key) for n in RUNS}
    top = max(np.nanmax(Z) for Z in Zs.values())
    zlim = (min(-0.2, min(np.nanmin(Z) for Z in Zs.values()) - 0.2), top + 0.3)
    for cc, name in enumerate(RUNS):
        Z = Zs[name]
        ax = fig.add_subplot(2, 2, 2 * rr + cc + 1, projection="3d")
        ok = np.isfinite(Z)
        ax.plot_surface(Y, X, Z, cmap=SEQ, vmin=0, vmax=zlim[1],
                        edgecolor="white", linewidth=0.5, alpha=0.92)
        ax.scatter(Y[ok], X[ok], Z[ok], color=INK, s=9, depthshade=False)
        for lo, hi in (GATE, FP):
            ax.plot([lo, hi, hi, lo, lo], [0, 0, 15, 15, 0], [zlim[0]] * 5, color=INK, lw=1.1)
        ax.set_zlim(*zlim)
        ax.set_ylim(-1, 15)
        ax.set_xlabel("trapMeanY (µm)\nsource → drain", fontsize=8, labelpad=4)
        ax.set_ylabel("depth (nm)\nsurface → 2DEG", fontsize=8, labelpad=4)
        ax.set_zlabel(zlab, fontsize=8, labelpad=4)
        ax.tick_params(labelsize=7)
        ax.view_init(elev=26, azim=-62)
        ax.set_title(f"{name} passivation: {zlab.replace('log10 ', '')}", color=INK, fontsize=10)
fig.suptitle(f"Trap map {TP:.0e} cm⁻³ / {TL} eV: HighK (εr 35) vs SiN (εr 6.3) above the "
             "nitride; each vs its own trap-free device (outlines: gate, field plate)",
             color=INK, fontsize=12)
fig.tight_layout()
fig.savefig("figures/trapSiN_3d.png", dpi=140)
plt.close(fig)

# 2) comparison: trap-free devices, suppression vs y per depth, Id-Vd at the gate
fig, axs = plt.subplots(1, 4, figsize=(24, 5.2), constrained_layout=True,
                        gridspec_kw={"width_ratios": [1, 1, 1, 1.1]})
ax = axs[0]
for name in RUNS:
    vr, ir = refs[name]
    ax.plot(vr, ir, color=DEV_C[name], lw=2.2, label=f"{name}, no traps")
ax.set_xlabel("Vd (V)")
ax.set_ylabel("Id (mA/mm)")
ax.set_title("Trap-free devices, Vg = -2 V", color=INK, fontsize=11)
ax.legend(frameon=False)
ax = axs[1]
for c, x in zip(CAT, xs):
    for name, ls in (("HighK", "-"), ("SiN", "--")):
        pts = sorted((r["trapMeanY"], -np.log10(r["r_3V"])) for r in rows
                     if r["device"] == name and r["trapMeanX"] == x and np.isfinite(r["r_3V"]))
        if pts:
            yy, vv = zip(*pts)
            ax.plot(yy, vv, color=c, lw=1.8, ls=ls, marker="o", ms=4,
                    label=f"{x * 1e3:g} nm, {name}")
ax.axvspan(*GATE, color=GRID, alpha=0.8, lw=0)
ax.axvspan(*FP, color=GRID, alpha=0.4, lw=0)
ax.set_xlabel("trapMeanY (µm), source → drain (shaded: gate, field plate)")
ax.set_ylabel("log10 suppression at Vd = 3 V")
ax.set_title("Suppression vs position (solid HighK, dashed SiN)", color=INK, fontsize=11)
ax.legend(frameon=False, fontsize=7, ncol=2)
ax = axs[2]
for c, y in zip(CAT, (-0.125, 0.0, 0.125, 0.5, 1.25)):
    for name, ls in (("HighK", "-"), ("SiN", "--")):
        k = (name, 0.0, y)
        if k in dev:
            vd, idd = dev[k]
            ax.semilogy(vd[vd > 0.05], idd[vd > 0.05], color=c, lw=1.8, ls=ls,
                        label=f"y = {y:g} µm, {name}")
ax.set_xlabel("Vd (V)")
ax.set_ylabel("Id (mA/mm)")
ax.set_title("Id-Vd, traps at the surface (x = 0); dashed SiN overlaps solid", color=INK, fontsize=11)
ax.legend(frameon=False, fontsize=7, ncol=2)
ax = axs[3]
D = grid("HighK", "r_3V") - grid("SiN", "r_3V")
lim = max(0.05, np.nanmax(np.abs(D)))
pc = ax.pcolormesh(np.arange(len(ys) + 1) - 0.5, np.arange(len(xs) + 1) - 0.5, D,
                   cmap="RdBu_r", vmin=-lim, vmax=lim)
for i in range(len(xs)):
    for j in range(len(ys)):
        if np.isfinite(D[i, j]):
            ax.text(j, i, f"{D[i, j]:+.2f}", ha="center", va="center", fontsize=7,
                    color="white" if abs(D[i, j]) > 0.6 * lim else INK)
ax.set_xticks(np.arange(len(ys)))
ax.set_xticklabels([f"{y:g}" for y in ys], fontsize=8)
ax.set_yticks(np.arange(len(xs)))
ax.set_yticklabels([f"{x * 1e3:g}" for x in xs], fontsize=8)
ax.invert_yaxis()
ax.set_xlabel("trapMeanY (µm)")
ax.set_ylabel("depth (nm)")
ax.set_title("log10(suppression HighK / SiN) at 3 V\n(red = HighK device hurt more)",
             color=INK, fontsize=11)
fig.colorbar(pc, ax=ax, shrink=0.85)
for ax in axs[:3]:
    ax.grid(True, color=GRID, lw=0.8)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
fig.suptitle(f"Effect of the HighK dielectric ({TP:.0e} cm⁻³ / {TL} eV traps, Run F hot-electron levers)",
             color=INK, fontsize=12)
fig.savefig("figures/trapSiN_compare.png", dpi=140)
plt.close(fig)
print("wrote figures/trapSiN_{metrics.csv,3d.png,compare.png}")
