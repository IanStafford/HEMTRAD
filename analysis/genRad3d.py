"""Write the sweeps/params_<name>.txt files of the 3D slice studies (kb/model/3d-plan.md).

usage (from the repo root):
  python3 analysis/genRad3d.py                 write new params files; refuse to change tracked ones
  python3 analysis/genRad3d.py --check         write nothing; list files that would be created or changed
  python3 analysis/genRad3d.py --force NAME    let study NAME's tracked file change (repeatable)
  python3 analysis/genRad3d.py --show NAME [TASK]
                                               print each line's effective levers (last value wins) and
                                               their differences from the study's base

Same rail as analysis/genRadStudy.py (analysis/radparams.py): a file is written only when it is new or its
content is unchanged; a tracked file that would change is left alone, its diff printed, exit 1 at the end.

Studies (STUDIES, in order; all for drivers/radIV.tcl through sweeps/radIV.slurm):
  rad3dBuild   Phase C.1: does the 3D deck build?
  rad3dSolve   2026-11-12: iterative solvers, and the 3-line deck against the 2D decks
  rad3dTrack1  2026-11-12: one TRIM track (damTube columns from data/trim/SiN_track.json)
  rad3dRod     2026-11-17: ion tracks along the gate width (damRod)
3D runs need the brick-gradient fix (CLAUDE.md section 6, kb/model/3d-plan.md).
"""
import json
import sys

from radparams import DAM2_GATE, DAM_LAW, HOT_TAU, POST, PRE, SIN_DECK, SKIP, SURF, Study, gauss, run

D3 = "deviceDeck=rfdevice3d.tcl;deviceDim=3"
# Phase C.1 build test (11-12): pre-irradiation, short Id-Vd at Vg +1, coarsened base mesh.
BUILD3D_1112 = f"{PRE};{D3};bot3d=1.5;yCoarse=2;W3d=0.5;doIdVg=0;Vd_max=1.0;Vd_step=0.25;noRampBack=1"
# Track-only post state (11-12): the Nov 11 damage law and hotEb 1.0, no stress solve.
POST_TRACK_1112 = (f"{POST};hotEb=1.0;{HOT_TAU};{DAM_LAW};retryDepth=8;{SKIP};noRampBack=1;doIdVg=0;Vd_max=6.0;"
                   "Vd_step=0.25")
# The 28 V stress of the final model with damage scale 2e18 and the gate site (11-17, rad3dRod).
STRESS28_1117 = (f"{POST};{SURF};hotEb=1.0;{HOT_TAU};{DAM_LAW};damPeak=2e18;{DAM2_GATE};noRampBack=1;retryDepth=8;"
                 "occSafe=1;Vd_stress=28.0;doIdVg=0;Vd_max=6.0;Vd_step=0.25")
# SiN slice for the tracks: BiCGSTAB (UMFPACK fails above ~50k points), 20 nm z spacing at the z = 0 wall.
T3 = f"{D3};bot3d=1.5;yCoarse=2;passMat=Nitride;zSpac0=0.02;mathDev3d={{row ilu bcgs scale}}"


def tubes(deck, y, z, eta, sigma_core, core_scale, sigma_vac_floor=0.002):
    """Track columns from data/trim/<deck>_track.json: per layer, a vacancy tube (TRIM vacancies per nm, radial
    Gaussian of width max(TRIM sigma, floor)) times eta, plus an electronic-track core of width sigma_core whose
    density is core_scale * Se (eV/A) * eta. Depths are converted to device x (AlGaN top = 0)."""
    j = json.load(open(f"data/trim/{deck}_track.json"))
    top = [L for L in j["layers"] if L["layer"] == "AlGaN"][0]["depth_nm"][0]
    out = []
    for L in j["layers"]:
        if L["layer"] in ("HfO2", "Si3N4", "GaN"):
            continue
        x0, x1 = (L["depth_nm"][0] - top) / 1e3, (L["depth_nm"][1] - top) / 1e3
        sv = max(L["sigma_nm"] / 1e3 if L["sigma_nm"] == L["sigma_nm"] else 0.0, sigma_vac_floor)   # NaN sigma -> floor
        nv = L["vac_per_nm"] * 1e7 / (2 * 3.141592653589793 * (sv * 1e-4) ** 2) * eta
        out.append((y, z, sv, x0, x1, nv))
        if core_scale > 0 and L["Se_eV_per_A"]:
            out.append((y, z, sigma_core, x0, x1, core_scale * L["Se_eV_per_A"] * eta))
    return "damTube={" + " ".join("{" + " ".join(f"{v:.6g}" for v in t) + "}" for t in out) + "}"


def rad3dBuild():
    """Phase C.1: does the 3D deck build? z line counts, the initial-guess variants and the SiN slice."""
    B = BUILD3D_1112
    return [("hk_nz3", f"{B};zSpac0=0.25;zSpac1=0.25"),
            ("hk_nz5", f"{B};zSpac0=0.125;zSpac1=0.125"),
            ("hk_nz11", f"{B};zSpac0=0.05;zSpac1=0.05"),
            ("hk_nz5_gas", f"{B};zSpac0=0.125;zSpac1=0.125;init3d={{quad}}"),
            ("hk_nz5_tet", f"{B};zSpac0=0.125;zSpac1=0.125;init3d={{}}"),
            ("sin_nz5", f"{B};zSpac0=0.125;zSpac1=0.125;passMat=Nitride")]


