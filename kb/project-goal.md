---
title: Project goal
tags: [overview]
date: 2026-11-20
---
# Project goal

**Pulsed-IV collapse (Sep 23 – Oct 23).** Model the **radiation-induced current collapse** seen on a **pulsed curve tracer**: at Vgs = −2 V the Id–Vd curve runs normally, then drops ~1000× at a small Vd (~0.4–0.5 V), then **creeps up slightly** with Vd. The creep is physical (part of the measurement). No experimental Id–Vd CSVs for this are in the repo; the old `radPlot`/`radPlot1` targets were static-era stand-ins ([[static-era-lessons]]).

The working hypothesis in the model: radiation creates acceptor-like traps (a Gaussian blob) near the surface/2DEG; **hot electrons** fill them over a capture barrier during the Vd sweep ([[hot-electron-capture]]), depleting the channel in a runaway ([[trap-model]]). That phase pushed the collapse onset out to higher Vd ([[late-onset-search]]) and classified collapses as deep/medium/shallow ([[collapse-classification]]).

**Pre/post-irradiation model (since 2026-10-23, Ian).** One model that reproduces, **qualitatively** (Ian, 2026-10-25), the measured pre- and post-irradiation behaviour of a HighK (HfO2) and a SiN passivated device. The devices were irradiated with high-LET heavy ions either non-biased or biased (Vg −10 / Vd 28 V). The biased SiN device collapses in steps in Id–Vd at Vg +1 V, and the biased HighK device doesn't. The model places acceptor damage from the field of an off-state stress solve at the irradiation bias, adds ion strikes, and fills the damage with hot electrons during the measurement ([[rad-model]], [[damage-model]]). Since 2026-11-17 the goal is stepped SiN curves with 1, 2 and 3 strikes after the 28 V stress ([[step-search-28v]]). The measured rad data are kept untracked (`data/rad_y2/`, the repo is public), so tracked notes compare with them qualitatively only.

Device: AlGaN/GaN HEMT, HighK (HfO2) over 50 nm SiN, or SiN only; T-gate + field plate, 200 µm gate width ([[device-structure]]). The deck has two calibrations: the Oct 1 fit to a measured HfO2 transfer curve at Vds 10 V, and the 2026-10-23 rad-device baseline at low Vd ([[calibration]]).

Current direction: see [[current-status]].
