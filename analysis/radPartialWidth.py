"""Partial-width estimate: Id_total = f*Id_damaged + (1-f)*Id_undamaged, parallel columns with no current
spreading between them. No solver. usage: python3 analysis/radPartialWidth.py"""
import glob

import numpy as np

from common import REF, read_csv


def load(run, tag):
    """radIV Id-Vd of the task labelled tag in results/<run> (columns Vd, Id_dev, ...)."""
    return read_csv(glob.glob(f"results/{run}/task_*/{tag}_IdVd.csv")[0])


W, L, FLU, TRACK = 200.0, 4.66, 1e7, 0.16  # um, um, cm^-2, um
ions = W * L * 1e-8 * FLU
print(f"ions on the device {ions:.0f}, one track covers {TRACK / W:.2%} of the width, all distinct {ions * TRACK / W:.1%}")
ref = read_csv(glob.glob(REF["pre_hk"])[0])   # HighK pre-irradiation, radMap1 (job 49570571)
for lab, run, t in (("0.3 um 4e18", "20261104_radMesh", "hk_y1.50_m05"), ("0.1 um 1.2e19", "20261104_radMesh", "hk_w0.1_m05")):
    d = load(run, t)
    print(lab)
    for f in (TRACK / W, 0.074, 0.2, 0.5, 1.0):
        tot = [f * np.interp(v, d[:, 0], d[:, 1]) + (1 - f) * np.interp(v, ref[:, 0], ref[:, 1]) for v in (0.25, 1, 4, 10)]
        print(f"  f {f:7.2%}: resistance ratio {ref[1, 1] / tot[0]:.3f}  Id ratio at 1, 4, 10 V: " + " ".join(
            f"{tot[i] / np.interp(v, ref[:, 0], ref[:, 1]):.3f}" for i, v in ((1, 1), (2, 4), (3, 10))))
