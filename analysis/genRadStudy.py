"""Write the sweeps/params_<name>.txt files of the 2026-11 damage-region and Vth studies.
usage: python3 analysis/genRadStudy.py   (run from the repo root; the task order is fixed)
Sites are {ymin ymax xmin xmax N}: um along the channel, um below the AlGaN top, cm^-3.
"""
import random

BASE = ("polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100;radState=post;"
        "hotEb=0.5;hotTau=1e-14;damXmax=0.05;damMax=1e20;trapLevel=0.30;damField=lat;damEref=5.0e5;damM=4;damYmin=0.30;"
        "retryDepth=8;noRampBack=1")
SKIP = "stressSkip=1"
DECKS = (("hk", ""), ("sin", "deviceDeck=rfdevice_SiN.tcl"))
YSRC, YDRN = -1.25, 3.41   # mesh edges


def sites(*s):
    return "damSites={" + " ".join("{" + " ".join(f"{v:g}" for v in q) + "}" for q in s) + "}"


def write(name, cases, common=""):
    with open(f"sweeps/params_{name}.txt", "w") as f:
        for lab, lev in cases:
            for d, dl in DECKS:
                extra = ";".join(x for x in (BASE, common, dl, lev) if x)
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
# Vth, gm, Ron and low-field current only, so stop before the high-Vd retries (about 1 h per task)
write("radVth", cases, "Vd_max=5.0")

# ---- Phase 3a: one site, position map (width 0.3 um, top 50 nm)
Y = [(-1.05, -0.75), (-0.75, -0.45), (-0.45, -0.15), (-0.15, 0.15)] + [(0.15 + 0.3 * i, 0.45 + 0.3 * i) for i in range(10)]
cases = [("ref", "")]
for n in (1e18, 4e18):
    cases += [(f"y{(a + b) / 2:.2f}_n{n:g}", sitecase((a, b, 0.0, 0.05, n))) for a, b in Y]
write("radMap1", cases)


# ---- explicit deck lists for the follow-up studies
def writex(name, cases, common=""):
    """cases: (deck, label, levers); deck is 'hk' or 'sin'."""
    dl = dict(DECKS)
    with open(f"sweeps/params_{name}.txt", "w") as f:
        for d, lab, lev in cases:
            extra = ";".join(x for x in (BASE, common, dl[d], lev) if x)
            f.write(f"{d}_{lab}|{extra}\n")
    print(name, len(cases))


def fine(y0, y1, sp):
    return f"meshY={{{y0:g} {sp:g} {y1:g} {sp:g}}}"


# ---- do the steps survive a finer mesh? same sites as radMap1, 10 and 5 nm across the site
MS = {"y3.00": (2.85, 3.15), "y1.50": (1.35, 1.65), "y-0.90": (-1.05, -0.75)}
cases = []
for lab, (a, b) in MS.items():
    for sp, sl in ((0.01, "m10"), (0.005, "m05")):
        cases.append(("hk", f"{lab}_{sl}", sitecase((a, b, 0.0, 0.05, 4e18)) + ";" + fine(a, b, sp)))
a, b = MS["y3.00"]
cases.append(("sin", "y3.00_m05", sitecase((a, b, 0.0, 0.05, 4e18)) + ";" + fine(a, b, 0.005)))
cases.append(("hk", "y3.00_step0.1", sitecase((a, b, 0.0, 0.05, 4e18)) + ";Vd_step=0.1"))
# a 0.1 um site with the same total charge, the width most exposed to the mesh
n01 = (1.45, 1.55, 0.0, 0.05, 1.2e19)
cases.append(("hk", "w0.1", sitecase(n01)))
for sp, sl in ((0.01, "m10"), (0.005, "m05")):
    cases.append(("hk", f"w0.1_{sl}", sitecase(n01) + ";" + fine(1.45, 1.55, sp)))
writex("radMesh", cases)

# ---- Vg family on SiN (R33 is SiN): is the current after a step independent of Vg?
S4 = lambda a, b: (a, b, 0.0, 0.05, 4e18)
cases = [("sin", "ref", ""),
         ("sin", "y-0.90", sitecase(S4(-1.05, -0.75))),
         ("sin", "y1.50", sitecase(S4(1.35, 1.65))),
         ("sin", "y3.00", sitecase(S4(2.85, 3.15))),
         ("sin", "3sites", sitecase(S4(1.05, 1.35), S4(1.95, 2.25), S4(2.85, 3.15))),
         ("sin", "ins1e18", f"{SKIP};insTrapSign=-1;damInsPeak=1e18;damInsM=0;damInsXmin=-0.05"),
         ("sin", "nb", f"surfCharge=-4.0e11;{SKIP};{sites((-0.125, 0.125, 0.0, 0.014, 5e17))}")]
writex("radFam", cases, "VgFam={-2 -1.5 -1 -0.5 0 0.5}")

# ---- Vth, second pass: the first buffer and dielectric cases could not act
# A level 0.30 eV below Ec stays empty in the buffer, so those traps carry no charge: repeat
# with deep levels. The first ins cases inherited damYmin = 0.30: repeat with charge at the gate.
cases = []
for lev in (1.0, 1.7):
    cases += [(f"buf{n:g}_L{lev:g}", sitecase((*A, 0.1, 1.4, n)) + f";trapLevel={lev:g}") for n in (1e16, 1e17, 5e17)]
INS = "insTrapSign=-1;damInsM=0;damInsXmin=-0.05"
cases += [(f"insAll{n:g}", f"{SKIP};{INS};damInsPeak={n:g};damYmin=-1.3") for n in (1e17, 5e17, 1e18)]
cases += [(f"insGate{n:g}", f"{SKIP};{INS};damInsPeak={n:g};damYmin=-0.35;damYmax=0.40") for n in (1e17, 5e17, 1e18)]
write("radVth2", cases, "Vd_max=5.0")

# ---- Phase 4: Ron candidates with Ron(Vg), low Vd only
GD = (0.125, 3.285)
SD = (YSRC, -0.125)
cases = [("ref", ""), ("nb", f"surfCharge=-4.0e11;{SKIP};{sites((-0.125, 0.125, 0.0, 0.014, 5e17))}")]
for lab, (a, b) in (("GD", GD), ("SD", SD), ("All", A)):
    cases += [(f"mob{lab}{m:g}", f"mobDamFac={m:g};mobDamYmin={a:g};mobDamYmax={b:g}") for m in (0.8, 0.5, 0.3)]
for lab, w in (("GD", GD), ("SD", SD)):
    cases += [(f"ch{lab}{n:g}", sitecase((*w, 0.015, 0.05, n))) for n in (1e17, 5e17, 2e18)]
cases += [(f"algGD{n:g}", sitecase((*GD, 0.0, 0.014, n))) for n in (5e17, 1e18, 5e18)]
cases += [(f"insGD{n:g}", f"{SKIP};{INS};damInsPeak={n:g}") for n in (1e17, 5e17, 1e18)]
write("radRon", cases, "Vd_max=1.0;VgFam={-2 -1 0}")

# ---- Phase 4: damage that follows the irradiation field at a low exponent, with the stress solve
cases = [(f"f{m}_p{p:g}", f"damM={m};damPeak={p:g}") for m in (1, 2) for p in (5e17, 2e18)]
write("radStress", cases)

# ---- Vth, third pass: charged buffer acceptors (back-gating)
# The model's buffer is undoped, with no electrons to fill a level at 1.0 or 1.7 eV (about 1e-26
# of the traps are charged, checked locally). A level 3.3 eV below Ec is filled there.
cases = [(f"buf{n:g}_L3.3", sitecase((*A, 0.1, 1.4, n)) + ";trapLevel=3.3") for n in (1e15, 1e16, 1e17)]
write("radVth3", cases, "Vd_max=5.0")

# ---- after radMesh: the 0.3 um / 4e18 steps went away at 10 and 5 nm, the 0.1 um site kept a collapse.
# Always 5 nm here unless labelled. Where does a real collapse start, is it converged, and does the
# line after it depend on Vg? Fresh curves use Vg_out (no trap memory); VgFam keeps the traps
# filled by the earlier curves.
M05 = lambda a, b, sp=0.005: fine(a, b, sp)
def site(yc, w, n):
    return (yc - w / 2, yc + w / 2, 0.0, 0.05, n)
def sc(yc, w, n, sp=0.005):
    s = site(yc, w, n)
    return sitecase(s) + ";" + fine(s[0], s[1], sp)
cases = []
for n in (6e18, 8e18, 1.2e19):
    cases.append(("hk", f"y1.5_w0.3_n{n:g}", sc(1.5, 0.3, n)))
