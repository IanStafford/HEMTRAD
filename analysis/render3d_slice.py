"""Render a damaged 3D slice (FLOOXS `struct vtk=` after a drivers/radIV.tcl run with damRod) to PNG with PyVista.

usage: ~/venvs/render/bin/python analysis/render3d_slice.py <file.vtu> <out.png> [ymin ymax um] [label]

Expects the point fields LogElec (log10 electron density) and LogTrap (log10 trap density), set after the driver
with `sel z=log10(abs(Elec)+1.0) name=LogElec` and the same for TrapN, plus the MatID field the VTK writer adds
(0 Metal, 1 passivation, 2 AlGaN, 3 GaN for rfdevice3d.tcl). FLOOXS coordinates are cm with x = depth (down),
y = along the channel, z = along the gate width; the render uses um with the channel along X, the width along Y and
height up. Shows the slice cropped to [ymin, ymax], the semiconductor translucent, the damage rod as the TrapN
isosurface, and a plane 2 nm under the AlGaN/GaN interface coloured by electron density (the 2DEG).
"""
import sys

import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True
COL = {0: "#b8a46a", 1: "#cfd8dc", 2: "#5b8fc9", 3: "#8d8476"}
ROD = "#c0392b"


def load(path, ymin, ymax):
    m = pv.read(path)
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


def main(path, out, ymin=0.15, ymax=1.6, label=""):
    ymin, ymax = float(ymin), float(ymax)
    m = load(path, ymin, ymax)
    al = part(m, 2)
    zint = al.bounds[4]                      # AlGaN/GaN interface height (um, up positive)
    W = m.bounds[3] - m.bounds[2]
    pl = pv.Plotter(window_size=(2200, 1300), lighting="three lights")
    pl.set_background("#f6f4ef")
    for k, op in ((3, 0.18), (2, 0.30), (1, 0.10), (0, 1.0)):
        s = part(m, k)
        if s.n_cells:
            pl.add_mesh(s.extract_surface(algorithm=None), color=COL[k], opacity=op, specular=0.15)
    semi = m.threshold([1.5, 3.5], scalars="MatID", preference="point", all_scalars=True)
    rod = semi.contour([18.0], scalars="LogTrap")
    if rod.n_points:
        pl.add_mesh(rod, color=ROD, smooth_shading=True, specular=0.3, opacity=0.85)
    sl = part(m, 3).slice(normal="z", origin=(0.0, 0.0, zint - 0.002))
    pl.add_mesh(sl, scalars="LogElec", cmap="viridis", clim=[15.0, 19.5], show_edges=False,
                scalar_bar_args=dict(title="log10 electron density at the 2DEG (cm^-3)", n_labels=4,
                                     title_font_size=26, label_font_size=22, color="#18212b",
                                     position_x=0.30, position_y=0.04, width=0.40, height=0.06, fmt="%.0f"))
    y0 = m.bounds[2]
    labels(pl, [((ymin + 0.15, y0, 0.36), "T-gate"), ((0.75, y0, 0.66), "Field plate"),
                ((ymax - 0.25, y0, 0.12), "SiN"), ((ymax - 0.2, y0, zint + 0.03), "AlGaN"),
                ((ymax - 0.2, y0, -0.6), "GaN buffer"),
                ((0.8, 0.5 * W, -0.75), "Damage rod, 8e18 cm^-3: half the slice width")])
    if label:
        pl.add_text(label, position="upper_left", font_size=16, color="#18212b")
    c = np.array(m.center)
    pl.camera_position = [(c[0] - 1.6, c[1] - 3.2, c[2] + 2.4), (c[0], c[1], zint - 0.1), (0, 0, 1)]
    pl.camera.zoom(1.25)
    pl.screenshot(out)
    pl.close()
    print("wrote", out, "AlGaN/GaN at", zint, "um; width", W, "um")


if __name__ == "__main__":
    main(*sys.argv[1:])
