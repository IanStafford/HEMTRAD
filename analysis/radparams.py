"""Lever strings, builders and the params-file rail shared by the params generators.

Used by analysis/genRadStudy.py (the 2D rad-model studies) and analysis/genRad3d.py (the 3D slice
studies). Importing this module has no side effects: nothing is read or written until a generator
calls run().

Params line format (sweeps/radIV.slurm): label|lever=value;lever=value;...
radIV.slurm splits the line at the first '|', splits the rest at ';', and turns each pair into
`set lever value` ahead of the driver, in order. So when a line sets a lever twice, the last value
wins. Most base sets below were built as "older set + overrides", so many lines repeat a lever
(NB_RADFINAL8_1026 sets hotEb 1.0 and then 0.5, for example). `--show` prints the value that wins.
The driver's own defaults apply to every lever a line does not set (kb/model/levers.md).

Units: y is um along the channel (gate foot -0.125 to 0.125, drain side positive), x is um below the
AlGaN top, trap and damage densities are cm^-3. Damage formats: damSites {ymin ymax xmin xmax N};
damGauss and damGaussF {y x sigma N} (kb/model/damage-model.md).

Names. The base sets are named by their source (the study that first used them, or what they hold)
and date (MMDD of 2026), because several of them were once each called "the final set". Labels
written into params files are frozen: they name task directories and figures. Two deck tags are in
use for that reason: 'hk' in most labels, 'highk' in the labels built from NB_DECKS (pre_ and nb_ of
radChk, nb_ of radEB1 and radExp3) and in their copies in radFinal12, radHV and fpFixEB1.

The rail (run, emit). A committed params file is the record of what a job ran. A generator run writes
a file only when it is new or its content is unchanged. When a git-tracked file would change it
refuses, prints the diff, and exits non-zero at the end, unless that study is named with --force.
"""
import argparse
import difflib
import os
import subprocess
import sys
from collections import namedtuple

# ---- calibration: the rad baseline of 2026-10-23 (kb/device/calibration.md)
CAL = "polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100"
PRE = f"{CAL};radState=pre"
POST = f"{CAL};radState=post"

# ---- damage and trap blocks (kb/model/damage-model.md)
# Stress-field damage law 1 of the Oct 27 model: TrapN = min(damMax, damPeak*(E_lat/damEref)^damM) in the top
# 50 nm (x <= damXmax) for y >= 0.30 um, as acceptor traps 0.30 eV below Ec. damPeak is set per study.
DAM_LAW = "damXmax=0.05;damMax=1e20;trapLevel=0.30;damField=lat;damEref=5.0e5;damM=4;damYmin=0.30"
# Law 2 as a hand-placed uniform site (dam2M 0): 5e17 in the AlGaN (x <= 14 nm) under the gate foot.
DAM2_GATE = "dam2Field=lat;dam2M=0;dam2Ymin=-0.125;dam2Ymax=0.125;dam2Peak=5e17;dam2Xmax=0.014"
HOT_TAU = "hotTau=1e-14"
SURF = "surfCharge=-4.0e11"          # fixed charge at the AlGaN/passivation surface
SKIP = "stressSkip=1"                # no stress solve: hand-placed damage only
INS = "insTrapSign=-1;damInsM=0;damInsXmin=-0.05"   # uniform negative charge in the 50 nm passivation

# ---- decks
SIN_DECK = "deviceDeck=rfdevice_SiN.tcl"
SIN = ";" + SIN_DECK                 # for appending to a lever string
DECKS = (("hk", ""), ("sin", SIN_DECK))
NB_DECKS = (("highk", ""), ("sin", SIN_DECK))   # radChk's pre_/nb_ and the nb_ of radEB1, radExp3 say 'highk'
DECK_FILE = {"hk": "rfdevice.tcl", "sin": "rfdevice_SiN.tcl"}   # explicit deviceDeck for pulsedIV
YSRC, YDRN = -1.25, 3.41             # mesh edges (y)
Y_GATE = (-0.125, 0.125)             # under the gate foot
Y_ALL = (YSRC, YDRN)                 # the whole channel
Y_GD = (0.125, 3.285)                # gate to drain
Y_SD = (YSRC, -0.125)                # source to gate
STRIKES_Y = (0.8, 1.6, 2.4)          # the three strike positions of radStrikeN on (um)

