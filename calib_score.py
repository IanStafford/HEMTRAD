"""Score calibIdVg.tcl runs against the measured transfer curve.

For each simulated Id-Vg (run at phiB = phiB_run), find the rigid gate shift dv
that minimises the rms % error over Vg -2.6..+1 V. Because phiB enters the gate
equation only as G - phiB, the shifted curve is what a run at
phiB = phiB_run - dv gives (apart from the field plate, which also uses phiB;
confirm the final value with a real run).

usage: python3 calib_score.py [--phiB 1.65] label=sim.csv [label=sim.csv ...]
"""
import sys

import numpy as np

EXP = "figures/rfDeviceHFO2_Experimental.csv"
W_MM = 0.2

args = sys.argv[1:]
phib = 1.65
if args and args[0] == "--phiB":
    phib = float(args[1])
    args = args[2:]

e = np.loadtxt(EXP, delimiter=",")
eg, ei = e[:, 0], e[:, 1] * 1e3 / W_MM
m_all = (eg >= -2.6) & (eg <= 1.0001)
m_0 = (eg >= -2.6) & (eg <= 0.0001)
egm = np.gradient(ei, eg)
print(f"{'run':24s} {'dv':>6s} {'phiB':>5s} {'rms->0':>7s} {'rms->+1':>8s} "
      f"{'@-2.8':>6s} {'@0':>6s} {'@+1':>6s} {'gm-1':>5s} {'gm0':>5s} {'gm+1':>5s}")
print(f"{'experiment':24s} {'':>6s} {'':>5s} {'':>7s} {'':>8s} {'':>6s} {'':>6s} {'':>6s} "
      f"{np.interp(-1, eg, egm):5.0f} {np.interp(0, eg, egm):5.0f} {np.interp(1, eg, egm):5.0f}")
for a in args:
    lab, path = a.split("=", 1)
    s = np.loadtxt(path, delimiter=",", ndmin=2)
    s = s[np.argsort(s[:, 0])]
    g, i = s[:, 0], s[:, 1]
    best = None
    for dv in np.arange(-3.0, 1.0, 0.005):
        if eg[m_all].min() + dv < g.min() or eg[m_all].max() + dv > g.max():
            continue
        err = 100 * (np.interp(eg[m_all] + dv, g, i) - ei[m_all]) / ei[m_all]
        r = np.sqrt(np.mean(err ** 2))
        if best is None or r < best[0]:
            best = (r, dv)
    if best is None:
        print(f"{lab:24s} Vg range too narrow to align")
        continue
    r, dv = best
    err = 100 * (np.interp(eg + dv, g, i) - ei) / ei
    gm = np.gradient(i, g)
    r0 = np.sqrt(np.mean(err[m_0] ** 2))
    print(f"{lab:24s} {dv:+6.3f} {phib - dv:5.2f} {r0:6.2f}% {r:7.2f}% "
          f"{np.interp(-2.8, eg, err):+5.0f}% {np.interp(0, eg, err):+5.1f}% {np.interp(1, eg, err):+5.1f}% "
          f"{np.interp(-1 + dv, g, gm):5.0f} {np.interp(dv, g, gm):5.0f} {np.interp(1 + dv, g, gm):5.0f}")