for n in (4e18, 6e18, 8e18):
    cases.append(("hk", f"y1.5_w0.1_n{n:g}", sc(1.5, 0.1, n)))
cases.append(("hk", "y1.5_w0.1_n1.2e19_m025", sc(1.5, 0.1, 1.2e19, 0.0025)))
cases.append(("hk", "y3.0_w0.1_n1.2e19", sc(3.0, 0.1, 1.2e19)))
cases.append(("hk", "y-0.9_w0.1_n1.2e19", sc(-0.9, 0.1, 1.2e19)))
FAMV = "VgFam={-2 -1.5 -1 -0.5 0 0.5}"
cases.append(("sin", "fam_y3.0_w0.3_n4e18", sc(3.0, 0.3, 4e18) + ";" + FAMV))
cases.append(("sin", "fam_y1.5_w0.1_n1.2e19", sc(1.5, 0.1, 1.2e19) + ";" + FAMV))
for vg in (-2, -1, 0):
    cases.append(("sin", f"fresh_y1.5_w0.1_n1.2e19_G{vg}", sc(1.5, 0.1, 1.2e19) + f";doIdVg=0;Vg_out={vg}"))
# trap-free family curves that radFam's ref could not finish: an empty trap density gets through
# the same off-state solves. G-1 checks it against the plain ref.
for vg in (-1, -0.5, 0, 0.5):
    cases.append(("sin", f"ref_G{vg}", f"{SKIP};damSites={{{{-1.25 3.41 0 0.05 1}}}};doIdVg=0;Vg_out={vg}"))
# is the final SiN curve's two-step collapse also a mesh effect? radFinal11 set, 10 nm from 0.3 to 1.6 um
FINAL = ("polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100;radState=post;surfCharge=-4.0e11;hotEb=1.0;"
         "hotTau=1e-14;damXmax=0.05;damMax=1e20;trapLevel=0.30;damField=lat;damEref=5.0e5;damM=4;damYmin=0.30;"
         "deviceDeck=rfdevice_SiN.tcl;damPeak=@P;hotEb=0.5;dam2Field=lat;dam2M=0;dam2Ymin=-0.125;dam2Ymax=0.125;dam2Peak=5e17;"
         "dam2Xmax=0.014;dam3Peak=@S;Vd_step=0.1;retryDepth=8;meshY={0.3 0.01 1.6 0.01}")
cases.append(("sin", "final_m10", FINAL.replace("@P", "6e18").replace("@S", "4.5e18")))
writex("radFine", cases)

# ---- Phase 3d: multiple strikes. 0.1 um sites at 1.2e19 (the one site known to collapse on a fine
# mesh), 5 nm in every site. Damage is static, so only the set matters, not the order. No site under
# the gate. Singles give the superposition check; radFine has HighK y 3.0, 1.5 and -0.9.
POOL = [-0.9, -0.6, -0.3, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0]
def multi(ys, n=1.2e19, w=0.1):
    ss = [site(y, w, n) for y in ys]
    lines = " ".join(f"{a:g} 0.005 {b:g} 0.005" for a, b, *_ in ss)
    return sitecase(*ss) + ";meshY={" + lines + "}"
cases = []
for y in POOL:
    for d in ("hk", "sin"):
        if d == "hk" and y in (-0.9, 1.5, 3.0):
            continue
        cases.append((d, f"ms_s_y{y:g}", multi([y])))
DRN = [0.6, 1.2, 1.8, 2.4, 3.0]
GATE = DRN[::-1]
sets = [(f"drn_k{k}", DRN[:k]) for k in range(2, 6)] + [(f"gat_k{k}", GATE[:k]) for k in range(2, 5)]
for seed in (1, 2, 3):
    order = random.Random(seed).sample(POOL, 5)
    print("seed", seed, order)
    sets += [(f"r{seed}_k{k}", sorted(order[:k])) for k in range(2, 6)]
for lab, ys in sets:
    for d in ("hk", "sin"):
        cases.append((d, f"ms_{lab}", multi(ys)))
writex("radMulti", cases)

# ---- trap emission (Ian, 2026-11-05): fill-only and fully fresh are the two extremes tried so far.
# emitFrac: some of the excess charge leaks per capture call. emitRest: some leaks at rest between
# curves, which could leave low Vd normal and then refill onto a line. SiN, 5 nm in the site.
ESITES = (("A", 3.0, 0.3, 4e18), ("B", 1.5, 0.3, 8e18), ("C", 1.5, 0.1, 1.2e19))
cases = []
for lab, y, w, n in ESITES:
    for f in (0.01, 0.03, 0.1, 0.3, 1.0):
        cases.append(("sin", f"site{lab}_ef{f:g}", sc(y, w, n) + f";emitFrac={f:g};doIdVg=0"))
for lab, y, w, n in ESITES[:2]:
    for r in (0.5, 0.9, 0.99):
        cases.append(("sin", f"site{lab}_er{r:g}", sc(y, w, n) + f";emitRest={r:g};doIdVg=0;VgFam={{-1.5 -1 -0.5 0 0.5}}"))
writex("radEmit", cases)

# ---- emitRest again, with TeTrap reset at rest. 1e-9 = charge kept, electrons cold: the memory case.
cases = []
for lab, y, w, n in ESITES[:2]:
    for r in (1e-9, 0.5, 0.9, 0.99):
        cases.append(("sin", f"site{lab}_er{r:g}", sc(y, w, n) + f";emitRest={r:g};doIdVg=0;VgFam={{-1.5 -0.5 0.5}}"))
writex("radEmit2", cases)

# ---- after radEmit2: do site B's drops at emitRest 0.9 survive 2.5 nm, and what happens between
# full memory and 50% released, where low Vd goes from dead to normal?
FAM3 = "doIdVg=0;VgFam={-1.5 -0.5 0.5}"
cases = [("sin", "siteB_er0.9_m025", sc(1.5, 0.3, 8e18, 0.0025) + f";emitRest=0.9;{FAM3}"),
         ("sin", "siteB_er0.99_m025", sc(1.5, 0.3, 8e18, 0.0025) + f";emitRest=0.99;{FAM3}")]
for lab, y, w, n in ESITES[:2]:
    for r in (0.1, 0.2, 0.3):
        cases.append(("sin", f"site{lab}_er{r:g}", sc(y, w, n) + f";emitRest={r:g};{FAM3}"))
writex("radEmit3", cases)

# ---- 2026-11-07: fine-mesh check of what the Oct 29 slides rest on (Ian). Biased curves at 10 nm;
# the fixed Gaussian trap set of job 47062225 at 5 nm through pulsedIV; Gaussians at 0.55 eV.
FB = ("polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100;radState=post;surfCharge=-4.0e11;hotEb=0.5;"
      "hotTau=1e-14;damXmax=0.05;damMax=1e20;trapLevel=0.30;damField=lat;damEref=5.0e5;damM=4;damYmin=0.30;damPeak=7e18;"
      "dam2Field=lat;dam2M=0;dam2Ymin=-0.125;dam2Ymax=0.125;dam2Peak=5e17;dam2Xmax=0.014;noRampBack=1;meshY={0.3 0.01 2.0 0.01}")
with open("sweeps/params_radChk2.txt", "w") as f:
    f.write(f"hk_b_m10|{FB}\n")
    f.write(f"sin_b_m10|{FB};deviceDeck=rfdevice_SiN.tcl\n")
print("radChk2 2")
PI = ("trapEn=1;trapSigma=0.04;trapMeanX=0.0;trapWidth=0.1;hotEb=1.0;hotTau=1e-14;hotMu=600;hotVsat=1.9e7;fillIters=4;"
      "fillRelax=0.5;eTemp=0;Vg_meas=1.0;Vd_max=10.0;Vd_step=0.1;dampValue=0.05;mobModel=field")
def gcase(lab, deck, y, peak, lev, sp):
    m = f";meshY={{{y - 0.16:g} {sp:g} {y + 0.16:g} {sp:g}}}" if sp else ""
    return f"{lab}|{PI};deviceDeck={deck};trapMeanY={y:g};trapPeak={peak:g};trapLevel={lev:g};ivCSV=pulsedIV_{lab}.csv{m}\n"
