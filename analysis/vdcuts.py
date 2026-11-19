"""Read the per-Vd cuts written by drivers/radIV.tcl with vdCuts=1 (<label>_vdcuts.txt): for each Vd a print1d cut
along the channel (y, um) at depth x = 0.016 um (the 2DEG row in GaN) of IonAcceptor (filled traps), Elec, Ey
(lateral field, V/cm) and TeTrap. load(path) -> {Vd: {label: (y, value)}}."""
import re
import numpy as np


def load(path):
    out, vd, lab, rows = {}, None, None, []

    def flush():
        if vd is not None and rows:
            a = np.array(rows)
            out.setdefault(vd, {})[lab] = (a[:, 0], a[:, 1])

    for line in open(path):
        m = re.match(r"# Vd=(\S+) (\S+)", line)
        if m:
            flush()
            vd, lab, rows = round(float(m.group(1)), 3), m.group(2), []
            continue
        p = line.strip().strip("{}").split()
        if len(p) >= 2:
            try:
                rows.append((float(p[0]), float(p[1])))
            except ValueError:
                pass
    flush()
    return out
