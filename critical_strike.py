"""Probability of a critical strike at a given ion fluence.

A strike leaves the Gaussian trap blob (sigma 0.04 um) at lateral position y
and depth x. It is *critical* if it cuts the drain current to <= 1/10 of the
trap-free device at any Vd in 0.1-3 V (off at rest or collapse). Critical
lateral band per trap setting comes from the job 43513462 maps (+ retry) and
the job 43542730 band-edge refinement; each sampled y owns the cell out to the
midpoints with its neighbours, clipped to the contact-safe range.

Poisson hits: lambda = fluence * dy_crit * W, P(>=1 critical) = 1 - exp(-lambda).

Writes figures/criticalStrike_summary.csv and figures/criticalStrike.png.
"""
import glob
import json
import math
import os

import matplotlib.pyplot as plt
import numpy as np

RUNS = ["results/20260927_trapMapSets", "results/20260927_trapMapSetsRetry",
        "results/20260928_critBand"]
FLUENCE = 1e7 * 1e-8          # ions/cm^2 -> ions/um^2
CRIT = 0.1                    # Id / Id_no-trap at or below this is critical
Y_LO, Y_HI = -0.425, 2.585    # contact-safe: >=0.7 um from contact doping edges
Y_LO_ALL, Y_HI_ALL = -1.125, 3.285   # contact doping edges (upper bound)
DEPTHS = (0.0, 0.0075, 0.015)
SIGMA = 0.04
WIDTHS = (1.0, 10.0, 100.0, 200.0, 1000.0)   # gate width, um
W_DEV = 200.0                               # this device's gate width, um
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]


def load(p):
    d = np.loadtxt(p, delimiter=",", ndmin=2)
    return d[:, 0], d[:, 1]


ref, dev = None, {}
for run in RUNS:
    for t in glob.glob(f"{run}/task_*"):
        p = json.load(open(os.path.join(t, "params.json")))
        c = glob.glob(os.path.join(t, "pulsedIV_*.csv"))
        if not c or os.path.getsize(c[0]) == 0:
            continue
        vd, idd = load(c[0])
        if p["trapPeak"] < 1e12:
            ref = ref or (vd, idd)
            continue
        k = (p["trapPeak"], p["trapLevel"], p["trapMeanX"], p["trapMeanY"])
        if k not in dev or vd[-1] > dev[k][0][-1]:
            dev[k] = (vd, idd)
vr, ir = ref


def status(k):
    """(critical?, worst ratio, complete?) for one device."""
    vd, idd = dev[k]
    m = vd > 0.05
    w = float(np.min(idd[m] / np.interp(vd[m], vr, ir)))
    return w <= CRIT, w, abs(vd[-1] - 3.0) < 1e-6


def band(tp, tl, x, lo, hi):
    """Critical length (um) along y at one depth, nearest-sample cells."""
    ys = sorted(k[3] for k in dev if k[:3] == (tp, tl, x))
    flags = []
    for y in ys:
        crit, w, done = status((tp, tl, x, y))
        if not crit and not done:
            # stalled at its collapse before resolving: infer from the same
            # position at the other depths (critical if any of them is)
            others = [status(k)[0] for k in dev
                      if k[:2] == (tp, tl) and k[3] == y and k[2] != x]
            crit = any(others)
            INFERRED.append((tp, tl, x, y, crit))
        flags.append(crit)
    edges = [lo] + [0.5 * (a + b) for a, b in zip(ys, ys[1:])] + [hi]
    L = 0.0
    for (a, b), f in zip(zip(edges, edges[1:]), flags):
        a, b = max(a, lo), min(b, hi)
        if f and b > a:
            L += b - a
    return L, flags[0], flags[-1]


INFERRED = []
rows = []
for tp, tl in sorted({k[:2] for k in dev}):
    per_depth, ub = [], []
    for x in DEPTHS:
        L, first, last = band(tp, tl, x, Y_LO, Y_HI)
        per_depth.append(L)
        # upper bound: extend critical ends out to the contact doping edges
        ub.append(L + (Y_LO - Y_LO_ALL if first else 0) + (Y_HI_ALL - Y_HI if last else 0))
    dy = float(np.mean(per_depth))
    dy_ub = float(np.mean(ub))
    r = dict(trapPeak=tp, trapLevel=tl,
             dy_crit_um=dy, dy_min_um=min(per_depth), dy_max_um=max(per_depth),
             dy_upper_um=dy_ub,
             lam_per_um_width=FLUENCE * dy,
             W50_um=math.log(2) / (FLUENCE * dy) if dy > 0 else float("inf"))
    for W in WIDTHS:
        r[f"P_W{W:g}um"] = 1 - math.exp(-FLUENCE * dy * W)
        r[f"P_W{W:g}um_upper"] = 1 - math.exp(-FLUENCE * dy_ub * W)
    # 3D caveat: a single cascade only damages ~4 sigma of gate width, so
    # the expected fraction of width disabled is fluence * dy * l_eff
    r["width_fraction_damaged"] = FLUENCE * dy * 4 * SIGMA
    rows.append(r)