# ---- base sets, by first study and date. Each is an older set plus overrides, so levers repeat.
# radChk/radVth base (11-04): Oct 27 damage law, hotEb 0.5, no damPeak, no surface charge.
BASE_1104 = f"{POST};hotEb=0.5;{HOT_TAU};{DAM_LAW};retryDepth=8;noRampBack=1"
# The non-biased (nb) case of radFinal8 (10-26): no field damage (damPeak 0), surface charge; effective hotEb 0.5.
NB_RADFINAL8_1026 = f"{POST};{SURF};hotEb=1.0;{HOT_TAU};{DAM_LAW};damPeak=0.0;hotEb=0.5"
# The biased set of radChk2 (11-07): damPeak 7e18 + the gate site, hotEb 0.5, 10 nm over y 0.3-2.0.
B_RADCHK2_1107 = (f"{POST};{SURF};hotEb=0.5;{HOT_TAU};{DAM_LAW};damPeak=7e18;{DAM2_GATE};noRampBack=1;"
                  "meshY={0.3 0.01 2.0 0.01}")
# radEB1's biased HighK line (11-09) = the Nov 11 model of radFinal12 (hotEb 1.0), without its Vd_stress.
B_RADEB1_1109 = f"{B_RADCHK2_1107};hotEb=1.0;Vd_step=0.1;retryDepth=8"
# From radExp2 (11-12) on: occSafe with the stress pinned at 17 V.
B_OS17_1112 = f"{B_RADEB1_1109};occSafe=1;Vd_stress=17.0"
# rad28fit (11-12): the 28 V stress, 10 nm over y 0.3-2.6.
B_S28_1112 = f"{B_RADEB1_1109};occSafe=1;Vd_stress=28.0;meshY={{0.3 0.01 2.6 0.01}}"


def sin_radfinal11_1027(mesh):
    """The SiN set of radFinal11 (10-27): damPeak 6e18, the gate site and a third site (dam3Peak 4.5e18),
    meshY={mesh}. Used by radFine, radEB1 and radEB2."""
    return (f"{POST};{SURF};hotEb=1.0;{HOT_TAU};{DAM_LAW};{SIN_DECK};damPeak=6e18;hotEb=0.5;{DAM2_GATE};"
            f"dam3Peak=4.5e18;Vd_step=0.1;retryDepth=8;meshY={{{mesh}}}")


# The pulsedIV Gaussian trap set of job 47062225 (Oct 29 slides), for radGauss / radGauss2 (DRV=pulsedIV).
PULSED_GAUSS_1107 = ("trapEn=1;trapSigma=0.04;trapMeanX=0.0;trapWidth=0.1;hotEb=1.0;hotTau=1e-14;hotMu=600;"
                     "hotVsat=1.9e7;fillIters=4;fillRelax=0.5;eTemp=0;Vg_meas=1.0;Vd_max=10.0;Vd_step=0.1;"
                     "dampValue=0.05;mobModel=field")
# seeIV strike maps at the irradiation bias (11-18, seeMap28, DRV=seeIV).
SEE28_1118 = (f"{CAL};occSafe=1;Vd_bias=28;Vg_bias=-10;seeY0=0.2;seeGenTau=2e-12;seeTend=1e-9;"
              "seeMapTimes={3e-12 6e-12 1.2e-11 3e-11 1e-10 3e-10 1e-9};seeMapDC=1;seeCutTimes={}")

