---
title: Pre/post-irradiation model (HPD vs SiN, biased heavy-ion)
tags: [results, radiation, model]
date: 2026-10-25
source: branch explore/rad-model, drivers/radIV.tcl, sweeps/params_rad*.txt
---
# Pre/post-irradiation model (branch `explore/rad-model`)

Goal (2026-10-23): one model that reproduces, **qualitatively** (Ian, 2026-10-25), the measured pre- and post-irradiation behaviour of the HPD (#11) and SiN (#35) devices, irradiated non-biased and biased (Vg −10 / Vd 28 V) with high-LET heavy ions. The measured data are kept untracked (`data/rad_y2/`, `kb/results/measured-rad-y2.md` on the workstation only), so this note gives model numbers and qualitative comparisons only.

## Driver and tools
- `drivers/radIV.tcl` (branch only):
  - `radState pre|post`;
  - Id–Vg at Vd 0.1 and Id–Vd at Vg +1 V;
  - for post: an off-state stress solve, damage traps set from the stress solution, then the measurement with hot-electron fill-only capture.
  - Every lever has an `info exists` default.
- `sweeps/radIV.slurm` is the generic template; each params line is `label|lever=value;...`.
- `analysis/radCompare.py`: Vth, gm, Id at fixed points, and ratios.
- `analysis/radFit.py`: fits lumped drain-access elements (series R and a contact-like offset V0) and scores post/pre ratios against the measured curves.

## Pre-irradiation calibration
Rounds 1–3 (jobs 47311016, 47324103, 47327599) settled on:
- polCharge 1e13, phiB 2.94;
- mobNref 1e18, vsat 1.75e7 cm/s, mumax 2100 (`mobVsat`/`mobMumax`/`mobNref` levers in `model/GaN.tcl`, branch).

Result: Vth within 0.03 V, Id–Vd at Vg +1 within ~4%, gm ~25% high.

## Post-irradiation model (all set at the stress bias)
1. **Fixed negative surface charge** `surfCharge −4e11 cm⁻²` (bias-independent): Vth +0.06 V and ~−4% current in both decks. The measured shift is a bit larger. −1.2e12 gives the size, but adds a flat ~15% loss that the data don't show.
2. **Lateral-field damage beyond the gate edge:**
   - N = damPeak·(E_lat/5e5)⁴ for y ≥ 0.30 µm in the top 50 nm, as acceptor traps at 0.30 eV;
   - hot-electron fill-only capture (hotEb 1.0, hotTau 1e-14);
   - SiN concentrates the stress field at y 0.35–0.65 µm (5.5e5 vs 2.9e5 V/cm in HighK at y 0.5), so only SiN collapses, and the collapse starts above the knee (radWin w2, radFine, radFit1).
3. **n·E damage in the gate–drain access region:** N = dam2Peak·(n·E_lat / peak) for y 0.125–3.0. This gives a Ron-like loss that is largest at low Vd and recovers toward 10 V, in both decks (radNE2: HighK 0.78 → 0.94 at 3e20).
4. **Gate–drain leakage:** a lumped `Rgd` (post-processing in `IdExt`), not physical.

## Consolidated run: radFinal (job 47693156, `sweeps/params_radFinal.txt`)
All 8 tasks COMPLETED, no GAVE UP. Figure: `figures/radFinal_model.png` (model only; the overlay with measured curves is kept untracked on the workstation, `data/rad_y2/radFinal_overlay.png`). Plot script: `analysis/plot_radFinal.py`.

Ratios to each deck's pre run, Id(Vg +1) at Vd 1 / 2 / 4 / 6 / 10 V, and low-field Id(Vg −1.4, Vd 0.1):
- pre: HighK and SiN within 1% of each other, Vth −3.00 V.
- nb (both decks): 0.96 flat, low field −4%, Vth +0.057 V.
- **biased HighK** (damPeak 5e18, n·E 3e20): 0.77 / 0.78 / 0.81 / 0.85 / 0.93. This is a Ron-like loss that recovers toward high Vd, with no collapse. Low field −23%, Vth +0.049 V, gm −10%.
- **biased SiN** (same levers): 0.71 / 0.72 / 0.57 / 0.55 / 0.56. Flat to ~3 V, then a collapse step at ~3.3 V. Low field −29%, Vth +0.049 V.
- damPeak 5.5e18: HighK unchanged, SiN step to 0.50.

**Qualitative comparison with the measured set** (Ian accepted a qualitative fit, 2026-10-25):

| Phenomenon | Model | Measured | |
|---|---|---|---|
| pre transfer/output | matches | — | ✓ |
| +Vth after irradiation, all devices | +0.05–0.06 V | larger | ✓ sign, smaller size |
| SiN biased: collapse above the knee | one step at ~3.3 V | two steps (~4.5 and ~7 V), deeper | ✓ qualitative |
| HPD biased: no collapse | ✓ | ✓ | ✓ |
| biased low-field loss, recovering with Vd | ✓ | ✓ (recovers faster) | ✓ |
| deck order of the low-field loss | SiN > HPD | HPD > SiN | ✗ |
| nb low-Vd loss | flat −4% | SiN has a low-Vd dip | partial |
| off-state gate–drain leakage (biased) | lumped `Rgd` only | ~linear in Vgd, steps during irradiation | lumped |

## What each run showed

| Run (job) | Finding |
|---|---|
| D1 (47327524) | m1/m2 damage: flat 4–10% losses, no collapse, decks identical |
| D2 (47356193) | m4/m6 damage: collapse, but both decks (gate-edge damage saturates equally) |
| radWin (47458256) | Damage position matters. Gate edge (y 0.125–0.30): early collapse in both decks. y 0.30–0.65: SiN-only drop from ~4 V |
| radIns (47458257) | Fixed charge in the SiN: same in both decks. Higher hotEb moves the onset earlier. Dropped |
| radPost / radFine (47523721 / 47562303) | y ≥ 0.30: HighK flat, SiN collapse; depth set by damPeak (4e18 → 7.5e18) |
| radFit1 (47593908) | surfCharge −4e11 moves the SiN onset ~1 V later than −1.2e12 |
| radFit2 (47606666) | A second, farther damage site gives a second, later step (onset Vd rises with distance from the gate). The same uniform damage collapses HighK too, so the deck difference must come from where the stress places damage |
| radNE1 (47628955) | n·E weighting over the whole device: contact-edge and source damage dominate; decks identical |
| radNE2 (47662463) | n·E limited to gate–drain: Ron-like, recovering loss in both decks |

## Caveats
- The off-state stress solve stops at Vd 17 V (Vdg ≈ 27 V; NaN in the minority quasi-Fermi levels in the depleted AlGaN), not 28 V. The damage scale absorbs the field magnitude. Solving the stress without holes might reach 28 V, but that is a physics change; it needs Ian's approval.
- The y ≥ 0.30 µm exclusion of gate-edge damage is a fitting choice. Without it, gate-edge damage collapses both decks equally, which the data don't show. n·E weighting gives no gate-edge damage naturally (no electrons there at stress), but it can't produce the SiN late collapse.
- The measured SiN collapse steps down twice (event-like damage); the model gives one step unless a second site is added by hand.
- The leakage (Rgd) and the low-Vd contact offset (V0, from radFit) are lumped elements.

Related: [[highk-vs-sin]], [[hot-electron-capture]], [[trap-model]], [[levers]].

## Final model (2026-10-26, radFinal2 job 47752290): n·E access term dropped
With `dam2Peak 0` (no n·E access damage), otherwise as radFinal:
- **Biased HighK:** 0.94 flat (Id ratios at Vd 1–10 V 0.93–0.96), gm −2%, Vth +0.057 V. Qualitatively on the measured HPD biased Id–Vd curve; the measured HPD gm is essentially unchanged.
- **Biased SiN:** low field 0.88, then a collapse from ~2.3 V to 0.57–0.59, gm −5%, Vth +0.054 V. Measured SiN loses clearly more gm and collapses in two steps, deeper.
- With the n·E term (1e20 / 3e20), HighK loses 10–23% at mid Vd: the n·E band is *larger* in HighK, the wrong deck direction, so the term was dropped.
- radPhys1 (job 47725314): weighting the field damage by electron density (n·E⁴) has no effect at any damPeak, because the high-field region is fully depleted at the stress bias. It can't replace the y ≥ 0.30 exclusion.
- **Final post-irradiation model:**
  - surfCharge −4e11;
  - lateral-field E⁴ damage at y ≥ 0.30 (damPeak 5e18, damEref 5e5, top 50 nm, acceptors at 0.30 eV);
  - hot-electron fill-only capture;
  - a lumped Rgd for the gate–drain leakage, sized per device from the measured off-state current (values kept with the untracked data).
- **Notes on the measured set (qualitative; details in the untracked note):**
  - Compare each device with its own pre.
  - The non-biased devices are different parts, and their device spread is larger than the radiation effect.
  - The biased HPD Id–Vg at Vd 0.1 loses more than its Id–Vd suggests, possibly a measurement-order or recovery effect that a static model can't reproduce.

## Final parameter set (2026-10-26, radFinal5 job 47806744)
Base: round-3 calibration.

**Post-irradiation:**
- surfCharge −4e11;
- under-gate fixed acceptor damage 1.5e17 cm⁻³ (uniform, y −0.125…0.125, top 50 nm; `dam2Field lat dam2M 0`);
- lateral-field E⁴ damage damPeak 7e18 (damEref 5e5, y ≥ 0.30, acceptors at 0.30 eV);
- hot-electron fill-only capture, hotEb 0.5, hotTau 1e-14;
- lumped Rgd for the leakage.

**Model results** (ratios to each deck's pre):
- Vth +0.19 V on every irradiated device (nb and biased, both decks); the measured shifts have the same scale.
- nb: 0.95 → 0.93 across Vd, gm −7%.
- **Biased HighK:** 0.92 flat (no collapse), gm −8%.
- **Biased SiN:** 0.83 at 1 V, 0.75 at 2 V, 0.62 at 2.5 V, 0.53 at 4 V, 0.48 at 10 V; gm −12%.
- SiN damPeak 6e18 / 8e18 brackets the depth (0.57 / 0.40 at 10 V).

**Lever findings (radFinal3–5):**
- **Capture barrier hotEb:** lowering it from 1.0 to 0.7 to 0.5 moves the SiN onset later and makes it gentler. HighK is unaffected.
- **Under-gate charge:** sets the Vth shift, about +0.24 V at 2e17, +0.40 V at 4e17 and +0.80 V at 1e18.
- **hotTau 1e-12:** collapses SiN completely. Not used.

**Remaining differences (qualitative):**
- The SiN collapse starts ~2 V earlier than measured and is a single step. The measured collapse comes in two steps and goes deeper.
- The model gm loss is similar in both decks (−8% / −12%), whereas measured shows a clear SiN > HPD difference.
- The leakage is lumped.
- The gate-edge exclusion is a fitting choice.
- The stress solve stops at 17 V.

## Second discrete damage site (2026-10-26, radFinal6 job 47829928)
The optional third site `dam3Peak/dam3Ymin/dam3Ymax` (uniform, default off) puts an ion-strike-like damage spot at y 1.0–1.6 µm on top of the final set.
- **SiN p6e18 + 4e18:** 0.60 at 1 V, then a *first step* near 5 V (0.53 → 0.44 at the Id–Vd level) and a *second step* near 6.3 V, followed by a slow creep up. The two-step shape, onset region and low-Vd loss now resemble the measured SiN biased curve qualitatively.
- **SiN p7e18 + 2e18 / 4e18:** steps merge or come earlier.
- **HighK p7e18 + 4e18:** the same uniform site collapses HighK too (0.63 → 0.39 near 6 V). So the second site is device-specific (a random strike location in that SiN device) and can't be derived from the deck. It's a fitting choice, documented as such. The leakage stepping during irradiation supports event-like damage.

## Consolidated final model (2026-10-27, radFinal8 job 47887339)
One parameter set for every device (`sweeps/params_radFinal8.txt`; pre from radFinal 47693156):
- **pre:** polCharge 1e13, phiB 2.94, mobNref 1e18, vsat 1.75e7, mumax 2100.
- **post (all devices):**
  - surfCharge −4e11;
  - fixed acceptor charge 5e17 cm⁻³ in the AlGaN under the gate (`dam2Peak 5e17 dam2M 0 dam2Ymin −0.125 dam2Ymax 0.125 dam2Xmax 0.014`).
- **post, biased:**
  - lateral-field E⁴ damage at the stress bias (damPeak 7e18, damEref 5e5, y ≥ 0.30, top 50 nm, acceptors at 0.30 eV);
  - hot-electron fill-only capture (hotEb 0.5, hotTau 1e-14);
  - optional second discrete strike site for the SiN device (damPeak 6e18 + `dam3Peak 4e18` at y 1.0–1.6).
- **Leakage:** a lumped Rgd per device.

**Model results** (vs each deck's pre):

| | ΔVth | Δgm | Id(Vg +1) ratio, Vd 1 → 10 V |
|---|---|---|---|
| nb HighK / SiN | +0.21 V | −1% | 0.95 flat |
| biased HighK | +0.21 V | −2% | 0.93 flat (no collapse) |
| biased SiN, one site | +0.21 V | −5% | 0.83 → 0.48, single step from ~2 V |
| biased SiN, two sites | +0.21 V | −17% | 0.60, steps near 5 V and 6.5 V, slow creep up |

**Qualitative match with the measured set:**
- every irradiated device shifts Vth positive;
- HPD biased: no collapse and gm essentially kept;
- SiN biased: a late, two-step collapse with a low-Vd loss and a clear gm loss (largest of all devices);
- nb: small changes.

**Remaining differences:**
- the SiN final level is shallower than measured;
- the lumped leakage, the gate-edge exclusion and the second-site placement are fitting choices.

**Stress limit (confirmed 2026-10-26):** the off-state stress stops at Vd 17 V (Vdg ≈ 27 V).
- Ian approved `stressNoHoles` (holes removed above `stressNoHolesX`; removing them everywhere breaks the Fe buffer). It runs, but stops at 17 V with identical fields.
- Qfn damping (`stressQfnDamp` 0.02 / 0.005) also stops at 17 V.
- The Newton log diverges in Qfn in the depleted AlGaN/GaN, a hard solver limit. Both levers stay in, default off (smokes 47861047, 47875456).
- radFinal9 (47908735): a stronger second site (5e18 / 6e18) deepens the SiN low-Vd loss (gm −19% / −21%), but every Id–Vd sweep gives up at Vd 3.75–4.5 V, right at the collapse step. So the deeper SiN final level couldn't be confirmed, and radFinal8 stays the final set.
