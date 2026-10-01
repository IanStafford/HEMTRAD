"""Transfer-curve calibration plot: experiment vs FLOOXS (calibIdVg.tcl).

Experiment: figures/rfDeviceHFO2_Experimental.csv, Id-Vg at Vds = 10 V, measured
in A for a 200 um gate width -> mA/mm = A * 1e3 / 0.2. FLOOXS currents are per
um of depth (A/um), written by calibIdVg.tcl as mA/mm already.

usage: python3 plot_calib.py out.png label1=sim1.csv [label2=sim2.csv ...]
Panels: Id-Vg (linear), Id-Vg (log), error vs experiment (%), gm (mS/mm).
"""
import sys

import matplotlib.pyplot as plt
import numpy as np

EXP = "figures/rfDeviceHFO2_Experimental.csv"
W_MM = 0.2                      # measured device gate width, 200 um
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e6e5df"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]

out = sys.argv[1]
sims = [a.split("=", 1) for a in sys.argv[2:]]

e = np.loadtxt(EXP, delimiter=",")
eg, ei = e[:, 0], e[:, 1] * 1e3 / W_MM
curves = []
for lab, path in sims:
    s = np.loadtxt(path, delimiter=",", ndmin=2)
    s = s[np.argsort(s[:, 0])]
    curves.append((lab, s[:, 0], s[:, 1]))

plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})
fig, axs = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
ax_lin, ax_log, ax_err, ax_gm = axs.ravel()
for ax in (ax_lin, ax_log):
    ax.plot(eg, ei, "o", color=INK, ms=4, mfc="white", label="experiment (Vd = 10 V)")
ax_gm.plot(eg, np.gradient(ei, eg), "o", color=INK, ms=4, mfc="white", label="experiment")
m = eg >= -2.8
print(f"{'model':28s} " + " ".join(f"{g:+5.1f}" for g in (-2.4, -2.0, -1.0, 0.0, 0.5, 1.0))
      + "   (error %)  rms(-2.6..0)  rms(-2.6..+1)")
for c, (lab, g, i) in zip(CAT, curves):
    ax_lin.plot(g, i, color=c, lw=2, label=lab)
    ax_log.semilogy(g, np.maximum(i, 1e-6), color=c, lw=2, label=lab)
    sim_at = np.interp(eg[m], g, i)
    err = 100 * (sim_at - ei[m]) / ei[m]
    ax_err.plot(eg[m], err, color=c, lw=2, marker="o", ms=3, label=lab)
    ax_gm.plot(g, np.gradient(i, g), color=c, lw=2, label=lab)
    pick = [float(np.interp(v, eg[m], err)) for v in (-2.4, -2.0, -1.0, 0.0, 0.5, 1.0)]
    r1 = np.sqrt(np.mean(err[(eg[m] >= -2.6) & (eg[m] <= 0.001)] ** 2))
    r2 = np.sqrt(np.mean(err[eg[m] >= -2.6] ** 2))
    print(f"{lab:28s} " + " ".join(f"{p:+5.1f}" for p in pick) + f"   {r1:10.1f}  {r2:12.1f}")
ax_log.set_ylim(1e-3, 2e3)
ax_err.axhline(0, color=MUTED, lw=1)
ax_err.axhspan(-5, 5, color=GRID, alpha=0.6, lw=0)
ax_err.axvline(0, color=MUTED, lw=0.8, ls=":")
ax_err.set_ylim(-30, 30)
for ax, t, yl in ((ax_lin, "Id-Vg, Vd = 10 V", "Id (mA/mm)"),
                  (ax_log, "Id-Vg (log)", "Id (mA/mm)"),
                  (ax_err, "Model error vs experiment (shaded ±5%)", "(sim - exp) / exp (%)"),
                  (ax_gm, "Transconductance", "gm (mS/mm)")):
    ax.set_title(t, color=INK, fontsize=11)
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel(yl)
    ax.grid(True, color=GRID, lw=0.8)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.set_xlim(-4.0, 1.05)
ax_lin.legend(frameon=False, fontsize=9)
fig.suptitle("HfO2 (HighK) device: FLOOXS field-mobility model vs measured transfer curve "
             "(200 µm device, shown per mm)", color=INK, fontsize=12)
fig.savefig(out, dpi=140)
print(f"wrote {out}")
