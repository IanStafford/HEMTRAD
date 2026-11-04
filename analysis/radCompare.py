"""Compare radIV runs (drivers/radIV.tcl, sweeps/radIV.slurm) with the measured
pre/post-irradiation set.

usage: python3 analysis/radCompare.py <run_or_task_dir>... [--targets t.csv] [--plot out.png] [--ref LABEL]
  targets.csv: digitized measured curves (curve,x,y; kept outside git, default
  ~/HEMTRAD/data/rad_y2/targets.csv).
Per task: Vth (linear extrapolation at max gm, Vd 0.1), gm max (mS/mm), Id at
Vg -2.6/-2.0/-1.4 (Vd 0.1), Id-Vd at Vg +1 at 1/2/4/6/10 V, Ioff at the lowest Vg.
--ref LABEL also prints each task's ratios to that task (post/pre).
"""
import csv
import glob
import json
import os
import sys

import numpy as np

args = [a for a in sys.argv[1:]]
plot = None
ref = None
if "--plot" in args:
    i = args.index("--plot"); plot = args[i + 1]; del args[i:i + 2]
if "--ref" in args:
    i = args.index("--ref"); ref = args[i + 1]; del args[i:i + 2]
TGT = os.path.expanduser("~/HEMTRAD/data/rad_y2/targets.csv")
if "--targets" in args:
    i = args.index("--targets"); TGT = args[i + 1]; del args[i:i + 2]
VG_PTS = (-2.6, -2.0, -1.4)
VD_PTS = (1.0, 2.0, 4.0, 6.0, 10.0)


def load_targets(path):
    t = {}
    if not os.path.exists(path):
        return t
    for r in csv.reader(l for l in open(path) if not l.startswith("#")):
        if r[0] == "curve":
            continue
        t.setdefault(r[0], []).append((float(r[1]), float(r[2])))
    return {k: np.array(v) for k, v in t.items()}


def vth_gm(vg, idd):
    o = np.argsort(vg)
    vg, idd = vg[o], idd[o]
    gm = np.gradient(idd, vg)
    k = int(np.argmax(gm))
    return vg[k] - idd[k] / gm[k], gm[k]


def metrics(t):
    m = {}
    f = glob.glob(os.path.join(t, "*_IdVg.csv"))
    if f and os.path.getsize(f[0]) > 0:
        d = np.loadtxt(f[0], delimiter=",", ndmin=2)
        vg, ie = d[:, 0], d[:, 2]
        if len(vg) > 5:
            m["Vth"], m["gm"] = vth_gm(vg, d[:, 1])
            for v in VG_PTS:
                m[f"Ig{v}"] = float(np.interp(v, vg[::-1], ie[::-1])) if vg.min() <= v else np.nan
            m["Ioff"] = float(ie[np.argmin(vg)])
            m["_IdVg"] = d
    f = glob.glob(os.path.join(t, "*_IdVd.csv"))
    if f and os.path.getsize(f[0]) > 0:
        d = np.loadtxt(f[0], delimiter=",", ndmin=2)
        for v in VD_PTS:
            m[f"Id{v:g}"] = float(np.interp(v, d[:, 0], d[:, 2])) if d[-1, 0] >= v - 1e-6 else np.nan
        m["lastVd"] = float(d[-1, 0])
        m["_IdVd"] = d
    return m


T = load_targets(TGT)
tasks = []
for a in args:
    if os.path.exists(os.path.join(a, "params.json")):
        tasks.append(a)
    else:
        tasks += sorted(glob.glob(f"{a}/task_*"), key=lambda s: int(s.rsplit("_", 1)[1]))
res = []
for t in tasks:
    p = json.load(open(os.path.join(t, "params.json")))
    res.append((p["label"], p, metrics(t)))

cols = ["Vth", "gm"] + [f"Ig{v}" for v in VG_PTS] + [f"Id{v:g}" for v in VD_PTS] + ["Ioff", "lastVd"]
print(f"{'label':<18}" + "".join(f"{c:>10}" for c in cols))
if T:
    meas = {"Vth": -2.97, "gm": 53.5, "Ioff": 5.4e-6}
    for v, y in T.get("IdVg_pre_SiN", []):
        meas[f"Ig{v:g}"] = y
    for v in VD_PTS:
        if "IdVd_pre_SiN" in T:
            meas[f"Id{v:g}"] = float(np.interp(v, *T["IdVd_pre_SiN"].T))
    print(f"{'meas pre SiN':<18}" + "".join(f"{meas.get(c, np.nan):>10.4g}" for c in cols))
for lab, p, m in res:
    print(f"{lab:<18}" + "".join(f"{m.get(c, np.nan):>10.4g}" for c in cols))
if ref:
    r = dict((l, m) for l, _, m in res)[ref]
    print(f"\nratios to {ref}")
    for lab, p, m in res:
        print(f"{lab:<18}" + "".join(
            f"{(m.get(c, np.nan) - r.get(c, np.nan)) if c == 'Vth' else m.get(c, np.nan) / r.get(c, np.nan):>10.3g}"
            for c in cols if c != "lastVd"))

if plot:
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.5))
    for lab, p, m in res:
        if "_IdVg" in m:
            d = m["_IdVg"]
            axs[0].plot(d[:, 0], d[:, 1], label=lab)
            axs[1].semilogy(d[:, 0], np.abs(d[:, 2]), label=lab)
        if "_IdVd" in m:
            d = m["_IdVd"]
            axs[2].plot(d[:, 0], d[:, 2], label=lab)
    for k, v in T.items():
        if k.startswith("IdVg_"):
            axs[0].plot(*v.T, "o", ms=5, label="meas " + k[5:])
        if k.startswith("IdVd_"):
            axs[2].plot(*v.T, "o", ms=4, label="meas " + k[5:])
    axs[0].set_xlabel("Vg (V)"); axs[0].set_ylabel("Id at Vd 0.1 (mA/mm)")
    axs[1].set_xlabel("Vg (V)"); axs[1].set_ylabel("|Id| (mA/mm)")
    axs[2].set_xlabel("Vd (V)"); axs[2].set_ylabel("Id at Vg +1 (mA/mm)")
    for a in axs:
        a.grid(alpha=0.3)
    axs[2].legend(fontsize=6, ncol=2)
    axs[0].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(plot, dpi=130)
    print("wrote", plot)