os.makedirs("figures", exist_ok=True)
cols = list(rows[0])
with open("figures/criticalStrike_summary.csv", "w") as f:
    f.write(",".join(cols) + "\n")
    for r in rows:
        f.write(",".join(f"{r[c]:.6g}" for c in cols) + "\n")

print(f"inferred (stalled at collapse) points: {len(INFERRED)} "
      f"({sum(c for *_, c in INFERRED)} critical)")
print(f"fluence {FLUENCE * 1e8:.0e} cm^-2 = {FLUENCE:g} ions/um^2; "
      f"critical = Id <= {CRIT:g} x trap-free at some Vd <= 3 V")
for r in rows:
    print(f"\n{r['trapPeak']:.0e} / {r['trapLevel']} eV: critical band "
          f"{r['dy_crit_um']:.2f} um (depths {r['dy_min_um']:.2f}-{r['dy_max_um']:.2f}; "
          f"up to {r['dy_upper_um']:.2f} incl. contact-adjacent)")
    print(f"  expected critical strikes per um of gate width: {r['lam_per_um_width']:.3f};"
          f" W for 50%: {r['W50_um']:.1f} um")
    print("  P(>=1): " + ", ".join(f"W={W:g} um: {r[f'P_W{W:g}um']:.3g}" for W in WIDTHS))
    print(f"  3D caveat - expected fraction of gate width damaged: "
          f"{r['width_fraction_damaged']:.2%}")

# Figure: P(>=1 critical strike) vs gate width at 1e7/cm^2, and vs fluence
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), constrained_layout=True)
Wg = np.logspace(-1, 3.3, 300)
Fl = np.logspace(5, 10, 300) * 1e-8
for c, r in zip(CAT, rows):
    lab = f"{r['trapPeak']:.0e} cm⁻³ / {r['trapLevel']} eV (Δy {r['dy_crit_um']:.2f} µm)"
    same = [q for q in rows if q is not r and abs(q["dy_crit_um"] - r["dy_crit_um"]) < 1e-9]
    if same and rows.index(same[0]) < rows.index(r):
        lab += " - same curve as above"
    a1.plot(Wg, 1 - np.exp(-FLUENCE * r["dy_crit_um"] * Wg), color=c, lw=2, label=lab)
    a1.fill_between(Wg, 1 - np.exp(-FLUENCE * r["dy_min_um"] * Wg),
                    1 - np.exp(-FLUENCE * r["dy_upper_um"] * Wg), color=c, alpha=0.12, lw=0)
    a2.plot(Fl * 1e8, 1 - np.exp(-Fl * r["dy_crit_um"] * W_DEV), color=c, lw=2, label=lab)
for ax in (a1, a2):
    ax.set_xscale("log")
    ax.set_ylim(0, 1.02)
    ax.grid(True, color=GRID, lw=0.8)
    for sd in ("top", "right"):
        ax.spines[sd].set_visible(False)
a1.axvline(W_DEV, color=MUTED, ls=":", lw=1.2)
a1.text(W_DEV * 1.1, 0.04, f"W = {W_DEV:g} µm", color=MUTED, fontsize=8)
a1.set_xlabel("gate width W (µm)")
a1.set_ylabel("P(≥1 critical strike)")
a1.set_title("At 1e7 ions/cm² (band: depth range → incl. contact-adjacent)", color=INK, fontsize=10)
a2.axvline(1e7, color=MUTED, ls=":", lw=1.2)
a2.text(1.1e7, 0.04, "1e7 cm⁻²", color=MUTED, fontsize=8)
a2.set_xlabel("fluence (ions/cm²)")
a2.set_title(f"vs fluence, W = {W_DEV:g} µm (this device)", color=INK, fontsize=10)
a1.legend(loc="upper left", frameon=False, fontsize=8)
fig.suptitle("Probability that at least one strike lands where its Gaussian trap blob cuts Id ≥10× "
             "(2D model: damage uniform along the gate width)", color=INK, fontsize=10.5,
             x=0.01, ha="left")
fig.savefig("figures/criticalStrike.png", dpi=150)
print("\nwrote figures/criticalStrike_summary.csv, figures/criticalStrike.png")