# ---- saved stress states (kb/workflow/stress-library.md). States saved before the FP contact fix of
# 2026-11-20 have the old FP box; radIV refuses to load or resume them unless fpBoxOld=1.
LIB = "/blue/ee1/ianstafford/stress"            # the stress library on /blue
FIXLIB = f"{LIB}/fpfix"                         # states saved with the fixed FP box
HPG_RESULTS = "/home/ianstafford/blue/ee1/ianstafford/HEMTRAD/results"   # results/ of the HPG checkout


def lib_state(deck, vd=28.0):
    """Library state of deck 'sin' or 'hk' at Vg -10 V and Vd vd."""
    return f"{LIB}/{deck}_Vg-10/{deck}_Vg-10_Vd{vd:06.2f}.str.gz"


def meshchk_state(tag):
    """28 V SiN state of the mesh check (meshChkStress / meshChkStress2p5) on mesh tag m10, m5fix or m2p5."""
    return f"{LIB}/meshchk/sin_{tag}/sin_{tag}_Vd028.00.str.gz"


def fpfix_state(deck):
    """28 V state of fpFixStress (fixed FP box), deck 'sin' or 'hk'."""
    return f"{FIXLIB}/{deck}_Vg-10/fpfix_{deck}_Vg-10_Vd028.00.str.gz"


# ---- mesh patches (meshY={y0 spacing y1 spacing ...}). Never put a meshY line exactly on a deck line
# (zero-area faces abort FLOOXS).
def fine(y0, y1, sp):
    """meshY lever (no leading ';'): spacing sp from y0 to y1."""
    return f"meshY={{{y0:g} {sp:g} {y1:g} {sp:g}}}"


def strike_mesh(ys, top=2.6, half=0.16):
    """';meshY=...': 10 nm over y 0.3-top plus 5 nm within half of each strike position in ys."""
    s = f"0.3 0.01 {top:g} 0.01"
    for y in ys:
        s += f" {y - half:g} 0.005 {y + half:g} 0.005"
    return f";meshY={{{s}}}"


LIB_MESH = strike_mesh(STRIKES_Y)[1:]   # the stress library's mesh (stressLib, rad28strike, rounds A-K)
# The mesh check of the strike steps (2026-11-18). m10: 10 nm over 0.3-2.6 (helper lines 0.715 / 0.735 cancel
# the deck's 20 nm rightFP line at 0.725). m5fix: the library mesh with a true 5 nm at y 0.8 (helper lines
# 0.72 / 0.73). m2p5 (M2P5): m5fix at 2.5 nm.
MESHCHK = {"m10": "0.3 0.01 0.715 0.01 0.735 0.01 2.6 0.01",
           "m5fix": "0.3 0.01 2.6 0.01 0.64 0.005 0.72 0.005 0.73 0.005 0.96 0.005 1.44 0.005 1.76 0.005 2.24 0.005 "
                    "2.56 0.005"}
M2P5 = ("0.3 0.01 2.6 0.01 0.64 0.0025 0.72 0.0025 0.73 0.0025 0.96 0.0025 1.44 0.0025 1.76 0.0025 2.24 0.0025 "
        "2.56 0.0025")


# ---- 28 V stress and library loading sets (they need lib_state and strike_mesh above)
# The 28 V stress on the library mesh (rad28strike, 11-15).
B_S28_1115 = f"{B_RADEB1_1109};occSafe=1;Vd_stress=28.0{strike_mesh(STRIKES_Y)}"
# The stress library (stressLib, 11-15): Vg -10 V, ramped in 1 V steps to 84 V, stress only, saved every volt.
LIB_STRESS_1115 = (f"{B_RADEB1_1109};occSafe=1;Vd_stress=84.0;stressStep=1.0{strike_mesh(STRIKES_Y)};"
                   "damPeak=1.5e18;stressOnly=1;stressSaveEvery=1.0")
