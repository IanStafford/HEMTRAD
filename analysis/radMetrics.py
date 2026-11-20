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


# ---- measured-data guards (2026-11-20, Ian: measured numbers stay out of tracked files of this public repo)
PRIVATE_DIRS = ("figures", "dashboard")


def guard_private_output(path, have_measured):
    """Refuse to write a figure that contains measured data into a tracked folder (figures/, dashboard/)."""
    import os
    if not (have_measured and path):
        return
    rel = os.path.relpath(os.path.abspath(path), os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if rel.split(os.sep)[0] in PRIVATE_DIRS:
        raise SystemExit(f"refusing to write measured data to {path}: tracked folder ({rel.split(os.sep)[0]}/) of a public "
                         "repo; write it outside the repo or under data/rad_y2/ (gitignored)")


def load_pre_scalars(targets_path):
    """Measured pre-irradiation scalars (Vth, gm, Ioff) from pre_scalars.csv next to the targets file (untracked)."""
    import csv
    import os
    f = os.path.join(os.path.dirname(targets_path), "pre_scalars.csv")
    if not os.path.exists(f):
        return {}
    rows = [r for r in csv.reader(l for l in open(f) if not l.startswith("#")) if r and r[0] != "key"]
    return {k: float(v) for k, v in rows}

