"""Deep-trap test (job: see progress.md, 2026-10-01).

Run F traps in a blob narrow in depth (sigma_x 10 nm) and 40 nm wide laterally,
centred 0-65 nm below the 2DEG (x = 15 nm), at 5 lateral positions, for two peak
densities: 4e18 (same local density as the sigma-40 nm maps) and 1.6e19 (same
total charge). Asks whether deep traps collapse the channel themselves, or only
through the blob's tail at the 2DEG.

Per device: r_rest = Id/Id_no-trap at Vd=0.1 V, r_3V at 3 V, r_worst = min over
Vd, collapse onset/depth (devices conducting at rest), regime.

Writes figures/trapDeep_metrics.csv, figures/trapDeep.png (worst suppression vs
depth, with the trap density left at the 2DEG on a top axis) and
figures/trapDeep_IdVd.png (Id-Vd at y = 1.0 um for every depth).
"""
import glob
import json
import math
import os

import matplotlib.pyplot as plt
import numpy as np

RUN = "results/archive_static_mobility/20261001_trapDeep"
VD_END = 3.0
X2DEG, SX = 0.015, 0.01
FLOOR = 8.0
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#7a5fd1", "#008300"]


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
    k = (p["trapPeak"], p["trapMeanX"], p["trapMeanY"])
    if k not in dev or vd[-1] > dev[k][0][-1]:
        dev[k] = (vd, idd)
if ref is None:
    raise SystemExit("trap-free reference missing")
vr, ir = ref
iref = lambda v: np.interp(v, vr, ir)

rows = []
for (tp, x, y), (vd, idd) in sorted(dev.items()):
    done = abs(vd[-1] - VD_END) < 1e-6
    m = vd > 0.05
    ratio = idd[m] / iref(vd[m])
    # collapse = Id falls below 1/10 of the highest Id reached so far (the
    # current can recover past its pre-collapse peak later in the sweep)
    runmax = np.maximum.accumulate(idd)
    below = np.nonzero(idd < runmax / 10)[0]
    onset = vd[below[0]] if below.size else np.nan
    imin = (below[0] + int(np.argmin(idd[below[0]:]))) if below.size else int(np.argmin(idd[m]))
    r_rest = float(ratio[0])
    depth = iref(vd[imin]) / idd[imin]
    if r_rest < 0.1:
        regime, onset, depth = "off at rest", np.nan, np.nan
    elif np.isfinite(onset):
        regime = "collapse"
    else:
        regime = "no collapse" if done else "incomplete"
        if not done:
            depth = np.nan
    rows.append(dict(trapPeak=tp, trapMeanX=x, trapMeanY=y,
                     below_2DEG_nm=(x - X2DEG) * 1e3,
                     frac_at_2DEG=math.exp(-(x - X2DEG) ** 2 / (2 * SX * SX)),
                     regime=regime, complete=int(done), last_Vd=vd[-1], r_rest=r_rest,
                     r_3V=float(idd[-1] / iref(VD_END)) if done else np.nan,
                     r_worst=float(ratio.min()), onset_Vd=onset,
                     collapse_depth_vs_ref=depth))

os.makedirs("figures", exist_ok=True)
cols = list(rows[0])
with open("figures/trapDeep_metrics.csv", "w") as f:
    f.write(",".join(cols) + "\n")
    for r in rows:
        f.write(",".join(r[c] if isinstance(r[c], str) else f"{r[c]:.6g}"
                         for c in cols) + "\n")
print(f"{len(rows)} devices, {sum(r['complete'] for r in rows)} complete; "
      f"ref Id(3V) = {iref(VD_END):.4g} mA/mm")
for tp in sorted({r["trapPeak"] for r in rows}):
    print(f"\ntrapPeak {tp:.1e}:  below-2DEG(nm) y  regime  r_rest  r_worst  onset")
    for r in rows:
        if r["trapPeak"] == tp:
            print(f"  {r['below_2DEG_nm']:5.0f} {r['trapMeanY']:5g}  {r['regime']:12s}"
                  f" {r['r_rest']:.2g}  {r['r_worst']:.2g}  {r['onset_Vd']}")

plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})
peaks = sorted({r["trapPeak"] for r in rows})
ys = sorted({r["trapMeanY"] for r in rows})
lab_y = {-0.2: "source side", 0.0: "under gate", 0.5: "field plate",
         1.0: "access", 2.0: "access, far"}

# 1) worst suppression vs depth below the 2DEG
fig, axs = plt.subplots(1, len(peaks), figsize=(7.5 * len(peaks), 5.4),
                        constrained_layout=True, sharey=True)
axs = np.atleast_1d(axs)
for ax, tp in zip(axs, peaks):
    for c, y in zip(CAT, ys):
        pts = sorted((r["below_2DEG_nm"], min(-math.log10(r["r_worst"]), FLOOR), r["regime"])
                     for r in rows if r["trapPeak"] == tp and r["trapMeanY"] == y)
        if not pts:
            continue
        d, v, reg = zip(*pts)
        ax.plot(d, v, color=c, lw=2, label=f"y = {y:g} µm ({lab_y.get(y, '')})")
        for di, vi, ri in pts:
            ax.plot(di, vi, "s" if ri == "off at rest" else "D" if ri == "incomplete" else "o",
                    ms=7, mfc=c if ri != "no collapse" else "white", mec=c, mew=1.5)
    ax.axhline(1, color=MUTED, lw=1, ls=":")
    ax.text(64, 1.08, "10× (critical)", color=MUTED,
            fontsize=8, ha="right")
    ax.grid(True, color=GRID, lw=0.8)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.set_xlabel("blob centre depth below the 2DEG (nm)")
    ax.set_title(f"peak {tp:.1e} cm⁻³ "
                 f"({'same density' if tp < 1e19 else 'same total charge'} as σ = 40 nm)",
                 color=INK, fontsize=11)
    sec = ax.secondary_xaxis("top", functions=(lambda d: d, lambda d: d))
    sec.set_xticks([0, 10, 15, 25, 35, 45, 65])
    sec.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda t, _: f"{math.exp(-(t * 1e-3) ** 2 / (2 * SX * SX)):.2g}"))
    sec.tick_params(labelsize=8)
    sec.set_xlabel("trap density left at the 2DEG (fraction of peak)", fontsize=9)
axs[0].set_ylabel(f"log10 worst suppression, Id_no-trap / Id, Vd 0.1-3 V\n(capped at {FLOOR:g})")
axs[-1].legend(frameon=False, fontsize=9, loc="upper right")
fig.suptitle("Do deep traps collapse the channel? Blob σ = 10 nm in depth, 40 nm laterally; "
             "● collapse, ■ off at rest, ○ no collapse, ◆ incomplete", color=INK, fontsize=12)
fig.savefig("figures/trapDeep.png", dpi=140)
plt.close(fig)

# 2) Id-Vd at y = 1.0 um for every depth
fig, axs = plt.subplots(1, len(peaks), figsize=(7.5 * len(peaks), 5.0),
                        constrained_layout=True, sharey=True)
axs = np.atleast_1d(axs)
xs = sorted({k[1] for k in dev})
for ax, tp in zip(axs, peaks):
    ax.semilogy(vr[vr > 0.05], ir[vr > 0.05], color=INK, lw=2.2, ls="--", label="no traps")
    for c, x in zip(CAT, xs):
        k = (tp, x, 1.0)
        if k in dev:
            vd, idd = dev[k]
            ax.semilogy(vd[vd > 0.05], idd[vd > 0.05], color=c, lw=1.8,
                        label=f"{(x - X2DEG) * 1e3:g} nm below 2DEG")
    ax.grid(True, color=GRID, lw=0.8, which="major")
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.set_xlabel("Vd (V)")
    ax.set_title(f"peak {tp:.1e} cm⁻³, y = 1.0 µm (access region)", color=INK, fontsize=11)
axs[0].set_ylabel("Id (mA/mm)")
axs[-1].legend(frameon=False, fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5))
fig.suptitle("Id-Vd vs blob depth (σx 10 nm, σy 40 nm, Run F traps, Vg = -2 V)",
             color=INK, fontsize=12)
fig.savefig("figures/trapDeep_IdVd.png", dpi=140)
plt.close(fig)
print("\nwrote figures/trapDeep_{metrics.csv,png,IdVd.png}")