# Rounds A-K (11-17 on): load the library's 28 V state, Id-Vd at Vg +1 to 12 V.
LOAD28_SIN_1117 = f"{B_S28_1115}{SIN};stressLoad={lib_state('sin')};Vd_max=12.0;doIdVg=0"
LOAD28_HK_1117 = f"{B_S28_1115};stressLoad={lib_state('hk')};Vd_max=12.0;doIdVg=0"
LIB_SRC = f"stressLoad={lib_state('sin')}"


def load_at_1117(vd):
    """As LOAD28_SIN_1117 with the SiN library state at another stress Vd (radStepE)."""
    return (f"{B_RADEB1_1109};occSafe=1;Vd_stress={vd:g}{strike_mesh(STRIKES_Y)}{SIN};"
            f"stressLoad={lib_state('sin', vd)};Vd_max=12.0;doIdVg=0")


# ---- uniform damage boxes (law 5)
def sites(*s):
    """damSites lever from boxes (ymin, ymax, xmin, xmax, N)."""
    return "damSites={" + " ".join("{" + " ".join(f"{v:g}" for v in q) + "}" for q in s) + "}"


def sitecase(*s):
    """No stress solve, damage only in the given boxes."""
    return f"{SKIP};{sites(*s)}"


def site(yc, w, n):
    """Box of width w centred at yc, top 50 nm, density n."""
    return (yc - w / 2, yc + w / 2, 0.0, 0.05, n)


def site_fine(yc, w, n, sp=0.005):
    """One box (site) with mesh spacing sp across it."""
    s = site(yc, w, n)
    return sitecase(s) + ";" + fine(s[0], s[1], sp)


# ---- Gaussian strikes (laws 6 and 7)
def num(v):
    """A density as written: a float formats with :g (3e18 -> 3e+18), a str is kept as written ('3e18')."""
    return v if isinstance(v, str) else f"{v:g}"


def gauss(pairs, lever="damGauss"):
    """';damGauss=...' with strikes at the AlGaN top, sigma 40 nm: pairs of (y, N). The text is '0.0 0.04'."""
    return f";{lever}={{" + " ".join(f"{{{y:g} 0.0 0.04 {num(n)}}}" for y, n in pairs) + "}"


def gauss_w(items):
    """';damGauss=...' from (y, x, sigma, N). All four format with :g, so x 0 is written '0', not '0.0'."""
    return ";damGauss={" + " ".join(f"{{{y:g} {x:g} {s:g} {n:g}}}" for y, x, s, n in items) + "}"


def strikes(n, k, ys=STRIKES_Y):
    """The first k strikes of density n at positions ys ('' when k is 0)."""
    return gauss([(y, n) for y in ys[:k]]) if k else ""


# ---- FP-fix remakes (2026-11-22, Ian: "Remake everything post Nov 11 model"). The FP contact box fixed on 2026-11-20
# raised the stress-field damage at the gate edge ~5x at a given scale (kb/results/fp-contact-fix.md), so a remake
# multiplies every FIELD-DEPENDENT damage density by a ratio r and leaves field-independent damage alone.
R_NOV11 = 1.5e18 / 7e18        # Nov 11 scale refit with the fixed box (fpFixScaleEB1 52223190): 7e18 -> 1.5e18


def _scale_braces(val, r):
    """Scale the 4th number of every {y x sigma N} in a strike list."""
    import re
    def one(m):
        y, x, sg, n = m.group(1).split()
        return "{" + f"{y} {x} {sg} {float(n) * r:g}" + "}"
    return re.sub(r"\{([^{}]+)\}", one, val)


