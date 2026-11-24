"""Write the sweeps/params_<name>.txt files of the rad-model studies from 2026-11-04 on.

usage (from the repo root):
  python3 analysis/genRadStudy.py                 write new params files; refuse to change tracked ones
  python3 analysis/genRadStudy.py --check         write nothing; list files that would be created or changed
  python3 analysis/genRadStudy.py --force NAME    let study NAME's tracked file change (repeatable)
  python3 analysis/genRadStudy.py --show NAME [TASK]
                                                  print each line's effective levers (last value wins) and
                                                  their differences from the study's base

A committed params file is the record of what its job ran, so a run writes a file only when it is new or
its content is unchanged. When a tracked file would change, the generator prints the diff, leaves the file
alone, and exits 1 at the end. Use --force only to correct a file whose job has not run. A new study gets
a new name, a new function and a new entry at the end of STUDIES. Constants and builders are in
analysis/radparams.py; the line format and the last-value-wins rule are explained there.

Studies (STUDIES, in build order; each writes sweeps/params_<name>.txt; driver radIV unless noted):
  2026-11-04/05  radChk radVth radMap1 radMesh radFam radVth2 radRon radStress radVth3 radFine radMulti
                 radEmit radEmit2
  2026-11-07     radEmit3 radChk2 radGauss (DRV=pulsedIV) radMap2 radGauss2 (DRV=pulsedIV)
  2026-11-09/13  radEB1 radEB2 radFinal12 radExp1 radExp1b radExp2 radExp3 radHV radStrike2 rad28fit
                 radStrikeN
  2026-11-14/16  radStressIO rad28strike stressLib rad28strikeL
  2026-11-17/18  radStepA-I meshChkStress radStepJ meshChkLoad_m10 meshChkLoad_m5fix radStepK
                 seeMap28 (DRV=seeIV)
  2026-11-19/20  stressLibResume radStepDiag radStepDiag5 radStepM meshChkStress2p5 radStepM2 radStepM3
  2026-11-20     fpFixPre fpFixStress fpFixEB1 fpFixLoad fpFixMesh fpFixEB1p
Each function's docstring says what the study is for. Results and job IDs are in progress.md and the KB
(kb/results/damage-region-map.md, kb/results/step-search-28v.md, kb/results/fp-contact-fix.md).

Derived studies. Some studies copy or edit their parents' lines (Study.parents): they get the parents'
rows from memory, not from the files on disk. The task order inside a file is fixed: SLURM array index i
runs line i+1 into results/<RUN>/task_<i>, so reordering breaks the map from task directories to cases.

FP contact fix (2026-11-20, kb/results/fp-contact-fix.md). States saved before the fix (radStressIO,
rad28strike, stressLib, stressLibResume, meshChkStress, meshChkStress2p5) have the old FP contact box.
radIV refuses to load or resume them unless fpBoxOld=1, so a file that loads them fails as written, and a
file that solves its own stress now builds the fixed box. The fpFix* files rerun the key cases with the
fixed box.

radFine: the params_radFine.txt written here is the Nov 5 radFine (job 49735196). The Oct 24 radFine
(job 47562303) used a different, hand-written file of the same name, kept in git at commit 0fbf0ce.

Not written here: the rad3d* files come from analysis/genRad3d.py. No tracked script writes the other
sweeps/params_*.txt files (radCal*, radFinal..radFinal11, radFit*, radNE*, radWin, rad28a,
stressAbs/Clamp/Diag/Floor/Safe*, seeGen*, seeIso1, seeSmoke1, the other rad* and vgEB* files, and the
pulsedIV-era files); they were written by hand.
"""
import random
import sys

from radparams import (
    BASE_1104, B_OS17_1112, B_RADCHK2_1107, B_RADEB1_1109, B_S28_1112, B_S28_1115, DAM2_GATE, DECK_FILE, FIXLIB,
    HPG_RESULTS, INS, LIB, LIB_MESH, LIB_SRC, LIB_STRESS_1115, LOAD28_HK_1117, LOAD28_SIN_1117, M2P5, MESHCHK,
    NB_DECKS, NB_RADFINAL8_1026, PRE, PULSED_GAUSS_1107, SEE28_1118, SIN, SKIP, STRIKES_Y, SURF, Y_ALL, Y_GATE,
    Y_GD, Y_SD, Study, by_label, fine, fpfix_state, gauss, gauss_w, join, lib_state, load_at_1117, meshchk_state,
    rows_both_decks, rows_on_decks, run, sin_radfinal11_1027, site, site_fine, sitecase, sites, strike_mesh,
    strikes, swap, R_NOV11, fx_rows,
)

# ---- shared by several studies
# radMap1 / radMap2 windows, 0.3 um wide (14 windows, including under the gate)
MAP_Y = [(-1.05, -0.75), (-0.75, -0.45), (-0.45, -0.15), (-0.15, 0.15)] + \
        [(0.15 + 0.3 * i, 0.45 + 0.3 * i) for i in range(10)]
EB = ";Vd_step=0.1;retryDepth=8"
L3 = "damPeak=1.5e18"
L4 = "trapLevel=0.40;damPeak=1.5e18"


def to_mesh(lev, mesh, state):
    """A library loading line moved to another saved state: its meshY and stressLoad swapped."""
    return swap(swap(lev, LIB_MESH, f"meshY={{{mesh}}}"), LIB_SRC, f"stressLoad={state}")


def pulsed_gauss(lab, deck, y, lev, sp, extra="", half=0.16, peak=None):
    """A pulsedIV Gaussian trap line (radGauss, radGauss2): sp > 0 adds meshY at spacing sp within half of y."""
    m = f";meshY={{{y - half:g} {sp:g} {y + half:g} {sp:g}}}" if sp else ""
    pk = peak if peak else (5e18 if lev == 0.30 else 4e18)
    return (lab, f"{PULSED_GAUSS_1107};deviceDeck={DECK_FILE[deck]};trapMeanY={y:g};trapPeak={pk:g};"
                 f"trapLevel={lev:g};ivCSV=pulsedIV_{lab}.csv{m}{extra}")


# ---------------------------------------------------------------- 2026-11-04/05: damage-region and Vth studies
def radChk():
    """Regression check of the new code paths: radFinal's pre and radFinal8's nb case."""
    rows = []
    for d, dl in NB_DECKS:
        rows.append((f"pre_{d}", join(PRE, dl)))
        rows.append((f"nb_{d}_skip", join(NB_RADFINAL8_1026, dl, SKIP, DAM2_GATE)))
        rows.append((f"nb_{d}_sites", join(NB_RADFINAL8_1026, dl, SKIP, sites((*Y_GATE, 0.0, 0.014, 5e17)))))
    return rows


def radVth():
    """Phase 2: ways to shift Vth. Vth, gm, Ron and low-field current only, so Vd stops at 5 V (about 1 h
    per task) before the high-Vd retries."""
    G, A = Y_GATE, Y_ALL
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
    cases += [(f"ins{n:g}", f"{SKIP};insTrapSign=-1;damInsPeak={n:g};damInsM=0;damInsXmin=-0.05")
              for n in (1e17, 5e17, 1e18)]
    return rows_both_decks(cases, "Vd_max=5.0")


def radMap1():
    """Phase 3a: one site, position map (width 0.3 um, top 50 nm)."""
    cases = [("ref", "")]
    for n in (1e18, 4e18):
        cases += [(f"y{(a + b) / 2:.2f}_n{n:g}", sitecase((a, b, 0.0, 0.05, n))) for a, b in MAP_Y]
    return rows_both_decks(cases)


def radMesh():
    """Do the steps survive a finer mesh? Same sites as radMap1, 10 and 5 nm across the site, plus a 0.1 um
    site with the same total charge (the width most exposed to the mesh)."""
    MS = {"y3.00": (2.85, 3.15), "y1.50": (1.35, 1.65), "y-0.90": (-1.05, -0.75)}
    cases = []
    for lab, (a, b) in MS.items():
        for sp, sl in ((0.01, "m10"), (0.005, "m05")):
            cases.append(("hk", f"{lab}_{sl}", sitecase((a, b, 0.0, 0.05, 4e18)) + ";" + fine(a, b, sp)))
    a, b = MS["y3.00"]
    cases.append(("sin", "y3.00_m05", sitecase((a, b, 0.0, 0.05, 4e18)) + ";" + fine(a, b, 0.005)))
    cases.append(("hk", "y3.00_step0.1", sitecase((a, b, 0.0, 0.05, 4e18)) + ";Vd_step=0.1"))
    n01 = (1.45, 1.55, 0.0, 0.05, 1.2e19)
    cases.append(("hk", "w0.1", sitecase(n01)))
    for sp, sl in ((0.01, "m10"), (0.005, "m05")):
        cases.append(("hk", f"w0.1_{sl}", sitecase(n01) + ";" + fine(1.45, 1.55, sp)))
    return rows_on_decks(cases)


def radFam():
    """Vg family on SiN (R33 is SiN): is the current after a step independent of Vg?"""
    def s4(a, b):
        return (a, b, 0.0, 0.05, 4e18)
    cases = [("sin", "ref", ""),
             ("sin", "y-0.90", sitecase(s4(-1.05, -0.75))),
             ("sin", "y1.50", sitecase(s4(1.35, 1.65))),
             ("sin", "y3.00", sitecase(s4(2.85, 3.15))),
             ("sin", "3sites", sitecase(s4(1.05, 1.35), s4(1.95, 2.25), s4(2.85, 3.15))),
             ("sin", "ins1e18", f"{SKIP};insTrapSign=-1;damInsPeak=1e18;damInsM=0;damInsXmin=-0.05"),
             ("sin", "nb", f"{SURF};{SKIP};{sites((*Y_GATE, 0.0, 0.014, 5e17))}")]
    return rows_on_decks(cases, "VgFam={-2 -1.5 -1 -0.5 0 0.5}")


