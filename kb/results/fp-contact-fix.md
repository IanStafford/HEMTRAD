---
title: FP contact covered the T-gate head (fixed 2026-11-20)
tags: [results, device, bug, rad-model]
date: 2026-11-20
source: progress.md 2026-11-20; survey finding MOD-1 (kb/workflow/cleanup-plan.md); local checks in the session scratchpad
---
# The FP contact covered the drain half of the T-gate head (fixed 2026-11-20)

**What was wrong.** In all three decks (`model/rfdevice.tcl`, `rfdevice_SiN.tcl`, `rfdevice3d.tcl`) the field-plate contact box went past the FP metal.
- **The box:** x −0.571..−0.150 µm, y 0.284..0.886 µm. Its xhi used `-(SiN_Thick+HPD_Thick)` and its yhi `Gtr+FP_Offset+FP2`.
- **The FP metal itself:** x −0.57..−0.30, y 0.285..0.725.
- **What the box caught:** FLOOXS puts every border node of a material inside a contact box on the contact (`~/flooxs/src/BasePDE/Boundary/Bound.cc:99-121`). So the T-gate head's top surface (x −0.20, y 0.285..0.485) and the top of its drain-side wall were FP contact nodes.
- **Local check (mesh build only):** a test contact on that part of the head panics with "node on two contacts", while a control box on the head outside the FP box is accepted. The FP contact measures 3.61e-8, against 3.06e-8 for the FP metal alone.

**Effect.** Metal is modelled with RelEps 1e12, so a metal body with two different fixed potentials carries a smooth potential gradient. The FP is at 0 V in every driver. At the 28 V stress (Vg −10 V), the DC snapshot of the seeMap28 runs (SiN and HighK identical) gives these metal potentials relative to the FP:

| Where in the metal | Potential vs FP |
|---|---|
| Gate foot | −9.8 V |
| Head, source side (y −0.3 µm) | −9.6 V |
| Head, y 0.3 µm | −1.2 to −2.4 V |
| Head drain corner (y 0.48 µm) | −0.5 to −0.6 V |

So during the stress the head's drain edge sat near 0 V instead of the gate potential. That is the region where the SiN E⁴ stress damage concentrates (y 0.45-0.65 µm, [[step-search-28v]]) and where SiN and HighK differ. Every rad-era result that uses the stress field probably changes: [[rad-model]], [[damage-region-map]], [[step-search-28v]], [[step-mechanism]], [[see-plan]] and [[3d-plan]]. Pre-irradiation curves at Vg +1 had the head drain half near 0 V instead of +1 V, a smaller effect.

**Fix (Ian, 2026-11-20).**
- **The decks:** the box now matches the FP metal (xhi = −(Gate_Thick+HPD_Thick)+buf, yhi = Gtr+FP2+buf). The new deck lever `fpBoxOld` (default 0) rebuilds the old box, only to reproduce pre-fix runs. This default deliberately departs from the rule that new options keep the old behaviour, because Ian asked for the bug to be fixed.
- **Local verification:** with the fix the head box is accepted and FP measures 3.06e-8; `fpBoxOld 1` reproduces the old 3.614441e-8. The 0.55e-8 difference is the head piece.
- **Saved states:** a state carries its own contacts (`B FP Metal` lines in the .str file), so every library and mesh-check state saved before the fix still has the old box. `drivers/radIV.tcl` now writes `fpBox=fixed|old` into each state's settings file. On stressLoad or stressResume it refuses a state whose box differs from the run's `fpBoxOld`; a settings file without the entry counts as old.

**Tests of the effect (params from `analysis/genRadStudy.py`, block 2026-11-20).**

