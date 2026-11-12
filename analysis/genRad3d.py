"""Parameter files for the 3D slice studies (kb/model/3d-plan.md). Run from the repo root.
usage: python3 analysis/genRad3d.py
"""
import json

PRE = "polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100;radState=pre"
D3 = "deviceDeck=rfdevice3d.tcl;deviceDim=3"


def write(name, rows):
    with open(f"sweeps/params_{name}.txt", "w") as f:
        for lab, lev in rows:
            f.write(f"{lab}|{lev}\n")
    print(name, len(rows))


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
        sv = max(L["sigma_nm"] / 1e3 if L["sigma_nm"] == L["sigma_nm"] else 0.0, sigma_vac_floor)
        nv = L["vac_per_nm"] * 1e7 / (2 * 3.141592653589793 * (sv * 1e-4) ** 2) * eta
        out.append((y, z, sv, x0, x1, nv))
        if core_scale > 0 and L["Se_eV_per_A"]:
            out.append((y, z, sigma_core, x0, x1, core_scale * L["Se_eV_per_A"] * eta))
    return "damTube={" + " ".join("{" + " ".join(f"{v:.6g}" for v in t) + "}" for t in out) + "}"


# ---- Phase C.1: does the 3D deck build? pre-irradiation, short Id-Vd at Vg +1, coarsened base mesh
B = f"{PRE};{D3};bot3d=1.5;yCoarse=2;W3d=0.5;doIdVg=0;Vd_max=1.0;Vd_step=0.25;noRampBack=1"
rows = [("hk_nz3", f"{B};zSpac0=0.25;zSpac1=0.25"),
        ("hk_nz5", f"{B};zSpac0=0.125;zSpac1=0.125"),
        ("hk_nz11", f"{B};zSpac0=0.05;zSpac1=0.05"),
        ("hk_nz5_gas", f"{B};zSpac0=0.125;zSpac1=0.125;init3d={{quad}}"),
        ("hk_nz5_tet", f"{B};zSpac0=0.125;zSpac1=0.125;init3d={{}}"),
        ("sin_nz5", f"{B};zSpac0=0.125;zSpac1=0.125;passMat=Nitride")]
write("rad3dBuild", rows)

# ---- Phase C/D (2026-11-12): UMFPACK fails at 5+ z lines (about 85k points); try the iterative solvers.
# Validate the 3-line deck against the 2D decks with the same coarsening (bot 1.5 um, y spacing x2).
VAL = f"{PRE};doIdVg=1;Vd_max=10.0;Vd_step=0.25;noRampBack=1"
C3 = f"{D3};bot3d=1.5;yCoarse=2;W3d=0.5"
rows = [("hk_nz5_bcgs", f"{B};zSpac0=0.125;zSpac1=0.125;mathDev3d={{row ilu bcgs scale}}"),
        ("hk_nz5_gmres", f"{B};zSpac0=0.125;zSpac1=0.125;mathDev3d={{col ilu gmres scale}}"),
        ("hk_nz11_bcgs", f"{B};zSpac0=0.05;zSpac1=0.05;mathDev3d={{row ilu bcgs scale}}"),
        ("hk3d_nz3_val", f"{VAL};{C3};zSpac0=0.25;zSpac1=0.25"),
        ("sin3d_nz3_val", f"{VAL};{C3};zSpac0=0.25;zSpac1=0.25;passMat=Nitride"),
        ("hk2d_coarse", f"{VAL};bot2d=1.5;yCoarse=2"),
        ("sin2d_coarse", f"{VAL};deviceDeck=rfdevice_SiN.tcl;bot2d=1.5;yCoarse=2")]
write("rad3dSolve", rows)

# ---- first tracks (2026-11-12): one TRIM track at the SiN overhang (y 0.5 um) on slices 0.25 / 0.5 / 1 um wide.
# Core sigma 30 nm (resolvable with 20 nm z spacing at the wall; nm-scale cores come later with the mesh study),
# core density 5e15 * Se(eV/A) * eta, about 2e19 cm^-3 in GaN at eta 1; TRIM vacancies spread to 20 nm.
# Post state, no stress solve, hotEb 1.0 as the final model. BiCGSTAB (UMFPACK fails above ~50k points).
POST = ("polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100;radState=post;hotEb=1.0;hotTau=1e-14;"
        "damXmax=0.05;damMax=1e20;trapLevel=0.30;damField=lat;damEref=5.0e5;damM=4;damYmin=0.30;retryDepth=8;"
        "stressSkip=1;noRampBack=1;doIdVg=0;Vd_max=6.0;Vd_step=0.25")
T3 = f"{D3};bot3d=1.5;yCoarse=2;passMat=Nitride;zSpac0=0.02;mathDev3d={{row ilu bcgs scale}}"
rows = [("umf_nz5_128g", f"{B};zSpac0=0.125;zSpac1=0.125")]
for w in (0.25, 0.5, 1.0):
    tb = tubes("SiN", 0.5, 0.0, 1.0, 0.03, 5e15, sigma_vac_floor=0.02)
    rows.append((f"sin_trk_W{w:g}", f"{POST};{T3};W3d={w:g};zSpac1={min(0.1, w / 4):g};{tb}"))
write("rad3dTrack1", rows)
