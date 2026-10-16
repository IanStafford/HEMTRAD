---
title: Current status
tags: [status]
updated: 2026-10-16
---
# Current status (as of 2026-10-16)

**Repo:** reorganised 2026-10-12 into `model/`, `drivers/`, `sweeps/`, `analysis/`, `data/` ([[repo-locations]]); FLOOXS internals in [[flooxs-overview]].

**Model:** calibrated field mobility ([[calibration]]), local-field hot-electron capture ([[hot-electron-capture]]), Te-ramp stall rescue ([[te-ramp]]). Since 2026-10-13 the standard electron energy balance (`eTemp 1`, `etStats 0`, `etThermo 0`) is the default for new trap work ([[energy-balance]]).

**Key results**
- With the standard energy balance the late set collapses at **0.4–0.7 V** (set by τ); at y = 2.4 µm a 60–4000× drop onto a creeping plateau, close to the measured shape ([[energy-balance]], job 45768739).
- Local-field model: latest deep collapse **3.5 V** (late-onset set at y = 2.4 µm), 177 → 0.0018 mA/mm in one step, then creep ([[late-onset-search]]).
- Trap **position** is the strongest onset lever near the charge threshold; deeper levels / more charge collapse early and uniformly ([[position-maps]]).
- The model's collapse is **current-driven**: raising Vg moves it earlier ([[gate-bias]]).
- **Measured onset is later at higher Vg** (reported Oct 15): opposite to the model, also with the energy balance (access-region traps 0.3–0.4 V at every Vg at τ 1 ps, 0.7/0.7/0.6 V at Vg −2/−1/0 for τ 0.1 ps; gate-edge traps 0.3–0.4 V at every Vg). A field-driven **virtual gate** (surface trap sheet, Fowler–Nordheim lateral-field capture; branch `explore/field-capture`) gives the measured ordering: collapse at 0.25 / 0.6 V for Vg −1.75 / −1.5, then a jump to ~3.8 V at −1.25 and ~4.1 V at −1 (job 46106674, `figures/vgOnset_virtGate4.png`). Those late drops move with the Vd step (3.6 → 4.1 V at Vg −1 for 0.1 → 0.05 V) and the solver gives up right after each, so they are not yet reliable. Still too deep and without creep ([[vg-dependence]]). Waiting for the new measured data.

**Parked / open**
- Electron energy balance: works without the thermoelectric term (but inflates Id), fails at the first step with it; `negative damp` on ETemp (Oct 12) made it worse (fails at equilibrium). A smaller ETemp damping (`etDamp` 0.5/1 with `etNeg 1`, job 45696870) reproduces the thermo-free result but does not fix the thermo term. The consistent convective flux (`etConv 1`, job 45711842) makes the thermo case fail already at equilibrium. **Decision (2026-10-13): continue with the thermo-free version; standard = `eTemp 1` with `etStats 0`, `etThermo 0` (now the defaults).** First trap study with it (job 45768739): collapse at 0.4–0.7 V set by τ; the late set at y 2.4 µm gives a 60–4000× drop to a creeping plateau, close to the measured shape (`figures/eTempStd_IdVd.png`). These runs are slow (1.9 s per Newton iteration, ~200 per post-collapse Vd point); a lower Newton limit does not help (job 45801978: keep `sweepIterLimit 300`), so future ETemp sweeps should stop at 1.5–2 V. Post-collapse Id depends on the step history (up to ~10x, [[retry-bisection]]). Remaining ideas in [[energy-balance]] and `progress.md` ("PARKED").
- **Next (Vg study):** find why the virtual gate's late onsets depend on the Vd step (does trap occupation carry over between Vd points?), then compare the onset-vs-Vg map with the new measured data. All 4 tasks of 46106674 ended the same way: a 5–60% drop over 1–3 steps, then `PULSED GAVE UP` (Fth 1.6e5 at Vg −1.5: 273 → 258 at 3.85 V, gave up at 3.9 V).
- **Next:** fit trap position and τ with the standard energy balance to the measured ~1000× at 0.4–0.5 V; end sweeps at 1.5–2 V (`sweepIterLimit` stays 300).
- Field-driven trapping tests proposed, not chosen: off-state pre-stress, Poole–Frenkel capture, field-filled surface traps ([[field-driven-trapping]]).
- 6 runs still stall near y = 2.0 µm; try a lower `teRampMin` ([[te-ramp]]).
- Calibration covers saturation only (Vds = 10 V); low-Vd region unvalidated; gm above +0.5 V too low ([[calibration]]).
- Passivation fill fraction unknown ([[insulator-traps]]); access-region mesh too coarse for narrow traps ([[mesh]]); 2D vs 3D question for single cascades ([[critical-strike]]).
- Is a trap blob ~2 µm into the access region physically plausible? ([[static-era-lessons]])

Update this note when a result changes the picture.
