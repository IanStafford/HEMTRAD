"""Register of the stepped-collapse tests (2026-11-17 goal): what each HPG task varies, its job, its state and the
drops found so far. Feeds the "Stepped-Collapse Test Register" dashboard.

usage: python3 analysis/testRegister.py <out.json> [--no-hpg]
Reads sweeps/params_<run>.txt, local results/<dir>/task_*/ (rsync them first), and job states from HPG (sacct)
unless --no-hpg.
"""
import glob
import json
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, "analysis")
from plot_radStep import drops  # noqa: E402

# round, params file, results dir, purpose, [(job id, first task, last task)]
ROUNDS = [
    ("S", "rad28strikeL", "20261117_rad28strikeL",
     "0-3 strikes of 3e18 on the 28 V stress damage, both decks, damage scale 1.5e18 and 2e18 (first 28 V strike set)",
     [("51763582", 0, 15)]),
    ("A", "radStepA", "20261117_radStepA",
     "Damage scale alone; strike density 4-8e18 with 1 or 3 strikes at scales 1.5e18 and 1.7e18; graded 4/5/6e18 strikes",
     [("51784676", 0, 20)]),
    ("B", "radStepB", "20261117_radStepB",
     "Levers A doesn't touch: trap level, strike width and depth, strikes nearer the gate, graded 3/6/9e18, capture time, scale 1.6e18, two strikes",
     [("51799601", 0, 19)]),
    ("C", "radStepC", "20261117_radStepC",
     "Complete matched 0-3 strike series for the stepped cases (6-8e18 strikes) and their HighK counterparts",
     [("51799741", 0, 8), ("51799742", 9, 15)]),
    ("D", "radStepD", "20261117_radStepD",
     "Checks: halved Vd step (0.05 V) for the stepped cases, and knock-out of single strikes",
     [("51801163", 0, 4)]),
    ("E", "radStepE", "20261117_radStepE",
     "Literature-led: stress at 24 and 30 V, strikes at the field-plate edges, trap level 0.40, wider strikes, Vg families",
     [("51801897", 0, 14), ("51801898", 15, 17)]),
    ("3D", "rad3dRod", "20261117_rad3dRod",
     "Ion tracks along the gate width (3D) and their 2D references; 3D tasks stopped (3D x-gradient is wrong)",
     [("51784348", 0, 2), ("51784349", 3, 3), ("51784350", 6, 7)]),
]
BASE = {"damPeak": "7e18", "trapLevel": "0.30", "hotTau": "1e-14", "Vd_step": "0.1", "Vd_max": "10.0",
        "deviceDeck": "rfdevice.tcl", "Vd_stress": "17.0"}


def parse_line(line):
    lab, rest = line.rstrip("\n").split("|", 1)
    kv = dict(BASE)
    for item in rest.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            kv[k.strip()] = v.strip()
    return lab, kv


def tcl_list(s):
    return [g.split() for g in re.findall(r"\{([^{}]+)\}", s or "")]


def fmt(x):
    return f"{float(x):.3g}".replace("e+", "e")