def radVth2():
    """Vth, second pass: the first buffer and dielectric cases could not act. A level 0.30 eV below Ec stays
    empty in the buffer, so those traps carry no charge: repeat with deep levels. The first ins cases
    inherited damYmin = 0.30: repeat with charge at the gate."""
    cases = []
    for lev in (1.0, 1.7):
        cases += [(f"buf{n:g}_L{lev:g}", sitecase((*Y_ALL, 0.1, 1.4, n)) + f";trapLevel={lev:g}")
                  for n in (1e16, 1e17, 5e17)]
    cases += [(f"insAll{n:g}", f"{SKIP};{INS};damInsPeak={n:g};damYmin=-1.3") for n in (1e17, 5e17, 1e18)]
    cases += [(f"insGate{n:g}", f"{SKIP};{INS};damInsPeak={n:g};damYmin=-0.35;damYmax=0.40")
              for n in (1e17, 5e17, 1e18)]
    return rows_both_decks(cases, "Vd_max=5.0")


def radRon():
    """Phase 4: Ron candidates with Ron(Vg), low Vd only."""
    cases = [("ref", ""), ("nb", f"{SURF};{SKIP};{sites((*Y_GATE, 0.0, 0.014, 5e17))}")]
    for lab, (a, b) in (("GD", Y_GD), ("SD", Y_SD), ("All", Y_ALL)):
        cases += [(f"mob{lab}{m:g}", f"mobDamFac={m:g};mobDamYmin={a:g};mobDamYmax={b:g}") for m in (0.8, 0.5, 0.3)]
    for lab, w in (("GD", Y_GD), ("SD", Y_SD)):
        cases += [(f"ch{lab}{n:g}", sitecase((*w, 0.015, 0.05, n))) for n in (1e17, 5e17, 2e18)]
    cases += [(f"algGD{n:g}", sitecase((*Y_GD, 0.0, 0.014, n))) for n in (5e17, 1e18, 5e18)]
    cases += [(f"insGD{n:g}", f"{SKIP};{INS};damInsPeak={n:g}") for n in (1e17, 5e17, 1e18)]
    return rows_both_decks(cases, "Vd_max=1.0;VgFam={-2 -1 0}")


def radStress():
    """Phase 4: damage that follows the irradiation field at a low exponent, with the stress solve."""
    return rows_both_decks([(f"f{m}_p{p:g}", f"damM={m};damPeak={p:g}") for m in (1, 2) for p in (5e17, 2e18)])


def radVth3():
    """Vth, third pass: charged buffer acceptors (back-gating). The model's buffer is undoped, with no
    electrons to fill a level at 1.0 or 1.7 eV (about 1e-26 of the traps are charged, checked locally).
    A level 3.3 eV below Ec is filled there."""
    cases = [(f"buf{n:g}_L3.3", sitecase((*Y_ALL, 0.1, 1.4, n)) + ";trapLevel=3.3") for n in (1e15, 1e16, 1e17)]
    return rows_both_decks(cases, "Vd_max=5.0")


def radFine():
    """After radMesh: the 0.3 um / 4e18 steps went away at 10 and 5 nm, the 0.1 um site kept a collapse.
    Always 5 nm here unless labelled. Where does a real collapse start, is it converged, and does the line
    after it depend on Vg? Fresh curves use Vg_out (no trap memory); VgFam keeps the traps filled by the
    earlier curves. Trap-free family curves (ref_G*) that radFam's ref could not finish: an empty trap
    density gets through the same off-state solves; G-1 checks it against the plain ref. final_m10: is the
    final SiN curve's two-step collapse also a mesh effect? radFinal11 set, 10 nm from 0.3 to 1.6 um."""
    sc = site_fine
    cases = []
    for n in (6e18, 8e18, 1.2e19):
        cases.append(("hk", f"y1.5_w0.3_n{n:g}", sc(1.5, 0.3, n)))
    for n in (4e18, 6e18, 8e18):
        cases.append(("hk", f"y1.5_w0.1_n{n:g}", sc(1.5, 0.1, n)))
    cases.append(("hk", "y1.5_w0.1_n1.2e19_m025", sc(1.5, 0.1, 1.2e19, 0.0025)))
    cases.append(("hk", "y3.0_w0.1_n1.2e19", sc(3.0, 0.1, 1.2e19)))
    cases.append(("hk", "y-0.9_w0.1_n1.2e19", sc(-0.9, 0.1, 1.2e19)))
    famv = "VgFam={-2 -1.5 -1 -0.5 0 0.5}"
    cases.append(("sin", "fam_y3.0_w0.3_n4e18", sc(3.0, 0.3, 4e18) + ";" + famv))
    cases.append(("sin", "fam_y1.5_w0.1_n1.2e19", sc(1.5, 0.1, 1.2e19) + ";" + famv))
    for vg in (-2, -1, 0):
        cases.append(("sin", f"fresh_y1.5_w0.1_n1.2e19_G{vg}", sc(1.5, 0.1, 1.2e19) + f";doIdVg=0;Vg_out={vg}"))
    for vg in (-1, -0.5, 0, 0.5):
        cases.append(("sin", f"ref_G{vg}", f"{SKIP};damSites={{{{-1.25 3.41 0 0.05 1}}}};doIdVg=0;Vg_out={vg}"))
    cases.append(("sin", "final_m10", sin_radfinal11_1027("0.3 0.01 1.6 0.01")))
    return rows_on_decks(cases)


# radMulti's three random strike orders, as random.Random(seed).sample(MULTI_POOL, 5) gave them on 2026-11-05
# (Python 3). The literals are the record; radMulti() asserts that the call still reproduces them.
MULTI_POOL = [-0.9, -0.6, -0.3, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0]
MULTI_ORDERS = {1: [-0.3, 2.1, -0.6, 0.6, 2.4],
                2: [-0.9, -0.6, 2.7, 0.9, -0.3],
                3: [0.3, 2.1, 1.8, -0.3, 0.9]}


def radMulti():
    """Phase 3d: multiple strikes. 0.1 um sites at 1.2e19 (the one site known to collapse on a fine mesh),
    5 nm in every site. Damage is static, so only the set matters, not the order. No site under the gate.
    Singles give the superposition check; radFine has HighK y 3.0, 1.5 and -0.9."""
    for seed, order in MULTI_ORDERS.items():
        assert random.Random(seed).sample(MULTI_POOL, 5) == order, \
            f"random.sample no longer gives radMulti order {seed}; MULTI_ORDERS is the record, drop this check"

    def multi(ys, n=1.2e19, w=0.1):
        ss = [site(y, w, n) for y in ys]
        lines = " ".join(f"{a:g} 0.005 {b:g} 0.005" for a, b, *_ in ss)
        return sitecase(*ss) + ";meshY={" + lines + "}"
    cases = []
    for y in MULTI_POOL:
        for d in ("hk", "sin"):
            if d == "hk" and y in (-0.9, 1.5, 3.0):
                continue
            cases.append((d, f"ms_s_y{y:g}", multi([y])))
    drn = [0.6, 1.2, 1.8, 2.4, 3.0]
    gate = drn[::-1]
    sets = [(f"drn_k{k}", drn[:k]) for k in range(2, 6)] + [(f"gat_k{k}", gate[:k]) for k in range(2, 5)]
    for seed, order in MULTI_ORDERS.items():
        sets += [(f"r{seed}_k{k}", sorted(order[:k])) for k in range(2, 6)]
    for lab, ys in sets:
        for d in ("hk", "sin"):
            cases.append((d, f"ms_{lab}", multi(ys)))
    return rows_on_decks(cases)


# ---------------------------------------------------------------- 2026-11-05/07: trap emission
ESITES = (("A", 3.0, 0.3, 4e18), ("B", 1.5, 0.3, 8e18), ("C", 1.5, 0.1, 1.2e19))


def radEmit():
    """Trap emission (Ian, 2026-11-05): fill-only and fully fresh are the two extremes tried so far.
    emitFrac: some of the excess charge leaks per capture call. emitRest: some leaks at rest between curves,
    which could leave low Vd normal and then refill onto a line. SiN, 5 nm in the site."""
    cases = []
    for lab, y, w, n in ESITES:
        for f in (0.01, 0.03, 0.1, 0.3, 1.0):
            cases.append(("sin", f"site{lab}_ef{f:g}", site_fine(y, w, n) + f";emitFrac={f:g};doIdVg=0"))
    for lab, y, w, n in ESITES[:2]:
        for r in (0.5, 0.9, 0.99):
            cases.append(("sin", f"site{lab}_er{r:g}",
                          site_fine(y, w, n) + f";emitRest={r:g};doIdVg=0;VgFam={{-1.5 -1 -0.5 0 0.5}}"))
    return rows_on_decks(cases)


def radEmit2():
    """emitRest again, with TeTrap reset at rest. 1e-9 = charge kept, electrons cold: the memory case."""
    cases = []
    for lab, y, w, n in ESITES[:2]:
        for r in (1e-9, 0.5, 0.9, 0.99):
            cases.append(("sin", f"site{lab}_er{r:g}",
                          site_fine(y, w, n) + f";emitRest={r:g};doIdVg=0;VgFam={{-1.5 -0.5 0.5}}"))
    return rows_on_decks(cases)


def radEmit3():
    """After radEmit2: do site B's drops at emitRest 0.9 survive 2.5 nm, and what happens between full memory
    and 50% released, where low Vd goes from dead to normal?"""
    fam3 = "doIdVg=0;VgFam={-1.5 -0.5 0.5}"
    cases = [("sin", "siteB_er0.9_m025", site_fine(1.5, 0.3, 8e18, 0.0025) + f";emitRest=0.9;{fam3}"),
             ("sin", "siteB_er0.99_m025", site_fine(1.5, 0.3, 8e18, 0.0025) + f";emitRest=0.99;{fam3}")]
    for lab, y, w, n in ESITES[:2]:
        for r in (0.1, 0.2, 0.3):
            cases.append(("sin", f"site{lab}_er{r:g}", site_fine(y, w, n) + f";emitRest={r:g};{fam3}"))
    return rows_on_decks(cases)


