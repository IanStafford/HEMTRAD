---
title: Current status
tags: [status]
date: 2026-11-20
---
# Current status (as of 2026-11-20)

What is running, what is open, and the current answer on each topic, with a link to the note that owns it.

**Repo:** reorganised 2026-10-12 into `model/`, `drivers/`, `sweeps/`, `analysis/`, `data/` ([[repo-locations]]); FLOOXS internals in [[flooxs-overview]]. The repo is public, so measured numbers stay in untracked files. The code and KB clean-up follows [[cleanup-plan]]; stage 1 (docs, KB, comments) started on Nov 20.

> **2026-11-24:** with the FP contact fixed, the Nov 11 damage scale (17.66 V stress) is 1.5e18 instead of 7e18 and reproduces the old curves, with the SiN/HighK contrast kept. At 28 V the SiN scale is 6e17 (old 1.5e18). The Nov 11-based remakes are done and the 28 V rounds (262 tasks) are running. Details: [[fp-contact-fix]].

## Now

**FP contact fix (Nov 20).** The FP contact box in every deck covered the drain half of the T-gate head, so during the 28 V stress the head's drain edge sat near 0 V instead of −10 V. That is where the SiN stress damage concentrates. Fixed in the decks (lever `fpBoxOld`, default 0 = fixed; Ian approved). A saved stress state carries its own contacts, so every state saved before the fix has the old box, and radIV refuses to load one into a fixed-box run. Results built on those states are marked *pre-fix* below and are being rerun ([[fp-contact-fix]]).

**On HPG (2026-11-24):**
- **28 V round remakes** (19 studies, 262 tasks, jobs 52610347-52610365, commit c77b59f): the strike rounds A-K, round S, the m10 / m5fix / 2.5 nm mesh checks and the diagnostic runs on the fixed-box library, field-dependent damage x0.4 (28 V SiN scale 6e17 instead of 1.5e18, [[fp-contact-fix]]).
- **fxNoCut28 52605290** (4): the y >= 0.30 cutoff moved to y 0.0. **fxStrikeField28 52605291** (8, DRV=seeIV): strike transients, unbiased control at Vg -10 / Vd 0, other positions, 0.1 um width ([[see-plan]]).
- **Done since Nov 20:** the fixed-box 28 V library, the mesh stresses, fpFixPre, fpFixEB1, the Nov 11 refit, the 28 V scan (fpFixScale28, fpFixScale28b: 6e17) and the Nov 11-based remakes. Results in [[fp-contact-fix]].

**Result (2026-11-25):** the stepped SiN series survives refinement: trap 0.40 eV / 7e18 gives 1 / 2 / 3 drops for 1 / 2 / 3 strikes on 5 nm and 2.5 nm, trap 0.30 / 8e18 at 2.5 nm. HighK also steps with the same plain strikes, so the passivation contrast is still missing ([[step-search-28v]]).

**Next:** HighK at the same setting and on the fine meshes; a strike law that steps SiN and not HighK; strike-field results; figures in the order of [[fpfix-rerun-list]].

**Cancelled Nov 20:** the old-box 2.5 nm stress meshChkStress2p5 52044407 (it had reached Vd 20 V). The four-mesh check that was to load it (radStepM3) was never submitted. fpFixMesh redoes the stress with the fixed box; the strike series are to be loaded on it once it saves Vd 28.

**Open decisions for Ian:**
- **28 V damage scale (settled 2026-11-24):** 6e17 on the fixed box, chosen by the rule announced on Nov 22 ([[fp-contact-fix]]).
- **SiN stress at the R35 bias.** The strike transients seeGen1 and seeGen2 use the slide-legend gate bias for R35; the rad model still stresses both decks at Vg −10. Rerun the SiN stress at the R35 bias? Open since Oct 29 ([[see-plan]]).
- Ian answered the clean-up plan's questions on Nov 20: the answers are in `progress.md` (Nov 20 evening), the questions in [[cleanup-plan]] §1.

**Waiting on:** a comprehensive measured dataset (same-device pre/post), and then a final summary of what in the rad model is empirical and what is fitted.

## Current answers

All results below ran with the old FP box. Those built on the stress field (the rad model, the stress library, every strike round, the step mechanism) are marked *pre-fix* and are being rerun. The 28 V strike maps (seeMap28) are marked *pre-fix* too; no rerun of them is queued. Results with placed damage and no stress solve, and the pulsedIV-era studies, are not being rerun. For measurements at Vg +1, [[fp-contact-fix]] expects only a smaller effect (head drain half near 0 V instead of +1 V); fpFixPre checks the pre-irradiation curves.

