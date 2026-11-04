"""Metrics shared by radCompare.py and radMap.py."""
import numpy as np


def vth_gm(vg, idd):
    o = np.argsort(vg)
    vg, idd = vg[o], idd[o]
    gm = np.gradient(idd, vg)
    k = int(np.argmax(gm))
    return vg[k] - idd[k] / gm[k], gm[k]


def ron_step(d, vmax=0.5):
    """From an Id-Vd array (Vd, Id, Id_ext, ... in V, mA/mm): Ron (ohm*mm) from the slope
    for 0 < Vd <= vmax, then the largest drop between neighbouring points and its Vd."""
    v, i = d[:, 0], d[:, 2]
    m = (v > 0) & (v <= vmax)
    ron = 1.0e3 / np.polyfit(v[m], i[m], 1)[0] if m.sum() >= 2 else np.nan
    di = np.diff(i)
    k = int(np.argmin(di)) if len(di) else 0
    drop = float(-di[k]) if len(di) and di[k] < 0 else 0.0
    return ron, drop, float(v[k + 1]) if drop > 0 else np.nan
