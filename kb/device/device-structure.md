---
title: Device structure
tags: [device]
source: model/rfdevice.tcl, model/rfdevice_SiN.tcl
date: 2026-11-20
---
# Device structure (`model/rfdevice.tcl`)

2D cross-section; **x = depth** (µm, 0 = AlGaN top, increasing into the device, negative in the passivation), **y = lateral** (µm, 0 = gate centre, source at −y, drain at +y). FLOOXS lengths are internally cm (so `peak` locations print in cm).

| Feature | Value (from the deck's `line` and `region` commands) |
|---|---|
| Gate length | 0.25 µm, y = −0.125 … 0.125 (drain edge 0.125) |
| Gate stem | Metal, x −0.05 … −0.005, y −0.125 … 0.125; 5 nm of nitride under it (x −0.005 … 0) |
| T-gate head | Metal, x −0.20 … −0.05 (150 nm), y −0.325 … 0.485 (`SourceT` 0.2, `DrainT` 0.36 beyond the foot) |
| Field plate (FP) | Metal, x −0.57 … −0.30 (**0.27 µm thick**), y 0.285 … 0.725 (`FP_Offset` 0.16 from the gate drain edge, length 0.44). It sits 100 nm above the head top. `FP_Thick` 0.42 only places the FP top line (−(SiN_Thick + HPD_Thick + FP_Thick) = −0.57) and the top of the FP contact box; it is not the FP thickness |
| Source / drain contacts | source edge y = −1.125 (Lgs 1 µm), drain edge y = 3.285 (Lgd 3.16 µm); mesh edges −1.25 / 3.41 |
| AlGaN barrier | 15 nm (x 0 … 0.015), Al fraction 0.22, doping 1e12 |
| 2DEG | x ≈ 0.015 (AlGaN/GaN interface; `polCharge` 7e12 cm⁻² by default, 1e13 in the rad baseline, [[calibration]]) |
| GaN buffer | x 0.015 … 7.5 µm, acceptor doping −8e16 |
| Contacts | S, D (ohmic, AlGaN side), B (GaN bottom), G (on the gate stem, Schottky-like, barrier `phiB`), FP |
| Gate width (for per-device numbers) | 200 µm |

**Passivation (HighK deck).** Every layer is full width except where metal cuts it:
- SiN (Nitride, εr 6.3): 50 nm, x −0.05 … 0, on the AlGaN everywhere except the gate stem.
- HighK (εr 35): x −0.30 … −0.20 over the whole width (100 nm, `HPD_Thick`), plus x −0.20 … −0.05 on both sides of the T-gate head. So the HighK is **250 nm thick beside the head** (x −0.30 … −0.05) and **100 nm over the head top**. Between the head's drain edge and the FP's drain edge (y 0.485 … 0.725), the FP sits on 250 nm of HighK over the 50 nm SiN.
- Above x −0.30 only the FP metal is meshed. No region covers the rest of that layer, or anything above x −0.57.
- The calibration device is described as 100 nm HfO2 (`data/RF_100nmHfOx_IdVgs_Example1.xlsx`, [[calibration]]), while the deck has 250 nm of HighK beside the head. Whether that matters is an open modelling question for Ian (survey finding MOD-11, [[cleanup-plan]]).

**SiN deck.** `model/rfdevice_SiN.tcl` is the same structure with the three HighK region lines changed to Nitride ([[highk-vs-sin]]); select it with the `deviceDeck` lever. Mesh lines and geometry are identical.

**FP contact (fixed 2026-11-20).** Before 2026-11-20 the FP contact box was x −0.571 … −0.150, y 0.284 … 0.886. It reached past the FP metal into the T-gate head, so the head's top surface and the top of its drain wall were FP contact nodes. During the 28 V stress (Vg −10 V, FP 0 V) the head's drain corner sat at about −0.5 to −0.6 V instead of the gate potential. The box now matches the FP metal; the deck lever `fpBoxOld 1` rebuilds the old box, only to reproduce pre-fix runs. Every stress state saved before the fix carries the old box ([[fp-contact-fix]], [[stress-library]]).

- Source/drain have Gaussian contact doping (1e19 peak, ~0.03 µm depth) so they are ohmic.
- Barrier height `phiB` sets Vth rigidly ([[calibration]], `model/Metal.tcl`).
- Metal is modelled with RelEps 1e12 (`model/Metal.tcl`), so a metal body held at two fixed potentials carries a smooth potential gradient. That is how the FP contact bug showed up.
- Contact-safe trap positions are ≥0.7 µm from the contact doping edges (y −0.425 … 2.585).
- `model/rfdevice3d.tcl` is the 3D slice version of the same deck ([[3d-plan]]).

Mesh/structure plot (PLplot, y −1.25…1.5 µm, depth to 1 µm): `figures/device_mesh.png`.

Related: [[mesh]], [[levers]].
