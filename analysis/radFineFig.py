"""Fine-mesh results: final SiN curve, current limit by density, gate independence, resistance per strike.
usage: python3 analysis/radFineFig.py <out.png>   (expects results/20261105_radFine, radMulti and FINAL_REF in the env)
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


F, M = "results/20261105_radFine", "results/20261105_radMulti"


def load(run, tag, k="IdVd"):
    g = glob.glob(f"{run}/task_*/{tag}_{k}.csv")
    if not g or os.path.getsize(g[0]) == 0:
        return None
    return np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(g[0]) if l.strip()])


fig, ax = plt.subplots(1, 4, figsize=(15.5, 3.8))
d = np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(os.environ["FINAL_REF"]) if l.strip()])
ax[0].plot(d[:, 0], d[:, 1], color="#e0732b", lw=1.8, label="standard mesh")
d = load(F, "sin_final_m10")
ax[0].plot(d[:, 0], d[:, 1], color="#14325c", lw=1.8, label="10 nm, y 0.3–1.6 µm")
ax[0].set_title("Final SiN biased curve", fontsize=11)
ax[0].legend(fontsize=8)

cm = {"4e+18": "#9ec5ee", "6e+18": "#5a9be0", "8e+18": "#2a78d6", "1.2e+19": "#14325c"}
for n, c in cm.items():
    a = load(F, f"hk_y1.5_w0.3_n{n}") if n != "4e+18" else load("results/20261104_radMesh", "hk_y1.50_m05")
    if a is not None:
        ax[1].plot(a[:, 0], a[:, 1], color=c, lw=1.6, label=f"{n.replace('e+', 'e')} cm⁻³")
    b = load(F, f"hk_y1.5_w0.1_n{n}")
    if b is None and n == "1.2e+19":
        b = load(F, "hk_y1.5_w0.1_n1.2e19_m025")
    if b is not None:
        ax[1].plot(b[:, 0], b[:, 1], color=c, lw=1.2, ls="--")
ax[1].set_title("Density (solid 0.3, dashed 0.1 µm)", fontsize=11)
ax[1].legend(fontsize=8)

for vg, c in ((-2, "#9ec5ee"), (-1, "#5a9be0"), (0, "#14325c")):
    a = load(F, f"sin_fresh_y1.5_w0.1_n1.2e19_G{vg}")
    ax[2].plot(a[:, 0], a[:, 1], color=c, lw=1.6, label=f"Vg {vg} V")
    r = load(F, f"sin_ref_G{vg}") if vg != -2 else load("results/20261104_radFam", "sin_ref", "IdVdG-2")
    ax[2].plot(r[:, 0], r[:, 1], color=c, lw=1, ls=":")
ax[2].set_title("Fresh curves (dotted undamaged)", fontsize=11)
ax[2].set_ylim(0, 450)
ax[2].legend(fontsize=8)

rows = []
for p in glob.glob(f"{M}/task_*/params.json"):
    l = json.load(open(p))["label"]
    m = re.search(r"ms_(\w+)_k(\d)", l)
    a = load(M, l)
    if a is None or len(a) < 3:
        continue
    k = int(m[2]) if m else 1
    rows.append((k, a[1, 0] / a[1, 1] * 1e3, l, a[-1, 0]))
rs = {k: [r[1] for r in rows if r[0] == k] for k in range(1, 6)}
rf = load("results/20261104_radMap1", "hk_ref")
base = rf[1, 0] / rf[1, 1] * 1e3
ax[3].scatter([0], [base], color="0.5", s=30)
for k, v in rs.items():
    ax[3].scatter([k] * len(v), v, color="#2a78d6", s=18, alpha=0.7)
ax[3].set_title("Vd/Id at 0.25 V vs strikes", fontsize=11)
ax[3].set_xlabel("Damaged sites")
ax[3].set_ylabel("Vd / Id (Ω·mm), Vg +1 V")
for a in ax[:3]:
    a.set_xlabel("Vd (V)")
    a.set_ylabel("Id (mA/mm)")
for a in ax:
    a.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=130)
print("ref Ron", round(base, 3))
for k, v in rs.items():
    print("k", k, "n", len(v), "Ron mean %.3f min %.3f max %.3f" % (np.mean(v), min(v), max(v)))
print("reach 10 V by k:", {k: (sum(1 for r in rows if r[0] == k and r[3] >= 10), len(rs[k])) for k in rs})
# plateau mean from 4 to 10 V
for lab, run, t in [("w0.3 4e18 m05", "results/20261104_radMesh", "hk_y1.50_m05"), ("w0.3 6e18", F, "hk_y1.5_w0.3_n6e+18"), ("w0.3 8e18", F, "hk_y1.5_w0.3_n8e+18"), ("w0.1 4e18", F, "hk_y1.5_w0.1_n4e+18"), ("w0.1 6e18", F, "hk_y1.5_w0.1_n6e+18"), ("w0.1 8e18", F, "hk_y1.5_w0.1_n8e+18"), ("w0.1 1.2e19 m05", "results/20261104_radMesh", "hk_w0.1_m05"), ("w0.1 1.2e19 m025", F, "hk_y1.5_w0.1_n1.2e19_m025")]:
    a = load(run, t)
    s = a[a[:, 0] >= 3]
    print(lab, "Id 3-10 V mean %.0f min %.0f max %.0f" % (s[:, 1].mean(), s[:, 1].min(), s[:, 1].max()))
