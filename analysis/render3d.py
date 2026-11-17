"""Render a FLOOXS 3D slice written with `struct vtk=` (an XML unstructured grid) to PNG with PyVista (offscreen).

usage: ~/venvs/render/bin/python analysis/render3d.py <file.vtu> <out prefix> [track field] [iso cm^-3]

FLOOXS coordinates are cm with x = depth (down), y = along the channel, z = along the gate width. The render
uses um with the channel along X, the width along Y and height up. Materials come from the MatID point field the
VTK writer adds (0 Metal, 1 passivation, 2 AlGaN, 3 GaN for rfdevice3d.tcl). The slice's z = 0 wall is reflecting,
so the overview mirrors it across that wall (a slice twice as wide with the track in the middle) and shows the
semiconductor translucent around the track isosurface; the close-up colours the wall face by track density.
Writes <prefix>_overview.png and <prefix>_track.png.
"""
import sys

import numpy as np
import pyvista as pv
from matplotlib.colors import LinearSegmentedColormap

pv.OFF_SCREEN = True
COL = {0: "#b8a46a", 1: "#cfd8dc", 2: "#5b8fc9", 3: "#8d8476"}
TRACK = "#c0392b"


def load(path, track):
    m = pv.read(path)
    p = m.points * 1.0e4
    m.points = np.column_stack([p[:, 1], p[:, 2], -p[:, 0]])   # (channel, width, up) in um
    if track in m.point_data:
        m.point_data["TrackLog"] = np.log10(np.asarray(m.point_data[track]) + 1.0e14)
    return m


def part(m, k):
    return m.threshold([k - 0.5, k + 0.5], scalars="MatID", preference="point", all_scalars=True)


def labels(pl, items, size=24):
    for pos, text in items:
        pl.add_point_labels(np.array([pos], dtype=float), [text], font_size=size, text_color="#18212b",
                            point_size=1, shape_color="#fbfaf7", shape_opacity=0.9, margin=6,
                            always_visible=True, show_points=False)


def overview(m, track, iso, out):
    mm = m.copy()
    mm.points = mm.points * np.array([1.0, -1.0, 1.0])
    full = m.merge(mm)
    pl = pv.Plotter(window_size=(2200, 1300), lighting="three lights")
    pl.set_background("#f6f4ef")
    for k, op in ((3, 0.30), (2, 0.55), (1, 0.16), (0, 1.0)):
        s = part(full, k)
        if s.n_cells:
            pl.add_mesh(s.extract_surface(algorithm=None), color=COL[k], opacity=op, specular=0.15)
    semi = full.threshold([1.5, 3.5], scalars="MatID", preference="point", all_scalars=True)
    iso_s = semi.contour([iso], scalars=track)
    if iso_s.n_points:
        pl.add_mesh(iso_s, color=TRACK, smooth_shading=True, specular=0.3)
    y0 = full.bounds[2]
    labels(pl, [((-0.3, y0, 0.32), "T-gate"), ((0.7, y0, 0.62), "Field plate"), ((2.7, y0, 0.22), "SiN passivation"),
                ((1.9, y0, -0.01), "AlGaN / 2DEG"), ((2.4, y0, -1.1), "GaN buffer"),
                ((0.5, 0.0, -1.55), "Ion track: Gaussian, sigma 30 nm (surface at 1e18)"), ((-1.15, y0, -0.05), "Source"), ((3.3, y0, -0.45), "Drain")])
    c = np.array(full.center)
    pl.camera_position = [(c[0] - 4.0, c[1] - 9.5, c[2] + 4.6), tuple(c), (0, 0, 1)]
    pl.camera.zoom(1.2)
    pl.screenshot(out)
    pl.close()
    print("wrote", out)


def closeup(m, out):
    pl = pv.Plotter(window_size=(2200, 1300), lighting="three lights")
    pl.set_background("#f6f4ef")
    for k in (3, 2):
        s = part(m, k)
        cm = LinearSegmentedColormap.from_list("t", [COL[k], TRACK])
        pl.add_mesh(s.extract_surface(algorithm=None), scalars="TrackLog", cmap=cm, clim=[16.5, 19.3],
                    show_scalar_bar=False, specular=0.1)
    for k, op in ((1, 0.16), (0, 1.0)):
        s = part(m, k)
        pl.add_mesh(s.extract_surface(algorithm=None), color=COL[k], opacity=op, specular=0.15)
    labels(pl, [((-0.2, 0.0, 0.35), "T-gate"), ((0.75, 0.0, 0.62), "Field plate"), ((1.5, 0.0, -0.01), "AlGaN / 2DEG"),
                ((0.5, 0.0, -1.2), "Ion track at y = 0.5 µm"), ((1.6, 0.0, -0.7), "GaN buffer")], size=26)
    pl.camera_position = [(0.6, -4.2, 0.4), (0.6, 0.4, -0.35), (0, 0, 1)]
    pl.camera.zoom(1.0)
    pl.screenshot(out)
    pl.close()
    print("wrote", out)


def main(path, prefix, track="Track", iso=1.0e18):
    m = load(path, track)
    overview(m, track, float(iso), f"{prefix}_overview.png")
    closeup(m, f"{prefix}_track.png")


if __name__ == "__main__":
    main(*sys.argv[1:])
