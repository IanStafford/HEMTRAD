---
title: Glossary
tags: [reference]
---
# Glossary

- **2DEG** — two-dimensional electron gas at the AlGaN/GaN interface, x = 0.015 µm. See [[device-structure]].
- **Run F** — the reference trap set: `trapPeak` 4e18, `trapSigma` 0.04, `trapLevel` 0.55, `hotEb` 0.5, `hotTau` 1.3e-13 at x = 0, y = 0.2 µm. See [[run-F]].
- **Late-onset set** — 0.30 eV / 5e18 / `hotTau` 1e-14 / `hotEb` 1.0, σ 40 nm; the round-3 best ([[late-onset-search]]).
- **Deep / medium / shallow** — largest single-step loss >95% / 50–95% / <50%. **Off at rest** — <10% of trap-free at Vd 0.1 V. **Stalled** — `PULSED GAVE UP` with no recorded collapse. See [[collapse-classification]].
- **Onset** — Vd of the first step that reaches the class threshold.
- **Suppression** — Id(trap-free)/Id(trapped) at a given Vd; **collapse depth vs trap-free** — Id_no-trap / Id at the post-collapse minimum.
- **Runaway** — positive feedback: trapped charge depletes the channel → local field ↑ → electrons hotter → more capture. Appears as a discontinuous jump that Vd continuation cannot follow ([[te-ramp]]).
- **Creep** — slow rise of Id with Vd after the collapse; physical, seen in the measurement ([[project-goal]]).
- **Te / TeTrap / ETemp** — electron temperature: local-field estimate ([[hot-electron-capture]]), the under-relaxed data field the traps see, and the solved PDE variable ([[energy-balance]]).
- **Qfn / Qfp** — electron / hole quasi-Fermi levels (eV-like units; current ∝ n μ ∇Qfn).
- **FillStep** — 4 × (UpdateTe w 0.5 → device → CaptureTraps) per Vd point ([[trap-model]]).
- **HPG** — HiPerGator, UF's cluster ([[hpg-workflow]]). **ee1-b** — the group's burst QOS (~171 CPUs).
- **radPlot / radPlot1** — the old measured-like collapse curves used as onset/depth targets in the static era; their post-collapse decay came from a sign bug ([[trap-model]]).
- **Static era** — 2026-09-23 to 10-01, constant mobility 600 ([[static-era-lessons]]); **field era** — calibrated field-dependent mobility from 10-01 on.
