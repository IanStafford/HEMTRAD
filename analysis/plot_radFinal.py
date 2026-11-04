"""Consolidated pre/post-irradiation model (sweeps/params_radFinal.txt, job 47693156).

usage: python3 analysis/plot_radFinal.py [run_dir] [--pre pre_run_dir] [--targets t.csv] [--out fig.png] [--damPeak 5e18|""]
  e.g. radFinal8: python3 analysis/plot_radFinal.py results/20261026_radFinal8 --pre results/20261025_radFinal --damPeak "" --out figures/radFinal8_model.png
Three panels:
- Id-Vd at Vg +1 as post/pre (HighK deck = HPD, SiN deck = SiN);
- the same for non-biased;
- Id-Vg at Vd 0.1 (linear, around threshold).
Without --targets only the model is drawn (figure safe to commit). With --targets
the measured curves (untracked lab data) are overlaid; write that figure outside
git, e.g. ~/HEMTRAD/data/rad_y2/.
"""
import csv
import glob
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

args = sys.argv[1:]
run = "results/20261025_radFinal"
tgt = None
out = "figures/radFinal_model.png"
dp = "5e18"
pre_run = None
for flag in ("--targets", "--out", "--damPeak", "--pre"):
    if flag in args:
        i = args.index(flag); val = args[i + 1]; del args[i:i + 2]
        if flag == "--targets": tgt = val
        elif flag == "--out": out = val
        elif flag == "--pre": pre_run = val
        else: dp = val
if args:
    run = args[0]

INK, MUTED, GRID = "#14171F", "#646B78", "#E2E4E9"
COL = {"highk": "#1B4F9C", "sin": "#C2410C"}
NAME = {"highk": "HPD (HighK deck)", "sin": "SiN"}

M = {}
for t in glob.glob(f"{run}/task_*") + (glob.glob(f"{pre_run}/task_*") if pre_run else []):
    p = json.load(open(os.path.join(t, "params.json")))
    d = {}
    for k in ("IdVd", "IdVg"):
        f = glob.glob(os.path.join(t, f"*_{k}.csv"))
        if f:
            d[k] = np.loadtxt(f[0], delimiter=",", ndmin=2)
    M[p["label"]] = d

T = {}
if tgt:
    for r in csv.reader(l for l in open(os.path.expanduser(tgt)) if not l.startswith("#")):
        if r[0] != "curve":
            T.setdefault(r[0], []).append((float(r[1]), float(r[2])))
    T = {k: np.array(sorted(v)) for k, v in T.items()}

plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED})
fig, axs = plt.subplots(1, 3, figsize=(15, 4.4))
vd = np.linspace(0.25, 10, 80)


def ratio(post, pre):
    a, b = M[post]["IdVd"], M[pre]["IdVd"]
    ok = vd <= a[-1, 0]
    return vd[ok], np.interp(vd[ok], a[:, 0], a[:, 2]) / np.interp(vd[ok], b[:, 0], b[:, 2])


for ax, state, title in ((axs[0], "b", "biased (Vg −10 / Vd 28 V)"), (axs[1], "nb", "non-biased")):
    for deck in ("highk", "sin"):
        lab = (f"b_{deck}_p{dp}" if dp else f"b_{deck}") if state == "b" else f"nb_{deck}"
        if lab in M and "IdVd" in M[lab]:
            ax.plot(*ratio(lab, f"pre_{deck}"), color=COL[deck], lw=2, label=f"model {NAME[deck]}")
        mk = f"IdVd_{state}_{'HPD' if deck == 'highk' else 'SiN'}"
        if mk in T and "IdVd_pre_SiN" in T:
            x = T[mk][:, 0]
            ax.plot(x, T[mk][:, 1] / np.interp(x, *T["IdVd_pre_SiN"].T), "o", ms=4,
                    color=COL[deck], mfc="none", label=f"measured {NAME[deck]}")
    ax.axhline(1.0, color=MUTED, lw=0.8)
    ax.set_ylim(0, 1.2); ax.set_xlabel("Vd (V)"); ax.set_ylabel("Id post / pre at Vg +1 V")
    ax.set_title(f"Id–Vd, {title}", color=INK, fontsize=11)
    ax.grid(color=GRID, lw=0.8); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="lower left")

ax = axs[2]
bl = (lambda d: f"b_{d}_p{dp}") if dp else (lambda d: f"b_{d}")
for lab, ls in (("pre_highk", ":"), ("nb_highk", "--"), (bl("highk"), "-"),
                ("pre_sin", ":"), ("nb_sin", "--"), (bl("sin"), "-")):
    if lab in M and "IdVg" in M[lab]:
        d = M[lab]["IdVg"]
        deck = "highk" if "highk" in lab else "sin"
        ax.plot(d[:, 0], d[:, 2], color=COL[deck], ls=ls, lw=1.6, label=f"model {lab}")
for k, v in T.items():
    if k.startswith("IdVg_"):
        deck = "highk" if "HPD" in k else "sin"
        ax.plot(*v.T, "o", ms=4, mfc="none", color=COL[deck], label=f"meas {k[5:]}")
ax.set_xlim(-3.4, -1.0); ax.set_ylim(0, 45)
ax.set_xlabel("Vg (V)"); ax.set_ylabel("Id at Vd 0.1 V (mA/mm)")
ax.set_title("Id–Vg (pre dotted, nb dashed, biased solid)", color=INK, fontsize=11)
ax.grid(color=GRID, lw=0.8); ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=6, ncol=2, loc="upper left")

fig.suptitle(f"Pre/post-irradiation model, {os.path.basename(run)}" + (f", biased damPeak {dp}" if dp else ""), color=INK, fontsize=11)
fig.tight_layout()
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
fig.savefig(out, dpi=150)
print("wrote", out)
