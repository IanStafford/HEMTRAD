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