**Rad model (pre/post irradiation, HPD vs SiN):**
- **The model** (pre-fix; being rerun, [[fp-contact-fix]]). Off-state stress at Vg −10 / Vd 28 V (Ian, Nov 12), loaded from the stress library. Lateral-field E⁴ acceptor damage beyond the gate edge (y ≥ 0.30 µm, top 50 nm) at scale damPeak 1.5e18, trap level 0.30 eV, hot-electron fill-only capture with hotEb 1.0 eV. surfCharge −4e11 and 5e17 AlGaN acceptors under the gate give the Vth shift.
  - SiN biased drops once, 395 → 273-281 mA/mm at 1.6-2.0 V on three meshes. HighK biased doesn't collapse (956 mA/mm at 10 V). Vth +0.21 V on every irradiated device.
  - Qualitative fit accepted by Ian; goal closed Oct 27, model updated Nov 11 (hotEb 1.0, no hand-placed second site) and Nov 12 (28 V stress). The stress damage alone gives no second SiN step.
  - Current model box, superseded versions and history: [[rad-model]]. Damage laws: [[damage-model]].
- **Stepped collapse with strikes at the 28 V stress** (pre-fix; being rerun, [[fp-contact-fix]]). Goal set by Ian on Nov 17 (1-3 strikes on top of the stress damage); he closed it on Nov 18 with two partial results, and the mesh-robust series of Nov 20 replaced that deliverable.
  - Trap 0.30 eV with 8e18 strikes (σ 40 nm at y 0.8 / 1.6 / 2.4 µm) gives 2 / 3 / 3 drops for 1 / 2 / 3 strikes on the library, m10 and m5fix meshes. The first drop starts at 1.1-1.7 V, within 0.1 V across meshes for each strike count; the later drops move with the mesh. HighK collapses with the same strikes.
  - Trap 0.40 eV with 7e18 gives one drop per strike, but only on m5fix. The Nov 18 deliverable's row A (6e18 strikes) is not mesh-robust.
  - Plain strikes dense enough to step SiN also drop HighK. Field-scaled strikes keep HighK flat but give SiN one deepening drop (rounds H-J). The hybrid of the two fails (round K, 51939558).
  - Corrected geometry, field-scaled strikes on a weak stress band (fxFieldStrike1 52761027, Nov 25, 72 runs): HighK flat in all 36; SiN one drop in most runs, two only with a single dense strike (e.g. 282 → 152 at 1.0 V and 328 → 231 at 6.8-8.0 V); more strikes never add drops. `figures/rad/fpfix/fieldstrike1.png`.
  - Figures `figures/rad/step28/mesh_deliverable.png`, `mesh_series.png`; Nov 18 deck https://claude.ai/artifact/5gkYKv6DZjGL7PAuTvZxR6. Details: [[step-search-28v]].
