"""Render a damaged 3D slice (FLOOXS `struct vtk=` after a drivers/radIV.tcl run with damRod) to PNG with PyVista.

usage: ~/venvs/render/bin/python analysis/render3d_slice.py <file.vtu> <out.png> [ymin ymax um] [label]

Expects the point fields LogElec (log10 electron density) and LogTrap (log10 trap density), set after the driver
with `sel z=log10(abs(Elec)+1.0) name=LogElec` and the same for TrapN, plus the MatID field the VTK writer adds
(0 Metal, 1 passivation, 2 AlGaN, 3 GaN for rfdevice3d.tcl). FLOOXS coordinates are cm with x = depth (down),
y = along the channel, z = along the gate width; the render uses um with the channel along X, the width along Y and
height up. Shows the slice cropped to [ymin, ymax] and to 0.3 um of buffer,
the damage rod as the TrapN = 1e18 isosurface below the 2DEG, and a plane
2 nm under the AlGaN/GaN interface coloured by electron density (the 2DEG).
"""
import sys

import numpy as np
import pyvista as pv
import vtk

pv.OFF_SCREEN = True
COL = {0: "#b8a46a", 1: "#cfd8dc", 2: "#5b8fc9", 3: "#8d8476"}
ROD = "#c0392b"


def load(path, ymin, ymax):
    r = vtk.vtkXMLUnstructuredGridReader()   # FLOOXS names the XML file .vtk, which pv.read takes for legacy VTK
    r.SetFileName(path)
    r.Update()
    m = pv.wrap(r.GetOutput())
    p = m.points * 1.0e4
    m.points = np.column_stack([p[:, 1], p[:, 2], -p[:, 0]])   # (channel, width, up) in um
    return m.clip_box([ymin, ymax, -1e3, 1e3, -1e3, 1e3], invert=False)


def part(m, k):
    return m.threshold([k - 0.5, k + 0.5], scalars="MatID", preference="point", all_scalars=True)


def labels(pl, items, size=24):
    for pos, text in items:
        pl.add_point_labels(np.array([pos], dtype=float), [text], font_size=size, text_color="#18212b",
                            point_size=1, shape_color="#fbfaf7", shape_opacity=0.9, margin=6,
                            always_visible=True, show_points=False)


def main(path, out, ymin=0.15, ymax=1.45, label=""):
    ymin, ymax = float(ymin), float(ymax)
    m = load(path, ymin, ymax).clip_box([-1e3, 1e3, -1e3, 1e3, -0.30, 1e3], invert=False)
    zint = part(m, 2).bounds[4]              # AlGaN/GaN interface height (um, up positive)
    w0, w1 = m.bounds[2], m.bounds[3]
    pl = pv.Plotter(window_size=(2200, 1300), lighting="three lights")
    pl.set_background("#f6f4ef")
    s = part(m, 0)
    pl.add_mesh(s.extract_surface(algorithm=None), color=COL[0], specular=0.15)
    gan = part(m, 3).clip_box([-1e3, 1e3, -1e3, 1e3, -1e3, zint - 0.03], invert=False)
    pl.add_mesh(gan.extract_surface(algorithm=None), color=COL[3], opacity=0.45, specular=0.1)
    al = part(m, 2).extract_surface(algorithm=None)
    pl.add_mesh(al, color=COL[2], opacity=0.10)
    pl.add_mesh(al.outline(), color="#3c6aa0", line_width=2)
    semi = m.threshold([1.5, 3.5], scalars="MatID", preference="point", all_scalars=True)
    rod = semi.contour([18.0], scalars="LogTrap").clip_box([-1e3, 1e3, -1e3, 1e3, -1e3, zint - 0.004], invert=False)
    if rod.n_points:
        pl.add_mesh(rod, color=ROD, smooth_shading=True, specular=0.3)
    sl = part(m, 3).slice(normal="z", origin=(0.0, 0.0, zint - 0.002))
    pl.add_mesh(sl, scalars="LogElec", cmap="viridis", clim=[17.0, 19.3], show_edges=False,
                scalar_bar_args=dict(title="electron density in the 2DEG, log10 cm^-3", n_labels=3,
                                     title_font_size=28, label_font_size=24, color="#18212b",
                                     position_x=0.31, position_y=0.05, width=0.38, height=0.055, fmt="%.0f"))
    labels(pl, [((0.62, w0, 0.40), "T-gate and field plate"), ((ymax - 0.12, w0, zint + 0.03), "AlGaN / 2DEG"),
                ((ymax - 0.12, w0, -0.22), "GaN buffer"), ((0.8, w0, -0.13), "Ion-track damage, 8e18 cm^-3"),
                ((0.8, w1, zint + 0.05), "2DEG intact")], size=26)
    if label:
        pl.add_text(label, position="upper_left", font_size=16, color="#18212b")
    pl.camera_position = [(1.55, -2.0, 1.25), (0.78, 0.2, 0.02), (0, 0, 1)]
    pl.camera.zoom(1.08)
    pl.screenshot(out)
    pl.close()
    print("wrote", out, "AlGaN/GaN at", zint, "um; shown width", w1 - w0, "um")


if __name__ == "__main__":
    main(*sys.argv[1:])
