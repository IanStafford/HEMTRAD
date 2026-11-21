"""Deliverable for the stepped-collapse goal (2026-11-17): matched 0/1/2/3-strike series at the 28 V stress.
One row per candidate series: SiN on the left with the Nov 11 model (radEB1, SiN biased) as a reference,
HighK with the same levers on the right when it exists. Drops (>= 10 mA/mm, mode 'any' of common.drop_episodes)
are marked with arrows. A curve with fewer than 3 points is left out.

usage: python3 analysis/plot_radStepSeries.py <out prefix> [key key ...]
Writes <prefix>_<series>.png per series and <prefix>_all.png with every series; with keys, also
<prefix>_deliverable.png with just those series, one row each (2026-11-18, Ian chose the two partial results:
plain strikes for the SiN steps, field-scaled strikes for the SiN vs HighK contrast).
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DROP_MIN_FIG, REF, drop_values, read_glob

R = "results/20261117_"
PRE = {"sin": REF["pre_sin"], "hk": REF["pre_hk"]}
NOV11 = REF["nov11_sin"]
SIN_RAMP = ["#9aa0a8", "#f0a060", "#d0611d", "#7a2a06"]
HK_RAMP = ["#9aa0a8", "#8db8e6", "#3f7fc4", "#123f7a"]

# series: title, {N: glob} for SiN, {N: glob} for HighK
SERIES = {
    "lev04_n6": ("trap level 0.40 eV, damage scale 1.5e18, strikes of 6e18 at y 0.8 / 1.6 / 2.4 µm",
                 {0: R + "radStepF/task_*/F_lev0.4_N0_IdVd.csv", 1: R + "radStepE/task_*/E_lev0.4_n6e18_N1_IdVd.csv",
                  2: R + "radStepE/task_*/E_lev0.4_n6e18_N2_IdVd.csv", 3: R + "radStepE/task_*/E_lev0.4_n6e18_N3_IdVd.csv"},
                 {k: R + f"radStepF/task_*/F_hk_lev0.4_n6e18_N{k}_IdVd.csv" for k in range(4)}),
    "s06_n6": ("Damage scale 1.5e18, strikes of 6e18, sigma 60 nm, at y 0.8 / 1.6 / 2.4 µm",
               {0: R + "radStepC/task_*/C_p1.5_N0_IdVd.csv", 1: R + "radStepE/task_*/E_s0.06_n6e18_N1_IdVd.csv",
                2: R + "radStepE/task_*/E_s0.06_n6e18_N2_IdVd.csv", 3: R + "radStepE/task_*/E_s0.06_n6e18_N3_IdVd.csv"},
               {}),
    "p15_n6": ("Damage scale 1.5e18, strikes of 6e18 at y 0.8 / 1.6 / 2.4 µm",
               {0: R + "radStepC/task_*/C_p1.5_N0_IdVd.csv", 1: R + "radStepA/task_*/A_p1.5e+18_n6e+18_N1_IdVd.csv",
                2: R + "radStepB/task_*/B_n6e18_N2_IdVd.csv", 3: R + "radStepA/task_*/A_p1.5e+18_n6e+18_N3_IdVd.csv"},
               {k: R + f"radStepC/task_*/C_hk_p1.5_n6e18_N{k}_IdVd.csv" for k in range(4)}),
    "p15_n8": ("Damage scale 1.5e18, strikes of 8e18 at y 0.8 / 1.6 / 2.4 µm",
               {0: R + "radStepC/task_*/C_p1.5_N0_IdVd.csv", 1: R + "radStepA/task_*/A_p1.5e+18_n8e+18_N1_IdVd.csv",
                2: R + "radStepC/task_*/C_p1.5_n8e18_N2_IdVd.csv", 3: R + "radStepA/task_*/A_p1.5e+18_n8e+18_N3_IdVd.csv"},
               {k: R + f"radStepC/task_*/C_hk_p1.5_n8e18_N{k}_IdVd.csv" for k in (1, 2, 3)}),
    "p17_n6": ("Damage scale 1.7e18, strikes of 6e18 at y 0.8 / 1.6 / 2.4 µm",
               {0: R + "radStepA/task_*/A_p1.7e+18_N0_IdVd.csv", 1: R + "radStepA/task_*/A_p1.7e+18_n6e+18_N1_IdVd.csv",
                2: R + "radStepC/task_*/C_p1.7_n6e18_N2_IdVd.csv", 3: R + "radStepA/task_*/A_p1.7e+18_n6e+18_N3_IdVd.csv"},
               {}),
    "fp_n6": ("Damage scale 1.5e18, strikes of 6e18 at the field-plate edges (y 0.9, then 0.3, then 2.0 µm)",
              {0: R + "radStepC/task_*/C_p1.5_N0_IdVd.csv", 1: R + "radStepE/task_*/E_fp_n6e18_N1_IdVd.csv",
               2: R + "radStepE/task_*/E_fp_n6e18_N2_IdVd.csv", 3: R + "radStepE/task_*/E_fp_n6e18_N3_IdVd.csv"},
              {}),
    "fs_bandb": ("field-scaled strikes (damage × (E/E_ref)⁴) at y 0.65 / 0.6 / 0.55 µm, damage scale 1.5e18",
                 {0: R + "radStepC/task_*/C_p1.5_N0_IdVd.csv",
                  **{k: f"results/20261118_radStepI/task_*/I_sin_bandb_N{k}_IdVd.csv" for k in (1, 2, 3)}},
                 {0: R + "radStepC/task_*/C_hk_p1.5_n6e18_N0_IdVd.csv",
                  **{k: f"results/20261118_radStepI/task_*/I_hk_bandb_N{k}_IdVd.csv" for k in (1, 2, 3)}}),
}
ROWTITLE = {"p15_n6": ("Plain strikes: SiN steps", "HighK, same strikes: drops too"),
            "fs_bandb": ("Field-scaled strikes: SiN collapses deeper per strike", "HighK, same strikes: flat")}
plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#8a8f98", "axes.labelcolor": "#2b2f36",
                     "xtick.color": "#4a4f58", "ytick.color": "#4a4f58"})


def load(p):
    """The first file matching the glob p, or None if there is none or it has fewer than 3 rows."""
    return read_glob(p, min_rows=3)


def panel(a, curves, ramp, pre, ref=None, title=""):
    a.plot(pre[:, 0], pre[:, 1], color="#c5c9ce", lw=1.4, ls="--", label="pre-irradiation")
    if ref is not None:
        a.plot(ref[:, 0], ref[:, 1], color="#5b616b", lw=1.2, ls=":", label="Nov 11 model (17.66 V stress)")
    for k in sorted(curves):
        d = curves[k]
        if d is None:
            continue
        a.plot(d[:, 0], d[:, 1], color=ramp[k], lw=2.6 if k == 3 else 1.7,
               label=f"{k} strike{'s' if k != 1 else ''}", zorder=3)
        for s in drop_values(d[:, 0], d[:, 1], DROP_MIN_FIG, "any"):
            a.annotate("", xy=(s[1], s[3]), xytext=(s[0], s[2]),
                       arrowprops=dict(arrowstyle="-|>", color=ramp[k], lw=1.0, shrinkA=0, shrinkB=0))
    a.set_title(title, fontsize=11, loc="left")
    a.set_xlim(0, 12.2)
    a.set_ylim(0, None)
    a.set_xlabel("Vd (V)")
    a.grid(color="#e3e5e8", lw=0.8)
    a.spines[["top", "right"]].set_visible(False)
    a.legend(frameon=False, fontsize=8.5, loc="center right", bbox_to_anchor=(1.0, 0.62))


def main(prefix, *keys):
    pre = {d: load(p) for d, p in PRE.items()}
    nov = load(NOV11)
    rows = []
    for key, (title, sin, hk) in SERIES.items():
        sc = {k: load(p) for k, p in sin.items()}
        hc = {k: load(p) for k, p in hk.items()}
        rows.append((key, title, sc, hc))
        two = any(v is not None for v in hc.values())
        fig, axs = plt.subplots(1, 2 if two else 1, figsize=(12.5 if two else 7.0, 4.6), sharey=True, squeeze=False)
        panel(axs[0][0], sc, SIN_RAMP, pre["sin"], nov, "SiN passivation")
        if two:
            panel(axs[0][1], hc, HK_RAMP, pre["hk"], None, "HighK passivation")
        axs[0][0].set_ylabel("Id (mA/mm) at Vg +1 V")
        fig.suptitle(f"28 V off-state stress (Vg −10 V), {title}", fontsize=11.5, x=0.01, ha="left")
        fig.tight_layout()
        fig.savefig(f"{prefix}_{key}.png", dpi=180)
        plt.close(fig)
        print("wrote", f"{prefix}_{key}.png")
    fig, axs = plt.subplots(len(rows), 2, figsize=(12.5, 4.0 * len(rows)), sharex=True, squeeze=False)
    for i, (key, title, sc, hc) in enumerate(rows):
        panel(axs[i][0], sc, SIN_RAMP, pre["sin"], nov, f"SiN: {title}")
        if any(v is not None for v in hc.values()):
            panel(axs[i][1], hc, HK_RAMP, pre["hk"], None, "HighK, same levers")
        else:
            axs[i][1].set_visible(False)
        axs[i][0].set_ylabel("Id (mA/mm)")
    fig.tight_layout()
    fig.savefig(f"{prefix}_all.png", dpi=130)
    print("wrote", f"{prefix}_all.png")
    if keys:
        sel = [r for r in rows if r[0] in keys]
        fig, axs = plt.subplots(len(sel), 2, figsize=(12.5, 4.3 * len(sel)), sharex=True, squeeze=False)
        for i, (key, title, sc, hc) in enumerate(sel):
            ts, th = ROWTITLE.get(key, (f"SiN: {title}", "HighK, same levers"))
            panel(axs[i][0], sc, SIN_RAMP, pre["sin"], nov, f"{'AB'[i] if i < 2 else i + 1}. {ts}\n{title}")
            panel(axs[i][1], hc, HK_RAMP, pre["hk"], None, f"{th}\n ")
            axs[i][0].set_ylabel("Id (mA/mm) at Vg +1 V")
            for a in axs[i]:
                a.title.set_fontsize(10)
                a.tick_params(labelbottom=True)
        fig.suptitle("28 V off-state stress (Vg −10 V) plus 0–3 ion strikes, model output", fontsize=12, x=0.01, ha="left")
        fig.tight_layout()
        fig.savefig(f"{prefix}_deliverable.png", dpi=170)
        print("wrote", f"{prefix}_deliverable.png")


if __name__ == "__main__":
    main(*sys.argv[1:])