# ---------------------------------------------------------------- 2026-11-07: fine-mesh checks
def radChk2():
    """Fine-mesh check of what the Oct 29 slides rest on (Ian): the biased curves at 10 nm."""
    return [("hk_b_m10", B_RADCHK2_1107), ("sin_b_m10", f"{B_RADCHK2_1107}{SIN}")]


def radGauss():
    """The fixed Gaussian trap set of job 47062225 at 5 nm through pulsedIV, and Gaussians at 0.55 eV."""
    rows = []
    for y in (1.0, 2.4):
        rows.append(pulsed_gauss(f"hk_y{y:g}_L0.3_m05", "hk", y, 0.30, 0.005, peak=5e18))
        rows.append(pulsed_gauss(f"sin_y{y:g}_L0.3_m05", "sin", y, 0.30, 0.005, peak=5e18))
        rows.append(pulsed_gauss(f"hk_y{y:g}_L0.55", "hk", y, 0.55, 0, peak=4e18))
        rows.append(pulsed_gauss(f"hk_y{y:g}_L0.55_m05", "hk", y, 0.55, 0.005, peak=4e18))
    return rows


def radMap2():
    """Refined position map: radMap1's 14 windows at 5 nm, including under the gate."""
    cases = [(f"y{(a + b) / 2:.2f}_n{n:g}", sitecase((a, b, 0.0, 0.05, n)) + ";" + fine(a, b, 0.005))
             for n in (4e18, 8e18) for a, b in MAP_Y]
    return rows_both_decks(cases)


def radGauss2():
    """After radGauss: Gaussian traps at hotEb 1.0 collapse abruptly at 5 nm, unlike the uniform sites at
    hotEb 0.5. Is it converged, is it the shape or the barrier, and does the onset move with Vg?"""
    rows = [pulsed_gauss("hk_L0.3_m025", "hk", 1.0, 0.30, 0.0025),
            pulsed_gauss("hk_L0.55_m025", "hk", 1.0, 0.55, 0.0025),
            pulsed_gauss("hk_L0.3_eb0.5", "hk", 1.0, 0.30, 0.005, ";hotEb=0.5"),
            pulsed_gauss("hk_L0.3_s0.1", "hk", 1.0, 0.30, 0.005, ";trapSigma=0.1", half=0.35)]
    rows += [pulsed_gauss(f"sin_L0.3_G{vg:g}", "sin", 1.0, 0.30, 0.005, f";Vg_meas={vg:g}") for vg in (-1.5, -0.5, 0)]
    return rows


# ---------------------------------------------------------------- 2026-11-09/13: the Nov 11 model and its tests
def nb_eb1(tail):
    """radEB1 / radExp3 non-biased lines on both decks (labels nb_highk_*, nb_sin_*)."""
    return [(d, join(NB_RADFINAL8_1026, dl, SKIP, DAM2_GATE) + tail) for d, dl in NB_DECKS]


def radEB1():
    """(Ian OK, 2026-11-09, test only): the final parameter set with the capture barrier at 1.0 eV instead of
    0.5, 10 nm over y 0.3-2.0. A Gaussian collapses on a fine mesh at 1.0 but not at 0.5."""
    rows = [("hk_b_eb1", f"{B_RADCHK2_1107};hotEb=1.0{EB}"),
            ("sin_b_eb1", f"{B_RADCHK2_1107}{SIN};hotEb=1.0{EB}"),
            ("sin_b_eb0.75", f"{B_RADCHK2_1107}{SIN};hotEb=0.75{EB}"),
            ("sin_final_eb1", f"{sin_radfinal11_1027('0.3 0.01 2.0 0.01')};noRampBack=1;hotEb=1.0")]
    rows += [(f"nb_{d}_eb1", lev) for d, lev in nb_eb1(f";noRampBack=1;hotEb=1.0{EB}")]
    return rows


def radEB2():
    """radEB1 showed SiN drops at hotEb 1.0 on 10 nm; check them at 5 nm before they count."""
    return [("sin_b_eb1_m05", f"{B_RADCHK2_1107}{SIN};hotEb=1.0{EB};meshY={{0.3 0.005 2.0 0.005}}"),
            ("sin_final_eb1_m05", f"{sin_radfinal11_1027('0.3 0.005 2.0 0.005')};noRampBack=1;hotEb=1.0")]


def radFinal12(chk, eb1):
    """Final rad model from 2026-11-11 (Ian): hotEb 1.0, 10 nm over y 0.3-2.0, one damage law for all
    devices, no hand-placed second site. Same inputs as radChk (pre) and radEB1 (nb, b), so those runs are
    its results. The biased stress stopped at 17 V in those runs (old occupancy overflow); said explicitly."""
    rows = [(lab, lev) for lab, lev in chk if lab.startswith("pre_")]
    for lab, lev in eb1:
        if lab in ("hk_b_eb1", "sin_b_eb1"):
            rows.append((lab, lev + ";Vd_stress=17.0"))
        elif lab in ("nb_highk_eb1", "nb_sin_eb1"):
            rows.append((lab, lev))
    return rows


def radExp1():
    """2026-11-11 exploration from the new final set (hotEb 1.0): onset too early, no converged second step,
    current recovers after the drop. Damage scale, trap level, and a smooth (Gaussian) second strike."""
    FE = B_RADEB1_1109
    rows = [(f"sin_p{p:g}", f"{FE}{SIN};damPeak={p:g}") for p in (4.5e18, 3e18, 2e18)]
    for lev in (0.40, 0.50):
        rows.append((f"hk_L{lev:g}", f"{FE};trapLevel={lev:g}"))
        rows.append((f"sin_L{lev:g}", f"{FE}{SIN};trapLevel={lev:g}"))
    for d, dl, y, n in (("sin", SIN, 1.5, 5e18), ("sin", SIN, 1.5, 3e18), ("sin", SIN, 2.4, 5e18),
                        ("hk", "", 1.5, 5e18)):
        rows.append((f"{d}_g{y:g}_n{n:g}", f"{FE}{dl}{gauss([(y, n)])}{strike_mesh([y])}"))
    return rows


def radExp1b():
    """radExp1's SiN deep-level tasks overflowed in the trap occupancy ramping down from the stress (the
    Oct 29 exp() overflow, reached sooner with a deeper level). occSafe is the exact overflow-free form."""
    return [(f"sin_L{lev:g}_os", f"{B_RADEB1_1109}{SIN};trapLevel={lev:g};occSafe=1;Vd_stress=17.0")
            for lev in (0.40, 0.50)]


def radExp2():
    """After radExp1/1c (2026-11-12). From here every stressed run uses occSafe with the stress pinned at 17 V
    (occSafe is exact; without it the Gaussian SiN stresses stalled or overflowed near 17 V)."""
    FO = B_OS17_1112
    rows = [(f"sin_g{y:g}_n{n:g}", f"{FO}{SIN}{gauss([(y, n)])}{strike_mesh([y])}")
            for y, n in ((1.5, 5e18), (1.5, 3e18), (2.4, 5e18))]
    rows += [(f"sin_p{p:g}", f"{FO}{SIN};damPeak={p:g}") for p in (5e18, 5.5e18, 6e18)]
    rows += [(f"sin_L{lev:g}_p{p:g}", f"{FO}{SIN};trapLevel={lev:g};damPeak={p:g}")
             for lev, p in ((0.5, 3e18), (0.5, 5e18), (0.4, 5e18))]
    return rows


def radExp3():
    """2026-11-12 (Ian: more tests aimed at the measured data), from the final set with occSafe and 17 V.
    (a) later onset: cooler hot electrons (hotTau); (b) stress at the real 28 V, where the field widens and
    may place damage in two regions; (c) onset against Vg for the final SiN curve, fresh curves; (d) Ron(Vg)
    at low Vd, biased against non-biased, both decks."""
    FO = B_OS17_1112
    rows = [(f"sin_tau{tau:g}", f"{FO}{SIN};hotTau={tau:g}") for tau in (5e-15, 7e-15)]
    rows += [(f"{d}_s28_p{p:g}", f"{FO}{dl};Vd_stress=28.0;damPeak={p:g};meshY={{0.3 0.01 2.6 0.01}}")
             for d, dl, p in (("sin", SIN, 1.5e18), ("sin", SIN, 2.5e18), ("hk", "", 2.5e18))]
    rows += [(f"sin_G{vg:g}", f"{FO}{SIN};doIdVg=0;Vg_out={vg:g}") for vg in (-1, 0, 0.5)]
    rv = ";Vd_max=1.0;VgFam={-2 -1 0};noRampBack=0"
    rows += [("hk_b_ron", f"{FO}{rv}"), ("sin_b_ron", f"{FO}{SIN}{rv}")]
    rows += [(f"nb_{d}_ron", lev) for d, lev in nb_eb1(f";hotEb=1.0{rv}")]
    return rows


def radHV(final12):
    """2026-11-12 (Ian): final model at higher drain voltage, Id-Vd to 28 V at Vg +1 and 0. occSafe keeps the
    occupancy from overflowing above ~17.7 V during the measurement too (exact form, same results below)."""
    hv = ";Vd_max=28.0;Vd_step=0.2;VgFam={0};noRampBack=0;occSafe=1"
    return [(f"{lab}_hv", f"{lev}{hv}") for lab, lev in final12]


