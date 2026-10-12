---
title: Device structure
tags: [device]
source: model/rfdevice.tcl
---
# Device structure (`model/rfdevice.tcl`)

2D cross-section; **x = depth** (µm, 0 = AlGaN top, increasing into the device), **y = lateral** (µm, 0 = gate centre, source at −y, drain at +y). FLOOXS lengths are internally cm (so `peak` locations print in cm).

| Feature | Value |
|---|---|
| Gate length | 0.25 µm, y = −0.125 … 0.125 (drain edge 0.125) |
| T-gate head | y ≈ −0.325 … 0.485 (SourceT 0.2, DrainT 0.36 beyond the foot) |
| Field plate | y = 0.285 … 0.725 (offset 0.16, length 0.44), 0.42 µm thick |
| Source / drain contacts | source edge y = −1.125 (Lgs 1 µm), drain edge y = 3.285 (Lgd 3.16 µm); mesh edges −1.25 / 3.41 |
| AlGaN barrier | 15 nm (x 0 … 0.015), Al fraction 0.22, doping 1e12 |
| 2DEG | x ≈ 0.015 (AlGaN/GaN interface; `polCharge` 7e12 cm⁻²) |
| GaN buffer | x 0.015 … 7.5 µm, acceptor doping −8e16 |
| Passivation | 50 nm SiN (Nitride, εr 6.3) on the AlGaN; 100 nm HfO2 (HighK, εr 35) above; ~5 nm nitride under the gate stem |
| Contacts | S, D (ohmic, AlGaN side), B (GaN bottom), G (Schottky-like, barrier `phiB`), FP |
| Gate width (for per-device numbers) | 200 µm |

- Source/drain have Gaussian contact doping (1e19 peak, ~0.03 µm depth) so they are ohmic.
- `model/rfdevice_SiN.tcl` = the same structure with every HighK region replaced by Nitride ([[highk-vs-sin]]); select it with the `deviceDeck` lever.
- Barrier height `phiB` sets Vth rigidly ([[calibration]], `model/Metal.tcl`).
- Contact-safe trap positions are ≥0.7 µm from the contact doping edges (y −0.425 … 2.585).

Mesh/structure plot (PLplot, y −1.25…1.5 µm, depth to 1 µm): `figures/device_mesh.png`.

Related: [[mesh]], [[levers]].
