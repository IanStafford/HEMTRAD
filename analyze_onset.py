"""Late-onset search (field mobility): classify each device's collapse.

Collapse classes (Ian, 2026-10-01; CLAUDE.md): the largest single-step loss
1 - Id(Vd_n)/Id(Vd_n-1) over the sweep is > 95% deep, 50-95% medium, < 50%
shallow; the collapse onset is the Vd of that step. Devices below 10% of the
trap-free current at Vd = 0.1 V are "off at rest" (no collapse to speak of).

usage: python3 analyze_onset.py run_dir tag [rows cols xpar ypar]
  defaults (round 1): rows=trapLevel cols=hotEb x=hotTau y=trapPeak
Writes figures/<tag>_metrics.csv and figures/<tag>.png (one panel per
rows x cols value; cells coloured by onset Vd, labelled by class).
"""
import glob
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

RUN, TAG = sys.argv[1], sys.argv[2]
ROWS, COLS, XP, YP = (sys.argv[3:7] if len(sys.argv) >= 7
                      else ("trapLevel", "hotEb", "hotTau", "trapPeak"))
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
SEQ = LinearSegmentedColormap.from_list(
    "onset", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
CLS = {"deep": "D", "medium": "M", "shallow": "S", "off at rest": "off", "incomplete": "?"}


def classify(loss):
    return "deep" if loss > 0.95 else "medium" if loss >= 0.5 else "shallow"


ref, dev = None, {}
for run in (RUN, RUN + "Retry"):
    for t in glob.glob(f"{run}/task_*"):
        p = json.load(open(os.path.join(t, "params.json")))
        c = glob.glob(os.path.join(t, "pulsedIV_*.csv"))
        if not c or os.path.getsize(c[0]) == 0:
            continue
        d = np.loadtxt(c[0], delimiter=",", ndmin=2)
        if p["trapPeak"] < 1e12:
            ref = (d[:, 0], d[:, 1])
            continue
        k = tuple(p[q] for q in (ROWS, COLS, XP, YP))
        if k not in dev or d[-1, 0] > dev[k][0][-1]:
            dev[k] = (d[:, 0], d[:, 1], p)
if ref is None:
    raise SystemExit("trap-free reference missing")
vr, ir = ref
iref = lambda v: np.interp(v, vr, ir)

rows = []
for k, (vd, idd, p) in sorted(dev.items()):
    m = vd > 0.05
    v, i = vd[m], idd[m]
    at_rest = float(i[0] / iref(v[0]))
    loss = 1.0 - i[1:] / i[:-1]
    j = int(np.argmax(loss))
    maxloss = float(loss[j])
    onset = float(v[j + 1])
    cls = classify(maxloss)
    ipre = j                               # last point before the drop
    post_min = int(j + 1 + np.argmin(i[j + 1:]))
    if at_rest < 0.1:
        cls, onset = "off at rest", np.nan
    rows.append({**{q: p[q] for q in (ROWS, COLS, XP, YP)},
                 "class": cls, "max_step_loss": maxloss, "onset_Vd": onset,
                 "pre_Id": float(i[ipre]), "at_rest_frac": at_rest,
                 "depth_vs_ref": float(iref(v[post_min]) / i[post_min]),
                 "last_Vd": float(vd[-1]), "Id_end": float(idd[-1])})

os.makedirs("figures", exist_ok=True)
cols = list(rows[0])
with open(f"figures/{TAG}_metrics.csv", "w") as f:
    f.write(",".join(cols) + "\n")
    for r in rows:
        f.write(",".join(r[c] if isinstance(r[c], str) else f"{r[c]:.6g}" for c in cols) + "\n")

cnt = {}
for r in rows:
    cnt[r["class"]] = cnt.get(r["class"], 0) + 1
print(f"{len(rows)} devices: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items()))
      + f"; ref Id(0.1/end) = {iref(0.1):.3g}/{ir[-1]:.4g} mA/mm")
print("latest-onset deep/medium collapses:")
for r in sorted((r for r in rows if r["class"] in ("deep", "medium")),
                key=lambda r: -r["onset_Vd"])[:15]:
    print(f"  {ROWS}={r[ROWS]:<6g} {COLS}={r[COLS]:<5g} {XP}={r[XP]:<8g} {YP}={r[YP]:<7g} "
          f"{r['class']:6s} onset {r['onset_Vd']:.2f} V, step loss {100*r['max_step_loss']:.1f}%, "
          f"pre {r['pre_Id']:.1f} mA/mm, at rest {r['at_rest_frac']:.2f}")

rv = sorted({r[ROWS] for r in rows})
cv = sorted({r[COLS] for r in rows})
xv = sorted({r[XP] for r in rows})
yv = sorted({r[YP] for r in rows})
vmax = max([r["onset_Vd"] for r in rows if np.isfinite(r["onset_Vd"])] + [1.0])
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})
fig, axs = plt.subplots(len(rv), len(cv), figsize=(4.6 * len(cv) + 1.5, 3.4 * len(rv) + 1),
                        squeeze=False, constrained_layout=True)
for a, r_ in enumerate(rv):
    for b, c_ in enumerate(cv):
        ax = axs[a, b]
        Z = np.full((len(yv), len(xv)), np.nan)
        for r in rows:
            if r[ROWS] == r_ and r[COLS] == c_:
                yi, xi = yv.index(r[YP]), xv.index(r[XP])
                if r["class"] in ("deep", "medium"):
                    Z[yi, xi] = r["onset_Vd"]
                lab = CLS[r["class"]]
                if r["class"] in ("deep", "medium", "shallow"):
                    lab += f"\n{r['onset_Vd']:.1f} V"
                ax.text(xi, yi, lab, ha="center", va="center", fontsize=8,
                        color="white" if np.isfinite(Z[yi, xi]) and Z[yi, xi] > 0.6 * vmax else INK)
        pc = ax.pcolormesh(np.arange(len(xv) + 1) - 0.5, np.arange(len(yv) + 1) - 0.5, Z,
                           cmap=SEQ, vmin=0, vmax=vmax)
        ax.set_xticks(range(len(xv)))
        ax.set_xticklabels([f"{x:g}" for x in xv], fontsize=8)
        ax.set_yticks(range(len(yv)))
        ax.set_yticklabels([f"{y:g}" for y in yv], fontsize=8)
        ax.set_xlabel(XP)
        ax.set_ylabel(YP)
        ax.set_title(f"{ROWS} = {r_:g}, {COLS} = {c_:g}", color=INK, fontsize=10)
fig.colorbar(pc, ax=axs, shrink=0.6, label="collapse onset Vd (V), deep/medium only")
fig.suptitle(f"{TAG}: collapse class by largest single-step loss (D >95%, M 50-95%, S <50%; "
             "off = off at rest), field mobility", color=INK, fontsize=12)
fig.savefig(f"figures/{TAG}.png", dpi=130)
print(f"wrote figures/{TAG}{{.png,_metrics.csv}}")