def rescale_damage(lev, r):
    """lev plus overrides that multiply each field-dependent damage density by r (last value wins in radIV.slurm):
    damPeak (E^damM law); dam2Peak / damInsPeak only when their exponent is non-zero; damGauss N only when
    gaussFieldM != 0; damGaussF N always (always field-scaled). Plain strikes, uniform dam2 (dam2M 0) and damSites
    are field-independent and unchanged. Any other damage law raises, so a remake never silently skips one."""
    _, pairs = parse_line("x|" + lev)
    eff, _ = effective(pairs)
    f = lambda k, d="0": float(eff.get(k, d) or d)
    for k in ("dam3Peak", "damList", "damTube", "damRod", "trackFieldM"):
        if k in eff and eff[k] not in ("", "{}", "0", "0.0"):
            raise ValueError(f"rescale_damage: {k}={eff[k]} not handled")
    out = []
    if "damPeak" in eff:
        out.append(f"damPeak={f('damPeak') * r:g}")
    if f("dam2Peak") > 0 and f("dam2M") != 0:
        out.append(f"dam2Peak={f('dam2Peak') * r:g}")
    if f("damInsPeak") > 0 and f("damInsM") != 0:
        out.append(f"damInsPeak={f('damInsPeak') * r:g}")
    if eff.get("damGauss", "{}") not in ("", "{}") and f("gaussFieldM") != 0:
        out.append(f"damGauss={_scale_braces(eff['damGauss'], r)}")
    if eff.get("damGaussF", "{}") not in ("", "{}"):
        out.append(f"damGaussF={_scale_braces(eff['damGaussF'], r)}")
    return lev + "".join(";" + o for o in out)


def fx_rows(rows, r, path_swaps=(), prefix="fx_"):
    """Remake rows with the fixed FP box: label prefix, saved-state paths swapped to their fixed-box versions,
    field-dependent damage rescaled by r."""
    out = []
    for lab, lev in rows:
        for old, new in path_swaps:
            lev = lev.replace(old, new)
        out.append((f"{prefix}{lab}", rescale_damage(lev, r)))
    return out


R_28V = 6e17 / 1.5e18          # 28 V scale ratio (0.4): fpFixScale28/28b, SiN 6e17 is closest to the old C_p1.5_N0 curve (rms 12)
FIX_MAX_VD = 28.0              # the fixed-box library is saved to 28 V only


def fx28_rows(rows, r, prefix="fx_"):
    """28 V round remakes: each saved-state path (library sin/hk_Vg-10 or meshchk m10/m5fix/m2p5) swapped to its
    fixed-box version, field-dependent damage rescaled by r. Returns (rows, dropped labels): rows that load a state
    above FIX_MAX_VD (no fixed-box state) are dropped. Every row must load a state."""
    import re
    lib = re.compile(r"stressLoad=" + re.escape(LIB) + r"/(sin|hk)_Vg-10/(sin|hk)_Vg-10_Vd(\d+\.\d+)\.str\.gz")
    mch = re.compile(r"stressLoad=" + re.escape(LIB) + r"/meshchk/sin_(m10|m5fix|m2p5)/sin_(m10|m5fix|m2p5)_Vd(\d+\.\d+)\.str\.gz")
    out, dropped = [], []
    for lab, lev in rows:
        vds = [float(m.group(3)) for m in lib.finditer(lev)] + [float(m.group(3)) for m in mch.finditer(lev)]
        if not vds:
            raise ValueError(f"fx28_rows: {lab} loads no library or meshchk state")
        if max(vds) > FIX_MAX_VD:
            dropped.append(lab)
            continue
        lev = lib.sub(lambda m: f"stressLoad={FIXLIB}/{m.group(1)}_Vg-10/fpfix_{m.group(1)}_Vg-10_Vd{m.group(3)}.str.gz", lev)
        lev = mch.sub(lambda m: f"stressLoad={FIXLIB}/meshchk/sin_{m.group(1)}/fpfix_sin_{m.group(1)}_Vd{m.group(3)}.str.gz", lev)
        assert f"{LIB}/sin_Vg-10/" not in lev and f"{LIB}/hk_Vg-10/" not in lev and f"{LIB}/meshchk/" not in lev, lab
        out.append((f"{prefix}{lab}", rescale_damage(lev, r)))
    return out, dropped


# ---- rows. A study is a list of (label, levers); a params line is f"{label}|{levers}".
def join(*parts):
    """Join lever strings with ';', skipping empty ones."""
    return ";".join(x for x in parts if x)