with open("sweeps/params_radGauss.txt", "w") as f:
    for y in (1.0, 2.4):
        f.write(gcase(f"hk_y{y:g}_L0.3_m05", "rfdevice.tcl", y, 5e18, 0.30, 0.005))
        f.write(gcase(f"sin_y{y:g}_L0.3_m05", "rfdevice_SiN.tcl", y, 5e18, 0.30, 0.005))
        f.write(gcase(f"hk_y{y:g}_L0.55", "rfdevice.tcl", y, 4e18, 0.55, 0))
        f.write(gcase(f"hk_y{y:g}_L0.55_m05", "rfdevice.tcl", y, 4e18, 0.55, 0.005))
print("radGauss 8")
# ---- refined position map: radMap1's 14 windows at 5 nm, including under the gate
cases = []
for n in (4e18, 8e18):
    for a, b in Y:
        cases.append((f"y{(a + b) / 2:.2f}_n{n:g}", sitecase((a, b, 0.0, 0.05, n)) + ";" + fine(a, b, 0.005)))
write("radMap2", cases)

# ---- after radGauss: Gaussian traps at hotEb 1.0 collapse abruptly at 5 nm, unlike the uniform sites at
# hotEb 0.5. Is it converged, is it the shape or the barrier, and does the onset move with Vg?
def g2(lab, deck, y, lev, sp, extra="", half=0.16, peak=None):
    m = f";meshY={{{y - half:g} {sp:g} {y + half:g} {sp:g}}}"
    pk = peak if peak else (5e18 if lev == 0.30 else 4e18)
    return f"{lab}|{PI};deviceDeck={deck};trapMeanY={y:g};trapPeak={pk:g};trapLevel={lev:g};ivCSV=pulsedIV_{lab}.csv{m}{extra}\n"
H, N = "rfdevice.tcl", "rfdevice_SiN.tcl"
with open("sweeps/params_radGauss2.txt", "w") as f:
    f.write(g2("hk_L0.3_m025", H, 1.0, 0.30, 0.0025))
    f.write(g2("hk_L0.55_m025", H, 1.0, 0.55, 0.0025))
    f.write(g2("hk_L0.3_eb0.5", H, 1.0, 0.30, 0.005, ";hotEb=0.5"))
    f.write(g2("hk_L0.3_s0.1", H, 1.0, 0.30, 0.005, ";trapSigma=0.1", half=0.35))
    for vg in (-1.5, -0.5, 0):
        f.write(g2(f"sin_L0.3_G{vg:g}", N, 1.0, 0.30, 0.005, f";Vg_meas={vg:g}"))
print("radGauss2 7")

# ---- 2026-11-09 (Ian OK, test only): the final parameter set with the capture barrier at 1.0 eV
# instead of 0.5, 10 nm over y 0.3-2.0. A Gaussian collapses on a fine mesh at 1.0 but not at 0.5.
EB = ";Vd_step=0.1;retryDepth=8"
with open("sweeps/params_radEB1.txt", "w") as f:
    f.write(f"hk_b_eb1|{FB};hotEb=1.0{EB}\n")
    f.write(f"sin_b_eb1|{FB};deviceDeck=rfdevice_SiN.tcl;hotEb=1.0{EB}\n")
    f.write(f"sin_b_eb0.75|{FB};deviceDeck=rfdevice_SiN.tcl;hotEb=0.75{EB}\n")
    f.write(f"sin_final_eb1|{FINAL.replace('@P', '6e18').replace('@S', '4.5e18').replace('meshY={0.3 0.01 1.6 0.01}', 'meshY={0.3 0.01 2.0 0.01}')};noRampBack=1;hotEb=1.0\n")
    for d, dl in (("highk", ""), ("sin", ";deviceDeck=rfdevice_SiN.tcl")):
        f.write(f"nb_{d}_eb1|{NB}{dl};{SKIP};{DAM2};noRampBack=1;hotEb=1.0{EB}\n")
print("radEB1 6")

# ---- radEB1 showed SiN drops at hotEb 1.0 on 10 nm; check them at 5 nm before they count
with open("sweeps/params_radEB2.txt", "w") as f:
    f.write(f"sin_b_eb1_m05|{FB};deviceDeck=rfdevice_SiN.tcl;hotEb=1.0{EB};meshY={{0.3 0.005 2.0 0.005}}\n")
    f.write(f"sin_final_eb1_m05|{FINAL.replace('@P', '6e18').replace('@S', '4.5e18').replace('meshY={0.3 0.01 1.6 0.01}', 'meshY={0.3 0.005 2.0 0.005}')};noRampBack=1;hotEb=1.0\n")
print("radEB2 2")

# ---- final rad model from 2026-11-11 (Ian): hotEb 1.0, 10 nm over y 0.3-2.0, one damage law for all devices,
# no hand-placed second site. Same inputs as radChk (pre) and radEB1 (nb, b), so those runs are its results.
with open("sweeps/params_radFinal12.txt", "w") as f:
    for line in open("sweeps/params_radChk.txt"):
        if line.startswith("pre_"):
            f.write(line)
    for line in open("sweeps/params_radEB1.txt"):
        lab = line.split("|")[0]
        if lab in ("hk_b_eb1", "sin_b_eb1"):
            # the stress stopped at 17 V in these runs (old occupancy overflow); say so explicitly
            f.write(line.rstrip("\n") + ";Vd_stress=17.0\n")
        elif lab in ("nb_highk_eb1", "nb_sin_eb1"):
            f.write(line)
print("radFinal12 6")

# ---- 2026-11-11 exploration from the new final set (hotEb 1.0): onset too early, no converged second
# step, current recovers after the drop. Damage scale, trap level, and a smooth (Gaussian) second strike.
FE = f"{FB};hotEb=1.0;Vd_step=0.1;retryDepth=8"
SINd = ";deviceDeck=rfdevice_SiN.tcl"
def gm(y):
    return f";meshY={{0.3 0.01 2.6 0.01 {y - 0.16:g} 0.005 {y + 0.16:g} 0.005}}"
with open("sweeps/params_radExp1.txt", "w") as f:
    for p in (4.5e18, 3e18, 2e18):
        f.write(f"sin_p{p:g}|{FE}{SINd};damPeak={p:g}\n")
    for lev in (0.40, 0.50):
        f.write(f"hk_L{lev:g}|{FE};trapLevel={lev:g}\n")
        f.write(f"sin_L{lev:g}|{FE}{SINd};trapLevel={lev:g}\n")
    for d, dl, y, n in (("sin", SINd, 1.5, 5e18), ("sin", SINd, 1.5, 3e18), ("sin", SINd, 2.4, 5e18), ("hk", "", 1.5, 5e18)):
        f.write(f"{d}_g{y:g}_n{n:g}|{FE}{dl};damGauss={{{{{y:g} 0.0 0.04 {n:g}}}}}{gm(y)}\n")
print("radExp1 11")

# ---- radExp1's SiN deep-level tasks overflowed in the trap occupancy ramping down from the stress
# (the Oct 29 exp() overflow, reached sooner with a deeper level). occSafe is the exact overflow-free form.
with open("sweeps/params_radExp1b.txt", "w") as f:
    for lev in (0.40, 0.50):
        f.write(f"sin_L{lev:g}_os|{FE}{SINd};trapLevel={lev:g};occSafe=1;Vd_stress=17.0\n")
print("radExp1b 2")

# ---- after radExp1/1c (2026-11-12). From here every stressed run uses occSafe with the stress pinned at 17 V
# (occSafe is exact; without it the Gaussian SiN stresses stalled or overflowed near 17 V).
FO = f"{FE};occSafe=1;Vd_stress=17.0"
with open("sweeps/params_radExp2.txt", "w") as f:
    for y, n in ((1.5, 5e18), (1.5, 3e18), (2.4, 5e18)):
        f.write(f"sin_g{y:g}_n{n:g}|{FO}{SINd};damGauss={{{{{y:g} 0.0 0.04 {n:g}}}}}{gm(y)}\n")
    for p in (5e18, 5.5e18, 6e18):
        f.write(f"sin_p{p:g}|{FO}{SINd};damPeak={p:g}\n")
    for lev, p in ((0.5, 3e18), (0.5, 5e18), (0.4, 5e18)):
        f.write(f"sin_L{lev:g}_p{p:g}|{FO}{SINd};trapLevel={lev:g};damPeak={p:g}\n")
print("radExp2 9")