def radStrike2():
    """2026-11-12 (Ian): how does the second strike's position set the Vd of the second dip? The one-site final
    curve already dips (393 at 6.3 V to 333 at 7.7 V, 5 nm). Smooth second strike (sigma 40 nm, 3e18) along
    the drift region on the final SiN set, plus the final set with its field-placed damage cut off past y 1.0
    and 0.7 um to find where the existing dip comes from."""
    FO = B_OS17_1112
    rows = [(f"sin_s2_y{y:g}", f"{FO}{SIN}{gauss([(y, '3e18')])}{strike_mesh([y], top=max(2.6, y + 0.2))}")
            for y in (0.8, 1.2, 2.0, 2.4, 2.8, 3.1)]
    rows += [(f"sin_cut{ym:g}", f"{FO}{SIN};damYmax={ym:g}") for ym in (1.0, 0.7)]
    return rows


def rad28fit():
    """2026-11-12 (Ian): the final model moves to a 28 V stress. Refit the damage scale at 28 V on the final set
    (hotEb 1.0, occSafe, 10 nm over y 0.3-2.6). radExp3 already has SiN 1.5e18 / 2.5e18 and HighK 2.5e18."""
    rows = [(f"sin_s28_p{p:g}", f"{B_S28_1112}{SIN};damPeak={p:g}") for p in (1e18, 2e18, 3e18, 4e18)]
    rows += [(f"hk_s28_p{p:g}", f"{B_S28_1112};damPeak={p:g}") for p in (1.5e18, 4e18)]
    return rows


def radStrikeN():
    """2026-11-13 (Ian): slides comparing 1, 2 and 3 ion strikes in SiN and HighK. Final set (17 V stress,
    hotEb 1.0, occSafe), biased, plus N Gaussian strikes (sigma 40 nm, 3e18, at the AlGaN top) at y 0.8, 1.6,
    2.4 um, added in that order. N = 0 is rerun on the same mesh (10 nm over y 0.3-2.6, 5 nm within 0.16 um
    of each strike)."""
    return [(f"{deck}_N{n}", f"{B_OS17_1112}{dk}{strikes('3e18', n)}{strike_mesh(STRIKES_Y[:n])}")
            for deck, dk in (("sin", SIN), ("hk", "")) for n in range(4)]


# ---------------------------------------------------------------- 2026-11-14/16: saved stress states
def radStressIO():
    """2026-11-14 (Ian): check stressSave / stressLoad on HPG. Task 0: final SiN set (17 V, occSafe, 10 nm to
    2.6 um) with stressSave. Tasks 1-2 (submitted after task 0 finishes): the same set loaded from task 0's
    file, and the same plus one Gaussian strike at y 0.8 um. Task 1 must reproduce task 0's curves."""
    iof = f"{B_OS17_1112}{SIN};meshY={{0.3 0.01 2.6 0.01}}"
    io_file = f"{HPG_RESULTS}/20261114_radStressIO/task_0/stress_sin17.str"
    return [("sin_save", f"{iof};stressSave=stress_sin17.str"),
            ("sin_load", f"{iof};stressLoad={io_file}"),
            ("sin_load_g0.8", f"{iof};stressLoad={io_file}{gauss([(0.8, '3e18')])}")]


def rad28strike():
    """2026-11-15 (Ian): strike count at the 28 V stress, using stressSave/stressLoad. Tasks 0-1 run the 28 V
    stress once per deck on the mesh refined at all three strike positions and save it (damPeak 1.5e18,
    0 strikes). Tasks 2-15 load that stress: damage scale 1.5e18 (1-3 strikes) and 2e18 (0-3 strikes), both
    decks, same strikes as radStrikeN (3e18, sigma 40 nm, y 0.8 / 1.6 / 2.4 um)."""
    r28 = f"{HPG_RESULTS}/20261115_rad28strike"
    decks = (("sin", SIN, 0), ("hk", "", 1))   # deck, deck lever, task that saves its stress
    rows = [(f"{deck}28_p1.5e+18_N0", f"{B_S28_1115}{dk};damPeak=1.5e18;stressSave=stress_{deck}28.str")
            for deck, dk, _ in decks]
    for deck, dk, t in decks:
        src = f"{r28}/task_{t}/stress_{deck}28.str"
        for p, ns in ((1.5e18, (1, 2, 3)), (2e18, (0, 1, 2, 3))):
            rows += [(f"{deck}28_p{p:g}_N{n}", f"{B_S28_1115}{dk};damPeak={p:g}{strikes('3e18', n)};stressLoad={src}")
                     for n in ns]
    return rows


def stressLib():
    """2026-11-15 (Ian): stress library. Off-state stress at Vg -10 V ramped in 1 V steps to 84 V (advertised
    breakdown), state at bias saved at every volt (stressSaveEvery, stressOnly), final model on the mesh
    refined at the three strike positions, both decks. Files go to /blue (not the 40 GB home). damPeak is
    only there so the stress branch runs; no damage is placed (stressOnly). A run that stops is continued
    with stressResume=<last file>."""
    return [(f"lib_{deck}_Vg-10",
             f"{LIB_STRESS_1115}{dk};stressSaveDir={LIB}/{deck}_Vg-10;stressSavePrefix={deck}_Vg-10")
            for deck, dk in (("sin", SIN), ("hk", ""))]


def rad28strikeL():
    """2026-11-16 (Ian): fallback for rad28strike. If its stress-saving tasks can't reach 28 V within their
    48 h limit, load the same 28 V stress from the stress library (stressLib: identical deck, mesh, levers
    and 1 V steps) for all 16 cases."""
    return [(f"{deck}28_p{p:g}_N{n}",
             f"{B_S28_1115}{dk};damPeak={p:g}{strikes('3e18', n)};stressLoad={lib_state(deck)}")
            for deck, dk in (("sin", SIN), ("hk", "")) for p in (1.5e18, 2e18) for n in range(4)]


# ---------------------------------------------------------------- 2026-11-17/18: stepped curves (rounds A-K)
def radStepA():
    """2026-11-17 goal (Ian): stepped SiN curves at the 28 V stress with 1-3 strikes on top of the stress
    damage. Every task loads the library's 28 V SiN state (strike-refined mesh). Round A: damage scale alone;
    strike density 4-8e18 (3e18 does nothing on its own; ~5e18 Gaussians collapse alone at hotEb 1.0) with 1
    or 3 strikes at two damage scales; graded densities so each strike might trigger at its own Vd. Id-Vd at
    Vg +1 to 12 V."""
    G28 = LOAD28_SIN_1117
    rows = [(f"A_p{p:g}_N0", f"{G28};damPeak={p:g}") for p in (1.6e18, 1.7e18, 1.8e18)]
    for p in (1.5e18, 1.7e18):
        for n in (4e18, 5e18, 6e18, 8e18):
            rows.append((f"A_p{p:g}_n{n:g}_N1", f"{G28};damPeak={p:g}{gauss([(0.8, n)])}"))
            rows.append((f"A_p{p:g}_n{n:g}_N3", f"{G28};damPeak={p:g}{gauss([(0.8, n), (1.6, n), (2.4, n)])}"))
    rows.append(("A_p1.5e+18_g456_N3", f"{G28};damPeak=1.5e18{gauss([(0.8, 4e18), (1.6, 5e18), (2.4, 6e18)])}"))
    rows.append(("A_p1.5e+18_g654_N3", f"{G28};damPeak=1.5e18{gauss([(0.8, 6e18), (1.6, 5e18), (2.4, 4e18)])}"))
    return rows


def radStepB():
    """2026-11-17 goal, round B (in parallel with A): levers A doesn't touch. SiN, 28 V library state, Vd to
    12 V, damage scale 1.5e18 unless noted. Trap level (also deepens the stress-damage traps), strike width
    (narrow TRIM-like and wide), strike depth below the 2DEG, strikes nearer the gate, wide graded densities,
    capture time, scale 1.6e18, and two-strike cases."""
    P3 = STRIKES_Y
    rows = [(f"B_lev{lv:g}_n5e18_N3", f"trapLevel={lv:g};{L3}{gauss([(y, 5e18) for y in P3])}")
            for lv in (0.35, 0.40, 0.45)]
    rows += [(f"B_s0.02_n{n:g}_N3", f"{L3}{gauss_w([(y, 0.0, 0.02, n) for y in P3])}") for n in (8e18, 1.2e19)]
    for n in (3e18, 4e18):
        rows.append((f"B_s0.1_n{n:g}_N1", f"{L3}{gauss_w([(0.8, 0.0, 0.1, n)])}"))
        rows.append((f"B_s0.1_n{n:g}_N3", f"{L3}{gauss_w([(y, 0.0, 0.1, n) for y in P3])}"))
    rows.append(("B_x0.03_n6e18_N3", f"{L3}{gauss_w([(y, 0.03, 0.04, 6e18) for y in P3])}"))
    rows += [(f"B_near_n{n:g}_N3", f"{L3}{gauss([(y, n) for y in (0.5, 0.8, 1.1)])}") for n in (5e18, 6e18)]
    rows.append(("B_g369_N3", f"{L3}{gauss([(0.8, 3e18), (1.6, 6e18), (2.4, 9e18)])}"))
    rows.append(("B_g963_N3", f"{L3}{gauss([(0.8, 9e18), (1.6, 6e18), (2.4, 3e18)])}"))
    rows += [(f"B_tau{tau:g}_n5e18_N3", f"hotTau={tau:g};{L3}{gauss([(y, 5e18) for y in P3])}")
             for tau in (5e-15, 2e-14)]
    rows += [(f"B_p1.6_n{n:g}_N3", f"damPeak=1.6e18{gauss([(y, n) for y in P3])}") for n in (5e18, 6e18)]
    rows.append(("B_n6e18_N2", f"{L3}{gauss([(0.8, 6e18), (1.6, 6e18)])}"))
    rows.append(("B_s0.1_n4e18_N2", f"{L3}{gauss_w([(0.8, 0.0, 0.1, 4e18), (1.6, 0.0, 0.1, 4e18)])}"))
    return [(lab, f"{LOAD28_SIN_1117};{lev}") for lab, lev in rows]