def rows_both_decks(cases, common=""):
    """BASE_1104 + common + deck + case levers, for each (label, levers) on HighK then SiN."""
    return [(f"{d}_{lab}", join(BASE_1104, common, dl, lev)) for lab, lev in cases for d, dl in DECKS]


def rows_on_decks(cases, common=""):
    """As rows_both_decks, for (deck, label, levers) cases with the deck ('hk' or 'sin') given."""
    dl = dict(DECKS)
    return [(f"{d}_{lab}", join(BASE_1104, common, dl[d], lev)) for d, lab, lev in cases]


def by_label(*row_lists):
    """Label -> levers over several studies' rows; labels must be unique across them."""
    out = {}
    for rows in row_lists:
        for lab, lev in rows:
            assert lab not in out, f"label {lab} appears twice"
            out[lab] = lev
    return out


def swap(s, old, new, count=1):
    """s.replace(old, new), asserting that old occurs exactly count times."""
    assert s.count(old) == count, f"expected {count} x {old!r} in {s!r}"
    return s.replace(old, new)


# ---- reading params lines the way sweeps/radIV.slurm does
def parse_line(line):
    """(label, [(lever, value), ...]) in file order, as radIV.slurm reads it: label up to the first '|',
    pairs split at ';', empty pairs skipped, lever up to the first '=' (a pair without '=' becomes
    `set x x` in the slurm loop, so it is returned as (x, x))."""
    line = line.rstrip("\n")
    label, bar, pairs = line.partition("|")
    if not bar:
        pairs = line
    out = []
    for kv in pairs.split(";"):
        if not kv:
            continue
        k, eq, v = kv.partition("=")
        out.append((k, v) if eq else (kv, kv))
    return label, out


def effective(pairs):
    """(lever -> winning value in order of first appearance, lever -> every value when set more than once)."""
    eff, seen = {}, {}
    for k, v in pairs:
        eff[k] = v
        seen.setdefault(k, []).append(v)
    return eff, {k: vs for k, vs in seen.items() if len(vs) > 1}


def lever_diff(base, eff):
    """Differences of an effective lever set from a base set: added, changed and missing levers."""
    out = [f"+{k}={v}" for k, v in eff.items() if k not in base]
    out += [f"{k} {base[k]} -> {v}" for k, v in eff.items() if k in base and base[k] != v]
    out += [f"-{k}" for k in base if k not in eff]
    return out


# ---- the rail
Study = namedtuple("Study", "name build parents base driver", defaults=((), None, "radIV"))
Study.__doc__ = """One params file. build(*parent_rows) returns its rows; parents name earlier studies whose rows
it reuses; base is (name, levers) for --show; driver is the DRV the file is submitted with."""


def params_path(name):
    return f"sweeps/params_{name}.txt"


def text_of(rows):
    return "".join(f"{lab}|{lev}\n" for lab, lev in rows)


def study_name(arg):
    """'radStepA', 'params_radStepA.txt' and 'sweeps/params_radStepA.txt' all name radStepA."""
    n = os.path.basename(arg)
    n = n[len("params_"):] if n.startswith("params_") else n
    return n[:-len(".txt")] if n.endswith(".txt") else n


def check_rows(name, rows):
    """Rows a params file can hold: labels unique and free of '|', ';', spaces and newlines; every pair k=v."""
    labels = [lab for lab, _ in rows]
    assert rows, f"{name}: no rows"
    assert len(set(labels)) == len(labels), f"{name}: repeated labels"
    for lab, lev in rows:
        assert lab and not any(c in lab for c in "|;\n "), f"{name}: bad label {lab!r}"
        assert "\n" not in lev, f"{name}: newline in the levers of {lab}"
        assert all("=" in kv for kv in lev.split(";") if kv), f"{name}: pair without '=' in {lab}"