# ---- 2026-11-12 (Ian: more tests aimed at the measured data), from the final set with occSafe and 17 V
# (a) later onset: cooler hot electrons (hotTau); (b) stress at the real 28 V, where the field widens and may
# place damage in two regions; (c) onset against Vg for the final SiN curve, fresh curves; (d) Ron(Vg) at low Vd,
# biased against non-biased, both decks.
with open("sweeps/params_radExp3.txt", "w") as f:
    for tau in (5e-15, 7e-15):
        f.write(f"sin_tau{tau:g}|{FO}{SINd};hotTau={tau:g}\n")
    for d, dl, p in (("sin", SINd, 1.5e18), ("sin", SINd, 2.5e18), ("hk", "", 2.5e18)):
        f.write(f"{d}_s28_p{p:g}|{FO}{dl};Vd_stress=28.0;damPeak={p:g};meshY={{0.3 0.01 2.6 0.01}}\n")
    for vg in (-1, 0, 0.5):
        f.write(f"sin_G{vg:g}|{FO}{SINd};doIdVg=0;Vg_out={vg:g}\n")
    RV = ";Vd_max=1.0;VgFam={-2 -1 0};noRampBack=0"
    f.write(f"hk_b_ron|{FO}{RV}\n")
    f.write(f"sin_b_ron|{FO}{SINd}{RV}\n")
    for d, dl in (("highk", ""), ("sin", SINd)):
        f.write(f"nb_{d}_ron|{NB}{dl};{SKIP};{DAM2};hotEb=1.0{RV}\n")
print("radExp3 12")

# ---- 2026-11-12 (Ian): final model at higher drain voltage, Id-Vd to 28 V at Vg +1 and 0. occSafe keeps the
# occupancy from overflowing above ~17.7 V during the measurement too (exact form, same results below that).
HV = ";Vd_max=28.0;Vd_step=0.2;VgFam={0};noRampBack=0;occSafe=1"
with open("sweeps/params_radHV.txt", "w") as f:
    for line in open("sweeps/params_radFinal12.txt"):
        lab, lev = line.rstrip("\n").split("|", 1)
        f.write(f"{lab}_hv|{lev}{HV}\n")
print("radHV 6")

# ---- 2026-11-12 (Ian): how does the second strike's position set the Vd of the second dip? The one-site final
# curve already dips (393 at 6.3 V to 333 at 7.7 V, 5 nm). Smooth second strike (sigma 40 nm, 3e18) along the
# drift region on the final SiN set, plus the final set with its field-placed damage cut off past y 1.0 and 0.7 um
# to find where the existing dip comes from.
def gm2(y):
    top = max(2.6, y + 0.2)
    return f";meshY={{0.3 0.01 {top:g} 0.01 {y - 0.16:g} 0.005 {y + 0.16:g} 0.005}}"
with open("sweeps/params_radStrike2.txt", "w") as f:
    for y in (0.8, 1.2, 2.0, 2.4, 2.8, 3.1):
        f.write(f"sin_s2_y{y:g}|{FO}{SINd};damGauss={{{{{y:g} 0.0 0.04 3e18}}}}{gm2(y)}\n")
    for ym in (1.0, 0.7):
        f.write(f"sin_cut{ym:g}|{FO}{SINd};damYmax={ym:g}\n")
print("radStrike2 8")

# ---- 2026-11-12 (Ian): the final model moves to a 28 V stress. Refit the damage scale at 28 V on the final set
# (hotEb 1.0, occSafe, 10 nm over y 0.3-2.6). radExp3 already has SiN 1.5e18 / 2.5e18 and HighK 2.5e18.
F28 = f"{FE};occSafe=1;Vd_stress=28.0;meshY={{0.3 0.01 2.6 0.01}}"
with open("sweeps/params_rad28fit.txt", "w") as f:
    for p in (1e18, 2e18, 3e18, 4e18):
        f.write(f"sin_s28_p{p:g}|{F28}{SINd};damPeak={p:g}\n")
    for p in (1.5e18, 4e18):
        f.write(f"hk_s28_p{p:g}|{F28};damPeak={p:g}\n")
print("rad28fit 6")

# ---- 2026-11-13 (Ian): slides comparing 1, 2 and 3 ion strikes in SiN and HighK. Final set (17 V stress,
# hotEb 1.0, occSafe), biased, plus N Gaussian strikes (sigma 40 nm, 3e18, at the AlGaN top) at y 0.8, 1.6, 2.4 um,
# added in that order. N = 0 is rerun on the same mesh (10 nm over y 0.3-2.6, 5 nm within 0.16 um of each strike).
SY = (0.8, 1.6, 2.4)
def gmN(ys):
    s = "0.3 0.01 2.6 0.01"
    for y in ys:
        s += f" {y - 0.16:g} 0.005 {y + 0.16:g} 0.005"
    return f";meshY={{{s}}}"
with open("sweeps/params_radStrikeN.txt", "w") as f:
    for deck, dk in (("sin", SINd), ("hk", "")):
        for n in range(4):
            ys = SY[:n]
            g = (";damGauss={" + " ".join(f"{{{y:g} 0.0 0.04 3e18}}" for y in ys) + "}") if ys else ""
            f.write(f"{deck}_N{n}|{FO}{dk}{g}{gmN(ys)}\n")
print("radStrikeN 8")

# ---- 2026-11-14 (Ian): check stressSave / stressLoad on HPG. Task 0: final SiN set (17 V, occSafe, 10 nm to 2.6 um)
# with stressSave. Tasks 1-2 (submitted after task 0 finishes): the same set loaded from task 0's file, and the same
# plus one Gaussian strike at y 0.8 um. Task 1 must reproduce task 0's curves.
IOF = f"{FO}{SINd};meshY={{0.3 0.01 2.6 0.01}}"
IO_FILE = "/home/ianstafford/blue/ee1/ianstafford/HEMTRAD/results/20261114_radStressIO/task_0/stress_sin17.str"
with open("sweeps/params_radStressIO.txt", "w") as f:
    f.write(f"sin_save|{IOF};stressSave=stress_sin17.str\n")
    f.write(f"sin_load|{IOF};stressLoad={IO_FILE}\n")
    f.write(f"sin_load_g0.8|{IOF};stressLoad={IO_FILE};damGauss={{{{0.8 0.0 0.04 3e18}}}}\n")
print("radStressIO 3")

# ---- 2026-11-15 (Ian): strike count at the 28 V stress, using stressSave/stressLoad. Tasks 0-1 run the 28 V stress
# once per deck on the mesh refined at all three strike positions (gmN(SY)) and save it (damPeak 1.5e18, 0 strikes).
# Tasks 2-15 load that stress: damage scale 1.5e18 (1-3 strikes) and 2e18 (0-3 strikes), both decks, same strikes
# as radStrikeN (3e18, sigma 40 nm, y 0.8 / 1.6 / 2.4 um).
R28 = "/home/ianstafford/blue/ee1/ianstafford/HEMTRAD/results/20261115_rad28strike"
S28 = f"{FE};occSafe=1;Vd_stress=28.0{gmN(SY)}"
def gstr(n):
    ys = SY[:n]
    return (";damGauss={" + " ".join(f"{{{y:g} 0.0 0.04 3e18}}" for y in ys) + "}") if ys else ""
with open("sweeps/params_rad28strike.txt", "w") as f:
    for deck, dk, t in (("sin", SINd, 0), ("hk", "", 1)):
        f.write(f"{deck}28_p1.5e+18_N0|{S28}{dk};damPeak=1.5e18;stressSave=stress_{deck}28.str\n")
    for deck, dk, t in (("sin", SINd, 0), ("hk", "", 1)):
        src = f"{R28}/task_{t}/stress_{deck}28.str"
        for p, ns in ((1.5e18, (1, 2, 3)), (2e18, (0, 1, 2, 3))):
            for n in ns:
                f.write(f"{deck}28_p{p:g}_N{n}|{S28}{dk};damPeak={p:g}{gstr(n)};stressLoad={src}\n")
print("rad28strike 16")

# ---- 2026-11-15 (Ian): stress library. Off-state stress at Vg -10 V ramped in 1 V steps to 84 V (advertised
# breakdown), state at bias saved at every volt (stressSaveEvery, stressOnly), final model on the mesh refined at the
# three strike positions, both decks. Files go to /blue (not the 40 GB home). damPeak is only there so the stress
# branch runs; no damage is placed (stressOnly). A run that stops is continued with stressResume=<last file>.
LIB = "/blue/ee1/ianstafford/stress"
SL = f"{FE};occSafe=1;Vd_stress=84.0;stressStep=1.0{gmN(SY)};damPeak=1.5e18;stressOnly=1;stressSaveEvery=1.0"
with open("sweeps/params_stressLib.txt", "w") as f:
    for deck, dk in (("sin", SINd), ("hk", "")):
        f.write(f"lib_{deck}_Vg-10|{SL}{dk};stressSaveDir={LIB}/{deck}_Vg-10;stressSavePrefix={deck}_Vg-10\n")
