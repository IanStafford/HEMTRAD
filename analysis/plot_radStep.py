"""Stepped-curve search at the 28 V stress (radStep*, 2026-11-17): every Id-Vd in a run directory, one panel per
group, plus a list of drop episodes (consecutive decreases totalling more than `min_drop` mA/mm) per curve.

usage: python3 analysis/plot_radStep.py <run dir> <out.png> [min_drop mA/mm] [group regex]
Labels look like A_p1.5e+18_n5e+18_N3: the panel is the label without its _N<k> suffix; colour by N.
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

PRE = "results/20261104_radMap1/task_*/sin_ref_IdVd.csv"
RAMP = {0: "#9aa0a8", 1: "#e0782f", 2: "#b8460f", 3: "#5a1d04"}


def load(p):
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(p) if l.strip()])


def drops(v, i, min_drop):
    """Episodes of falling current: (Vd start, Vd end, Id before, Id after)."""
    out, k = [], 1
    while k < len(i):
        if i[k] < i[k - 1]:
            a = k - 1
            while k < len(i) and i[k] < i[k - 1]:
                k += 1
            if i[a] - i[k - 1] >= min_drop:
                out.append((float(v[a]), float(v[k - 1]), float(i[a]), float(i[k - 1])))
        else:
            k += 1
    return out


def main(run, out, min_drop=10.0, rx=".*"):
    min_drop = float(min_drop)
    curves = {}
    for t in sorted(glob.glob(f"{run}/task_*")):
        try:
            lab = json.load(open(f"{t}/params.json"))["label"]
        except (OSError, ValueError):
            continue
        f = glob.glob(f"{t}/*_IdVd.csv")
        if not f or not re.search(rx, lab):
            continue
        d = load(f[0])
        if d.ndim < 2 or len(d) < 3:
            continue
        curves[lab] = d
    groups = {}
    for lab in curves:
        m = re.match(r"(.*)_N(\d)$", lab)
        g, n = (m.group(1), int(m.group(2))) if m else (lab, 0)
        groups.setdefault(g, []).append((n, lab))
    pre = load(glob.glob(PRE)[0])
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