| Set | What | Compare with |
|---|---|---|
| fpFixPre | Pre-irradiation Id-Vg / Id-Vd, both decks | radMap1 sin_ref / hk_ref (calibration) |
| fpFixStress | The 28 V stress library with the fixed box, both decks, saved every volt to `/blue/ee1/ianstafford/stress/fpfix/` | The old library: lateral field along y under the head drain edge, (E_SiN/E_HK)⁴ over y 0.45-0.65 (old: 17 / 30 / 17 / 8.3 / 3.7) |
| fpFixLoad (after fpFixStress) | SiN stress-only at scale 1.5 / 1.6 / 1.8e18; mesh-robust 8e18 series N1-3 (with vdCuts); row A 6e18 N1-3; field-scaled band b N1-3; HighK N0, 8e18 N1-3, band b N1-3 | Rounds A-C, I; does SiN still collapse and HighK not, and do the steps survive? |
| fpFixEB1 | The Nov 11 model (17.66 V stress), all six cases | radEB1, the reference curve in every step figure |

## Results so far (2026-11-21)

- **Pre-irradiation curves: nearly the same, and identical at Vg 0** (fpFixPre 52134553 against radMap1; fxRadHV 52357001 against radHV; figure `figures/rad/fpfix/pre_contact.png`, `analysis/plot_fpFixPre.py`).
  - Id-Vd at Vg +1: +0.3 to +0.8% (SiN 884 → 890, HighK 875 → 882 mA/mm at Vd 4 V).
  - Id-Vd at Vg 0: identical to the last printed digit (at most 1e-4 mA/mm), because the gate and FP are both at 0 V. It is the control that nothing else changed between the runs.
  - Id-Vg at Vd 0.1 V, above 1 mA/mm: −1.2 to +0.7%. The change has the sign of Vg (negative below 0 V, positive above), as expected when the head's drain half follows Vg instead of 0 V. It is largest at Vg −2.2 (SiN −1.0%, HighK −1.2%). Vth −2.997 → −2.998 V; peak gm −0.7% (SiN) and −0.8% (HighK).
  - Off-state Id at Vg −4 (~1e-9 mA/mm): HighK unchanged, SiN 2.6e-9 → 4.3e-10.
  - **Not the same: the field in the off state.** At the 17.66 V stress (Vg −10) the peak field in the damage region (y ≥ 0.3) is about 1.5× higher on SiN and 1.6× on HighK, from the 4.7× and 6.4× damage ratios and the E⁴ scaling. The device is still unirradiated when that field is taken.
  - The Vd 10 V transfer curve of the HfO2 calibration moves more than the Vd 0.1 V one: −2.4% at Vg −2 and +1.6% at +1 V, rms against experiment 1.8 → 2.6% ([[calibration]]). Not measured yet with the fixed box: pre-irradiation sweeps at Vg −2 (curve tracer).
  - Non-biased curves (fpFixEB1 nb cases) moved by under 1%.
- **Biased, Nov 11 levers (damPeak 7e18):** the fixed box gives about 5× more damage at the 2DEG row (fpFixEB1 52134554, fpFixEB1p 52140899).

| Deck | Peak acceptors, GaN side (old → fixed) | AlGaN side (old → fixed) |
|---|---|---|
| SiN | 5.9e18 → 2.7e19 | 1.2e19 → 5.4e19 |
| HighK | 6.6e17 → 4.2e18 | 1.0e18 → 6.5e18 |

- **The curves:**
  - **SiN biased** now collapses completely at 0.1-0.4 V (old: a 375 → 248 mA/mm step at 1.4-1.8 V, then 370 at 10 V).
  - **HighK biased** drops 489 → 409 at 2.2-2.7 V and ends near 500 at 10 V (old: flat, 951).
  - The free stress ramp stopped at 17.77 V (SiN) and 17.93 V (HighK), against 17.66 V before; the pinned 17.66 V runs give the same curves.
