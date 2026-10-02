"""HighK vs SiN field-plate check (fieldPlateTest.tcl, 2026-10-01, CLAUDE.md 10l).

Trap-free, Vg = -2 V, Vd 0.5-20 V on rfdevice.tcl (HighK, eps_r 35) and
rfdevice_SiN.tcl (SiN, 6.3). Reads results/20261001_fieldPlate/ (fp_<tag>.csv
and the print.1d cuts along the 2DEG) and writes figures/fieldPlate_sweep.csv,
figures/fieldPlate_cuts.csv and figures/fieldPlate.png.
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

RUN = sys.argv[1] if len(sys.argv) > 1 else "results/archive_static_mobility/20261001_fieldPlate"
TAGS = {"highk": "HighK (εr 35)", "sin": "SiN (εr 6.3)"}
VDS = ("3", "10", "20")
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
DEV_C = {"highk": "#2a78d6", "sin": "#eb6834"}
GATE, THEAD, FP = (-0.125, 0.125), (-0.325, 0.485), (0.285, 0.725)


def cut(path):
    """print.1d output -> array of (y um, value)."""
    rows = []
    for line in open(path):
        parts = line.strip().strip("{}").split()
        if len(parts) >= 2:
            try:
                rows.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass
    return np.array(rows)


sweep = {t: np.genfromtxt(os.path.join(RUN, f"fp_{t}.csv"), delimiter=",", names=True)
         for t in TAGS}
cuts = {(t, v): cut(os.path.join(RUN, f"cutE_{t}_{v}.txt")) for t in TAGS for v in VDS}

os.makedirs("figures", exist_ok=True)
with open("figures/fieldPlate_sweep.csv", "w") as f:
    f.write("Vd,Id_highk,Id_sin,Epk_highk,Epk_sin,Te_highk,Te_sin\n")
    h, s = sweep["highk"], sweep["sin"]
    for i in range(len(h)):
        f.write(f"{h['Vd'][i]:g},{h['Id'][i]:.6g},{s['Id'][i]:.6g},{h['Epk_Vcm'][i]:.6g},"
                f"{s['Epk_Vcm'][i]:.6g},{h['Te_pk'][i]:.6g},{s['Te_pk'][i]:.6g}\n")
with open("figures/fieldPlate_cuts.csv", "w") as f:
    f.write("Vd,y_um," + ",".join(f"E_{t}_Vcm" for t in TAGS) + "\n")
    for v in VDS:
        a, b = cuts[("highk", v)], cuts[("sin", v)]
        for (y, eh), (_, es) in zip(a, b):
            f.write(f"{v},{y:.6g},{eh:.6g},{es:.6g}\n")

print("peak |grad Qfn| (kV/cm) by region, HighK / SiN:")
regions = (((-0.2, 0.3), "gate drain edge"), ((0.3, 0.6), "T-gate head edge"),
           ((0.6, 1.0), "field plate edge"), ((1.0, 3.0), "access region"))
for v in VDS:
    out = []
    for (lo, hi), name in regions:
        vals = []
        for t in TAGS:
            c = cuts[(t, v)]
            m = (c[:, 0] > lo) & (c[:, 0] < hi)
            vals.append(c[m, 1].max() / 1e3)
        out.append(f"{name} {vals[0]:.0f}/{vals[1]:.0f}")
    print(f"  Vd={v:>2} V: " + "; ".join(out))

plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})
fig = plt.figure(figsize=(17, 9))
gs = fig.add_gridspec(2, 3)
for k, v in enumerate(VDS):
    ax = fig.add_subplot(gs[0, k])
    for t, lab in TAGS.items():
        c = cuts[(t, v)]
        ax.plot(c[:, 0], c[:, 1] / 1e3, color=DEV_C[t], lw=1.8, label=lab)
    ax.axvspan(*GATE, color=GRID, alpha=0.9, lw=0)
    ax.axvspan(*FP, color=GRID, alpha=0.45, lw=0)
    ax.axvline(THEAD[1], color=MUTED, lw=0.8, ls=":")
    ax.set_xlim(-0.6, 3.0)
    ax.set_title(f"Vd = {v} V: |∇Qfn| along the 2DEG", color=INK, fontsize=11)
    ax.set_xlabel("y (µm), source → drain")
    if k == 0:
        ax.set_ylabel("lateral driving field (kV/cm)")
        ax.legend(frameon=False)
    ax.text(0.0, ax.get_ylim()[1] * 0.93, "gate", ha="center", fontsize=8, color=MUTED)
    ax.text(0.505, ax.get_ylim()[1] * 0.93, "FP", ha="center", fontsize=8, color=MUTED)
    ax.text(THEAD[1] + 0.02, ax.get_ylim()[1] * 0.80, "T-head\nedge", fontsize=7, color=MUTED)
ax = fig.add_subplot(gs[1, 0])
for t, lab in TAGS.items():
    ax.plot(sweep[t]["Vd"], sweep[t]["Id"], color=DEV_C[t], lw=2, label=lab)
ax.set_xlabel("Vd (V)")
ax.set_ylabel("Id (mA/mm)")
ax.set_title("Trap-free Id, Vg = -2 V", color=INK, fontsize=11)
ax.legend(frameon=False)
ax = fig.add_subplot(gs[1, 1])
for t, lab in TAGS.items():
    ax.plot(sweep[t]["Vd"], sweep[t]["Epk_Vcm"] / 1e3, color=DEV_C[t], lw=2, label=lab)
ax.axvspan(0, 3, color=GRID, alpha=0.7, lw=0)
ax.text(1.5, 30, "trap sweeps\n(0-3 V)", ha="center", fontsize=8, color=MUTED)
ax.set_xlabel("Vd (V)")
ax.set_ylabel("peak |∇Qfn| in the channel (kV/cm)")
ax.set_title("Peak field (at the gate drain edge)", color=INK, fontsize=11)
ax = fig.add_subplot(gs[1, 2])
for v, ls in zip(VDS, (":", "--", "-")):
    a, b = cuts[("highk", v)], cuts[("sin", v)]
    m = (a[:, 0] > -0.6) & (a[:, 0] < 3.0)
    ax.plot(a[m, 0], (a[m, 1] - b[m, 1]) / 1e3, color=INK, lw=1.6, ls=ls, label=f"Vd = {v} V")
ax.axhline(0, color=MUTED, lw=0.8)
ax.axvspan(*GATE, color=GRID, alpha=0.9, lw=0)
ax.axvspan(*FP, color=GRID, alpha=0.45, lw=0)
ax.set_xlabel("y (µm), source → drain")
ax.set_ylabel("E(HighK) - E(SiN) (kV/cm)")
ax.set_title("Field moved by the HighK (negative = passivated)", color=INK, fontsize=11)
ax.legend(frameon=False, fontsize=9)
for ax in fig.axes:
    ax.grid(True, color=GRID, lw=0.8)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
fig.suptitle("HighK vs SiN passivation, trap-free: the HighK flattens the field at the T-gate head "
             "and field plate, but only above ~5 V; the gate-edge peak is unchanged",
             color=INK, fontsize=12)
fig.tight_layout()
fig.savefig("figures/fieldPlate.png", dpi=140)
print("wrote figures/fieldPlate{.png,_sweep.csv,_cuts.csv}")
