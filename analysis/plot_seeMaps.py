"""Fig. 5-style maps of a strike transient (after Sun et al., IEEE EDL 46, 813 (2025), Fig. 5): log10 of the
hole (or electron) current density on the 2D cross-section at several times, with arrows for its direction.

usage: ~/venvs/render/bin/python analysis/plot_seeMaps.py <out.png> <row label>=<prefix> [<row label>=<prefix> ...]
           [--carrier p|n] [--y ymin ymax] [--x xmin xmax] [--clim lo hi] [--strike y0]

Each <prefix> names the snapshots written by drivers/seeIV.tcl with seeMapTimes (and seeMapDC): <prefix>_map_dc.vtk,
<prefix>_map_0.vtk, ... each with a <file>.txt holding "t <seconds>". One row per prefix, one panel per snapshot.
FLOOXS writes XML VTK under a .vtk name, so the files are read with vtkXMLUnstructuredGridReader. Coordinates are
cm with x = depth (down) and y = along the channel; the plot uses um, channel across, depth down.
Material outlines come from the MatID field (0 Metal, 1 passivation, 2 AlGaN, 3 GaN).
"""
import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
import pyvista as pv
import vtk


def read(path):
    r = vtk.vtkXMLUnstructuredGridReader()
    r.SetFileName(path)
    r.Update()
    return pv.wrap(r.GetOutput()).triangulate()


def snaps(prefix):
    files = sorted(glob.glob(f"{prefix}_map_*.vtk"), key=lambda f: (not f.endswith("_dc.vtk"), f))
    out = []
    for f in files:
        t = 0.0
        if os.path.exists(f + ".txt"):
            t = float(open(f + ".txt").read().split()[1])
        out.append((t, f, f.endswith("_dc.vtk")))
    dc = [s for s in out if s[2]]
    tr = sorted([s for s in out if not s[2]])
    return dc + tr


def tlabel(t, dc):
    if dc:
        return "before the strike (DC)"
    if t < 1e-9:
        return f"t = {t * 1e12:.3g} ps"
    return f"t = {t * 1e9:.3g} ns"


def panel(ax, path, t, dc, car, xr, yr, clim, y0):
    m = read(path)
    p = m.points * 1.0e4                     # um: p[:,0] depth x, p[:,1] channel y
    cells = m.cells.reshape(-1, 4)[:, 1:]
    tri = mtri.Triangulation(p[:, 1], p[:, 0], cells)
    mat = np.asarray(m.point_data["MatID"])
    semi = (mat >= 2)
    J = np.asarray(m.point_data[f"J{car}Mag"])
    lg = np.log10(np.clip(J, 10.0 ** clim[0], None))
    tmask = ~np.all(semi[cells], axis=1)     # colour the semiconductors only
    tri.set_mask(tmask)
    pc = ax.tripcolor(tri, lg, shading="gouraud", cmap="jet", vmin=clim[0], vmax=clim[1], rasterized=True)
    # metals and dielectrics as flat fills
    for k, col in ((0, "#c9b16b"), (1, "#e6e8ea")):
        tk = mtri.Triangulation(p[:, 1], p[:, 0], cells)
        tk.set_mask(~np.all(mat[cells] == k, axis=1))
        ax.tripcolor(tk, np.zeros(len(p)), cmap=matplotlib.colors.ListedColormap([col]), shading="flat")
    # material outlines
    ax.tricontour(mtri.Triangulation(p[:, 1], p[:, 0], cells), mat, levels=[0.5, 1.5, 2.5], colors="k",
                  linewidths=0.6)
    # direction arrows on a regular grid, semiconductor only, where |J| is within 4 decades of the panel max.
    # Probed on the semiconductor cells with VTK (FLOOXS repeats interface points per region, which makes
    # the full triangulation invalid for matplotlib's tri-finder).
    gy, gx = np.meshgrid(np.linspace(yr[0], yr[1], 26), np.linspace(xr[0], xr[1], 22))
    sm = m.extract_cells(np.where(np.all(semi[cells], axis=1))[0])
    probe = pv.PolyData(np.column_stack([gx.ravel() * 1e-4, gy.ravel() * 1e-4, np.zeros(gx.size)])).sample(sm)
    valid = np.asarray(probe.point_data["vtkValidPointMask"]).astype(bool).reshape(gx.shape)
    fx = np.asarray(probe.point_data[f"J{car}X"]).reshape(gx.shape)
    fy = np.asarray(probe.point_data[f"J{car}Y"]).reshape(gx.shape)
    mag = np.hypot(fx, fy)
    ok = valid & (mag > max(10.0 ** clim[0], mag[valid].max() * 1e-4 if valid.any() else 0.0))
    u = np.where(ok, fy / np.where(ok, mag, 1.0), np.nan)
    v = np.where(ok, fx / np.where(ok, mag, 1.0), np.nan)
    ax.quiver(gy, gx, u, v, color="white", scale=34, width=0.004, headwidth=4, pivot="mid", alpha=0.85)
    if y0 is not None and not dc:
        ax.axvline(y0, color="w", lw=0.8, ls=":")
    ax.set_xlim(*yr)
    ax.set_ylim(xr[1], xr[0])
    ax.set_aspect("equal")
    ax.set_title(tlabel(t, dc), fontsize=10)
    return pc


def main(argv):
    out = argv[0]
    rows, car, yr, xr, clim, y0 = [], "p", (-0.4, 1.4), (-0.45, 1.5), (-2.0, 6.0), None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--carrier":
            car = argv[i + 1]; i += 2
        elif a == "--y":
            yr = (float(argv[i + 1]), float(argv[i + 2])); i += 3
        elif a == "--x":
            xr = (float(argv[i + 1]), float(argv[i + 2])); i += 3
        elif a == "--clim":
            clim = (float(argv[i + 1]), float(argv[i + 2])); i += 3
        elif a == "--strike":
            y0 = float(argv[i + 1]); i += 2
        else:
            lab, pre = a.split("=", 1)
            rows.append((lab, pre)); i += 1
    sets = [(lab, snaps(pre)) for lab, pre in rows]
    nc = max(len(s) for _, s in sets)
    fig, axs = plt.subplots(len(sets), nc, figsize=(3.3 * nc + 1.0, 3.4 * len(sets) + 0.4), squeeze=False)
    pc = None
    for r, (lab, ss) in enumerate(sets):
        for c in range(nc):
            ax = axs[r][c]
            if c >= len(ss):
                ax.axis("off")
                continue
            t, f, dc = ss[c]
            pc = panel(ax, f, t, dc, car, xr, yr, clim, y0)
            if c == 0:
                ax.set_ylabel(f"{lab}\ndepth (µm)")
            if r == len(sets) - 1:
                ax.set_xlabel("position along the channel (µm)")
    cb = fig.colorbar(pc, ax=axs, shrink=0.8, pad=0.02)
    name = "hole" if car == "p" else "electron"
    cb.set_label(f"log10 {name} current density (A/cm²)")
    fig.savefig(out, dpi=170, bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1:])