print("stressLib 2")

# ---- 2026-11-16 (Ian): fallback for rad28strike. If its stress-saving tasks can't reach 28 V within their 48 h
# limit, load the same 28 V stress from the stress library (stressLib: identical deck, mesh, levers and 1 V steps)
# for all 16 cases.
with open("sweeps/params_rad28strikeL.txt", "w") as f:
    for deck, dk in (("sin", SINd), ("hk", "")):
        src = f"{LIB}/{deck}_Vg-10/{deck}_Vg-10_Vd028.00.str.gz"
        for p in (1.5e18, 2e18):
            for n in range(4):
                f.write(f"{deck}28_p{p:g}_N{n}|{S28}{dk};damPeak={p:g}{gstr(n)};stressLoad={src}\n")
print("rad28strikeL 16")

# ---- 2026-11-17 goal (Ian): stepped SiN curves at the 28 V stress with 1-3 strikes on top of the stress damage.
# Every task loads the library's 28 V SiN state (strike-refined mesh). Round A: damage scale alone; strike density
# 4-8e18 (3e18 does nothing on its own; ~5e18 Gaussians collapse alone at hotEb 1.0) with 1 or 3 strikes at two
# damage scales; graded densities so each strike might trigger at its own Vd. Id-Vd at Vg +1 to 12 V.
SRC28 = f"{LIB}/sin_Vg-10/sin_Vg-10_Vd028.00.str.gz"
G28 = f"{S28}{SINd};stressLoad={SRC28};Vd_max=12.0;doIdVg=0"
def gl(pairs):
    return ";damGauss={" + " ".join(f"{{{y:g} 0.0 0.04 {n:g}}}" for y, n in pairs) + "}"
with open("sweeps/params_radStepA.txt", "w") as f:
    for p in (1.6e18, 1.7e18, 1.8e18):
        f.write(f"A_p{p:g}_N0|{G28};damPeak={p:g}\n")
    for p in (1.5e18, 1.7e18):
        for n in (4e18, 5e18, 6e18, 8e18):
            f.write(f"A_p{p:g}_n{n:g}_N1|{G28};damPeak={p:g}{gl([(0.8, n)])}\n")
            f.write(f"A_p{p:g}_n{n:g}_N3|{G28};damPeak={p:g}{gl([(0.8, n), (1.6, n), (2.4, n)])}\n")
    f.write(f"A_p1.5e+18_g456_N3|{G28};damPeak=1.5e18{gl([(0.8, 4e18), (1.6, 5e18), (2.4, 6e18)])}\n")
    f.write(f"A_p1.5e+18_g654_N3|{G28};damPeak=1.5e18{gl([(0.8, 6e18), (1.6, 5e18), (2.4, 4e18)])}\n")
print("radStepA 21")

# ---- 2026-11-17 goal, round B (in parallel with A): levers A doesn't touch. SiN, 28 V library state, Vd to 12 V,
# damage scale 1.5e18 unless noted. Trap level (also deepens the stress-damage traps), strike width (narrow
# TRIM-like and wide), strike depth below the 2DEG, strikes nearer the gate, wide graded densities, capture time,
# scale 1.6e18, and two-strike cases.
def glw(items):   # (y, x, sigma, N)
    return ";damGauss={" + " ".join(f"{{{y:g} {x:g} {s:g} {n:g}}}" for y, x, s, n in items) + "}"
P3 = (0.8, 1.6, 2.4)
rowsB = []
for lv in (0.35, 0.40, 0.45):
    rowsB.append((f"B_lev{lv:g}_n5e18_N3", f"trapLevel={lv:g};damPeak=1.5e18{gl([(y, 5e18) for y in P3])}"))
for n in (8e18, 1.2e19):
    rowsB.append((f"B_s0.02_n{n:g}_N3", f"damPeak=1.5e18{glw([(y, 0.0, 0.02, n) for y in P3])}"))
for n in (3e18, 4e18):
    rowsB.append((f"B_s0.1_n{n:g}_N1", f"damPeak=1.5e18{glw([(0.8, 0.0, 0.1, n)])}"))
    rowsB.append((f"B_s0.1_n{n:g}_N3", f"damPeak=1.5e18{glw([(y, 0.0, 0.1, n) for y in P3])}"))
rowsB.append(("B_x0.03_n6e18_N3", f"damPeak=1.5e18{glw([(y, 0.03, 0.04, 6e18) for y in P3])}"))
for n in (5e18, 6e18):
    rowsB.append((f"B_near_n{n:g}_N3", f"damPeak=1.5e18{gl([(y, n) for y in (0.5, 0.8, 1.1)])}"))
rowsB.append(("B_g369_N3", f"damPeak=1.5e18{gl([(0.8, 3e18), (1.6, 6e18), (2.4, 9e18)])}"))
rowsB.append(("B_g963_N3", f"damPeak=1.5e18{gl([(0.8, 9e18), (1.6, 6e18), (2.4, 3e18)])}"))
for tau in (5e-15, 2e-14):
    rowsB.append((f"B_tau{tau:g}_n5e18_N3", f"hotTau={tau:g};damPeak=1.5e18{gl([(y, 5e18) for y in P3])}"))
for n in (5e18, 6e18):
    rowsB.append((f"B_p1.6_n{n:g}_N3", f"damPeak=1.6e18{gl([(y, n) for y in P3])}"))
rowsB.append(("B_n6e18_N2", f"damPeak=1.5e18{gl([(0.8, 6e18), (1.6, 6e18)])}"))
rowsB.append(("B_s0.1_n4e18_N2", f"damPeak=1.5e18{glw([(0.8, 0.0, 0.1, 4e18), (1.6, 0.0, 0.1, 4e18)])}"))
with open("sweeps/params_radStepB.txt", "w") as f:
    for lab, lev in rowsB:
        f.write(f"{lab}|{G28};{lev}\n")
print("radStepB", len(rowsB))

# ---- 2026-11-17 goal, round C: round A found steps with 6-8e18 strikes (6e18, 1 strike at 1.5e18: drops at ~2 V
# and ~6.3 V, the Nov 11 shape; 8e18, 3 strikes: drops near 1.8, 3.9, 6.7 V). Complete matched 0-3 strike series
# (N2 cases, 7e18 in between, 1.6e18 scale, N0 to 12 V) and the HighK counterparts (28 V HighK library state).
SRC28HK = f"{LIB}/hk_Vg-10/hk_Vg-10_Vd028.00.str.gz"
G28HK = f"{S28};stressLoad={SRC28HK};Vd_max=12.0;doIdVg=0"
def gN(n, k):
    return gl([(y, n) for y in P3[:k]]) if k else ""
rowsC = [("C_p1.7_n6e18_N2", G28, "damPeak=1.7e18" + gN(6e18, 2)),
         ("C_p1.5_n8e18_N2", G28, "damPeak=1.5e18" + gN(8e18, 2)),
         ("C_p1.7_n8e18_N2", G28, "damPeak=1.7e18" + gN(8e18, 2)),
         ("C_p1.5_N0", G28, "damPeak=1.5e18")]
rowsC += [(f"C_p1.5_n7e18_N{k}", G28, "damPeak=1.5e18" + gN(7e18, k)) for k in (1, 2, 3)]
rowsC += [(f"C_p1.6_n6e18_N{k}", G28, "damPeak=1.6e18" + gN(6e18, k)) for k in (1, 2)]
rowsC += [(f"C_hk_p1.5_n6e18_N{k}", G28HK, "damPeak=1.5e18" + gN(6e18, k)) for k in (0, 1, 2, 3)]
rowsC += [(f"C_hk_p1.5_n8e18_N{k}", G28HK, "damPeak=1.5e18" + gN(8e18, k)) for k in (1, 2, 3)]
with open("sweeps/params_radStepC.txt", "w") as f:
    for lab, base, lev in rowsC:
        f.write(f"{lab}|{base};{lev}\n")
print("radStepC", len(rowsC))

# ---- 2026-11-17 goal, round D: checks the literature review asks for. Convergence (Vd step halved to 0.05 V; the
# mesh is already 5 nm round each strike) for the stepped cases, and knock-out of single strikes from the
# three-8e18-strike case (independent sites keep their steps at the same Vd; a cascade moves them).
rowsD = [("D_p1.5_n6e18_N1_dv05", "damPeak=1.5e18" + gN(6e18, 1) + ";Vd_step=0.05"),
         ("D_p1.7_n6e18_N3_dv05", "damPeak=1.7e18" + gN(6e18, 3) + ";Vd_step=0.05"),
         ("D_p1.5_n8e18_N3_dv05", "damPeak=1.5e18" + gN(8e18, 3) + ";Vd_step=0.05"),
         ("D_p1.5_n8e18_ko1", "damPeak=1.5e18" + gl([(1.6, 8e18), (2.4, 8e18)])),
         ("D_p1.5_n8e18_ko2", "damPeak=1.5e18" + gl([(0.8, 8e18), (2.4, 8e18)]))]
