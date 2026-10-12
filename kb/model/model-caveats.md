---
title: Model caveats
tags: [model, caveat]
---
# Known model caveats

- **Mesh:** the access region (25–40 nm lateral spacing) doesn't resolve narrow traps; access-region onsets can shift ~0.1 V on a 4 nm mesh ([[mesh]]).
- **Calibration covers saturation only** (Vds = 10 V); the low-Vd linear region where collapses occur is unvalidated; gm above +0.5 V not reproduced; off-state drain leakage not modelled ([[calibration]]).
- **Not modelled:** self-heating (lattice `Temp` is a constant 300 K); dielectric fixed/interface charge by default (`surfCharge` exists, unset); dynamic surface or dielectric trapping (insulator traps are static, [[insulator-traps]]); gate injection / field-driven capture ([[field-driven-trapping]]); non-local electron heating (Te is local-field; the solved [[energy-balance]] is parked).
- **Hot-electron fit parameter:** `hotTau` 1e-14 s in the late-onset fits is unphysically small ([[hot-electron-capture]]).
- **Numerics:** the runaway is a discontinuous jump; stalled devices are rescued by the [[te-ramp]] (6 still stall); rescued points sit closer to the fill-only steady state than normal points.
- **2D:** each trap blob spans the whole gate width ([[critical-strike]]).