- **Read:** the old box held the head's drain edge near 0 V and shielded the field at the gate edge. Every damage scale fitted with the bug (7e18 at 17.66 V, 1.5e18 at 28 V) is about 5× too strong with the fixed geometry. The SiN/HighK damage ratio falls from about 9× to 7×.
- **Refit of the Nov 11 model (fpFixScaleEB1 52223190, 2026-11-22; figure `figures/rad/fpfix_scale_eb1.png`):** damage scale 1.5e18 with the fixed box reproduces the old-box 7e18 curves.
  - SiN biased: 376 → 223 mA/mm at 1.5-2.0 V and 397 at 10 V (old 375 → 248 at 1.4-1.8 V and 370).
  - HighK biased: flat, 955 at 10 V (old 951). It stays flat up to 3e18 (889 at 10 V), so the SiN-vs-HighK contrast is fully back.
  - The scale is 4.7× lower, matching the extra damage. The old curve's small second SiN dip near 7 V does not appear.
  - The same factor would put the 28 V scale near 3e17. The scan below shows that is wrong: it is about 6e17.
- **28 V scale scan (fpFixScale28, HighK 52354341 and SiN 52385669, 2026-11-24).** SiN stress damage only, against the old-box C_p1.5_N0 (395 → 281 mA/mm at 1.6-2.0 V, 432 at 12 V):

| damPeak | SiN drop | Id at 12 V | rms vs old |
|---|---|---|---|
| 1e17, 2e17, 3e17 | none | 796 at 3e17 | - |
| 5e17 | 481 → 421 at 2.0-2.4 V | 523 | 105 (lowest) |
| 7e17 | 332 → 120 at 1.3-1.7 V | 316 | 153 |
| 1e18, 1.5e18 | collapse to ~0 | ~0 | - |

  - The old curve lies between 5e17 and 7e17 (about 6e17): a factor 2.5, not the 4.7 found at 17.66 V.
  - HighK has no drop at any of these scales; 7e17 is closest (rms 1.1), and 1.5e18 is slightly low (921 at 12 V).
  - **Refined (fpFixScale28b 52585664, 2026-11-24): the 28 V SiN scale is 6e17, a ratio of 0.4 to the old 1.5e18.** SiN 6e17 gives 398 → 266 mA/mm at 1.6-2.0 V and 428 at 11.9 V (rms 11.8 against the old curve); 5.5e17 gives 437 → 345 (rms 50.6), 6.5e17 361 → 190 (rms 78.8). HighK 6e17 is flat (961 at 11.0 V). `R_28V` in `analysis/radparams.py`. The head-edge DC field ratio to the fourth power is 2.5 on SiN ([[see-plan]]), the same factor.
- **Nov 11-based remakes (2026-11-24, scale ×1.5/7):**
  - fxRadStrikeN 52357003: the SiN drop is 414 → 306 with no strike and 413-414 → 341-346 with 1-3 strikes, moving from 1.6-2.0 V to 1.9-2.3 V. HighK has no drops, and its 10 V currents are within 1% of the old.
  - fxRadStrike2 52357002: strikes from y 1.2 to 3.1 µm leave the drop at 414-415 → 307; at y 0.8 it is 413 → 341.
  - fxRadHV 52357001: SiN biased to 23 V has further dips at 10.2-11.4 V (456 → 413) and 12.6-14.2 V (429 → 413). Four tasks gave up early, at 10.6, 12.2, 14.8 and 23.2 V.
  - fxSeeMap28 52357004 (figures `figures/see/map28_fix_holeJ.png`, `map28_fix_elecJ.png`): the strike transient barely changes. Drain current at 1 ns is 1.910 against 1.913 mA (SiN) and 1.947 against 1.957 (HighK), substrate hole current 0.338 in both decks. The old box showed a spurious 4.5e-5 A/µm between the gate and FP contacts through the head metal; with the fix it is ~1e-14. Figures for the rest: `figures/rad/fpfix/{nov11_IdVd,strikeN_IdVd,strike2_radHV}.png` (`analysis/plot_fpFixRemakes.py`).
- **Next (Ian, 2026-11-21: refit the scale first; report the HighK contrast before touching other levers; 2026-11-22: remake everything after the Nov 11 model):** choose the 28 V scale, then remake the 28 V rounds ([[fpfix-rerun-list]]).
  - The old-scale fpFixLoad set was never run. Related: [[cleanup-plan]], [[levers]], [[device-structure]].

Which figures and published pages need remaking, marking pre-fix or spot-checking: [[fpfix-rerun-list]].