with open("sweeps/params_radStepD.txt", "w") as f:
    for lab, lev in rowsD:
        f.write(f"{lab}|{G28};{lev}\n")
print("radStepD", len(rowsD))

# ---- 2026-11-17 goal, round E (Ian: fill ee1-b): directions from the literature review (kb rad-literature-steps).
# Stress Vd series (24 and 30 V states from the library; damage scale adjusted for the E^4 law: (28/Vd)^4),
# strikes at the field-plate edges (y 0.9 and 0.3, then 2.0), trap level 0.40 with 6e18 strikes, wider strikes
# (sigma 60 nm), and Vg families (0 and -1 V) for the best stepped cases.
def g28at(vd):
    return f"{FE};occSafe=1;Vd_stress={vd:g}{gmN(SY)}{SINd};stressLoad={LIB}/sin_Vg-10/sin_Vg-10_Vd{vd:06.2f}.str.gz;Vd_max=12.0;doIdVg=0"
rowsE = []
for vd, p in ((24.0, 2.8e18), (30.0, 1.15e18)):
    for k in (0, 1, 3):
        rowsE.append((f"E_vs{vd:g}_p{p:g}_n6e18_N{k}", g28at(vd), f"damPeak={p:g}" + gN(6e18, k)))
FPP = (0.9, 0.3, 2.0)
for k in (1, 2, 3):
    rowsE.append((f"E_fp_n6e18_N{k}", G28, "damPeak=1.5e18" + gl([(y, 6e18) for y in FPP[:k]])))
for k in (1, 2, 3):
    rowsE.append((f"E_lev0.4_n6e18_N{k}", G28, "trapLevel=0.40;damPeak=1.5e18" + gN(6e18, k)))
for k in (1, 2, 3):
    rowsE.append((f"E_s0.06_n6e18_N{k}", G28, "damPeak=1.5e18" + glw([(y, 0.0, 0.06, 6e18) for y in P3[:k]])))
for lab, lev in (("E_fam_n6e18_N1", "damPeak=1.5e18" + gN(6e18, 1)), ("E_fam_n6e18_N3", "damPeak=1.5e18" + gN(6e18, 3)),
                 ("E_fam_n8e18_N3", "damPeak=1.5e18" + gN(8e18, 3))):
    rowsE.append((lab, G28, lev + ";VgFam={0 -1}"))
with open("sweeps/params_radStepE.txt", "w") as f:
    for lab, base, lev in rowsE:
        f.write(f"{lab}|{base};{lev}\n")
print("radStepE", len(rowsE))

# ---- 2026-11-17 goal, round F: trap level 0.40 eV with 6e18 strikes gave a staircase whose step count grows with
# the strike count (E_lev0.4: 3 steps near 1.7 / 2.9 / 4.4 V with 3 strikes). Complete it: 0 strikes, HighK
# counterparts, strike densities 5e18 and 7e18, and Vd step 0.05 V for the 1-3 strike cases.
L4 = "trapLevel=0.40;damPeak=1.5e18"
rowsF = [("F_lev0.4_N0", G28, L4)]
rowsF += [(f"F_hk_lev0.4_n6e18_N{k}", G28HK, L4 + gN(6e18, k)) for k in range(4)]
rowsF += [(f"F_lev0.4_n{n:g}_N{k}", G28, L4 + gN(n, k)) for n in (5e18, 7e18) for k in (1, 2, 3)]
rowsF += [(f"F_lev0.4_n6e18_N{k}_dv05", G28, L4 + gN(6e18, k) + ";Vd_step=0.05") for k in (1, 2, 3)]
with open("sweeps/params_radStepF.txt", "w") as f:
    for lab, base, lev in rowsF:
        f.write(f"{lab}|{base};{lev}\n")
print("radStepF", len(rowsF))

# ---- 2026-11-17 goal, round G: strikes of 6e18 and up collapse HighK too (C_hk, F_hk), which the measured HighK
# devices don't do. Find the strike-density window where SiN still steps and HighK stays flat: HighK and SiN at
# 5e18 / 5.5e18 (trap level 0.30) and 4e18 / 5e18 (trap level 0.40), 1-3 strikes.
L3 = "damPeak=1.5e18"
rowsG = []
for n in (5e18, 5.5e18):
    rowsG += [(f"G_hk_n{n:g}_N{k}", G28HK, L3 + gN(n, k)) for k in (1, 2, 3)]
rowsG += [("G_n5e18_N2", G28, L3 + gN(5e18, 2))]
rowsG += [(f"G_n5.5e18_N{k}", G28, L3 + gN(5.5e18, k)) for k in (1, 2, 3)]
for n in (4e18, 5e18):
    rowsG += [(f"G_hk_lev0.4_n{n:g}_N{k}", G28HK, L4 + gN(n, k)) for k in (1, 2, 3)]
rowsG += [(f"G_lev0.4_n4e18_N{k}", G28, L4 + gN(4e18, k)) for k in (1, 2, 3)]
with open("sweeps/params_radStepG.txt", "w") as f:
    for lab, base, lev in rowsG:
        f.write(f"{lab}|{base};{lev}\n")
print("radStepG", len(rowsG))

# ---- 2026-11-18 goal, round H: strikes dense enough to step SiN (>= 5e18) also step HighK (round G), so strike
# damage alone can't keep HighK flat. Field-scaled strikes (new lever gaussFieldM: strike density times
# (Estress/damEref)^m from the stored 28 V field): under the T-gate overhang SiN's field is 2.1x HighK's (y 0.5), so
# strikes there are dense in SiN and weak in HighK. Strikes at y 0.5, then 0.35, then 0.65 um (150 nm apart),
# both decks, scale 1.5e18, trap level 0.30; plus field-scaled 6e18 strikes at the old positions as a check.
POH = (0.5, 0.35, 0.65)
def gP(n, k, pos):
    return gl([(y, n) for y in pos[:k]]) if k else ""
rowsH = []
for tag, extra, n in (("nofm_n3e18", "", 3e18), ("fm4_n3e18", ";gaussFieldM=4", 3e18),
                      ("fm4_n2e18", ";gaussFieldM=4", 2e18), ("fm2_n4e18", ";gaussFieldM=2", 4e18)):
    for deck, base in (("sin", G28), ("hk", G28HK)):
        rowsH += [(f"H_{deck}_{tag}_N{k}", base, "damPeak=1.5e18" + gP(n, k, POH) + extra) for k in (1, 2, 3)]
for deck, base in (("sin", G28), ("hk", G28HK)):
    rowsH.append((f"H_{deck}_fm4_old_n6e18_N3", base, "damPeak=1.5e18" + gN(6e18, 3) + ";gaussFieldM=4"))
with open("sweeps/params_radStepH.txt", "w") as f:
    for lab, base, lev in rowsH:
        f.write(f"{lab}|{base};{lev}\n")
print("radStepH", len(rowsH))

# ---- 2026-11-18 goal, round I: round H's field-scaled strikes keep HighK flat to 7 V, but a single SiN strike at
# y 0.5 (base 2-4e18, m 2 or 4) collapses SiN completely at 0.4-1.0 V, so strikes 2-3 add nothing. SiN's 28 V field
# exceeds HighK's over y 0.45-0.65 um ((E_SiN/E_HK)^4 = 3.7-30 at 10 nm depth). Lower base densities: one strike at
# y 0.5 (3e17 / 6e17 / 1e18) or y 0.6 / 0.65; and three strikes spread over the band (0.65, 0.6, 0.55 in that order).
rowsI = []
for deck, base in (("sin", G28), ("hk", G28HK)):
    rowsI += [(f"I_{deck}_y0.5_n{n:g}_N1", base, "damPeak=1.5e18" + gl([(0.5, n)]) + ";gaussFieldM=4")
              for n in (3e17, 6e17, 1e18)]
    rowsI += [(f"I_{deck}_y{y:g}_n{n:g}_N1", base, "damPeak=1.5e18" + gl([(y, n)]) + ";gaussFieldM=4")
              for y, n in ((0.6, 1e18), (0.65, 3e18))]
    for tag, trio in (("a", ((0.65, 3e18), (0.6, 1e18), (0.55, 3e17))), ("b", ((0.65, 2e18), (0.6, 6e17), (0.55, 2e17)))):
        rowsI += [(f"I_{deck}_band{tag}_N{k}", base, "damPeak=1.5e18" + gl(trio[:k]) + ";gaussFieldM=4")
                  for k in ((2, 3) if tag == "a" else (1, 2, 3))]   # band a N1 = y0.65_n3e18_N1
