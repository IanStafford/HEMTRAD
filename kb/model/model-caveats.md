---
title: Model caveats
tags: [model, caveat]
date: 2026-11-20
---
# Known model caveats

## Whole model
- **FP contact (fixed 2026-11-20):** until then the FP contact box in every deck also covered the drain half of the T-gate head, so that part of the gate metal sat near the FP potential. During the 28 V stress the head's drain corner was at about −0.5 to −0.6 V instead of −10 V, right where the SiN stress damage concentrates. Every stress state saved before the fix carries the old box. Rad-era results built on them (stress library, mesh checks, strike rounds, the Nov 11 model) are being rerun ([[fp-contact-fix]], [[stress-library]]).
- **Calibration, per baseline** ([[calibration]]):
  - The Oct 1 fit covers saturation only (Vds 10 V); its low-Vd linear region, where the pulsed-IV collapses occur, is unvalidated; gm above +0.5 V is too low; off-state drain leakage isn't modelled.
  - The rad-device baseline (2026-10-23) fits Id–Vg at Vd 0.1 V and Id–Vd at Vg +1 V, so it covers low Vd, but its peak gm is too high.
- **Passivation thickness:** the deck has 250 nm of HighK beside the T-gate head and 100 nm over it, while the calibration device is described as 100 nm HfO2 (open question, [[device-structure]]).
- **Mesh:** the deck's access region is 20-50 nm laterally (y 0.725 → 3.285), which doesn't resolve narrow traps. Rad-era steps need `meshY` refinement and are mesh-sensitive ([[mesh]]).
- **Not modelled:** self-heating (lattice `Temp` is a constant 300 K); dielectric fixed/interface charge by default (`surfCharge` exists, unset); dynamic surface or dielectric trapping (insulator traps are static, [[insulator-traps]]); gate injection / field-driven capture ([[field-driven-trapping]]); non-local electron heating (Te is local-field; the solved [[energy-balance]] is optional and its thermo term parked).
- **Te parameters:** the local-field Te uses fixed `hotMu` 600 cm²/V·s and `hotVsat` 1.9e7 cm/s whatever `mobModel` or the mob* levers are set to. Transport uses ~1160 cm²/V·s in the 2DEG on the Oct 1 deck, and mumax 2100 / vsat 1.75e7 in the rad baseline ([[mobility-models]]). This is a documented inconsistency, not a change request.
- **Hot-electron fit parameter:** `hotTau` 1e-14 s, used in the late-onset fits and in the rad model, is unphysically small ([[hot-electron-capture]]).

## Pulsed-IV era (Sep–Oct)
- **Numerics:** the runaway is a discontinuous jump; stalled devices are rescued by the [[te-ramp]] (6 still stall); rescued points sit closer to the fill-only steady state than normal points.

## Rad era (since 2026-10-23)
- **Damage laws are phenomenological** ([[damage-model]]):
  - stress damage N = `damPeak`·(E_lat/`damEref`)^4 in the top 50 nm, as acceptors at 0.30 eV; the y ≥ 0.30 µm window that keeps it off the gate edge was a fitting choice with the old contact; on the fixed contact it makes no difference (fxNoCut28, [[fp-contact-fix]]);
  - strikes are Gaussians (σ 40 nm) with hand-set density and position;
  - field-scaled strikes multiply by (E/E_ref)^m from the stored stress field;
  - the damage scale `damPeak` absorbs the stress field magnitude (7e18 at the 17.66 V stress of the Nov 11 model, 1.5e18 at 28 V).
- **Stress voltage:** without `occSafe` the stress ramp aims for 28 V and keeps the furthest converged point, accepted down to `Vd_stressMin` 12 V. The Nov 11 model was stressed at 17.66 V this way. The reached Vd is printed in the summary ("field taken at Vd=…", [[rad-model]]).
- **Capture is fill-only during each Id–Vd sweep.** Release is crude: `emitRest` frees a fixed fraction of the captured charge at rest before each curve, and `emitFrac` releases a fraction before each capture ([[levers]]).
- **Gate–drain leakage** is a lumped `Rgd` added in post-processing (Id_ext = Id + (Vd − Vg)/Rgd), not a physical path ([[rad-model]]).
- **Strike steps are mesh-sensitive:** only the trap 0.30 eV / 8e18 series keeps its drop count on the library, m10 and m5fix meshes; 2.5 nm is pending ([[mesh]], [[step-search-28v]]; pre-fix; being rerun, [[fp-contact-fix]]).
- **2D full-width strikes:** in 2D each trap blob or strike spans the whole 200 µm gate width, while a real track is about 0.16 µm wide ([[critical-strike]]). With the brick-gradient fix, a full-width rod in a 3D slice (W 0.25 µm) matches 2D within 1.5% up to 6 V (3D/2D Id 0.986-1.002). Whether one strike can switch a large part of the width is open ([[3d-plan]]).
- **3D needs the brick fix:** stock FLOOXS computes wrong gradients on brick meshes. The fix is in a patched copy (`~/flooxs-brickfix`) and in a FANGS pull request (not merged), not in HPG's stock FLOOXS ([[flooxs-builds]], [[3d-plan]]).

Related: [[levers]], [[current-status]].