- **Why the strike curves step** (pre-fix; being rerun, [[fp-contact-fix]]). Each damaged spot (the stress band at y 0.45-0.72 µm and each strike) is a partly depleted pocket of the 2DEG; the pockets sit in series and share the drain voltage. Each first switch came once ~0.5 V sat across the pocket (|Ey| integral 0.46-0.59 V at all 14 first switches; necessary, not always enough). The barrier traps over its drain flank then finish filling with hot electrons and Id drops. Switches and drops are not one-to-one. Runs: radStepDiag 51998840 and radStepDiag5b 52018703 (the latter from `sweeps/params_radStepDiag5.txt` as of commit f2edae8). FLOOXS `print1d` resamples cuts to 500 points, so spacings read from cuts are unreliable ([[flooxs-gotchas]]). Details: [[step-mechanism]].
- **Stress library** ([[stress-library]]). The old-box library (stressLib 51459840) holds a state every volt at Vg −10 on both decks, on the 93,080-point library mesh (~13.7 MB per state). HighK finished in that job; SiN hit the 4-day limit and was resumed from 60 V (51998839), which completed to 84 V on Nov 20. It has the old FP box, so fixed-box runs can't load it. fpFixStress rebuilds it to 28 V.
- **Strike count at a true 17 V stress** (radStrikeN 51174895; pre-fix). SiN stays near half of pre above 4 V whatever the strike count. HighK saturation falls with each strike (0.93 → 0.79 → 0.75 → 0.72 of pre at 10 V). Both lose ~0.04 of pre per strike at 1 V ([[rad-model]]).
- **Damage by region** (radMap1 49570571, radMesh 49606872, radFine Nov 5 49735196, radMulti 49735488; placed damage, no stress solve). Vth moves only under the gate (+0.78 V at 1e18, +1.96 V at 4e18). Each section adds series resistance, about the same anywhere (0.1 µm at 1.2e19: about +1.1 Ω·mm per site, additive up to 5). Current saturates at a level set by density (558, 346, 229 mA/mm at 4e18, 6e18, 8e18), independent of Vg. The uniform-site steps of the standard mesh did not survive 10/5 nm; a σ 40 nm Gaussian's first drop converges between 5 and 2.5 nm, later drops move ([[damage-region-map]]).
- **Ron candidates** (radRon 49606877): dielectric charge, access acceptors and mobility loss all raise Ron without moving Vth; low-exponent field damage reaches only +9% ([[ron-increase]]).
- **Vth routes** (radVth 49570570): barrier, polarization, AlGaN acceptors and surface charge all reach about +0.2 V; Ron and gm tell them apart. Back-gating works but needs about 1e13 cm⁻² for +0.1 V (radVth3 49614033) ([[rad-model]]).
- **HighK vs SiN with the same hand-placed traps** (Vg +1, Vd to 10 V, job 47062225): identical onsets on both decks (1.3 / 1.5 / 1.7 V for traps at y 0.3 / 1.0 / 2.4 µm). Only the post-collapse recovery differs (SiN 20-60× lower at 10 V). So the deck difference of the rad model comes from where the stress places the damage, not from the trap model ([[highk-vs-sin]]).
- **Literature:** nothing at our fluence for Vth or Ron ([[rad-literature]]); no published stepped collapse after heavy ions ([[rad-literature-steps]]).

**Single-event transient** ([[see-plan]]). Generation-pulse strikes (`seeMethod gen`, `tranSign 1`) at Vd 28 V; the quasi-Fermi injection route was dropped because FLOOXS's TR-BDF2 first step never converges.
- seeGen1 49135298 to 1 ns: drain ~2 mA/µm, 3× the deposited charge. The buffer and the gate barrier both collapse, and the peak field moves to the drain edge.
- seeGen2 49511531: the current turns over near 0.7 ns. The run was cancelled at 22.9 h after bad steps at 1.39 / 1.47 ns, so the decay is not followed to the end. No lasting step or gate current yet.
- seeMap28 51945449 (pre-fix): at Vg −10 / Vd 28 V SiN and HighK are nearly identical. Holes go down the track and out through the p-type buffer to the substrate (0.34 mA/µm from 100 ps), none to the gate.

**Curve-tracer collapse (pulsedIV era, Sep 23 to Oct 23; the original goal, [[project-goal]]):**
- **Model:** calibrated field mobility ([[calibration]]), local-field hot-electron capture ([[hot-electron-capture]]), Te-ramp stall rescue ([[te-ramp]]). **Since 2026-10-16 (Ian) the local-field model (`eTemp 0`, the model-file default) is the standard, to save computation time.** The electron energy balance (`eTemp 1`; standard Oct 13-16) is an option: it collapses at the measured voltage but costs ~1.9 s per Newton iteration ([[energy-balance]]).
- With the energy balance the late set collapses at **0.4–0.7 V** (set by τ); at y = 2.4 µm a 60–4000× drop onto a creeping plateau, close to the measured shape (job 45768739, `figures/eTempStd_IdVd.png`, [[energy-balance]]).
- Local-field model: latest deep collapse **3.5 V** (late-onset set at y = 2.4 µm), 177 → 0.0018 mA/mm in one step, then creep ([[late-onset-search]]).
- Trap **position** is the strongest onset lever near the charge threshold; deeper levels / more charge collapse early and uniformly ([[position-maps]]).
- **Lever sensitivity** (job 46462234, one lever at a time around the late set at y 1.0 µm, onset 2.3 V): `trapLevel`, `hotEb`, `hotTau` set onset and depth (1–2 V, orders of magnitude); `hotMu`/`hotVsat` move the onset 1.4–1.7 V; `trapWidth`, `fillIters`, `fillRelax` ≤ 0.6 V. Below a capture threshold (level ≤ 0.25 eV, `hotEb` ≤ 0.75, `hotTau` ≤ 7e-15) the collapse disappears; sets just above it recover strongly after the drop ([[trap-sensitivity]]).
- The model's collapse is **current-driven**: raising Vg moves it earlier ([[gate-bias]]).
- **Measured onset is later at higher Vg** (reported Oct 15): opposite to the model, also with the energy balance (access-region traps 0.3–0.4 V at every Vg at τ 1 ps, 0.7/0.7/0.6 V at Vg −2/−1/0 for τ 0.1 ps; gate-edge traps 0.3–0.4 V at every Vg). A field-driven **virtual gate** (surface trap sheet, Fowler–Nordheim lateral-field capture; branch `explore/field-capture`) gives the measured ordering: collapse at 0.25 / 0.6 V for Vg −1.75 / −1.5, then a jump to ~3.8 V at −1.25 and ~4.1 V at −1 (job 46106674, `figures/vgOnset_virtGate4.png`). Those late drops move with the Vd step and were step artifacts: with the fill iterated to convergence at each Vd (`fillConv`, jobs 46209709 / 46224198), Vg −2 and −1.5 are off from the first step and Vg −1 never collapses (380 mA/mm at 4.2 V, same at 0.1 and 0.05 V steps) ([[vg-dependence]]).