def radStepC():
    """2026-11-17 goal, round C: round A found steps with 6-8e18 strikes (6e18, 1 strike at 1.5e18: drops at
    ~2 V and ~6.3 V, the Nov 11 shape; 8e18, 3 strikes: drops near 1.8, 3.9, 6.7 V). Complete matched 0-3
    strike series (N2 cases, 7e18 in between, 1.6e18 scale, N0 to 12 V) and the HighK counterparts (28 V
    HighK library state)."""
    G28, G28HK = LOAD28_SIN_1117, LOAD28_HK_1117
    rows = [("C_p1.7_n6e18_N2", G28, "damPeak=1.7e18" + strikes(6e18, 2)),
            ("C_p1.5_n8e18_N2", G28, "damPeak=1.5e18" + strikes(8e18, 2)),
            ("C_p1.7_n8e18_N2", G28, "damPeak=1.7e18" + strikes(8e18, 2)),
            ("C_p1.5_N0", G28, "damPeak=1.5e18")]
    rows += [(f"C_p1.5_n7e18_N{k}", G28, "damPeak=1.5e18" + strikes(7e18, k)) for k in (1, 2, 3)]
    rows += [(f"C_p1.6_n6e18_N{k}", G28, "damPeak=1.6e18" + strikes(6e18, k)) for k in (1, 2)]
    rows += [(f"C_hk_p1.5_n6e18_N{k}", G28HK, "damPeak=1.5e18" + strikes(6e18, k)) for k in (0, 1, 2, 3)]
    rows += [(f"C_hk_p1.5_n8e18_N{k}", G28HK, "damPeak=1.5e18" + strikes(8e18, k)) for k in (1, 2, 3)]
    return [(lab, f"{base};{lev}") for lab, base, lev in rows]


def radStepD():
    """2026-11-17 goal, round D: checks the literature review asks for. Convergence (Vd step halved to 0.05 V;
    the mesh is already 5 nm round each strike) for the stepped cases, and knock-out of single strikes from
    the three-8e18-strike case (independent sites keep their steps at the same Vd; a cascade moves them)."""
    rows = [("D_p1.5_n6e18_N1_dv05", "damPeak=1.5e18" + strikes(6e18, 1) + ";Vd_step=0.05"),
            ("D_p1.7_n6e18_N3_dv05", "damPeak=1.7e18" + strikes(6e18, 3) + ";Vd_step=0.05"),
            ("D_p1.5_n8e18_N3_dv05", "damPeak=1.5e18" + strikes(8e18, 3) + ";Vd_step=0.05"),
            ("D_p1.5_n8e18_ko1", "damPeak=1.5e18" + gauss([(1.6, 8e18), (2.4, 8e18)])),
            ("D_p1.5_n8e18_ko2", "damPeak=1.5e18" + gauss([(0.8, 8e18), (2.4, 8e18)]))]
    return [(lab, f"{LOAD28_SIN_1117};{lev}") for lab, lev in rows]


def radStepE():
    """2026-11-17 goal, round E (Ian: fill ee1-b): directions from the literature review (kb
    rad-literature-steps). Stress Vd series (24 and 30 V states from the library; damage scale adjusted for
    the E^4 law: (28/Vd)^4), strikes at the field-plate edges (y 0.9 and 0.3, then 2.0), trap level 0.40 with
    6e18 strikes, wider strikes (sigma 60 nm), and Vg families (0 and -1 V) for the best stepped cases."""
    G28 = LOAD28_SIN_1117
    rows = [(f"E_vs{vd:g}_p{p:g}_n6e18_N{k}", load_at_1117(vd), f"damPeak={p:g}" + strikes(6e18, k))
            for vd, p in ((24.0, 2.8e18), (30.0, 1.15e18)) for k in (0, 1, 3)]
    fpp = (0.9, 0.3, 2.0)
    rows += [(f"E_fp_n6e18_N{k}", G28, "damPeak=1.5e18" + gauss([(y, 6e18) for y in fpp[:k]])) for k in (1, 2, 3)]
    rows += [(f"E_lev0.4_n6e18_N{k}", G28, "trapLevel=0.40;damPeak=1.5e18" + strikes(6e18, k)) for k in (1, 2, 3)]
    rows += [(f"E_s0.06_n6e18_N{k}", G28, "damPeak=1.5e18" + gauss_w([(y, 0.0, 0.06, 6e18) for y in STRIKES_Y[:k]]))
             for k in (1, 2, 3)]
    for lab, lev in (("E_fam_n6e18_N1", "damPeak=1.5e18" + strikes(6e18, 1)),
                     ("E_fam_n6e18_N3", "damPeak=1.5e18" + strikes(6e18, 3)),
                     ("E_fam_n8e18_N3", "damPeak=1.5e18" + strikes(8e18, 3))):
        rows.append((lab, G28, lev + ";VgFam={0 -1}"))
    return [(lab, f"{base};{lev}") for lab, base, lev in rows]


def radStepF():
    """2026-11-17 goal, round F: trap level 0.40 eV with 6e18 strikes gave a staircase whose step count grows
    with the strike count (E_lev0.4: 3 steps near 1.7 / 2.9 / 4.4 V with 3 strikes). Complete it: 0 strikes,
    HighK counterparts, strike densities 5e18 and 7e18, and Vd step 0.05 V for the 1-3 strike cases."""
    G28, G28HK = LOAD28_SIN_1117, LOAD28_HK_1117
    rows = [("F_lev0.4_N0", G28, L4)]
    rows += [(f"F_hk_lev0.4_n6e18_N{k}", G28HK, L4 + strikes(6e18, k)) for k in range(4)]
    rows += [(f"F_lev0.4_n{n:g}_N{k}", G28, L4 + strikes(n, k)) for n in (5e18, 7e18) for k in (1, 2, 3)]
    rows += [(f"F_lev0.4_n6e18_N{k}_dv05", G28, L4 + strikes(6e18, k) + ";Vd_step=0.05") for k in (1, 2, 3)]
    return [(lab, f"{base};{lev}") for lab, base, lev in rows]


def radStepG():
    """2026-11-17 goal, round G: strikes of 6e18 and up collapse HighK too (C_hk, F_hk), which the measured
    HighK devices don't do. Find the strike-density window where SiN still steps and HighK stays flat: HighK
    and SiN at 5e18 / 5.5e18 (trap level 0.30) and 4e18 / 5e18 (trap level 0.40), 1-3 strikes."""
    G28, G28HK = LOAD28_SIN_1117, LOAD28_HK_1117
    rows = []
    for n in (5e18, 5.5e18):
        rows += [(f"G_hk_n{n:g}_N{k}", G28HK, L3 + strikes(n, k)) for k in (1, 2, 3)]
    rows += [("G_n5e18_N2", G28, L3 + strikes(5e18, 2))]
    rows += [(f"G_n5.5e18_N{k}", G28, L3 + strikes(5.5e18, k)) for k in (1, 2, 3)]
    for n in (4e18, 5e18):
        rows += [(f"G_hk_lev0.4_n{n:g}_N{k}", G28HK, L4 + strikes(n, k)) for k in (1, 2, 3)]
    rows += [(f"G_lev0.4_n4e18_N{k}", G28, L4 + strikes(4e18, k)) for k in (1, 2, 3)]
    return [(lab, f"{base};{lev}") for lab, base, lev in rows]


def radStepH():
    """2026-11-18 goal, round H: strikes dense enough to step SiN (>= 5e18) also step HighK (round G), so strike
    damage alone can't keep HighK flat. Field-scaled strikes (new lever gaussFieldM: strike density times
    (Estress/damEref)^m from the stored 28 V field): under the T-gate overhang SiN's field is 2.1x HighK's
    (y 0.5), so strikes there are dense in SiN and weak in HighK. Strikes at y 0.5, then 0.35, then 0.65 um
    (150 nm apart), both decks, scale 1.5e18, trap level 0.30; plus field-scaled 6e18 strikes at the old
    positions as a check."""
    POH = (0.5, 0.35, 0.65)
    decks = (("sin", LOAD28_SIN_1117), ("hk", LOAD28_HK_1117))
    rows = []
    for tag, extra, n in (("nofm_n3e18", "", 3e18), ("fm4_n3e18", ";gaussFieldM=4", 3e18),
                          ("fm4_n2e18", ";gaussFieldM=4", 2e18), ("fm2_n4e18", ";gaussFieldM=2", 4e18)):
        for deck, base in decks:
            rows += [(f"H_{deck}_{tag}_N{k}", base, "damPeak=1.5e18" + strikes(n, k, POH) + extra) for k in (1, 2, 3)]
    for deck, base in decks:
        rows.append((f"H_{deck}_fm4_old_n6e18_N3", base, "damPeak=1.5e18" + strikes(6e18, 3) + ";gaussFieldM=4"))
    return [(lab, f"{base};{lev}") for lab, base, lev in rows]