def build(studies):
    """Rows of every study, in order; a derived study gets its parents' rows from memory."""
    built = {}
    for st in studies:
        assert st.name not in built, f"study {st.name} defined twice"
        missing = [p for p in st.parents if p not in built]
        assert not missing, f"{st.name}: parents {missing} must come earlier"
        rows = list(st.build(*(built[p] for p in st.parents)))
        check_rows(st.name, rows)
        built[st.name] = rows
    return built


def tracked_params():
    """Paths under sweeps/ in the git index, or None when the current directory is not the top of a git
    work tree (then every existing params file counts as tracked)."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        if os.path.realpath(top.stdout.strip()) != os.path.realpath(os.getcwd()):
            return None
        out = subprocess.run(["git", "ls-files", "-z", "--", "sweeps"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return {p for p in out.stdout.split("\0") if p}


def print_diff(path, old, new):
    """Unified diff of a params file, then the effective-lever changes per task."""
    sys.stdout.writelines(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                               f"{path} (in sweeps/)", f"{path} (generator)", n=0))
    ol, nl = old.splitlines(), new.splitlines()
    if len(ol) != len(nl):
        print(f"    lines: {len(ol)} -> {len(nl)}")
    for i, (a, b) in enumerate(zip(ol, nl)):
        if a == b:
            continue
        la, pa = parse_line(a)
        lb, pb = parse_line(b)
        ch = lever_diff(effective(pa)[0], effective(pb)[0])
        if la != lb:
            ch.insert(0, f"label {la} -> {lb}")
        print(f"    task {i} {lb}: " + ("; ".join(ch) if ch else "no change in the effective levers"))


def emit(name, rows, check=False, force=False, tracked=None):
    """Write sweeps/params_<name>.txt from rows, or (check) report what a write would do. Returns the status:
    'unchanged', 'created', 'rewritten' (untracked file changed), 'forced', 'refused', or 'would create' /
    'would change' with check."""
    path = params_path(name)
    new = text_of(rows)
    old = None
    if os.path.exists(path):
        with open(path) as f:
            old = f.read()
    is_tracked = old is not None and (tracked is None or path in tracked)
    if old == new:
        status = "unchanged"
    elif check:
        status = "would create" if old is None else "would change"
    elif old is None:
        status = "created"
    elif is_tracked and not force:
        status = "refused"
    else:
        status = "forced" if is_tracked else "rewritten"
    note = {"refused": f": tracked file would change; diff below, rerun with --force {name} to write it",
            "would change": " (tracked)" if is_tracked else " (untracked)",
            "rewritten": " (untracked file, overwritten)"}.get(status, "")
    print(f"{name:<20} {len(rows):3d}  {status}{note}")
    if status in ("refused", "would change", "forced", "rewritten"):
        print_diff(path, old, new)
    if status in ("created", "forced", "rewritten"):
        with open(path, "w") as f:
            f.write(new)
    return status


def wrap(items, first, width=112):
    """Join items with '; ' into lines of at most width, the first starting with first, the rest indented."""
    if not items:
        return first + "(none)"
    lines, cur, pad = [], first, " " * len(first)
    for it in items:
        if cur.strip() and len(cur) > len(pad) and len(cur) + len(it) + 2 > width:
            lines.append(cur.rstrip())
            cur = pad
        cur += it + "; "
    lines.append(cur.rstrip().rstrip(";"))
    return "\n".join(lines)


def show(studies, built, arg, task=None):
    """Print each line's effective levers (last value wins) and its differences from the study's base."""
    name = study_name(arg)
    st = {s.name: s for s in studies}.get(name)
    path = params_path(name)
    if os.path.exists(path):
        with open(path) as f:
            lines = f.read().splitlines()
        src = path
        if st and text_of(built[name]) != "\n".join(lines) + "\n":
            src += "  (NOTE: the generator would change this file; see --check)"
    elif st:
        lines = [f"{lab}|{lev}" for lab, lev in built[name]]
        src = f"generator rows, {path} not written yet"
    else:
        print(f"no params file {path} and no study {name} in this generator", file=sys.stderr)
        return 2
    parsed = [parse_line(l) for l in lines if l.strip()]
    if not parsed:
        print(f"{path} has no lines", file=sys.stderr)
        return 2
    if any("=" not in kv for l in lines for kv in l.partition("|")[2].split(";") if kv):
        print(f"{path} is not in the label|lever=value format of sweeps/radIV.slurm (its template reads the fields "
              "by position)", file=sys.stderr)
        return 2
    picked = list(enumerate(parsed))
    if task is not None:
        t = task[len("task_"):] if task.startswith("task_") else task
        picked = [(i, lp) for i, lp in picked if lp[0] == task or (t.isdigit() and i == int(t))]
        if not picked:
            print(f"no line labelled {task} (or task index) in {path}", file=sys.stderr)
            return 2
    if st and st.base:
        bname, bstr = st.base
        base = effective(parse_line("|" + bstr)[1])[0]
    else:
        bname = "(levers common to every line)"
        effs = [effective(p)[0] for _, p in parsed]
        base = {k: v for k, v in effs[0].items() if all(e.get(k) == v for e in effs[1:])}
    print(f"{name}: {src}; {len(parsed)} lines" + (f"; driver {st.driver}" if st else
                                                   "; not a study of this generator"))
    print(wrap([f"{k}={v}" for k, v in base.items()], f"base {bname}: "))
    print("Each line sets only the levers listed; the driver's defaults apply to the rest.\n"
          "vs base: +lever added, -lever not set (driver default), lever a -> b changed.")
    for i, (lab, pairs) in picked:
        eff, rep = effective(pairs)
        print(f"\ntask {i}  {lab}  ({len(eff)} levers)")
        if rep:
            print(wrap([f"{k} {' -> '.join(vs)}" for k, vs in rep.items()], "  set more than once (last wins): "))
        d = lever_diff(base, eff)
        print(wrap(d, "  vs base: ") if d else "  vs base: same")
        print(wrap([f"{k}={v}" for k, v in eff.items()], "  effective: "))
    return 0


def run(studies, doc, argv=None):
    """Command line of a generator: write (default), --check, --force NAME, --show NAME [TASK]."""
    ap = argparse.ArgumentParser(description=doc.split("\n\n")[0], formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="write nothing; list the files that would be created or changed (exit 1 if any)")
    ap.add_argument("--force", action="append", default=[], metavar="NAME",
                    help="allow this study's tracked params file to change (repeatable)")
    ap.add_argument("--show", nargs="+", metavar=("NAME", "TASK"),
                    help="print the effective levers of each line of a params file (or of one task, by label\n"
                         "or index) and their differences from the study's base; writes nothing")
    a = ap.parse_args(argv)
    if not os.path.exists("sweeps/radIV.slurm"):
        print("run from the repo root (sweeps/radIV.slurm not found)", file=sys.stderr)
        return 2
    built = build(studies)
    if a.show:
        if len(a.show) > 2:
            ap.error("--show takes NAME and at most one TASK")
        return show(studies, built, *a.show)
    force = {study_name(n) for n in a.force}
    unknown = force - set(built)
    if unknown:
        ap.error(f"--force: no such study {sorted(unknown)}")
    tracked = tracked_params()
    if tracked is None:
        print("note: not the top of a git work tree, so every existing params file counts as tracked")
    status = [emit(n, rows, check=a.check, force=n in force, tracked=tracked) for n, rows in built.items()]
    counts = {s: status.count(s) for s in dict.fromkeys(status)}
    print("summary: " + ", ".join(f"{v} {k}" for k, v in counts.items()))
    if a.check:
        todo = [s for s in status if s != "unchanged"]
        print("nothing to change" if not todo else f"{len(todo)} file(s) would be created or changed")
        return 1 if todo else 0
    if "refused" in status:
        print("refused: some tracked params files were not written (see the diffs above)", file=sys.stderr)
        return 1
    return 0
