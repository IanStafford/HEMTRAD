---
title: Pre/post-irradiation model (HPD vs SiN, biased heavy-ion)
tags: [results, radiation, model]
date: 2026-10-25
source: branch explore/rad-model, drivers/radIV.tcl, sweeps/params_rad*.txt
---
# Pre/post-irradiation model (branch `explore/rad-model`)

> **Final model as of 2026-11-11 (Ian):** the radFinal8 parameter set with the hot-electron capture barrier at **1.0 eV** (was 0.5), a **10 nm** mesh from y 0.3 to 2.0 µm (`meshY`), Vd step 0.1 V, and **no hand-placed second SiN site**. Stress at **Vd 17 V** (`Vd_stress=17.0`; earlier runs stopped there because of the old occupancy overflow, and with `occSafe` the driver would otherwise go on to its 28 V target). Parameters `sweeps/params_radFinal12.txt`; results are radChk 49552956 (pre), radEB1 50411481 (nb, biased) and radEB2 50470082 (5 nm check). Figure `figures/rad/radFinalEB_IdVd.png`.
> - Vth +0.21 V on every irradiated device. Non-biased: 0.93–0.95 of pre, gm −1%.
> - HighK biased: 342 / 951 mA/mm at 1 / 10 V (0.93 / 0.92 of pre), no collapse, gm −2%.
> - SiN biased: 306 at 1 V (0.83), 374 → 255 mA/mm at 1.6–1.8 V, partial recovery to about 390 at 6 V, a dip near 7–8 V, 370 at 10 V (0.36). gm −6%.
> - Not reproduced: the measured second step, the current staying down after the drop, and onset moving later at higher Vg. The sections below are the history, and their steps (radFinal8, radFinal11) are mesh artifacts.

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
- radFinal10 (47943462): the same cases with Vd_step 0.1 and retryDepth 8 still give up at Vd 4.2 / 3.6 V, so the deeper SiN level stays unresolved and radFinal8 is final.

## Final SiN biased curve (2026-10-27, radFinal11 job 47959281)
Settings: radFinal8 set with damPeak 6e18 + second site `dam3Peak 4.5e18` (y 1.0–1.6), Id–Vd at `Vd_step 0.1, retryDepth 8`. It runs to 10 V:
- Id (Vg +1) 212 / 342 / 417 / 452 mA/mm at Vd 1–4 V;
- **steps near 4.5 V (→ 360) and 5.8 V (→ 255)**;
- then a slow creep up to 377 at 10 V;
- gm −18%, Vth +0.20 V.

Qualitatively the measured SiN biased curve: low-Vd loss, two steps, late onset, creep. The final level is close to measured.