def radStepI():
    """2026-11-18 goal, round I: round H's field-scaled strikes keep HighK flat to 7 V, but a single SiN strike
    at y 0.5 (base 2-4e18, m 2 or 4) collapses SiN completely at 0.4-1.0 V, so strikes 2-3 add nothing. SiN's
    28 V field exceeds HighK's over y 0.45-0.65 um ((E_SiN/E_HK)^4 = 3.7-30 at 10 nm depth). Lower base
    densities: one strike at y 0.5 (3e17 / 6e17 / 1e18) or y 0.6 / 0.65; and three strikes spread over the
    band (0.65, 0.6, 0.55 in that order). Band a has no N1 line: it would equal y0.65_n3e18_N1."""
    rows = []
    for deck, base in (("sin", LOAD28_SIN_1117), ("hk", LOAD28_HK_1117)):
        rows += [(f"I_{deck}_y0.5_n{n:g}_N1", base, "damPeak=1.5e18" + gauss([(0.5, n)]) + ";gaussFieldM=4")
                 for n in (3e17, 6e17, 1e18)]
        rows += [(f"I_{deck}_y{y:g}_n{n:g}_N1", base, "damPeak=1.5e18" + gauss([(y, n)]) + ";gaussFieldM=4")
                 for y, n in ((0.6, 1e18), (0.65, 3e18))]
        for tag, trio, ks in (("a", ((0.65, 3e18), (0.6, 1e18), (0.55, 3e17)), (2, 3)),
                              ("b", ((0.65, 2e18), (0.6, 6e17), (0.55, 2e17)), (1, 2, 3))):
            rows += [(f"I_{deck}_band{tag}_N{k}", base, "damPeak=1.5e18" + gauss(trio[:k]) + ";gaussFieldM=4")
                     for k in ks]
    return [(lab, f"{base};{lev}") for lab, base, lev in rows]


def meshChkStress():
    """2026-11-18 (Ian: check the mesh refinement of the strike steps). Every round A-I task loads the library
    mesh (stressLoad keeps the file's mesh): 93,080 points, but the deck's own rightFP line (y 0.725, 20 nm)
    sits inside the 0.64-0.96 meshY patch, so the y 0.8 strike is on ~15 nm cells (2.7 per sigma), while 1.6
    and 2.4 are on a true 5 nm; the SiN E^4 damage core (y 0.48-0.63) is on 6-10 nm. No A-I case has a
    second mesh. Two new 28 V SiN stresses (stressOnly, saved every volt so a stalled run can resume), same
    levers as the library, on MESHCHK m10 (~64k points) and m5fix (~99k points). Loading runs follow once
    saved."""
    return [(f"mc_sin_{tag}", f"{B_RADEB1_1109};occSafe=1;Vd_stress=28.0;stressStep=1.0;meshY={{{my}}};damPeak=1.5e18;"
                              f"stressOnly=1;stressSaveEvery=1.0{SIN};stressSaveDir={LIB}/meshchk/sin_{tag};"
                              f"stressSavePrefix=sin_{tag}")
            for tag, my in MESHCHK.items()]


def radStepJ():
    """2026-11-18 goal, round J: field-scaled strikes keep HighK flat but give SiN one drop that only deepens
    with more strikes (round I), because every SiN-favoured strike sits in the same band (y 0.45-0.65) and
    shares the first capture onset. Levers that might separate the onsets inside the band: a deeper trap level
    (0.40 eV gave the plain-strike staircases, rounds E/F; 0.35 as a middle value), and strikes at different
    depths in the band (x 0, 30 and 60 nm below the AlGaN top). Both decks; field scaling m 4 throughout."""
    G28, G28HK = LOAD28_SIN_1117, LOAD28_HK_1117
    bandb = ((0.65, 2e18), (0.6, 6e17), (0.55, 2e17))
    rows = []
    for lv in (0.40, 0.35):
        for deck, base in (("sin", G28), ("hk", G28HK)):
            ks = (1, 2, 3) if (lv == 0.40 or deck == "sin") else (3,)
            rows += [(f"J_{deck}_lev{lv:g}_bandb_N{k}", base, f"trapLevel={lv:g};damPeak=1.5e18" + gauss(bandb[:k]) +
                      ";gaussFieldM=4") for k in ks]
    for deck, base in (("sin", G28), ("hk", G28HK)):
        rows += [(f"J_{deck}_lev0.4_y0.5_n{n:g}_N1", base, "trapLevel=0.40;damPeak=1.5e18" + gauss([(0.5, n)]) +
                  ";gaussFieldM=4") for n in (3e17, 6e17, 1e18)]
    depth = ((0.55, 0.0, 0.04, 6e17), (0.55, 0.03, 0.04, 6e17), (0.55, 0.06, 0.04, 6e17))
    rows += [(f"J_sin_depth_N{k}", G28, "damPeak=1.5e18" + gauss_w(depth[:k]) + ";gaussFieldM=4") for k in (1, 2, 3)]
    rows += [("J_hk_depth_N3", G28HK, "damPeak=1.5e18" + gauss_w(depth) + ";gaussFieldM=4")]
    rows += [("J_sin_lev0.4_bandb_N3_dv05", G28, "trapLevel=0.40;damPeak=1.5e18" + gauss(bandb) +
              ";gaussFieldM=4;Vd_step=0.05")]
    return [(lab, f"{base};{lev}") for lab, base, lev in rows]


# The deliverable's row A series (0-3 plain 6e18 strikes at scale 1.5e18) and the other two best step cases.
CHK_CASES = ("C_p1.5_N0", "A_p1.5e+18_n6e+18_N1", "B_n6e18_N2", "A_p1.5e+18_n6e+18_N3", "E_lev0.4_n6e18_N2",
             "C_p1.5_n8e18_N2")


def meshChkLoad(tag, a, b, c, e):
    """2026-11-18: loading runs for the mesh check of the strike steps (meshChkStress 51883722): CHK_CASES rerun
    on each new 28 V stress (m10, m5fix), the same lines as the library runs with stressLoad and meshY swapped
    (stressLoad takes the file's mesh anyway; meshY is matched so the deck build agrees). Submitted with
    afterok on each stress task."""
    orig = by_label(a, b, c, e)
    return [(f"{tag}_{lab}", to_mesh(orig[lab], MESHCHK[tag], meshchk_state(tag))) for lab in CHK_CASES]


def radStepK():
    """2026-11-18 goal, round K: hybrid strikes. A field-scaled strike near the gate (damGaussF, 2e18 at y 0.65
    um, m 4: SiN partial drop 386 -> 174, HighK untouched; round I band b N1) plus 1-3 plain strikes further
    out (damGauss at y 0.8 / 1.6 / 2.4 um, unscaled) at 3e18 or 4e18, below the density that drops HighK
    (5e18; 3e18 left HighK flat, rad28strikeL). Does SiN, with its near-gate region already collapsed, step
    on the far strikes while HighK stays flat? Plus plain 4e18 HighK (trap level 0.30) to place HighK's
    threshold between 3e18 and 5e18."""
    nearf = gauss([(0.65, 2e18)], lever="damGaussF") + ";gaussFieldMF=4"
    rows = []
    for deck, base in (("sin", LOAD28_SIN_1117), ("hk", LOAD28_HK_1117)):
        for nf in (3e18, 4e18):
            rows += [(f"K_{deck}_hyb_far{nf:g}_N{k}", base, "damPeak=1.5e18" + nearf + strikes(nf, k))
                     for k in (1, 2, 3)]
    rows += [(f"K_hk_n4e18_N{k}", LOAD28_HK_1117, "damPeak=1.5e18" + strikes(4e18, k)) for k in (1, 2, 3)]
    return [(lab, f"{base};{lev}") for lab, base, lev in rows]


def seeMap28():
    """2026-11-18 (Ian): Fig. 5-style strike maps at the irradiation bias (after the local proof of concept at
    Vg -5 / Vd 10 V): SiN and HighK, Vg -10 / Vd 28 V, strike at y 0.2 um (between the gate foot's drain
    edge and the field plate), tau 2 ps, maps from DC to 1 ns. drivers/seeIV.tcl via DRV=seeIV."""
    return [("sin_y0.2_map", f"{SEE28_1118}{SIN}"), ("hk_y0.2_map", SEE28_1118)]


# ---------------------------------------------------------------- 2026-11-19/20: resume, diagnostics, mesh series
def stressLibResume(lib):
    """2026-11-19 (Ian): resume the SiN stress library from its last state (Vd 60 V at the 4-day limit)."""
    lab, lev = lib[0]
    assert lab == "lib_sin_Vg-10", lab
    return [(f"{lab}_r60", f"{lev};stressResume={lib_state('sin', 60.0)}")]


def radStepDiag(a, b, c):
    """2026-11-19 (Ian): the deliverable's row A series with vdCuts (filled traps, electrons, lateral field, Te
    along y at every Vd) to show which damage fills at each drop."""
    orig = by_label(a, b, c)
    return [(f"D_{lab}", f"{orig[lab]};vdCuts=1")
            for lab in ("C_p1.5_N0", "A_p1.5e+18_n6e+18_N1", "B_n6e18_N2", "A_p1.5e+18_n6e+18_N3")]


def radStepDiag5(m5fix, a):
    """2026-11-19: the 5 nm mesh check (meshChkLoad_m5fix 51939192) keeps the stress-only drop but shrinks and
    moves the strike steps, so the per-Vd diagnostic cuts are repeated on the m5fix mesh for the cases that
    still step there, plus the library-mesh 1-strike case (three drops there), now that VdCuts also cuts the
    AlGaN barrier."""
    keep = ("C_p1.5_N0", "A_p1.5e+18_n6e+18_N1", "E_lev0.4_n6e18_N2", "C_p1.5_n8e18_N2")
    rows = [(f"D5_{lab}", f"{lev};vdCuts=1") for lab, lev in m5fix if lab.split("_", 1)[1] in keep]
    rows.append(("D5_lib_A_p1.5e+18_n6e+18_N1", f"{by_label(a)['A_p1.5e+18_n6e+18_N1']};vdCuts=1"))
    return rows


