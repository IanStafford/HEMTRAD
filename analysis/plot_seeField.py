"""Lateral field |dpsi/dy| at the 2DEG row during a strike transient (2026-11-24): SiN and HighK, fixed FP contact,
Vg -10 / Vd 28 V (fxSeeMap28 52357004), and the old-contact runs (seeMap28 51945449) for the DC panel. Field from
the potential of the snapshots (drivers/seeIV.tcl, 2D mesh; not refined at the head edge, so peaks are approximate).
Model output only.
usage: ~/venvs/render/bin/python analysis/plot_seeField.py [out.png]"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy as v2n

PRE = {"SiN": "results/20261122_fxSeeMap28/task_0/fx_sin_y0.2_map", "HighK": "results/20261122_fxSeeMap28/task_1/fx_hk_y0.2_map"}
OLD = {"SiN": "results/20261118_seeMap28/task_0/sin_y0.2_map", "HighK": "results/20261118_seeMap28/task_1/hk_y0.2_map"}
COL = {"SiN": "#C2410C", "HighK": "#1B4F9C"}
XROW = 0.016          # um, 1 nm below the AlGaN/GaN interface


def load(f):
    r = vtk.vtkXMLUnstructuredGridReader()
    r.SetFileName(f)
    r.Update()
    g = r.GetOutput()
    P = v2n(g.GetPoints().GetData()) * 1e4
    c = v2n(g.GetCells().GetConnectivityArray()).reshape(-1, 3)
    mat = v2n(g.GetPointData().GetArray("MatID")).astype(int)
    gan = mat.max()                        # HighK deck has one insulator more than SiN, so its GaN is ID 4, SiN's 3
    assert P[mat == gan][:, 0].max() > 5.0, "highest MatID is not the buffer"
    return P, c, v2n(g.GetPointData().GetArray("DevPsi")), np.where(mat == gan, 3, np.where(mat < gan, 0, mat))


def row_mask(P, mat):
    """GaN nodes on the mesh row nearest x = XROW (the depth rows differ slightly between the decks)."""
    xs = np.unique(np.round(P[mat == 3][:, 0], 5))
    x0 = xs[np.argmin(np.abs(xs - XROW))]
    return np.abs(P[:, 0] - x0) < 1e-5


def efield(f):
    """(y, |Ey|) in um and V/cm on the GaN nodes of the row x = XROW: triangle gradients, area-weighted to nodes."""
    P, c, psi, mat = load(f)
    tri = c[(mat[c] == 3).all(1)]
    x, y, s = P[tri][:, :, 0], P[tri][:, :, 1], psi[tri]
    det = (x[:, 1] - x[:, 0]) * (y[:, 2] - y[:, 0]) - (x[:, 2] - x[:, 0]) * (y[:, 1] - y[:, 0])
    ok = np.abs(det) > 1e-12
    tri, x, y, s, det = tri[ok], x[ok], y[ok], s[ok], det[ok]
    dy = ((x[:, 1] - x[:, 0]) * (s[:, 2] - s[:, 0]) - (x[:, 2] - x[:, 0]) * (s[:, 1] - s[:, 0])) / det
    W, G = np.zeros(len(P)), np.zeros(len(P))
    for k in range(3):
        np.add.at(W, tri[:, k], np.abs(det))
        np.add.at(G, tri[:, k], np.abs(det) * dy)
    m = (mat == 3) & (W > 0) & row_mask(P, mat)
    o = np.argsort(P[m][:, 1])
    return P[m][o, 1], np.abs(G[m] / W[m])[o] * 1e4


def fd(f):
    """Independent check: node-to-node finite difference of DevPsi along the row."""
    P, c, psi, mat = load(f)
    m = (mat == 3) & row_mask(P, mat)
    o = np.argsort(P[m][:, 1])
    y, s = P[m][o, 1], psi[m][o]
    k = np.diff(y) > 1e-5
    return (y[1:] + y[:-1])[k] / 2, np.abs(np.diff(s) / np.diff(y))[k] * 1e4


def snaps(pre):
    out = [("DC", pre + "_map_dc.vtk")]
    for k in range(8):
        f = f"{pre}_map_{k}.vtk"
        if os.path.exists(f):
            out.append((f"{float(open(f + '.txt').read().split()[1]) * 1e12:.0f} ps", f))
    return out


def main(out="figures/see/strike_field_28V.png"):
    fig, axs = plt.subplots(1, 3, figsize=(16, 4.6))
    ax = axs[0]
    for d in ("SiN", "HighK"):
        y, e = efield(OLD[d] + "_map_dc.vtk")
        ax.plot(y, e / 1e5, color=COL[d], lw=1.2, ls=":", label=f"{d}, old contact")
        y, e = efield(PRE[d] + "_map_dc.vtk")
        ax.plot(y, e / 1e5, color=COL[d], lw=2, label=f"{d}, fixed contact")
    ax.set_title("Before the strike (DC, Vg -10 / Vd 28 V)", fontsize=11, loc="left")
    for ax, d in zip(axs[1:], ("SiN", "HighK")):
        ss = snaps(PRE[d])
        keep = [s for s in ss if s[0] in ("DC", "3 ps", "6 ps", "12 ps", "13 ps", "31 ps", "32 ps", "105 ps", "116 ps")
                or s[0] == ss[-1][0]]
        cm = plt.get_cmap("viridis")
        for i, (lab, f) in enumerate(keep):
            y, e = efield(f)
            ax.plot(y, e / 1e5, color=cm(i / max(len(keep) - 1, 1)) if lab != "DC" else "0.1", lw=2 if lab == "DC" else 1.4, label=lab)
        ax.set_title(f"{d}, fixed contact: strike at y 0.2 um", fontsize=11, loc="left")
    for ax in axs:
        ax.axvspan(0.3, 0.725, color="#eef1f5", lw=0)
        ax.set_xlim(-0.2, 3.35)
        ax.set_ylim(0, 10.5)
        ax.set_xlabel("y along the channel (um)")
        ax.grid(color="#e3e5e8", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, fontsize=8.5)
    axs[0].set_ylabel("lateral field |Ey| at x 16 nm (1e5 V/cm)")
    fig.text(0.5, 0.005, "shaded: y 0.3-0.725 um, the stress-damage window under the T-gate head and field plate", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out, dpi=150)
    print("wrote", out)


def check():
    for d in ("SiN", "HighK"):
        for lab, f in snaps(PRE[d])[:2] + snaps(PRE[d])[-1:]:
            y, e = efield(f)
            yf, ef = fd(f)
            w = lambda yy: (yy > 0.3) & (yy < 0.725)
            print(f"{d:5s} {lab:>6s} peak 0.3-0.725: tri {e[w(y)].max():.3e}  finite diff {ef[w(yf)].max():.3e}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        check()
    else:
        main(*sys.argv[1:])
