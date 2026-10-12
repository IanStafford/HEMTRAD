---
title: Project goal
tags: [overview]
---
# Project goal

Model the **radiation-induced current collapse** seen on a **pulsed curve tracer**: at Vgs = −2 V the Id–Vd curve runs normally, then drops ~1000× at a small Vd (~0.4–0.5 V), then **creeps up slightly** with Vd. The creep is physical (part of the measurement). No experimental Id–Vd CSVs for this are in the repo; the old `radPlot`/`radPlot1` targets were static-era stand-ins ([[static-era-lessons]]).

The working hypothesis in the model: radiation creates acceptor-like traps (a Gaussian blob) near the surface/2DEG; **hot electrons** fill them over a capture barrier during the Vd sweep ([[hot-electron-capture]]), depleting the channel in a runaway ([[trap-model]]).

Device: AlGaN/GaN HEMT, 100 nm HfO2 (HighK) over 50 nm SiN, T-gate + field plate, 200 µm gate width ([[device-structure]]). The deck is calibrated against a measured HfO2 transfer curve with the field-dependent mobility ([[calibration]]).

Current direction: push the collapse onset out to higher Vd ([[late-onset-search]]) and understand what sets it (position, level, gate bias), classifying collapses as deep/medium/shallow ([[collapse-classification]]). See [[current-status]].
