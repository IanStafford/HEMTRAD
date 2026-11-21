"""Stepped-curve search at the 28 V stress (radStep*, 2026-11-17): every Id-Vd in a run directory, one panel per
group, plus the drop episodes of each curve (runs of strictly falling Id that fall by at least `min_drop` mA/mm in
total, default 10: mode 'any' of common.drop_episodes).

usage: python3 analysis/plot_radStep.py <run dir> <out.png> [min_drop mA/mm] [group regex]
Labels look like A_p1.5e+18_n5e+18_N3: the panel is the label without its _N<k> suffix; colour by N. Only tasks whose
label matches the group regex and whose Id-Vd has at least 3 points are drawn. Writes out.png and
<out>_drops.json and prints one line per curve.
"""
import glob
import json
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common import DROP_MIN_FIG, REF, STRIKE_SIN_STEP, drop_values, label_index, read_csv

PRE = REF["pre_sin"]
RAMP = dict(enumerate(STRIKE_SIN_STEP))   # colour by number of strikes


def drops(v, i, min_drop):
    """Episodes of falling current: (Vd start, Vd end, Id before, Id after), mode 'any' of common.drop_values.
    Kept under this name because archive/analysis_dayfigs/plot_radStepHighlights.py imports it."""
    return drop_values(v, i, min_drop, "any")


def main(run, out, min_drop=DROP_MIN_FIG, rx=".*"):
    min_drop = float(min_drop)
    # tasks in sorted order; a repeated label keeps the last task
    tasks = label_index(f"{run}/task_*", keep="last", sort=True, match=rx)
    curves = {lab: read_csv(f) for lab, f in tasks.items()}
    groups = {}
    for lab in curves:
        m = re.match(r"(.*)_N(\d)$", lab)
        g, n = (m.group(1), int(m.group(2))) if m else (lab, 0)
        groups.setdefault(g, []).append((n, lab))
    pre = read_csv(glob.glob(PRE)[0])
    nc = min(4, len(groups))
    nr = int(np.ceil(len(groups) / nc))
    fig, axs = plt.subplots(nr, nc, figsize=(4.2 * nc, 3.3 * nr), sharex=True, sharey=True, squeeze=False)
    rep = {}
    for a, (g, items) in zip(axs.flat, sorted(groups.items())):
        a.plot(pre[:, 0], pre[:, 1], color="#c5c9ce", lw=1.2, ls="--")
        for n, lab in sorted(items):
            d = curves[lab]
            a.plot(d[:, 0], d[:, 1], color=RAMP.get(n, "k"), lw=1.6, label=f"N={n}")
            ep = drops(d[:, 0], d[:, 1], min_drop)
            rep[lab] = {"Vd_last": float(d[-1, 0]), "Id1": float(np.interp(1, d[:, 0], d[:, 1])),
                        "Id_end": float(d[-1, 1]), "drops": ep}
            for s in ep:
                a.plot([s[0]], [s[2]], marker="v", ms=5, color=RAMP.get(n, "k"))
        a.set_title(g, fontsize=9)
        a.grid(alpha=0.3)
        a.legend(fontsize=7, frameon=False, loc="lower right")
    for a in axs.flat[len(groups):]:
        a.set_visible(False)
    for a in axs[-1]:
        a.set_xlabel("Vd (V)")
    for a in axs[:, 0]:
        a.set_ylabel("Id (mA/mm)")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    json.dump(rep, open(os.path.splitext(out)[0] + "_drops.json", "w"), indent=1)
    for lab in sorted(rep):
        r = rep[lab]
        ds = "; ".join(f"{s[0]:.1f}-{s[1]:.1f} V {s[2]:.0f}->{s[3]:.0f}" for s in r["drops"]) or "none"
        print(f"{lab:28s} last {r['Vd_last']:5.1f} V  Id1 {r['Id1']:5.0f}  end {r['Id_end']:5.0f}  drops: {ds}")


if __name__ == "__main__":
    main(*sys.argv[1:])