def radStepM(a, c, e, f):
    """2026-11-19 goal (stop hook: the stepped 1/2/3-strike series must survive mesh refinement). On m5fix
    (5 nm over y 0.64-0.96) row A's plain 6e18 strikes at trap 0.30 lose their 2- and 3-strike steps, but
    trap 0.40 with two 6e18 strikes keeps three drops on all three meshes (library 1.4/2.7/10.4, m10
    1.4/3.1/7.7, m5fix 1.4/2.4/6.3 V) and 8e18 at trap 0.30 keeps two. radStepM: full 0-3 strike series at
    those settings on the m5fix stress (trap 0.40 with 5, 6, 7e18; trap 0.30 with 7 and 8e18), plus the
    trap-0.40 6e18 series on m10, all with vdCuts."""
    orig = by_label(a, c, e, f)
    cases = {"m5fix": ("F_lev0.4_N0", "E_lev0.4_n6e18_N1", "E_lev0.4_n6e18_N3", "F_lev0.4_n5e+18_N1",
                       "F_lev0.4_n5e+18_N2", "F_lev0.4_n5e+18_N3", "F_lev0.4_n7e+18_N1", "F_lev0.4_n7e+18_N2",
                       "F_lev0.4_n7e+18_N3", "A_p1.5e+18_n8e+18_N1", "A_p1.5e+18_n8e+18_N3", "C_p1.5_n7e18_N1",
                       "C_p1.5_n7e18_N2", "C_p1.5_n7e18_N3"),
             "m10": ("F_lev0.4_N0", "E_lev0.4_n6e18_N1", "E_lev0.4_n6e18_N3")}
    return [(f"M_{tag}_{lab}", f"{to_mesh(orig[lab], MESHCHK[tag], meshchk_state(tag))};vdCuts=1")
            for tag, labs in cases.items() for lab in labs]


def meshChkStress2p5(mc):
    """2026-11-19: 2.5 nm at the three strike sites (m2p5), same levers as the library and meshChkStress, saved
    every volt."""
    lab, lev = mc[0]
    assert lab == "mc_sin_m10", lab
    lev = swap(swap(lev, f"meshY={{{MESHCHK['m10']}}}", f"meshY={{{M2P5}}}"), "sin_m10", "sin_m2p5", count=2)
    return [("mc_sin_m2p5", lev)]


def radStepM2(a, f):
    """radStepM2 (2026-11-19 night): on m5fix, trap 0.40 eV with 7e18 strikes gives one drop per strike (1 / 2 /
    3 drops with 1 / 2 / 3 strikes) and trap 0.30 with 8e18 keeps 2 / 3 / 3 drops as on the library mesh. Same
    series on m10 for the three-mesh check (m10 C_p1.5_n8e18_N2 exists from meshChkLoad)."""
    orig = by_label(a, f)
    return [(f"M_m10_{lab}", f"{to_mesh(orig[lab], MESHCHK['m10'], meshchk_state('m10'))};vdCuts=1")
            for lab in ("F_lev0.4_n7e+18_N1", "F_lev0.4_n7e+18_N2", "F_lev0.4_n7e+18_N3", "A_p1.5e+18_n8e+18_N1",
                        "A_p1.5e+18_n8e+18_N3")]


def radStepM3(a, c, e, f):
    """radStepM3 (2026-11-20): the four-mesh check. The stepping series on the 2.5 nm stress (meshChkStress2p5
    52044407, Ian: keep it running): trap 0.30 / 8e18 (mesh-robust 2/3/3 on library, m10, m5fix), trap 0.40 /
    7e18 (1/2/3 on m5fix only) and trap 0.40 / 6e18, with their no-strike references. Submitted once
    sin_m2p5_Vd028.00.str.gz exists."""
    orig = by_label(a, c, e, f)
    m3 = ("C_p1.5_N0", "A_p1.5e+18_n8e+18_N1", "C_p1.5_n8e18_N2", "A_p1.5e+18_n8e+18_N3", "F_lev0.4_N0",
          "F_lev0.4_n7e+18_N1", "F_lev0.4_n7e+18_N2", "F_lev0.4_n7e+18_N3", "E_lev0.4_n6e18_N1", "E_lev0.4_n6e18_N2",
          "E_lev0.4_n6e18_N3")
    return [(f"M_m2p5_{lab}", f"{to_mesh(orig[lab], M2P5, meshchk_state('m2p5'))};vdCuts=1") for lab in m3]


# ---------------------------------------------------------------- 2026-11-20: FP contact fix
# (Ian: "Let's fix that contact node bug"): the FP contact box covered the drain half of the T-gate head
# (kb/results/fp-contact-fix.md); the decks now build a box that matches the FP metal (fpBoxOld 0, default).
# A saved state carries its own contacts, so every earlier library state still has the old box (radIV refuses
# to load it unless fpBoxOld=1).
def fpFixPre(map1):
    """Pre-irradiation baseline, both decks (radMap1 hk_ref / sin_ref, unchanged levers)."""
    return [(f"fpfix_{lab}", lev) for lab, lev in map1 if lab in ("sin_ref", "hk_ref")]


def fpFixStress(lib):
    """The 28 V stress library again (stressLib levers, saved every volt to 28 V), both decks."""
    rows = []
    for lab, lev in lib:
        deck = "sin" if "rfdevice_SiN.tcl" in lev else "hk"
        lev = swap(lev, "Vd_stress=84.0", "Vd_stress=28.0")
        lev = swap(lev, f"stressSaveDir={LIB}/{deck}_Vg-10;stressSavePrefix={deck}_Vg-10",
                   f"stressSaveDir={FIXLIB}/{deck}_Vg-10;stressSavePrefix=fpfix_{deck}_Vg-10")
        rows.append((f"fpfix_{lab}", lev))
    return rows


def fpFixEB1(eb1):
    """The Nov 11 model (radEB1, 17.66 V stress from scratch), all six cases."""
    return [(f"fpfix_{lab}", lev) for lab, lev in eb1]


def fpFixLoad(a, b, c, i):
    """After fpFixStress: stress-only, damage scale, mesh-robust 8e18 series, row A, field-scaled band b, SiN and
    HighK, loading the new states (same labels with an fpfix_ prefix)."""
    orig = by_label(a, b, c, i)
    load = ("C_p1.5_N0", "A_p1.6e+18_N0", "A_p1.8e+18_N0",                                   # SiN stress only, scale
            "A_p1.5e+18_n8e+18_N1", "C_p1.5_n8e18_N2", "A_p1.5e+18_n8e+18_N3",               # mesh-robust series
            "A_p1.5e+18_n6e+18_N1", "B_n6e18_N2", "A_p1.5e+18_n6e+18_N3",                    # row A
            "I_sin_bandb_N1", "I_sin_bandb_N2", "I_sin_bandb_N3",                            # field-scaled, SiN
            "C_hk_p1.5_n6e18_N0", "C_hk_p1.5_n8e18_N1", "C_hk_p1.5_n8e18_N2", "C_hk_p1.5_n8e18_N3",
            "I_hk_bandb_N1", "I_hk_bandb_N2", "I_hk_bandb_N3")
    cuts = {"C_p1.5_N0", "A_p1.5e+18_n8e+18_N1", "C_p1.5_n8e18_N2", "A_p1.5e+18_n8e+18_N3"}
    rows = []
    for lab in load:
        lev, n = orig[lab], 0
        for deck in ("sin", "hk"):
            old = f"stressLoad={lib_state(deck)}"
            if old in lev:
                lev = swap(lev, old, f"stressLoad={fpfix_state(deck)}")
                n += 1
        assert n == 1, lab
        rows.append((f"fpfix_{lab}", f"{lev}{';vdCuts=1' if lab in cuts else ''}"))
    return rows


def fpFixMesh(mc, mc2p5):
    """(Ian: "queue it now"): the mesh check again with the fixed FP box, SiN, the same levers as meshChkStress:
    m5fix (5 nm over y 0.64-0.96) and m2p5 (2.5 nm at the three strike sites), saved every volt."""
    assert mc2p5[0][0] == "mc_sin_m2p5", mc2p5[0][0]
    rows = []
    for tag, lab, lev in (("m5fix", "mc_sin_m5fix", by_label(mc)["mc_sin_m5fix"]), ("m2p5", *mc2p5[0])):
        lev = swap(lev, f"{LIB}/meshchk/sin_{tag}", f"{FIXLIB}/meshchk/sin_{tag}")
        lev = swap(lev, f"stressSavePrefix=sin_{tag}", f"stressSavePrefix=fpfix_sin_{tag}")
        rows.append((f"fpfix_{lab}", lev))
    return rows


def fpFixEB1p(eb1):
    """radEB1 sets no Vd_stress or occSafe, so its stress stopped where the ramp failed (17.66 V). With the fixed
    FP box the ramp may stop elsewhere; this copy of the biased cases pins Vd_stress at 17.66 V for a
    like-for-like comparison with the Nov 11 curves."""
    rows = []
    for lab, lev in eb1:
        if lab.startswith("nb_"):
            continue
        assert "Vd_stress" not in lev, lab
        rows.append((f"fpfix_p_{lab}", f"{lev};Vd_stress=17.66"))
    return rows


def fpFixScaleEB1(eb1p):
    """(Ian 2026-11-21: refit the damage scale first.) With the fixed FP box the Nov 11 scale (7e18) gives ~5x the
    damage: SiN biased collapses completely and HighK drops. The biased SiN and HighK cases of fpFixEB1p (17.66 V
    pinned) at damPeak 7e17-3e18."""
    rows = []
    base = by_label(eb1p)
    for lab in ("fpfix_p_sin_b_eb1", "fpfix_p_hk_b_eb1"):
        for dp in ("7e17", "1e18", "1.5e18", "2e18", "3e18"):
            rows.append((f"{lab.replace('fpfix_p_', 'fpscale_')}_d{dp}", f"{base[lab]};damPeak={dp}"))
    return rows