def describe(kv):
    deck = "SiN" if "SiN" in kv.get("deviceDeck", "") else ("3D slice" if "3d" in kv.get("deviceDeck", "") else "HighK")
    if "rfdevice3d" in kv.get("deviceDeck", ""):
        deck = "SiN 3D slice" if kv.get("passMat") == "Nitride" else "HighK 3D slice"
    out = {"deck": deck}
    stress_skip = kv.get("stressSkip") == "1"
    out["stress"] = "none (track only)" if stress_skip else (
        f"{float(kv['Vd_stress']):g} V" + (" (loaded from library)" if kv.get("stressLoad") else ""))
    out["damage_scale"] = "none" if stress_skip else fmt(kv["damPeak"])
    g = tcl_list(kv.get("damGauss"))
    rod = tcl_list(kv.get("damRod"))
    if rod:
        out["strikes"] = len(rod)
        out["strike_y"] = ", ".join(f"{float(r[0]):g}" for r in rod)
        out["strike_density"] = ", ".join(fmt(r[5]) for r in rod)
        out["strike_sigma_nm"] = ", ".join(f"{float(r[2]) * 1000:g}" for r in rod)
        out["strike_note"] = "along width z " + ", ".join(f"{float(r[3]):g}-{float(r[4]):g} um" for r in rod)
    else:
        out["strikes"] = len(g)
        out["strike_y"] = ", ".join(f"{float(r[0]):g}" for r in g) or "-"
        out["strike_density"] = ", ".join(fmt(r[3]) for r in g) or "-"
        out["strike_sigma_nm"] = ", ".join(f"{float(r[2]) * 1000:g}" for r in g) or "-"
        deep = [f"{float(r[1]):g}" for r in g if float(r[1]) != 0.0]
        out["strike_note"] = (f"{float(g[0][1]) * 1000:g} nm below the AlGaN top" if deep else ("at the AlGaN top" if g else ""))
    out["trap_level_eV"] = float(kv["trapLevel"])
    out["capture_time_s"] = fmt(kv["hotTau"])
    out["Vd_step"] = float(kv["Vd_step"])
    out["Vd_max"] = float(kv["Vd_max"])
    out["Vg_family"] = kv.get("VgFam", "").strip("{}") or "-"
    bits = [deck, f"stress {out['stress']}"]
    if not stress_skip:
        bits.append(f"damage scale {out['damage_scale']} cm^-3")
    if out["strikes"]:
        bits.append(f"{out['strikes']} strike{'s' if out['strikes'] > 1 else ''} of {out['strike_density']} cm^-3 at y {out['strike_y']} um "
                    f"(sigma {out['strike_sigma_nm']} nm, {out['strike_note']})")
    else:
        bits.append("no strikes")
    if out["trap_level_eV"] != 0.30:
        bits.append(f"trap level {out['trap_level_eV']:g} eV")
    if out["capture_time_s"] != "1e-14":
        bits.append(f"capture time {out['capture_time_s']} s")
    if out["Vd_step"] != 0.1:
        bits.append(f"Vd step {out['Vd_step']:g} V")
    if out["Vg_family"] != "-":
        bits.append(f"also Vg {out['Vg_family']} V")
    bits.append(f"Id-Vd at Vg +1 V to {out['Vd_max']:g} V")
    out["what"] = "; ".join(bits)
    return out


def states(jobs):
    if not jobs:
        return {}
    cmd = "sacct -n -X -j " + ",".join(jobs) + " -o JobID%24,State%20,Elapsed"
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "hpg", cmd], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return {}
    st = {}
    for line in r.stdout.splitlines():
        p = line.split()
        if len(p) < 3 or "_" not in p[0]:
            continue
        jid, rng = p[0].split("_", 1)
        state = p[1].split()[0]
        rng = rng.strip("[]").split("%")[0]
        for part in rng.split(","):
            if "-" in part:
                a, b = part.split("-")
                for t in range(int(a), int(b) + 1):
                    st[(jid, t)] = (state, p[-1])
            elif part.isdigit():
                st[(jid, int(part))] = (state, p[-1])
    return st


def main(out, *flags):
    jobs = [j for r in ROUNDS for j, _, _ in r[4]]
    st = {} if "--no-hpg" in flags else states(jobs)
    rows = []
    for rnd, pf, rdir, purpose, ranges in ROUNDS:
        lines = open(f"sweeps/params_{pf}.txt").read().splitlines()
        for t, line in enumerate(lines):
            lab, kv = parse_line(line)
            job = next((j for j, a, b in ranges if a <= t <= b), None)
            row = {"test": lab, "round": rnd, "task": t, "job": job or "not submitted", "purpose": purpose}
            row.update(describe(kv))
            s = st.get((job, t)) if job else None
            state = s[0] if s else ("HELD" if not job else "UNKNOWN")
            row["state"] = {"COMPLETED": "done", "RUNNING": "running", "PENDING": "queued", "CANCELLED": "cancelled",
                            "FAILED": "failed", "TIMEOUT": "timed out", "HELD": "held", "OUT_OF_MEMORY": "failed"}.get(state, state.lower())
            row["elapsed"] = s[1] if s else ""
            f = glob.glob(f"results/{rdir}/task_{t}/*_IdVd.csv")
            row.update({"Vd_reached": None, "Id_1V": None, "Id_end": None, "n_drops": None, "drops": ""})
            if f:
                d = np.array([[float(v) for v in l.split(",") if v.strip()] for l in open(f[0]) if l.strip()])
                if d.ndim == 2 and len(d) >= 3:
                    ep = drops(d[:, 0], d[:, 1], 10.0)
                    row.update({"Vd_reached": round(float(d[-1, 0]), 2), "Id_1V": round(float(np.interp(1, d[:, 0], d[:, 1])), 1),
                                "Id_end": round(float(d[-1, 1]), 1), "n_drops": len(ep),
                                "drops": "; ".join(f"{a:.1f}-{b:.1f} V: {ia:.0f} -> {ib:.0f}" for a, b, ia, ib in ep) or "none"})
            rows.append(row)
    json.dump(rows, open(out, "w"), indent=1)
    print(len(rows), "tests;", {k: sum(1 for r in rows if r["state"] == k) for k in sorted({r["state"] for r in rows})})


if __name__ == "__main__":
    main(*sys.argv[1:])
