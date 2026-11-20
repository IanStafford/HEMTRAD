"""Goal deliverable, mesh-checked (2026-11-20): SiN 0-3 strike series at the 28 V stress on the library mesh
(15 nm at y 0.8), 10 nm uniform and 5 nm at y 0.8, with pre-irradiation and the Nov 11 model as references and
each drop (>= 10 mA/mm) marked by an arrow. One row per strike setting (keys of plot_meshSeries.SETS).
usage: python3 analysis/plot_meshDeliverable.py <out.png> <key> [<key> ...]"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "analysis")
from plot_meshSeries import MESHES, SETS, find, index, load  # noqa: E402
from plot_radStepSeries import NOV11, PRE, SIN_RAMP, panel  # noqa: E402
from plot_radStepSeries import load as loadg  # noqa: E402


def main(out, *keys):
    idx = index()
    pre, nov = loadg(PRE["sin"]), loadg(NOV11)
    fig, axs = plt.subplots(len(keys), len(MESHES), figsize=(5.2 * len(MESHES), 4.2 * len(keys)), sharex=True,
                            squeeze=False)
    for r, key in enumerate(keys):
        title, labs = SETS[key]
        for c, (mname, prefixes) in enumerate(MESHES):
            ax = axs[r][c]
            curves = {}
            for n in range(4):
                f = find(idx, prefixes, labs[n])
                curves[n] = load(f) if f else None
            if all(curves[n] is None for n in (1, 2, 3)):
                ax.text(0.5, 0.5, "not run yet", ha="center", va="center", transform=ax.transAxes, color="#8a8f98")
                ax.set_title(f"{mname}", fontsize=10, loc="left")
                ax.set_axis_off()
                continue
            panel(ax, curves, SIN_RAMP, pre, nov if c == 0 else None, f"{title}\n{mname}")
            ax.title.set_fontsize(10)
            ax.set_ylim(0, 450)          # pre-irradiation (to ~1030 mA/mm) runs off the top so the steps stay readable
            ax.tick_params(labelbottom=True)
            if c != 0:
                ax.get_legend().remove()
        axs[r][0].set_ylabel("Id (mA/mm) at Vg +1 V")
    fig.suptitle("SiN, 28 V off-state stress (Vg −10 V, damage scale 1.5e18) plus 0–3 strikes at y 0.8 / 1.6 / 2.4 µm, "
                 "on three meshes (model output)", fontsize=11.5, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
