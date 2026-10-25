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

Consolidated run: radFinal, job 47693156 (pre / nb / biased × both decks).

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
