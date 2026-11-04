"""Write the sweeps/params_<name>.txt files of the 2026-11 damage-region and Vth studies.
usage: python3 analysis/genRadStudy.py   (run from the repo root; the task order is fixed)
Sites are {ymin ymax xmin xmax N}: um along the channel, um below the AlGaN top, cm^-3.
"""
import random

BASE = ("polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100;radState=post;"
        "hotEb=0.5;hotTau=1e-14;damXmax=0.05;damMax=1e20;trapLevel=0.30;damField=lat;damEref=5.0e5;damM=4;damYmin=0.30;"
        "retryDepth=8")
SKIP = "stressSkip=1"
DECKS = (("hk", ""), ("sin", "deviceDeck=rfdevice_SiN.tcl"))
YSRC, YDRN = -1.25, 3.41   # mesh edges


def sites(*s):
    return "damSites={" + " ".join("{" + " ".join(f"{v:g}" for v in q) + "}" for q in s) + "}"


def write(name, cases):
    with open(f"sweeps/params_{name}.txt", "w") as f:
        for lab, lev in cases:
            for d, dl in DECKS:
                extra = ";".join(x for x in (BASE, dl, lev) if x)
                f.write(f"{d}_{lab}|{extra}\n")
    print(name, 2 * len(cases))


def sitecase(*s):
    return f"{SKIP};{sites(*s)}"


# ---- checks: same cases as radFinal8 nb / radFinal pre through the new code paths
NB = ("polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100;radState=post;surfCharge=-4.0e11;hotEb=1.0;"
      "hotTau=1e-14;damXmax=0.05;damMax=1e20;trapLevel=0.30;damField=lat;damEref=5.0e5;damM=4;damYmin=0.30;damPeak=0.0;hotEb=0.5")
DAM2 = "dam2Field=lat;dam2M=0;dam2Ymin=-0.125;dam2Ymax=0.125;dam2Peak=5e17;dam2Xmax=0.014"
with open("sweeps/params_radChk.txt", "w") as f:
    for d, dl in (("highk", ""), ("sin", "deviceDeck=rfdevice_SiN.tcl")):
        pre = "polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100;radState=pre"
        f.write(f"pre_{d}|" + ";".join(x for x in (pre, dl) if x) + "\n")
        f.write(f"nb_{d}_skip|" + ";".join(x for x in (NB, dl, SKIP, DAM2) if x) + "\n")
        f.write(f"nb_{d}_sites|" + ";".join(x for x in (NB, dl, SKIP, sites((-0.125, 0.125, 0.0, 0.014, 5e17))) if x) + "\n")
print("radChk 6")

# ---- Phase 2: ways to shift Vth
G = (-0.125, 0.125)
A = (YSRC, YDRN)
cases = [("ref", "")]
cases += [(f"phiB{v:g}", f"phiB={v:g}") for v in (3.04, 3.14, 3.24)]
cases += [(f"surf{v:g}", f"surfCharge={v:g}") for v in (-2e11, -4e11, -8e11, -1.2e12)]
cases += [(f"polAll{v:g}", f"polCharge={v:g}") for v in (9.7e12, 9.5e12, 9.0e12)]
cases += [(f"polGate{v:g}", f"polWinFac={v:g};polWinYmin=-0.125;polWinYmax=0.125") for v in (0.97, 0.95, 0.90)]
cases += [(f"algGate{n:g}", sitecase((*G, 0.0, 0.014, n))) for n in (2e17, 5e17, 1e18)]
cases += [(f"algAll{n:g}", sitecase((*A, 0.0, 0.014, n))) for n in (2e17, 5e17, 1e18)]
cases += [(f"chGate{n:g}", sitecase((*G, 0.015, 0.05, n))) for n in (1e17, 5e17, 2e18)]
cases += [(f"chAll{n:g}", sitecase((*A, 0.015, 0.05, n))) for n in (1e17, 5e17, 2e18)]
cases += [(f"buf{n:g}", sitecase((*A, 0.1, 1.4, n))) for n in (1e16, 1e17, 5e17)]
cases += [(f"ins{n:g}", f"{SKIP};insTrapSign=-1;damInsPeak={n:g};damInsM=0;damInsXmin=-0.05") for n in (1e17, 5e17, 1e18)]
write("radVth", cases)

# ---- Phase 3a: one site, position map (width 0.3 um, top 50 nm)
Y = [(-1.05, -0.75), (-0.75, -0.45), (-0.45, -0.15), (-0.15, 0.15)] + [(0.15 + 0.3 * i, 0.45 + 0.3 * i) for i in range(10)]
cases = [("ref", "")]
for n in (1e18, 4e18):
    cases += [(f"y{(a + b) / 2:.2f}_n{n:g}", sitecase((a, b, 0.0, 0.05, n))) for a, b in Y]
write("radMap1", cases)