with open("sweeps/params_radStepI.txt", "w") as f:
    for lab, base, lev in rowsI:
        f.write(f"{lab}|{base};{lev}\n")
print("radStepI", len(rowsI))

# ---- 2026-11-18 (Ian: check the mesh refinement of the strike steps). Every round A-I task loads the library mesh
# (stressLoad keeps the file's mesh): 93,080 points, but the deck's own rightFP line (y 0.725, 20 nm) sits inside the
# 0.64-0.96 meshY patch, so the y 0.8 strike is on ~15 nm cells (2.7 per sigma), while 1.6 and 2.4 are on a true
# 5 nm; the SiN E^4 damage core (y 0.48-0.63) is on 6-10 nm. No A-I case has a second mesh. Two new 28 V SiN
# stresses (stressOnly, saved every volt so a stalled run can resume), same levers as the library:
#   m10:   10 nm uniform over 0.3-2.6 (helper lines 0.715/0.735 cancel the 20 nm rightFP line), ~64k points;
#   m5fix: the library mesh with a true 5 nm at 0.8 (helper lines 0.72/0.73), ~99k points.
# Never put a meshY line exactly on a deck line (zero-area faces abort FLOOXS). Loading runs follow once saved.
MESHCHK = {"m10": "0.3 0.01 0.715 0.01 0.735 0.01 2.6 0.01",
           "m5fix": "0.3 0.01 2.6 0.01 0.64 0.005 0.72 0.005 0.73 0.005 0.96 0.005 1.44 0.005 1.76 0.005 2.24 0.005 2.56 0.005"}
with open("sweeps/params_meshChkStress.txt", "w") as f:
    for tag, my in MESHCHK.items():
        f.write(f"mc_sin_{tag}|{FE};occSafe=1;Vd_stress=28.0;stressStep=1.0;meshY={{{my}}};damPeak=1.5e18;stressOnly=1;"
                f"stressSaveEvery=1.0{SINd};stressSaveDir={LIB}/meshchk/sin_{tag};stressSavePrefix=sin_{tag}\n")
print("meshChkStress", len(MESHCHK))

# ---- 2026-11-18 goal, round J: field-scaled strikes keep HighK flat but give SiN one drop that only deepens with
# more strikes (round I), because every SiN-favoured strike sits in the same band (y 0.45-0.65) and shares the first
# capture onset. Levers that might separate the onsets inside the band: a deeper trap level (0.40 eV gave the
# plain-strike staircases, rounds E/F; 0.35 as a middle value), and strikes at different depths in the band
# (x 0, 30 and 60 nm below the AlGaN top). Both decks; field scaling m 4 throughout.
BANDB = ((0.65, 2e18), (0.6, 6e17), (0.55, 2e17))
YSING = (3e17, 6e17, 1e18)
rowsJ = []
for lv in (0.40, 0.35):
    for deck, base in (("sin", G28), ("hk", G28HK)):
        ks = (1, 2, 3) if (lv == 0.40 or deck == "sin") else (3,)
        rowsJ += [(f"J_{deck}_lev{lv:g}_bandb_N{k}", base, f"trapLevel={lv:g};damPeak=1.5e18" + gl(BANDB[:k]) + ";gaussFieldM=4")
                  for k in ks]
for deck, base in (("sin", G28), ("hk", G28HK)):
    rowsJ += [(f"J_{deck}_lev0.4_y0.5_n{n:g}_N1", base, "trapLevel=0.40;damPeak=1.5e18" + gl([(0.5, n)]) + ";gaussFieldM=4")
              for n in YSING]
DEPTH = ((0.55, 0.0, 0.04, 6e17), (0.55, 0.03, 0.04, 6e17), (0.55, 0.06, 0.04, 6e17))
rowsJ += [(f"J_sin_depth_N{k}", G28, "damPeak=1.5e18" + glw(DEPTH[:k]) + ";gaussFieldM=4") for k in (1, 2, 3)]
rowsJ += [("J_hk_depth_N3", G28HK, "damPeak=1.5e18" + glw(DEPTH) + ";gaussFieldM=4")]
rowsJ += [("J_sin_lev0.4_bandb_N3_dv05", G28, "trapLevel=0.40;damPeak=1.5e18" + gl(BANDB) + ";gaussFieldM=4;Vd_step=0.05")]
with open("sweeps/params_radStepJ.txt", "w") as f:
    for lab, base, lev in rowsJ:
        f.write(f"{lab}|{base};{lev}\n")
print("radStepJ", len(rowsJ))

# ---- 2026-11-18: loading runs for the mesh check of the strike steps (meshChkStress 51883722). The deliverable's
# row A series (0-3 plain 6e18 strikes at scale 1.5e18) and the other two best step cases, rerun on each new 28 V
# stress (m10, m5fix): the same parameter lines as the library runs, with stressLoad and meshY swapped (stressLoad
# takes the file's mesh anyway; meshY is matched so the deck build agrees). Submitted with afterok on each stress task.
LIBMESH = "meshY={0.3 0.01 2.6 0.01 0.64 0.005 0.96 0.005 1.44 0.005 1.76 0.005 2.24 0.005 2.56 0.005}"
LIBSRC = f"stressLoad={LIB}/sin_Vg-10/sin_Vg-10_Vd028.00.str.gz"
CHK_CASES = ("C_p1.5_N0", "A_p1.5e+18_n6e+18_N1", "B_n6e18_N2", "A_p1.5e+18_n6e+18_N3", "E_lev0.4_n6e18_N2",
             "C_p1.5_n8e18_N2")
orig = {}
for r in "ABCE":
    for line in open(f"sweeps/params_radStep{r}.txt"):
        lab, lev = line.rstrip("\n").split("|", 1)
        orig[lab] = lev
for tag, my in MESHCHK.items():
    with open(f"sweeps/params_meshChkLoad_{tag}.txt", "w") as f:
        for lab in CHK_CASES:
            lev = orig[lab]
            assert LIBMESH in lev and LIBSRC in lev, lab
            lev = lev.replace(LIBMESH, f"meshY={{{my}}}").replace(
                LIBSRC, f"stressLoad={LIB}/meshchk/sin_{tag}/sin_{tag}_Vd028.00.str.gz")
            f.write(f"{tag}_{lab}|{lev}\n")
print("meshChkLoad", len(CHK_CASES), "x", len(MESHCHK))

# ---- 2026-11-18 goal, round K: hybrid strikes. A field-scaled strike near the gate (damGaussF, 2e18 at y 0.65 um, m 4:
# SiN partial drop 386 -> 174, HighK untouched; round I band b N1) plus 1-3 plain strikes further out (damGauss at
# y 0.8 / 1.6 / 2.4 um, unscaled) at 3e18 or 4e18, below the density that drops HighK (5e18; 3e18 left HighK flat,
# rad28strikeL). Does SiN, with its near-gate region already collapsed, step on the far strikes while HighK stays
# flat? Plus plain 4e18 HighK (trap level 0.30) to place HighK's threshold between 3e18 and 5e18.
NEARF = ";damGaussF={{0.65 0.0 0.04 2e+18}};gaussFieldMF=4"
rowsK = []
for deck, base in (("sin", G28), ("hk", G28HK)):
    for nf in (3e18, 4e18):
        rowsK += [(f"K_{deck}_hyb_far{nf:g}_N{k}", base, "damPeak=1.5e18" + NEARF + gN(nf, k)) for k in (1, 2, 3)]
rowsK += [(f"K_hk_n4e18_N{k}", G28HK, "damPeak=1.5e18" + gN(4e18, k)) for k in (1, 2, 3)]
with open("sweeps/params_radStepK.txt", "w") as f:
    for lab, base, lev in rowsK:
        f.write(f"{lab}|{base};{lev}\n")
print("radStepK", len(rowsK))