def rad3dSolve():
    """Phase C/D (2026-11-12): UMFPACK fails at 5+ z lines (about 85k points); try the iterative solvers.
    Validate the 3-line deck against the 2D decks with the same coarsening (bot 1.5 um, y spacing x2)."""
    B = BUILD3D_1112
    val = f"{PRE};doIdVg=1;Vd_max=10.0;Vd_step=0.25;noRampBack=1"
    c3 = f"{D3};bot3d=1.5;yCoarse=2;W3d=0.5"
    return [("hk_nz5_bcgs", f"{B};zSpac0=0.125;zSpac1=0.125;mathDev3d={{row ilu bcgs scale}}"),
            ("hk_nz5_gmres", f"{B};zSpac0=0.125;zSpac1=0.125;mathDev3d={{col ilu gmres scale}}"),
            ("hk_nz11_bcgs", f"{B};zSpac0=0.05;zSpac1=0.05;mathDev3d={{row ilu bcgs scale}}"),
            ("hk3d_nz3_val", f"{val};{c3};zSpac0=0.25;zSpac1=0.25"),
            ("sin3d_nz3_val", f"{val};{c3};zSpac0=0.25;zSpac1=0.25;passMat=Nitride"),
            ("hk2d_coarse", f"{val};bot2d=1.5;yCoarse=2"),
            ("sin2d_coarse", f"{val};{SIN_DECK};bot2d=1.5;yCoarse=2")]


def rad3dTrack1():
    """First tracks (2026-11-12): one TRIM track at the SiN overhang (y 0.5 um) on slices 0.25 / 0.5 / 1 um wide.
    Core sigma 30 nm (resolvable with 20 nm z spacing at the wall; nm-scale cores come later with the mesh
    study), core density 5e15 * Se(eV/A) * eta, about 2e19 cm^-3 in GaN at eta 1; TRIM vacancies spread to
    20 nm. Post state, no stress solve, hotEb 1.0 as the final model."""
    tb = tubes("SiN", 0.5, 0.0, 1.0, 0.03, 5e15, sigma_vac_floor=0.02)
    rows = [("umf_nz5_128g", f"{BUILD3D_1112};zSpac0=0.125;zSpac1=0.125")]
    rows += [(f"sin_trk_W{w:g}", f"{POST_TRACK_1112};{T3};W3d={w:g};zSpac1={min(0.1, w / 4):g};{tb}")
             for w in (0.25, 0.5, 1.0)]
    return rows


def rad3dRod():
    """2026-11-17 (Ian): ion tracks along the gate width ("into the page" of the 2D cross-section), damRod. The
    track is the 2D strike spot (Gaussian 3e18 cm^-3, sigma 40 nm, at the AlGaN top, y 0.8 um) run along z
    from the z = 0 wall for the full slice (W3d 0.5 um: the 2D strike by symmetry), half or a quarter of it.
    SiN deck. Track only (no stress, like rad3dTrack1) and on the final model's stress damage (28 V, damage
    scale 2e18, occSafe). 2D references on the same coarsening (bot2d 1.5, yCoarse 2) and the same y
    refinement."""
    rod = "{{0.8 0.0 0.04 0 %g 3e18}}"
    w = 0.5
    t3r = f"{T3};W3d={w:g};zSpac1=0.1"
    my_trk = "meshY={0.64 0.01 0.96 0.01}"
    my_str = "meshY={0.3 0.01 2.6 0.01 0.64 0.005 0.96 0.005}"
    c2 = f"{SIN_DECK};bot2d=1.5;yCoarse=2"
    strike2d = gauss([(0.8, "3e18")])
    rows = [(f"rod_{lab}", f"{POST_TRACK_1112};{t3r};{my_trk};damRod={rod % length}{mz}")
            for lab, length, mz in (("full", w, ""), ("half", w / 2, f";meshZ={{{w / 2:g} 0.01}}"),
                                    ("quarter", w / 4, f";meshZ={{{w / 4:g} 0.01}}"))]
    rows.append(("rod_2dref", f"{POST_TRACK_1112};{c2};{my_trk}{strike2d}"))
    rows.append(("s28_3d_none", f"{STRESS28_1117};{t3r};{my_str}"))
    rows.append(("s28_3d_half", f"{STRESS28_1117};{t3r};{my_str};damRod={rod % (w / 2)};meshZ={{{w / 2:g} 0.01}}"))
    rows.append(("s28_2d_none", f"{STRESS28_1117};{c2};{my_str}"))
    rows.append(("s28_2d_strike", f"{STRESS28_1117};{c2};{my_str}{strike2d}"))
    return rows


STUDIES = [
    Study("rad3dBuild", rad3dBuild, base=("BUILD3D_1112", BUILD3D_1112)),
    Study("rad3dSolve", rad3dSolve, base=("BUILD3D_1112", BUILD3D_1112)),
    Study("rad3dTrack1", rad3dTrack1, base=("POST_TRACK_1112", POST_TRACK_1112)),
    Study("rad3dRod", rad3dRod, base=("POST_TRACK_1112", POST_TRACK_1112)),
]

if __name__ == "__main__":
    sys.exit(run(STUDIES, __doc__))