## Parked

- **3D slice (parked 2026-11-18).** On FLOOXS's brick mesh the depth (x) gradient is wrong, so 3D runs with hot-electron capture or field mobility are invalid on stock FLOOXS. The fix is in a local patched copy only (`~/flooxs-brickfix`, Ian: patch, don't modify the main repo); there a full-width rod matches 2D within 0.2% to 2.75 V. HPG has stock FLOOXS, so 3D runs with traps there need a patched build first. Single cascades, 2D vs 3D: strike probability in [[critical-strike]], the 3D route in [[3d-plan]].
- **SEE decay and later effects (parked 2026-11-05).** A seeGen2 rerun needs a maximum time step and over a day per task; SRH (`srhTau`) for times beyond ~1 ns; the lasting leakage step needs a damage term in seeIV ([[see-plan]]).
- **Electron energy balance (parked 2026-10-16).**
  - Oct 13-16 the standard was `eTemp 1` without the thermoelectric term. Since Oct 16 `eTemp 0` is the default and `eTemp 1` is an option; when `eTemp 1` is used, `etStats 0` and `etThermo 0` are the defaults (`model/GaN_modelfile_masterD`).
  - It works without the thermoelectric term (but inflates Id) and fails at the first step with it. `negative damp` on ETemp (Oct 12) made it worse (fails at equilibrium). A smaller ETemp damping (`etDamp` 0.5/1 with `etNeg 1`, job 45696870) reproduces the thermo-free result but does not fix the thermo term. The consistent convective flux (`etConv 1`, job 45711842) makes the thermo case fail already at equilibrium.
  - The eTempDebug "first Newton update" readings are unverified: `iterLimit` is read once at solver build, so those dumps followed full solves (Ian, Nov 20; [[flooxs-gotchas]]).
  - Runs are slow (1.9 s per Newton iteration, ~200 per post-collapse Vd point); a lower Newton limit does not help (job 45801978: keep `sweepIterLimit 300`), so ETemp sweeps should stop at 1.5–2 V. Post-collapse Id depends on the step history (up to ~10x, [[retry-bisection]]).
  - On hold with it: the energy-balance fit of trap position and τ to the measured ~1000× at 0.4–0.5 V. Remaining ideas in [[energy-balance]] and `progress.md` ("PARKED").
- **Curve-tracer next steps (parked since Oct 17; the work moved to the rad model on Oct 23):**
  - a second one-at-a-time lever pass around a baseline nearer the measured onset (e.g. level 0.45 eV or `hotTau` 3e-14), to get ~1000× at 0.4–0.5 V ([[trap-sensitivity]]);
  - keep, drop or rework `fillConv` (Ian's call), and compare onset vs Vg once the measured onset at each Vg arrives ([[vg-dependence]]);
  - field-driven trapping tests proposed, not chosen: off-state pre-stress, Poole–Frenkel capture, field-filled surface traps ([[field-driven-trapping]]);
  - 6 runs still stall near y = 2.0 µm; try a lower `teRampMin` ([[te-ramp]]);
  - the HfO2 calibration covers saturation only (Vds = 10 V); the low-Vd region is unvalidated and gm above +0.5 V is too low ([[calibration]]);
  - passivation fill fraction unknown ([[insulator-traps]]); access-region mesh too coarse for narrow traps ([[mesh]]);
  - is a trap blob ~2 µm into the access region physically plausible? ([[static-era-lessons]])

The history is in `progress.md` (dated log) and the work-log dashboard (https://claude.ai/artifact/7gwNdzD3SysL7TP9swRkEd, [[dashboard]]). Update this note when a result changes the picture.