# ---- 2026-11-18 (Ian): Fig. 5-style strike maps at the irradiation bias (after the local proof of concept at
# Vg -5 / Vd 10 V): SiN and HighK, Vg -10 / Vd 28 V, strike at y 0.2 um (between the gate foot's drain edge and the
# field plate), tau 2 ps, maps from DC to 1 ns. drivers/seeIV.tcl via DRV=seeIV.
SEEB = ("polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100;occSafe=1;Vd_bias=28;Vg_bias=-10;"
        "seeY0=0.2;seeGenTau=2e-12;seeTend=1e-9;seeMapTimes={3e-12 6e-12 1.2e-11 3e-11 1e-10 3e-10 1e-9};seeMapDC=1;seeCutTimes={}")
with open("sweeps/params_seeMap28.txt", "w") as f:
    f.write(f"sin_y0.2_map|{SEEB};deviceDeck=rfdevice_SiN.tcl\n")
    f.write(f"hk_y0.2_map|{SEEB}\n")
print("seeMap28 2")

# ---- 2026-11-19 (Ian): resume the SiN stress library from its last state (Vd 60 V at the 4-day limit), and rerun
# the deliverable's row A series with vdCuts (filled traps, electrons, lateral field, Te along y at every Vd) to show
# which damage fills at each drop.
with open("sweeps/params_stressLibResume.txt", "w") as f:
    lab, lev = open("sweeps/params_stressLib.txt").readline().rstrip("\n").split("|", 1)
    f.write(f"{lab}_r60|{lev};stressResume={LIB}/sin_Vg-10/sin_Vg-10_Vd060.00.str.gz\n")
with open("sweeps/params_radStepDiag.txt", "w") as f:
    for lab in ("C_p1.5_N0", "A_p1.5e+18_n6e+18_N1", "B_n6e18_N2", "A_p1.5e+18_n6e+18_N3"):
        f.write(f"D_{lab}|{orig[lab]};vdCuts=1\n")
print("stressLibResume 1, radStepDiag 4")

# ---- 2026-11-19: the 5 nm mesh check (meshChkLoad_m5fix 51939192) keeps the stress-only drop but shrinks and moves the
# strike steps, so the per-Vd diagnostic cuts are repeated on the m5fix mesh for the cases that still step there.
with open("sweeps/params_radStepDiag5.txt", "w") as f:
    for line in open("sweeps/params_meshChkLoad_m5fix.txt"):
        lab, lev = line.rstrip("\n").split("|", 1)
        if lab.split("_", 1)[1] in ("C_p1.5_N0", "A_p1.5e+18_n6e+18_N1", "E_lev0.4_n6e18_N2", "C_p1.5_n8e18_N2"):
            f.write(f"D5_{lab}|{lev};vdCuts=1\n")
    # plus the library-mesh 1-strike case (three drops there), now that VdCuts also cuts the AlGaN barrier
    f.write(f"D5_lib_A_p1.5e+18_n6e+18_N1|{orig['A_p1.5e+18_n6e+18_N1']};vdCuts=1\n")
print("radStepDiag5 5")

# ---- 2026-11-19 goal (stop hook: the stepped 1/2/3-strike series must survive mesh refinement). On m5fix (5 nm over
# y 0.64-0.96) row A's plain 6e18 strikes at trap 0.30 lose their 2- and 3-strike steps, but trap 0.40 with two 6e18
# strikes keeps three drops on all three meshes (library 1.4/2.7/10.4, m10 1.4/3.1/7.7, m5fix 1.4/2.4/6.3 V) and
# 8e18 at trap 0.30 keeps two. radStepM: full 0-3 strike series at those settings on the m5fix stress (trap 0.40 with
# 5, 6, 7e18; trap 0.30 with 7 and 8e18), plus the trap-0.40 6e18 series on m10, all with vdCuts.
for r in "F":
    for line in open(f"sweeps/params_radStep{r}.txt"):
        lab, lev = line.rstrip("\n").split("|", 1)
        orig[lab] = lev
M_CASES = {"m5fix": ("F_lev0.4_N0", "E_lev0.4_n6e18_N1", "E_lev0.4_n6e18_N3", "F_lev0.4_n5e+18_N1", "F_lev0.4_n5e+18_N2",
                     "F_lev0.4_n5e+18_N3", "F_lev0.4_n7e+18_N1", "F_lev0.4_n7e+18_N2", "F_lev0.4_n7e+18_N3",
                     "A_p1.5e+18_n8e+18_N1", "A_p1.5e+18_n8e+18_N3", "C_p1.5_n7e18_N1", "C_p1.5_n7e18_N2",
                     "C_p1.5_n7e18_N3"),
           "m10": ("F_lev0.4_N0", "E_lev0.4_n6e18_N1", "E_lev0.4_n6e18_N3")}
with open("sweeps/params_radStepM.txt", "w") as f:
    for tag, labs in M_CASES.items():
        for lab in labs:
            lev = orig[lab]
            assert LIBMESH in lev and LIBSRC in lev, lab
            lev = lev.replace(LIBMESH, f"meshY={{{MESHCHK[tag]}}}").replace(
                LIBSRC, f"stressLoad={LIB}/meshchk/sin_{tag}/sin_{tag}_Vd028.00.str.gz")
            f.write(f"M_{tag}_{lab}|{lev};vdCuts=1\n")
print("radStepM", sum(len(v) for v in M_CASES.values()))

# 2.5 nm at the three strike sites (m2p5), same levers as the library and meshChkStress, saved every volt.
M2P5 = "0.3 0.01 2.6 0.01 0.64 0.0025 0.72 0.0025 0.73 0.0025 0.96 0.0025 1.44 0.0025 1.76 0.0025 2.24 0.0025 2.56 0.0025"
with open("sweeps/params_meshChkStress2p5.txt", "w") as f:
    lab, lev = open("sweeps/params_meshChkStress.txt").readline().rstrip("\n").split("|", 1)
    assert "sin_m10" in lev
    lev = lev.replace(f"meshY={{{MESHCHK['m10']}}}", f"meshY={{{M2P5}}}").replace("sin_m10", "sin_m2p5")
    f.write(f"mc_sin_m2p5|{lev}\n")
print("meshChkStress2p5 1")

# radStepM2 (2026-11-19 night): on m5fix, trap 0.40 eV with 7e18 strikes gives one drop per strike (1 / 2 / 3 drops
# with 1 / 2 / 3 strikes) and trap 0.30 with 8e18 keeps 2 / 3 / 3 drops as on the library mesh. Same series on m10
# for the three-mesh check (m10 C_p1.5_n8e18_N2 exists from meshChkLoad).
with open("sweeps/params_radStepM2.txt", "w") as f:
    for lab in ("F_lev0.4_n7e+18_N1", "F_lev0.4_n7e+18_N2", "F_lev0.4_n7e+18_N3", "A_p1.5e+18_n8e+18_N1",
                "A_p1.5e+18_n8e+18_N3"):
        lev = orig[lab]
        assert LIBMESH in lev and LIBSRC in lev, lab
        lev = lev.replace(LIBMESH, f"meshY={{{MESHCHK['m10']}}}").replace(
            LIBSRC, f"stressLoad={LIB}/meshchk/sin_m10/sin_m10_Vd028.00.str.gz")
        f.write(f"M_m10_{lab}|{lev};vdCuts=1\n")
print("radStepM2 5")

# radStepM3 (2026-11-20): the four-mesh check. The stepping series on the 2.5 nm stress (meshChkStress2p5 52044407,
# Ian: keep it running): trap 0.30 / 8e18 (mesh-robust 2/3/3 on library, m10, m5fix), trap 0.40 / 7e18 (1/2/3 on m5fix
# only) and trap 0.40 / 6e18, with their no-strike references. Submitted once sin_m2p5_Vd028.00.str.gz exists.
M3 = ("C_p1.5_N0", "A_p1.5e+18_n8e+18_N1", "C_p1.5_n8e18_N2", "A_p1.5e+18_n8e+18_N3", "F_lev0.4_N0",
      "F_lev0.4_n7e+18_N1", "F_lev0.4_n7e+18_N2", "F_lev0.4_n7e+18_N3", "E_lev0.4_n6e18_N1", "E_lev0.4_n6e18_N2",
      "E_lev0.4_n6e18_N3")
with open("sweeps/params_radStepM3.txt", "w") as f:
    for lab in M3:
        lev = orig[lab]
        assert LIBMESH in lev and LIBSRC in lev, lab
        lev = lev.replace(LIBMESH, f"meshY={{{M2P5}}}").replace(
            LIBSRC, f"stressLoad={LIB}/meshchk/sin_m2p5/sin_m2p5_Vd028.00.str.gz")
        f.write(f"M_m2p5_{lab}|{lev};vdCuts=1\n")
print("radStepM3", len(M3))