def fpFixScale28(load):
    """(Ian 2026-11-21: refit the damage scale first; replaces running fpFixLoad at the old 1.5-1.8e18.) 28 V stress
    damage only on the fixed-box library, SiN and HighK, damPeak 1e17-1.5e18 (the fpFixLoad N0 lines, vdCuts kept
    on SiN)."""
    rows = []
    base = by_label(load)
    for lab in ("fpfix_C_p1.5_N0", "fpfix_C_hk_p1.5_n6e18_N0"):
        deck = "hk" if "_hk_" in lab else "sin"
        for dp in ("1e17", "2e17", "3e17", "5e17", "7e17", "1e18", "1.5e18"):
            rows.append((f"fpscale28_{deck}_d{dp}", f"{base[lab]};damPeak={dp}"))
    return rows


def fpFixScale28b(load):
    """2026-11-24: refine fpFixScale28 (52354341 / 52385669) around the target SiN drop (old C_p1.5_N0: 395 -> 281
    mA/mm at 1.6-2.0 V; 5e17 gave 481 -> 421, 7e17 gave 332 -> 120): SiN 5.5e17 / 6e17 / 6.5e17, HighK 6e17."""
    base = by_label(load)
    rows = [(f"fpscale28_sin_d{dp}", f"{base['fpfix_C_p1.5_N0']};damPeak={dp}") for dp in ("5.5e17", "6e17", "6.5e17")]
    rows += [(f"fpscale28_hk_d{dp}", f"{base['fpfix_C_hk_p1.5_n6e18_N0']};damPeak={dp}") for dp in ("6e17",)]
    return rows


# ---------------------------------------------------------------- 2026-11-22: remakes with the fixed FP box
# (Ian: "Remake everything post Nov 11 model. Send it to HPG"). Same rows, label prefix fx_, field-dependent damage
# rescaled (radparams.rescale_damage), saved states swapped to their fixed-box versions. The 28 V rounds wait for
# the 28 V scale refit (fpFixScale28); these do not depend on it.
def fxRadHV(hv):
    """radHV (Nov 11 model measured to Vd 28 V, Vg +1 and 0) at the refit Nov 11 scale."""
    return fx_rows(hv, R_NOV11)


def fxRadStrike2(s2):
    """radStrike2 (second-strike position on the Nov 11 SiN set, true 17 V stress) at the refit Nov 11 scale."""
    return fx_rows(s2, R_NOV11)


def fxRadStrikeN(sn):
    """radStrikeN (0-3 plain 3e18 strikes on the Nov 11 set, both decks) at the refit Nov 11 scale."""
    return fx_rows(sn, R_NOV11)


def fxSeeMap28(see):
    """seeMap28 (strike transient maps at Vg -10 / Vd 28 V) with the fixed deck; no damage to rescale."""
    return fx_rows(see, 1.0)


def fxMeshStressM10(mc):
    """The 10 nm uniform 28 V SiN stress (meshChkStress m10) with the fixed FP box, saved every volt, for the
    three-mesh remakes (fpFixMesh already has m5fix and m2p5). stressOnly, so the damage scale is not used."""
    row = [(lab, lev) for lab, lev in mc if lab == "mc_sin_m10"]
    assert len(row) == 1
    lab, lev = row[0]
    lev = swap(lev, f"{LIB}/meshchk/sin_m10", f"{FIXLIB}/meshchk/sin_m10")
    lev = swap(lev, "stressSavePrefix=sin_m10", "stressSavePrefix=fpfix_sin_m10")
    return [(f"fpfix_{lab}", lev)]


# ---------------------------------------------------------------- registry, in build (and history) order
# base sets for --show, as (name, levers)
B1104 = ("BASE_1104", BASE_1104)
BNB8 = ("NB_RADFINAL8_1026", NB_RADFINAL8_1026)
BCHK2 = ("B_RADCHK2_1107", B_RADCHK2_1107)
BEB1 = ("B_RADEB1_1109", B_RADEB1_1109)
BOS17 = ("B_OS17_1112", B_OS17_1112)
BS28 = ("B_S28_1112", B_S28_1112)
BS28L = ("B_S28_1115", B_S28_1115)
BLIB = ("LIB_STRESS_1115", LIB_STRESS_1115)
BGAUSS = ("PULSED_GAUSS_1107", PULSED_GAUSS_1107)
LOADSIN = ("LOAD28_SIN_1117", LOAD28_SIN_1117)
STEP_PARENTS = ("radStepA", "radStepB", "radStepC", "radStepE")
STUDIES = [
    Study("radChk", radChk, base=BNB8),
    Study("radVth", radVth, base=B1104),
    Study("radMap1", radMap1, base=B1104),
    Study("radMesh", radMesh, base=B1104),
    Study("radFam", radFam, base=B1104),
    Study("radVth2", radVth2, base=B1104),
    Study("radRon", radRon, base=B1104),
    Study("radStress", radStress, base=B1104),
    Study("radVth3", radVth3, base=B1104),
    Study("radFine", radFine, base=B1104),
    Study("radMulti", radMulti, base=B1104),
    Study("radEmit", radEmit, base=B1104),
    Study("radEmit2", radEmit2, base=B1104),
    Study("radEmit3", radEmit3, base=B1104),
    Study("radChk2", radChk2, base=BCHK2),
    Study("radGauss", radGauss, base=BGAUSS, driver="pulsedIV"),
    Study("radMap2", radMap2, base=B1104),
    Study("radGauss2", radGauss2, base=BGAUSS, driver="pulsedIV"),
    Study("radEB1", radEB1, base=BCHK2),
    Study("radEB2", radEB2, base=BCHK2),
    Study("radFinal12", radFinal12, ("radChk", "radEB1"), base=BEB1),
    Study("radExp1", radExp1, base=BEB1),
    Study("radExp1b", radExp1b, base=BEB1),
    Study("radExp2", radExp2, base=BOS17),
    Study("radExp3", radExp3, base=BOS17),
    Study("radHV", radHV, ("radFinal12",), base=BEB1),
    Study("radStrike2", radStrike2, base=BOS17),
    Study("rad28fit", rad28fit, base=BS28),
    Study("radStrikeN", radStrikeN, base=BOS17),
    Study("radStressIO", radStressIO, base=BOS17),
    Study("rad28strike", rad28strike, base=BS28L),
    Study("stressLib", stressLib, base=BLIB),
    Study("rad28strikeL", rad28strikeL, base=BS28L),
    Study("radStepA", radStepA, base=LOADSIN),
    Study("radStepB", radStepB, base=LOADSIN),
    Study("radStepC", radStepC, base=LOADSIN),
    Study("radStepD", radStepD, base=LOADSIN),
    Study("radStepE", radStepE, base=LOADSIN),
    Study("radStepF", radStepF, base=LOADSIN),
    Study("radStepG", radStepG, base=LOADSIN),
    Study("radStepH", radStepH, base=LOADSIN),
    Study("radStepI", radStepI, base=LOADSIN),
    Study("meshChkStress", meshChkStress, base=BEB1),
    Study("radStepJ", radStepJ, base=LOADSIN),
    Study("meshChkLoad_m10", lambda *p: meshChkLoad("m10", *p), STEP_PARENTS, base=LOADSIN),
    Study("meshChkLoad_m5fix", lambda *p: meshChkLoad("m5fix", *p), STEP_PARENTS, base=LOADSIN),
    Study("radStepK", radStepK, base=LOADSIN),
    Study("seeMap28", seeMap28, base=("SEE28_1118", SEE28_1118), driver="seeIV"),
    Study("stressLibResume", stressLibResume, ("stressLib",), base=BLIB),
    Study("radStepDiag", radStepDiag, ("radStepA", "radStepB", "radStepC"), base=LOADSIN),
    Study("radStepDiag5", radStepDiag5, ("meshChkLoad_m5fix", "radStepA"), base=LOADSIN),
    Study("radStepM", radStepM, ("radStepA", "radStepC", "radStepE", "radStepF"), base=LOADSIN),
    Study("meshChkStress2p5", meshChkStress2p5, ("meshChkStress",), base=BEB1),
    Study("radStepM2", radStepM2, ("radStepA", "radStepF"), base=LOADSIN),
    Study("radStepM3", radStepM3, ("radStepA", "radStepC", "radStepE", "radStepF"), base=LOADSIN),
    Study("fpFixPre", fpFixPre, ("radMap1",), base=B1104),
    Study("fpFixStress", fpFixStress, ("stressLib",), base=BLIB),
    Study("fpFixEB1", fpFixEB1, ("radEB1",), base=BCHK2),
    Study("fpFixLoad", fpFixLoad, ("radStepA", "radStepB", "radStepC", "radStepI"), base=LOADSIN),
    Study("fpFixMesh", fpFixMesh, ("meshChkStress", "meshChkStress2p5"), base=BEB1),
    Study("fpFixEB1p", fpFixEB1p, ("radEB1",), base=BCHK2),
    Study("fpFixScaleEB1", fpFixScaleEB1, ("fpFixEB1p",), base=BCHK2),
    Study("fpFixScale28", fpFixScale28, ("fpFixLoad",), base=LOADSIN),
    Study("fpFixScale28b", fpFixScale28b, ("fpFixLoad",), base=LOADSIN),
    Study("fxRadHV", fxRadHV, ("radHV",), base=BEB1),
    Study("fxRadStrike2", fxRadStrike2, ("radStrike2",), base=BOS17),
    Study("fxRadStrikeN", fxRadStrikeN, ("radStrikeN",), base=BOS17),
    Study("fxSeeMap28", fxSeeMap28, ("seeMap28",), base=("SEE28_1118", SEE28_1118), driver="seeIV"),
    Study("fxMeshStressM10", fxMeshStressM10, ("meshChkStress",), base=BEB1),
]

if __name__ == "__main__":
    sys.exit(run(STUDIES, __doc__))
