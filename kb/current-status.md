---
title: Current status
tags: [status]
updated: 2026-10-27
---
# Current status (as of 2026-10-27)

**Repo:** reorganised 2026-10-12 into `model/`, `drivers/`, `sweeps/`, `analysis/`, `data/` ([[repo-locations]]); FLOOXS internals in [[flooxs-overview]].

**Model:** calibrated field mobility ([[calibration]]), local-field hot-electron capture ([[hot-electron-capture]]), Te-ramp stall rescue ([[te-ramp]]). **Since 2026-10-16 (Ian) the local-field model (`eTemp 0`, the model-file default) is the standard again, to save computation time.** The standard electron energy balance (`eTemp 1`, `etStats 0`, `etThermo 0`; standard Oct 13–16) is kept as an option: it collapses at the measured voltage but costs ~1.9 s per Newton iteration ([[energy-balance]]).

**Key results**
- **Pre/post-irradiation model (branch `explore/rad-model`, goal closed 2026-10-27, qualitative fit accepted by Ian)**: `drivers/radIV.tcl` stresses the device off-state (Vg −10, drain ramp; the solve stops at Vd 17 V), places acceptor damage ∝ E⁴ beyond the gate edge, then measures with hot-electron capture. SiN concentrates the stress field under the T-gate overhang (2× HighK), so only SiN collapses after biased irradiation (two steps near 4.5 and 5.8 V with a second strike site); HighK stays flat, gm −2%; Vth +0.21 V on every irradiated device. Final jobs 47887339 / 47959281. Fitting choices and the 17 V stress limit in [[rad-model]] (branch note). Not merged yet (Ian).
- **HighK vs SiN with traps at Vg +1, Vd to 10 V** (job 47062225): identical onsets on both decks (1.3 / 1.5 / 1.7 V for traps at y 0.3 / 1.0 / 2.4). Only the post-collapse recovery differs (SiN 20–60× lower at 10 V). The trap model can't make SiN collapse while HighK doesn't ([[highk-vs-sin]]).
- With the standard energy balance the late set collapses at **0.4–0.7 V** (set by τ); at y = 2.4 µm a 60–4000× drop onto a creeping plateau, close to the measured shape ([[energy-balance]], job 45768739).
- Local-field model: latest deep collapse **3.5 V** (late-onset set at y = 2.4 µm), 177 → 0.0018 mA/mm in one step, then creep ([[late-onset-search]]).
- Trap **position** is the strongest onset lever near the charge threshold; deeper levels / more charge collapse early and uniformly ([[position-maps]]).
- **Lever sensitivity** (job 46462234, one lever at a time around the late set at y 1.0 µm, onset 2.3 V): `trapLevel`, `hotEb`, `hotTau` set onset and depth (1–2 V, orders of magnitude); `hotMu`/`hotVsat` move the onset 1.4–1.7 V; `trapWidth`, `fillIters`, `fillRelax` ≤ 0.6 V. Below a capture threshold (level ≤ 0.25 eV, `hotEb` ≤ 0.75, `hotTau` ≤ 7e-15) the collapse disappears; sets just above it recover strongly after the drop ([[trap-sensitivity]]).
- The model's collapse is **current-driven**: raising Vg moves it earlier ([[gate-bias]]).
- **Measured onset is later at higher Vg** (reported Oct 15): opposite to the model, also with the energy balance (access-region traps 0.3–0.4 V at every Vg at τ 1 ps, 0.7/0.7/0.6 V at Vg −2/−1/0 for τ 0.1 ps; gate-edge traps 0.3–0.4 V at every Vg). A field-driven **virtual gate** (surface trap sheet, Fowler–Nordheim lateral-field capture; branch `explore/field-capture`) gives the measured ordering: collapse at 0.25 / 0.6 V for Vg −1.75 / −1.5, then a jump to ~3.8 V at −1.25 and ~4.1 V at −1 (job 46106674, `figures/vgOnset_virtGate4.png`). Those late drops move with the Vd step and were step artifacts: with the fill iterated to convergence at each Vd (`fillConv`, jobs 46209709 / 46224198), Vg −2 and −1.5 are off from the first step and Vg −1 never collapses (380 mA/mm at 4.2 V, same at 0.1 and 0.05 V steps). Keep, drop or rework `fillConv` is Ian's call ([[vg-dependence]]). Waiting for the measured onset at each Vg.

**Parked / open**
- Electron energy balance: works without the thermoelectric term (but inflates Id), fails at the first step with it; `negative damp` on ETemp (Oct 12) made it worse (fails at equilibrium). A smaller ETemp damping (`etDamp` 0.5/1 with `etNeg 1`, job 45696870) reproduces the thermo-free result but does not fix the thermo term. The consistent convective flux (`etConv 1`, job 45711842) makes the thermo case fail already at equilibrium. **Decision (2026-10-13): continue with the thermo-free version; standard = `eTemp 1` with `etStats 0`, `etThermo 0` (now the defaults).** First trap study with it (job 45768739): collapse at 0.4–0.7 V set by τ; the late set at y 2.4 µm gives a 60–4000× drop to a creeping plateau, close to the measured shape (`figures/eTempStd_IdVd.png`). These runs are slow (1.9 s per Newton iteration, ~200 per post-collapse Vd point); a lower Newton limit does not help (job 45801978: keep `sweepIterLimit 300`), so future ETemp sweeps should stop at 1.5–2 V. Post-collapse Id depends on the step history (up to ~10x, [[retry-bisection]]). Remaining ideas in [[energy-balance]] and `progress.md` ("PARKED").
- **Next:** a second one-at-a-time lever pass around a baseline nearer the measured onset (e.g. level 0.45 eV or `hotTau` 3e-14), to get ~1000× at 0.4–0.5 V ([[trap-sensitivity]]); decide on `fillConv`; compare onset vs Vg once the measured numbers arrive.
- Energy-balance fit (on hold since 2026-10-16, local-field model is standard): fit trap position and τ to the measured ~1000× at 0.4–0.5 V; end such sweeps at 1.5–2 V (`sweepIterLimit` stays 300).
- Field-driven trapping tests proposed, not chosen: off-state pre-stress, Poole–Frenkel capture, field-filled surface traps ([[field-driven-trapping]]).
- 6 runs still stall near y = 2.0 µm; try a lower `teRampMin` ([[te-ramp]]).
- Calibration covers saturation only (Vds = 10 V); low-Vd region unvalidated; gm above +0.5 V too low ([[calibration]]).
- Passivation fill fraction unknown ([[insulator-traps]]); access-region mesh too coarse for narrow traps ([[mesh]]); 2D vs 3D question for single cascades ([[critical-strike]]).
- Is a trap blob ~2 µm into the access region physically plausible? ([[static-era-lessons]])

Update this note when a result changes the picture.
