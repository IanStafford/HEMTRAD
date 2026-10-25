"""Fit lumped post-irradiation elements to radIV Id-Vd curves (branch explore/rad-model).

usage: python3 analysis/radFit.py <pre_task> <post_task>:<curve> ... [--targets t.csv] [--plot out.png]
  pre_task   radIV task dir of the pre-irradiation model (reference for ratios)
  post_task  radIV task dir of a post model; curve = measured curve name in targets.csv
             (e.g. IdVd_b_SiN); ratios are taken to the measured IdVd_pre_SiN.
Adds a lumped series access resistance R (ohm mm) to the post model,
Vd_ext = Vd + Id*R (Id in A/mm), scans R and reports the R that minimises the rms
of log(model post/pre) - log(measured post/pre) over Vd 0.5-10 V.
"""
import csv
import glob
import os
import sys

import numpy as np

args = sys.argv[1:]
TGT = os.path.expanduser("~/HEMTRAD/data/rad_y2/targets.csv")
plot = None
if "--targets" in args:
    i = args.index("--targets"); TGT = args[i + 1]; del args[i:i + 2]
if "--plot" in args:
    i = args.index("--plot"); plot = args[i + 1]; del args[i:i + 2]
VD = np.linspace(0.5, 10.0, 39)
RS = np.arange(0.0, 2.01, 0.05)


def targets(path):
    t = {}
    for r in csv.reader(l for l in open(path) if not l.startswith("#")):
        if r[0] != "curve":
            t.setdefault(r[0], []).append((float(r[1]), float(r[2])))
    return {k: np.array(sorted(v)) for k, v in t.items()}


def idvd(task):
    d = np.loadtxt(glob.glob(os.path.join(task, "*_IdVd.csv"))[0], delimiter=",", ndmin=2)
    return d[:, 0], d[:, 2]


def with_r(v, i, r):
    return v + i * 1e-3 * r, i


T = targets(TGT)
mpre = T["IdVd_pre_SiN"]
pv, pi = idvd(args[0])
res = []
for a in args[1:]:
    task, curve = a.rsplit(":", 1)
    v, i = idvd(task)
    meas = np.interp(VD, *T[curve].T) / np.interp(VD, *mpre.T)
    ok = VD <= v[-1]
    best = None
    for r in RS:
        x, y = with_r(v, i, r)
        mod = np.interp(VD[ok], x, y) / np.interp(VD[ok], pv, pi)
        rms = float(np.sqrt(np.mean((np.log(mod) - np.log(meas[ok])) ** 2)))
        if best is None or rms < best[1]:
            best = (r, rms, mod)
    res.append((task, curve, best, meas, ok))
    pts = [1, 2, 3, 4, 6, 8, 10]
    sel = [int(np.argmin(abs(VD - p))) for p in pts]
    print(f"{os.path.basename(task.rstrip('/'))} vs {curve}: best R {best[0]:.2f} ohm mm, rms(log) {best[1]:.3f}")
    print("   Vd    " + " ".join(f"{p:>5}" for p in pts))
    print("   model " + " ".join(f"{best[2][k]:5.2f}" if ok[k] else "   --" for k in sel))
    print("   meas  " + " ".join(f"{meas[k]:5.2f}" for k in sel))

if plot:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for task, curve, best, meas, ok in res:
        l, = ax.plot(VD[ok], best[2], lw=2, label=f"{os.path.basename(task)} R={best[0]:.2f}")
        ax.plot(VD, meas, "o", ms=4, color=l.get_color(), label=curve)
    ax.set_xlabel("Vd (V)"); ax.set_ylabel("Id post / pre at Vg +1")
    ax.grid(alpha=0.3); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(plot, dpi=130)
    print("wrote", plot)