Other cases in the run:
- 6.5e18 + 4e18 and 7e18 + 3e18 also run to 10 V, but end at 472 / 494 with a single step.
- (radFinal9/10 with 5e18–6e18 sites can't be followed through the step.)

This replaces the radFinal8 two-site SiN curve. All other devices stay at radFinal8.

## Stress at the real 28 V (2026-10-29, rad28a job 48206375)
With `occSafe 1` the stress reaches Vd 28 V. pre/nb with occSafe are identical to radFinal/radFinal8 (the rewrite is exact).
- **Lateral field at 28 V** (x = 0.001 µm):
  - SiN: 7.5e5 V/cm at y = 0.5, 5.8e5 at 0.6, 3.4e5 at 0.7 (up to the field-plate edge);
  - HighK: 3.4e5 / 3.5e5 / 3.2e5 at the same y, still 2e5 at y = 1.0;
  - gate-edge peak 1.04e6 in both.
- **Damage scale:** the same law needs damPeak ~1.5e18 at 28 V instead of 7e18 at 17 V.
  - SiN 1.5e18: 0.82 / 0.77 / 0.66 / 0.55 / 0.49 at Vd 1 / 2 / 2.5 / 4 / 10 V;
  - HighK 1.5e18: 0.93 flat;
  - 3e18 and 7e18 overdamage SiN (0.08, 0).
- **Conclusion:** the full stress voltage changes the damage scale but not the picture. The SiN onset stays near 2 V; the 17 V result was not an artefact of the solver limit.

## Ways to make the Vth shift (2026-11-04, radVth job 49570570, radVth2 job 49606876)

Each row is one mechanism, no stress solve, ratios against the undamaged reference. HighK and SiN agree to within about 0.001 V, so one column serves both. Numbers are model results, and none of these says the mechanism is what happens in the device.

| Mechanism | Setting | ΔVth (V) | gm ratio | Ron ratio | Id(1 V) ratio |
|---|---|---|---|---|---|
| Schottky barrier | `phiB` +0.2 eV | +0.20 | 1.00 | 1.01 | 0.99 |
| Polarization under the gate | −5% | +0.22 | 1.01 | 1.01 | 0.99 |
| AlGaN acceptors under the gate (current model) | 5e17 | +0.17 | 1.00 | 1.00 | 0.995 |
| Channel acceptors under the gate | 5e17 | +0.27 | 0.87 | 1.02 | 0.98 |
| Polarization, whole device | −5% | +0.22 | 0.985 | 1.06 | 0.94 |
| AlGaN acceptors, whole device | 5e17 | +0.17 | 0.98 | 1.07 | 0.93 |
| Surface charge | −1.2e12 cm⁻² | +0.17 | 0.96 | 1.15 | 0.87 |
| Channel acceptors, whole device | 5e17 | +0.26 | 0.78 | 1.35 | 0.74 |
| Dielectric charge near the gate (y −0.35 to 0.40) | 1e18 | +0.03 | 0.97 | 1.04 | 0.96 |
| Dielectric charge, y ≥ 0.30 | 1e18 | −0.015 | 0.80 | 2.0–2.1 | 0.46–0.49 |
| Buffer acceptors that fill (level 3.3 eV) | 1e16 / 1e17 | +0.017 / +0.108 | 1.00 / 0.98 | 1.00 / 1.03 | 0.995 / 0.965 |
| Buffer acceptors that stay empty (0.30, 1.0, 1.7 eV) | up to 5e17 | 0, not a test | 1.00 | 1.00 | 1.00 |

- **Vth alone can't separate these.** Ron and gm can: gate-local routes leave Ron within 2%, whole-device routes raise it, and channel-depth routes cost gm.
- **One lever for two effects?** A whole-device route gives the Vth shift and a small Ron rise together, which the current model does with two levers (`dam2Peak`, `surfCharge`). Not yet tested against measured data.
- **Dielectric charge isn't a Vth route.** At the gate it reaches only +0.03 V at 1e18, because there's no dielectric under the gate foot.
- **Back-gating works but takes a lot of charge.** The model's buffer is undoped and holds no electrons to fill levels at 0.30–1.7 eV: at 1.7 eV, IonAcceptor is about 4e-9 cm⁻³ out of 5e17 (local check). A level of 3.3 eV does fill, 58–100% at 1e16 (local check). With it (radVth3, job 49614033), +0.108 V takes 1e17 cm⁻³ over 1.3 µm, a sheet of about 1e13 cm⁻², roughly ten times what surface charge needs for a similar shift.
- **Reduced polarization needs care on SiN.** `sin_polAll9.7e12`, `sin_polAll9e12` and `sin_polGate0.9` ran hours longer than the rest, retrying in Id–Vd with Qfp not converging. Their Id–Vg is fine.

Reachable size is a separate question: [[rad-literature]] finds no Vth data near 1e7 cm⁻². Candidate high-Vd behaviour isn't covered, since these runs stop at 5 V to save CPU.

Related: [[damage-region-map]], [[ron-increase]].

**Correction 2026-11-05 (radFine, job 49735196): the two steps of the final SiN curve above are mesh artifacts.** With 10 nm from y 0.3 to 1.6 µm, the same parameter set gives 118 / 211 / 340 / 451 mA/mm at Vd 0.5 / 1 / 2 / 4 V, then a smooth rise to 473 at 10 V, with no step larger than 1 mA/mm. The standard mesh gave steps near 4.5 and 5.8 V and 377 at 10 V. Below the steps, the two meshes agree within 1%, so the low-Vd loss, the Vth shift and the SiN vs HighK difference stand; the late collapse does not. The model doesn't currently reproduce the measured steps. The final set is unchanged pending Ian's decision. Not yet rechecked on a fine mesh: radFinal8's other curves and the 28 V set. See [[damage-region-map]].

## Capture barrier 1.0 eV in the final set (radEB1, job 50411481, 2026-11-09, test only)

10 nm from y 0.3 to 2.0 µm, Vd step 0.1 V, otherwise the final set. 6 tasks, no crashes. Figure `figures/rad/hotEb_final.png`. Id in mA/mm at Vg +1 V.

| Device | hotEb 0.5 (final) | hotEb 1.0 |
|---|---|---|
| HighK biased | smooth, 952 at 10 V | identical, 951 |
| SiN biased, one site | 455 at 2 V, smooth, 503 at 10 V | 373 at 1.5 V, falls to 255 at 2 V, recovers to about 387, dips again near 7 V, 370 at 10 V |
| SiN biased, one site, hotEb 0.75 | | small drop near 1.8 V (400 to 351), 448 at 10 V |
| SiN final, two sites | smooth, 473 at 10 V | drops near 3.4 V (388 to 322) and 6.6 V (393 to 299), recovers to 376 at 10 V |
| Non-biased, both decks | no collapse | no collapse, same curves |

- Vth and gm are unchanged by the barrier (SiN two sites gm 55.8 against 68.0 pre, −18%, as before).
- At hotEb 1.0 the model again collapses SiN and not HighK, on a fine mesh, with two drops when there are two sites. The drops recover partly between and after, unlike the measured slow creep.
- **5 nm check (radEB2, job 50470082, 2 tasks, no crashes):** the one-site collapse is converged: 374 to 256 mA/mm at 1.6–1.7 V, then the same recovery, within 2 mA/mm of 10 nm everywhere. The two-site drops are not: at 5 nm they shrink to 28 mA/mm at 3.4 V and 22 at 4.9 V, with smaller wiggles, ending at 395. The second site (dam3, 4.5e18 at y 1.0–1.6) is still mesh-sensitive.
- So hotEb 1.0 gives one real, SiN-only collapse from the field-placed damage. A converged second step isn't there yet. The final model stays at 0.5 unless Ian decides otherwise.

## Exploring from the final set (radExp1 50831893, radExp1c 50892179, 2026-11-11/12)

Figure `figures/rad/radExp1.png`. SiN biased unless stated, Vg +1 V, Id in mA/mm, hotEb 1.0, 10 nm mesh.

| Change | Result |
|---|---|
| Damage scale 4.5e18 / 3e18 / 2e18 (final 7e18) | no collapse: 663 / 847 / 940 at 10 V. Lowering the scale removes the collapse rather than delaying it |
| Trap level 0.40 eV (occSafe, 17 V) | drop at 1.3–1.4 V (290 to 225), rises to 348 at 6 V, 334 at 10 V; Vth +0.25 V, gm 63.0 |
| Trap level 0.50 eV (occSafe, 17 V) | drop at 0.9–1.0 V (149 to 99), slow rise to 183 at 4 V and 239 at 10 V; Vth +0.26 V, gm 61.2 |
| HighK at 0.40 / 0.50 eV | no collapse, 941 / 936 at 10 V; Vth +0.26 V |
| HighK with a Gaussian strike (y 1.5, 5e18) | no step, but a hard limit near 480–560 mA/mm (563 at 10 V, 0.55 of pre) |

- **A deeper level makes SiN stay down and creep, as measured, but moves the onset earlier** (0.9 V at 0.50 eV), the wrong way; measured SiN collapses near 4.5 V. It also adds about 0.05 V to the Vth shift on both decks.
- **A smooth strike in HighK costs it about 45% at high Vd.** The measured HPD stays flat, so a strike like that didn't land in it, or its damage was weaker.
- **The SiN Gaussian tasks didn't finish:** two timed out in the stress solve at 12.5–15.5 V (over 200 retries), one overflowed at 17 V. None had occSafe. Rerun in radExp2 with occSafe and the stress pinned at 17 V.
- **Running (radExp2):** SiN Gaussian second strikes again; damage scale 5e18–6e18 (does the onset move later near threshold?); level 0.40–0.50 eV with a smaller scale (later onset that still stays down?).

