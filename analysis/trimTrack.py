"""Per-ion track parameters from a TRIM full-cascade run with collision details (COLLISON.txt).

usage: python3 analysis/trimTrack.py <trim_out_dir> <deck: HighK|SiN> <out.json>

For each layer of the model-deck stack it reports, per ion:
  vac_per_nm      vacancies per nm of depth (mean over ions, and the spread between ions)
  sigma_nm        radial Gaussian width of the vacancies around the ion path, from <r^2> = 2 sigma^2
  r50_nm, r90_nm  radii holding 50% and 90% of the vacancies
  peak_cm3        vac_per_nm / (2 pi sigma^2), the on-axis density of that Gaussian, cm^-3
  Se_eV_per_A     electronic stopping of the ion in the layer (from the cascade-start lines)
Depths are from the TRIM front surface; the AlGaN top is at the passivation thickness.
"""
import json
import math
import re
import sys
from collections import defaultdict

STACKS = {"HighK": [("HfO2", 2500), ("Si3N4", 500), ("AlGaN", 150), ("GaN", 20000)],
          "SiN": [("Si3N4", 3000), ("AlGaN", 150), ("GaN", 20000)]}
NUM = r"[-+]?\d+\.?\d*(?:[EeDd][-+]?\d+)?"   # TRIM writes e.g. 18053.E-02 (no digit after the point)


def layer_bounds(stack):
    out, x0 = [], 0.0
    for name, w in stack:
        out.append((name, x0, x0 + w))
        x0 += w
    return out


def main(d, deck, out):
    bounds = layer_bounds(STACKS[deck])
    # extra sub-layers near the 2DEG: the top 50 nm of GaN, and 50-500 nm below
    gtop = [b for b in bounds if b[0] == "GaN"][0][1]
    zones = bounds[:-1] + [("GaN_top50nm", gtop, gtop + 500), ("GaN_50-500nm", gtop + 500, gtop + 5000),
                           ("GaN_0.5-2um", gtop + 5000, bounds[-1][2])]
    vac = defaultdict(lambda: defaultdict(int))      # zone -> ion -> count
    r2 = defaultdict(list)                            # zone -> r^2 (A^2) per vacancy
    se = defaultdict(list)
    ion, iy, iz = 0, 0.0, 0.0
    nums = re.compile(NUM)
    with open(f"{d}/COLLISON.txt", encoding="latin-1") as fh:
        for line in fh:
            if "Start of New Cascade" in line:
                f = nums.findall(line.split("Start")[0])
                # ion number, energy, depth, Y, Z, Se, (atom), recoil energy
                ion, x, iy, iz, s = int(f[0]), float(f[2]), float(f[3]), float(f[4]), float(f[5])
                z = zone_of(zones, x)
                if z:
                    se[z].append(s)
                continue
            f = nums.findall(line)
            if len(f) >= 8 and line.lstrip()[:1] not in ("=", "-", "R", "S") and "Summary" not in line:
                # recoil #, atom Z, energy, X, Y, Z, Vac, Repl
                try:
                    x, y, zz, v = float(f[3]), float(f[4]), float(f[5]), int(f[6])
                except ValueError:
                    continue
                if v < 1:
                    continue
                z = zone_of(zones, x)
                if not z:
                    continue
                vac[z][ion] += v
                r2[z].append((y - iy) ** 2 + (zz - iz) ** 2)
    nions = max((max(v.keys()) for v in vac.values() if v), default=0)
    res = {"deck": deck, "ion": "Au 2256 MeV", "ions": nions, "source": d, "layers": []}
    for name, a, b in zones:
        w_nm = (b - a) / 10.0
        counts = [vac[name].get(i, 0) for i in range(1, nions + 1)]
        mean = sum(counts) / nions / w_nm if nions else 0.0
        sd = (sum((c / w_nm - mean) ** 2 for c in counts) / max(1, nions - 1)) ** 0.5 if nions else 0.0
        rs = sorted(r2[name])
        sig = math.sqrt(sum(rs) / len(rs) / 2.0) / 10.0 if rs else float("nan")
        q = lambda p: math.sqrt(rs[int(p * (len(rs) - 1))]) / 10.0 if rs else float("nan")
        peak = mean / (2 * math.pi * (sig * 1e-7) ** 2) / 1e-7 if rs and sig > 0 else 0.0
        res["layers"].append({"layer": name, "depth_nm": [a / 10.0, b / 10.0],
                              "vac_per_nm": round(mean, 4), "vac_per_nm_sd_between_ions": round(sd, 4),
                              "sigma_nm": round(sig, 3), "r50_nm": round(q(0.5), 3), "r90_nm": round(q(0.9), 3),
                              "peak_cm3": float(f"{peak:.3e}"),
                              "Se_eV_per_A": round(sum(se[name]) / len(se[name]), 1) if se[name] else None,
                              "n_vac": len(rs)})
    json.dump(res, open(out, "w"), indent=1)
    for L in res["layers"]:
        print(f"{L['layer']:14s} {L['depth_nm'][0]:7.1f}-{L['depth_nm'][1]:7.1f} nm  vac/nm/ion {L['vac_per_nm']:7.3f} "
              f"(sd {L['vac_per_nm_sd_between_ions']:.3f})  sigma {L['sigma_nm']:7.2f} r50 {L['r50_nm']:6.2f} "
              f"r90 {L['r90_nm']:7.2f} nm  peak {L['peak_cm3']:.2e}  Se {L['Se_eV_per_A']}")


def zone_of(zones, x):
    hit = None
    for name, a, b in zones:
        if a <= x < b:
            hit = name           # later zones (GaN sub-zones) override the full GaN layer
    return hit


if __name__ == "__main__":
    main(*sys.argv[1:4])
