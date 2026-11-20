"""Table of the drops of vdCuts runs (drivers/radIV.tcl vdCuts=1) and what switches at each one: for every drop
(a run of falling Id of at least 8 mA/mm) the y position and size of the largest rise of the filled traps
mid-barrier (IonAcceptor at x 0.008 um, if cut), the barrier/2DEG electron temperature there, and the 2DEG density
and lateral field at that spot before and after.
usage: python3 analysis/vdcutsDropTable.py <task dir> [<task dir> ...]"""
import glob
import json
import sys

import numpy as np

sys.path.insert(0, "analysis")
import vdcuts  # noqa: E402


def drops(v, i, thr=8.0):
    out, k = [], 0
    while k < len(v) - 1:
        if i[k + 1] < i[k] - 1.0:
            s = k
            while k < len(v) - 1 and i[k + 1] < i[k] - 0.5:
                k += 1
            if i[s] - i[k] >= thr:
                out.append((s, k))
        k += 1
    return out


def at(c, vd, lab, y0):
    y, val = c[vd][lab]
    return val[np.argmin(np.abs(y - y0))]


def table(task):
    lab = json.load(open(f"{task}/params.json"))["label"]
    c = vdcuts.load(glob.glob(f"{task}/*_vdcuts.txt")[0])
    iv = np.loadtxt(glob.glob(f"{task}/*_IdVd.csv")[0], delimiter=",", usecols=(0, 1))
    v, i = iv[:, 0], iv[:, 1]
    rows = []
    for s, k in drops(v, i):
        a, b = round(v[s], 3), round(v[k], 3)
        bar = "IonAcceptor_x0.008" in c[a]
        if bar:
            y, fa = c[a]["IonAcceptor_x0.008"]
            _, fb = c[b]["IonAcceptor_x0.008"]
        else:                                   # no barrier cut: locate by the largest fall of the 2DEG density
            y, fa = c[a]["Elec"]
            _, fb = c[b]["Elec"]
            fa, fb = -np.log10(np.maximum(fa, 1)), -np.log10(np.maximum(fb, 1))
        m = (y > 0.2) & (y < 2.8)
        d = fb - fa
        j = np.argmax(np.where(m, d, -np.inf))
        y0 = y[j]
        r = dict(label=lab, vd=f"{a:g}-{b:g}", id=f"{i[s]:.0f}->{i[k]:.0f}", y=round(float(y0), 3),
                 n=f"{at(c, a, 'Elec', y0):.1e}->{at(c, b, 'Elec', y0):.1e}",
                 E=f"{at(c, a, 'Ey', y0):.1e}->{at(c, b, 'Ey', y0):.1e}",
                 Te=f"{at(c, a, 'TeTrap', y0):.0f}->{at(c, b, 'TeTrap', y0):.0f}")
        if bar:
            r["fill"] = f"{fa[j]:.1e}->{fb[j]:.1e}"
            r["TeBar"] = f"{at(c, a, 'TeTrap_x0.008', y0):.0f}->{at(c, b, 'TeTrap_x0.008', y0):.0f}"
        rows.append(r)
    return lab, v[-1], rows


if __name__ == "__main__":
    for t in sys.argv[1:]:
        lab, vend, rows = table(t)
        print(f"== {lab} (to {vend:g} V)")
        for r in rows:
            extra = f" barrier fill {r['fill']} TeBar {r['TeBar']} K" if "fill" in r else ""
            print(f"  {r['vd']:>9} V  Id {r['id']:>9}  at y {r['y']:.3f}: n {r['n']}  E {r['E']}  Te {r['Te']} K{extra}")
