---
title: Calibration
tags: [device, results]
date: 2026-10-01
---
# Calibration vs the measured HfO2 device

**Target:** `data/rfDeviceHFO2_Experimental.csv` (raw: `data/RF_100nmHfOx_IdVgs_Example1.xlsx`): Id–Vgs at **Vds = 10 V**, 25 °C, 100 nm HfO2, standard FP. `Ids` is in A for a **200 µm** device → mA/mm = A·1e3/0.2 (634 mA/mm at Vg 0, 810 at +1 V). Gate leakage ≤2e-3 mA/mm; the off-state floor (~0.075 mA/mm) is drain leakage, not modelled (Ian: qualitative OFF vs ON only).

**Driver:** `drivers/calibIdVg.tcl` (trap-free, Vd ramp then Vg +1 → −4 V; levers `Vd_cal`, `Rs_contact`/`Rd_contact` lumped series resistance via SolveRc, `deviceDeck`). Scored by `analysis/calib_score.py` (aligns by a rigid Vg shift = ΔphiB), plotted by `analysis/plot_calib.py` → `figures/calib_IdVg.png`.

**Result: the existing deck with `mobModel field` is the calibration; no parameters changed.** Id within ±2.4% from Vg −2.6 to +1 V (rms 1.9% to 0 V); −2 V: −1.5%; 0 V: 649 vs 634; +1 V: 802 vs 810. Threshold region ±15% (model turns on slightly steeper). Static mobility: 10% rms, wrong shape.

**Known miss — gm above +0.5 V** (88 vs 160 mS/mm at +1 V) while Id still matches: the source access region (2DEG ~5e12) and the strip under the T-gate head quasi-saturate (access-resistance gm roll-off, Palacios et al. TED 2006). Every physically motivated fix traded the turn-on / −2 V region for forward gm:

| change (phiB refit) | rms to 0 V | at −2 V | gm −1/0/+1 (exp 220/196/159) |
|---|---|---|---|
| none (adopted) | 1.8% | −2% | 232/199/88 |
| polCharge 9e12 / 1.1e13 | 13% / 22% | | 286/262/222, 326/312/281 |
| polCharge 8e12 + Rc 0.6 Ω·mm, phiB 2.07 | 4.5% | −5% | 223/205/170 |
| polCharge 7.5e12 + Rc 0.35, phiB 1.86 | 3.1% | −4% | 225/203/135 |
| polCharge 9e12 + Rc 1.0, phiB 2.50 | 6.8% | −6% | 216/207/188 |
| surfCharge 4e12 | 22% | | 325/313/293 |
| surfCharge 1.5e12 + Rc 0.6, phiB 1.86 | 3.2% | −4% | 231/219/189 |
| 2DEG mobility without buffer doping (~1900) | 36% | | |

Kept unmodified: best in the required range and at Vg −2 V where all trap studies run. Rigid-shift approximation confirmed (field-plate effect <0.1%). Levers added with old defaults: `polCharge`, `phiB`, `surfCharge` ([[levers]]).

**Caveat:** only saturation (Vds 10 V) is validated; the low-Vd linear region where the collapses happen is not (needs measured Id–Vd). The [[energy-balance]] with ETemp statistics would shift this calibration.

Related: [[mobility-models]], [[current-status]].
