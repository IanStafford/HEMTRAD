---
title: Calibration
tags: [device, results]
date: 2026-11-20
source: drivers/calibIdVg.tcl, drivers/radIV.tcl, sweeps/params_radCal1.txt, sweeps/params_radMap1.txt, progress.md 2026-10-01 and 2026-10-23
---
# Calibration

The deck has two calibrations, one per measured device set. Both use `mobModel field` ([[mobility-models]]).

| | Oct 1 (HfO2 transfer curve) | Rad-device baseline (2026-10-23) |
|---|---|---|
| Target | Id–Vgs at Vds 10 V (saturation) | pre-irradiation Id–Vg at Vd 0.1 V and Id–Vd at Vg +1 V of the rad devices |
| Levers | the defaults: `polCharge` 7e12, `phiB` 1.65, GaN mumax 1907, Nref 1e17, Heller vs 3.3e7 − 3e6·T/300 | `polCharge` 1e13, `phiB` 2.94, `mobNref` 1e18, `mobVsat` 1.75e7, `mobMumax` 2100 |
| Used by | `drivers/pulsedIV.tcl` and `calibIdVg.tcl` work (Sep–Oct) | every `drivers/radIV.tcl` / `seeIV.tcl` run since 2026-10-23 |

## Oct 1: the measured HfO2 transfer curve

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

**Caveat:** only saturation (Vds 10 V) is validated; the low-Vd linear region where the pulsed-IV collapses happen is not (needs measured Id–Vd). The [[energy-balance]] with ETemp statistics would shift this calibration.

## Rad-device baseline (2026-10-23)

The rad devices are a different device set, measured at low Vd. At Vd 0.1 V the Oct 1 deck had a clearly higher on-resistance than these devices, so the deck was recalibrated against their pre-irradiation curves. The measured curves are kept untracked (`data/rad_y2/`; the repo is public), so this section gives model values and qualitative fit quality only.

**Lever block** (as in every rad params file, e.g. `sweeps/params_radMap1.txt`):

`polCharge=1.0e13;phiB=2.94;mobNref=1e18;mobVsat=1.75e7;mobMumax=2100`

**Rounds** (driver `drivers/radIV.tcl` with `radState pre`, template `sweeps/radIV.slurm`):
- Round 1 (job 47311016, `params_radCal1.txt`): `polCharge` 7/8/9/10e12 × `mobNref` 1e17/1e18, with `phiB` pre-shifted about 0.43 V per 1e12. Vth fits in every variant; the low-Vd transfer currents fit at 9e12 / 1e18, but Id–Vd at Vg +1 saturates too high.
- Round 2 (job 47324103, `params_radCal2.txt`): `polCharge` 9 / 9.5 / 10e12 × `mobVsat` 1.5 / 2.0 / 2.5e7. Best: 1e13 with 2e7.
- Round 3 (job 47327599, `params_radCal3.txt`): `polCharge` 1e13 with `mobVsat` 1.75e7 (with and without `mobMumax` 2100) and 2.0e7 with `mobMumax` 2100, plus a SiN-deck pre run. Adopted: task `p10_vs1.75_mu2100`.

**Fit (qualitative):** Vth and the Id–Vd shape at Vg +1 V fit; the peak gm is still too high (the model turns on too steeply, as in the Oct 1 fit). Fit details are in [[rad-model]]. Model values: Vth −3.00 V, with the HighK and SiN pre curves within 1% of each other (radFinal, job 47693156).

**FP contact fix:** all of these pre curves were run with the old FP contact box, which held the top of the T-gate head's drain half near the FP potential (0 V) instead of Vg. At Vg +1 V that is a smaller effect than during the stress. The pre curves are being rerun with the fixed box (fpFixPre, job 52134553; compare with radMap1 `hk_ref` / `sin_ref`), so the model values above are pre-fix ([[fp-contact-fix]]). The Oct 1 fit also predates the fix; it was rechecked on Nov 24 (next section).

## Oct 1 fit rechecked with the fixed FP contact (2026-11-24)

Local runs of `drivers/calibIdVg.tcl` with the default levers (fixed contact, and `fpBoxOld 1` as a control). The control reproduces `figures/calib_IdVg_field.csv` exactly, so the contact is the only difference. Figure `figures/calib_IdVg_fpfix.png`, curve `figures/calib_IdVg_fpfix.csv`.

| | Old contact | Fixed contact |
|---|---|---|
| rms error, Vg −2.6 to 0 V | 1.9% | 2.7% |
| rms error, Vg −2.6 to +1 V | 1.8% | 2.6% |
| Id error at −2.8 V | +19% | +7% |
| −2.4 V | −1.5% | −5.5% |
| −2.0 V | −1.5% | −3.9% |
| −1.0 V | +1.4% | +0.5% |
| 0 V | +2.3% | +2.3% |
| +1.0 V | −1.0% | +0.6% |
| gm at +1 V (experiment 159 mS/mm) | 88 | 109 |

- The calibration holds (a rigid Vg shift gives no improvement: best phiB 1.65), but Id is 2-5% lower between Vg −2.5 and −1.75 V, where the Oct curve-tracer studies ran (Vg −2: −2.4% against the old contact).
- Turn-on at −2.8 V and gm above +0.5 V are better; −2.4 to −2 V is worse. No parameter was refit: Ian (2026-11-24) judged the fit close enough, so the Oct 1 parameters stay.

Related: [[mobility-models]], [[rad-model]], [[device-structure]], [[current-status]].
