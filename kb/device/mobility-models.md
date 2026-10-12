---
title: Mobility models
tags: [device, model]
source: model/GaN.tcl, model/AlGaN.tcl
---
# Mobility models (`mobModel` lever)

- **`field`** (default since 2026-10-01, calibrated): Farahmand low-field mobility (doping- and temperature-dependent, counts ionized trap acceptors `IonAcceptor` as impurities; GaN mumax 1907, mumin 295) with **Heller high-field saturation** μ = μlow / (1 + (μlow·E/vs)^β)^(1/β), E = lateral field from DevPsi (`dot(DevPsi, y)`), vs = 3.3e7 − 3e6·T/300, β = 0.85·(T/300)^0.4. AlGaN uses Farahmand high-field. In the 2DEG the effective low-field mobility is ~1160 cm²/V·s.
- **`static`**: constant GaN mobility 600 (AlGaN 213.3). Everything in `archive/static_mobility/` used this ([[static-era-lessons]]).

Effect on the collapse ([[field-mobility-trap-map]]): field mobility gives an **earlier, deeper and more uniform** collapse than static, partly because the trap-free baseline current is ~75% higher at low Vd.

Note for [[energy-balance]]: `lowfldmob` exists only with `mobModel field`.

Related: [[calibration]], [[levers]].
