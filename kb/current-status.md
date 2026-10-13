---
title: Current status
tags: [status]
updated: 2026-10-12
---
# Current status (as of 2026-10-12)

**Repo:** reorganised 2026-10-12 into `model/`, `drivers/`, `sweeps/`, `analysis/`, `data/` ([[repo-locations]]); FLOOXS internals in [[flooxs-overview]].

**Model:** calibrated field mobility ([[calibration]]), local-field hot-electron capture ([[hot-electron-capture]]), Te-ramp stall rescue ([[te-ramp]]).

**Key results**
- Latest deep collapse **3.5 V** (late-onset set at y = 2.4 µm), 177 → 0.0018 mA/mm in one step, then creep ([[late-onset-search]]).
- Trap **position** is the strongest onset lever near the charge threshold; deeper levels / more charge collapse early and uniformly ([[position-maps]]).
- The model's collapse is **current-driven**: raising Vg moves it earlier ([[gate-bias]]).

**Parked / open**
- Electron energy balance: works without the thermoelectric term (but inflates Id), fails at the first step with it; `negative damp` on ETemp (Oct 12) made it worse (fails at equilibrium). A smaller ETemp damping (`etDamp` 0.5/1 with `etNeg 1`, job 45696870) reproduces the thermo-free result but does not fix the thermo term. The consistent convective flux (`etConv 1`, job 45711842) makes the thermo case fail already at equilibrium. **Decision (2026-10-13): continue with the thermo-free version; standard = `eTemp 1` with `etStats 0`, `etThermo 0` (now the defaults).** Remaining ideas in [[energy-balance]] and `progress.md` ("PARKED").
- Field-driven trapping tests proposed, not chosen: off-state pre-stress, Poole–Frenkel capture, field-filled surface traps ([[field-driven-trapping]]).
- 6 runs still stall near y = 2.0 µm; try a lower `teRampMin` ([[te-ramp]]).
- Calibration covers saturation only (Vds = 10 V); low-Vd region unvalidated; gm above +0.5 V too low ([[calibration]]).
- Passivation fill fraction unknown ([[insulator-traps]]); access-region mesh too coarse for narrow traps ([[mesh]]); 2D vs 3D question for single cascades ([[critical-strike]]).
- Is a trap blob ~2 µm into the access region physically plausible? ([[static-era-lessons]])

Update this note when a result changes the picture.
