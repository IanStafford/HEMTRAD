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
