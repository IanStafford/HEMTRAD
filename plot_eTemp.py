"""Electron energy balance (eTemp) runs vs the old local-field model.

usage: python3 plot_eTemp.py [run_dir]   (default results/20261008_eTemp1)
Writes figures/eTemp_IdVd.png (trap-free variants and trap runs vs the
local-model / drift-diffusion counterparts) and figures/eTemp_profiles.png
(ETemp along the 2DEG and the trap row at several Vd), and prints a summary.
"""
import glob
import json
import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np

RUN = sys.argv[1] if len(sys.argv) > 1 else "results/20261008_eTemp1"
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
SET = "pulsedIV_tp5.00e+18_tl0.30_ht1.00e-14_eb1.00_my"
R3 = "results/20261002_onsetField3"
OLD = {"notrap": f"{R3}/task_56/pulsedIV_notrap.csv",
       "late10": f"{R3}/task_17/{SET}1.000e+00.csv",
       "late24": f"{R3}RetryRamp/task_7/{SET}2.400e+00.csv"}
for t in glob.glob("results/20261002_onsetField1/task_*"):
    p = json.load(open(f"{t}/params.json"))
    if p["trapPeak"] == 4e18 and p["trapLevel"] == 0.55 and p["hotTau"] == 1.3e-13 and p["hotEb"] == 0.5:
        OLD["runF"] = glob.glob(f"{t}/pulsedIV_*.csv")[0]


def load(f):
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        return None
    d = np.loadtxt(f, delimiter=",", ndmin=2)
    m = d[:, 0] > 0.05
    return d[m, 0], d[m, 1], d[m, 2]


def onset(v, i):
    loss = 1 - i[1:] / i[:-1]
    k = np.nonzero(loss > 0.95)[0]
    return (v[k[0] + 1], i[k[0]]) if len(k) else (None, None)


runs = {}
for t in sorted(glob.glob(f"{RUN}/*/params.json")):
    p = json.load(open(t))
    d = os.path.dirname(t)
    runs[p["tag"]] = (p, load(f"{d}/pulsedIV_{p['tag']}.csv"), d)

print(f"{'tag':22s} {'lastVd':>6s} {'Id0.5':>7s} {'Id1':>7s} {'Id2':>7s} {'Id4':>7s} {'peakTe':>8s} onset")
for tag, (p, r, _) in runs.items():
    if r is None:
        print(f"{tag:22s} no data"); continue
    v, i, te = r
    g = lambda x: f"{np.interp(x, v, i):7.2f}" if v[-1] >= x - 1e-6 else "      -"
    o, pre = onset(v, i)
    print(f"{tag:22s} {v[-1]:6.1f} {g(0.5)} {g(1.0)} {g(2.0)} {g(4.0)} {te.max():8.0f} "
          + (f"deep {o:.1f} V from {pre:.1f}" if o else ""))
for k, f in OLD.items():
    r = load(f)
    if r:
        o, pre = onset(r[0], r[1])
        print(f"old {k:18s} {r[0][-1]:6.1f} Id1 {np.interp(1, r[0], r[1]):.2f} Id4 {np.interp(4, r[0], r[1]):.2f}"
              + (f"  deep {o:.1f} V from {pre:.1f}" if o else ""))

plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.labelcolor": INK})
fig, axs = plt.subplots(1, 2, figsize=(13, 4.8), constrained_layout=True)
ax = axs[0]
r = load(OLD["notrap"])
ax.plot(r[0], r[1], "-", color=INK, lw=2.4, label="drift-diffusion (old)")
cols = ["#86b6ef", "#3987e5", "#0d366b", "#d0752a", "#8a8984", "#c1d0a4"]
for c, tag in zip(cols, [t for t in runs if t.startswith("nt_") or t.startswith("reg")]):
    rr = runs[tag][1]
    if rr:
        ax.plot(rr[0], rr[1], "--" if tag.startswith("reg") else "-", color=c, lw=1.5, label=tag)
ax.set_title("Trap-free Id-Vd, Vg = −2 V", color=INK)
ax2 = axs[1]
pal = {"runF": "#d0752a", "late10": "#86b6ef", "late24": "#1c5cab"}
for base, c in pal.items():
    o = load(OLD.get(base, ""))
    if o:
        ax2.semilogy(o[0], o[1], "--", color=c, lw=1, alpha=0.7)
    for tag, (p, rr, _) in runs.items():
        if tag.startswith(base + "_") and rr:
            ls = {"1e-12": "-", "3e-13": "-.", "1e-13": ":"}[tag.split("_t")[1].split("_")[0]]
            ax2.semilogy(rr[0], rr[1], ls, color=c, lw=1.8, label=tag)
ax2.plot([], [], "--", color=MUTED, lw=1, label="old local-field model")
ax2.set_title("With traps (late set y 1.0 / 2.4 µm, Run F)", color=INK)
for a in axs:
    a.set_xlabel("Vd (V)"); a.set_ylabel("Id (mA/mm)"); a.set_xlim(0, 4)
    a.grid(True, color=GRID, lw=0.6)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
axs[0].legend(frameon=False, fontsize=8, loc="lower right")
ax2.legend(frameon=False, fontsize=7.5, loc="lower left", ncol=2)
fig.suptitle("Electron energy balance (ETemp) vs local-field / drift-diffusion", color=INK)
fig.savefig("figures/eTemp_IdVd.png", dpi=130)
plt.close(fig)


def read_prof(f):
    out, cur = {}, None
    for line in open(f):
        m = re.match(r"# ETemp .* x = ([\d.]+) um", line)
        if m:
            cur = float(m.group(1)); out[cur] = []; continue
        nums = re.findall(r"[-\d.]+e[+-]\d+", line)
        if cur is not None and len(nums) == 2 and ("GaN" in line):
            out[cur].append((float(nums[0]), float(nums[1])))
    return {k: np.array(sorted(v)) for k, v in out.items() if v}


ptags = [t for t in ("nt_t1e-12_low", "nt_t1e-12_field", "late24_t1e-12") if t in runs]
fig, axs = plt.subplots(1, len(ptags), figsize=(5.2 * len(ptags), 4.4), constrained_layout=True, squeeze=False)
for ax, tag in zip(axs[0], ptags):
    files = sorted(glob.glob(f"{runs[tag][2]}/*_Te_Vd*.txt"))
    shades = plt.cm.Blues(np.linspace(0.35, 0.95, max(len(files), 1)))
    for c, f in zip(shades, files):
        vd = re.search(r"Vd([\d.]+)\.txt", f).group(1)
        pr = read_prof(f)
        if 0.016 in pr:
            ax.semilogy(pr[0.016][:, 0], pr[0.016][:, 1], color=c, lw=1.6, label=f"Vd {vd} V, 2DEG")
        if 0.0 in pr:
            ax.semilogy(pr[0.0][:, 0], pr[0.0][:, 1], ":", color=c, lw=1.2)
    for lo, hi in ((-0.125, 0.125), (0.285, 0.725)):
        ax.axvspan(lo, hi, color=GRID, alpha=0.6, lw=0)
    ax.set_title(tag + "  (dotted: AlGaN top, trap row)", color=INK, fontsize=9)
    ax.set_xlabel("y (µm), source → drain; shaded: gate, field plate")
    ax.set_ylabel("ETemp (K)")
    ax.set_xlim(-1.3, 3.0)
    ax.grid(True, color=GRID, lw=0.6)
    ax.legend(frameon=False, fontsize=7.5)
fig.savefig("figures/eTemp_profiles.png", dpi=130)
print("wrote figures/eTemp_IdVd.png, figures/eTemp_profiles.png")
