---
title: Mobility models
tags: [device, model]
source: model/GaN.tcl, model/AlGaN.tcl, model/GaN_modelfile_masterD
date: 2026-11-20
---
# Mobility models (`mobModel` lever)

- **`field`** (default since 2026-10-01, calibrated): Farahmand low-field mobility (doping- and temperature-dependent, counts ionized trap acceptors `IonAcceptor` as impurities; GaN mumax 1907, mumin 295, Nref 1e17) with **Heller high-field saturation** μ = μlow / (1 + (μlow·E/vs)^β)^(1/β), E = lateral field from DevPsi (`dot(DevPsi, y)`), vs = 3.3e7 − 3e6·T/300, β = 0.85·(T/300)^0.4. AlGaN uses Farahmand high-field. With the default levers the effective low-field mobility in the 2DEG is ~1160 cm²/V·s.
- **`static`**: constant GaN mobility 600 (AlGaN 213.3). Everything in `archive/static_mobility/` used this ([[static-era-lessons]]).

**Calibration levers (`model/GaN.tcl`, field model only; unset = the values above):**
- `mobMumax` replaces the GaN mumax (1907).
- `mobNref` replaces the GaN Nref (1e17).
- `mobVsat` replaces the Heller vs (3.3e7 − 3e6·T/300) with a constant.
- The rad-device baseline sets `mobMumax` 2100, `mobNref` 1e18, `mobVsat` 1.75e7 ([[calibration]]).
- `mobDamFac` (read by GaN.tcl; `drivers/radIV.tcl` builds the window `mobDamYmin`/`mobDamYmax`/`mobDamXmax`) multiplies μlow by the data field `MobDam`, which is `mobDamFac` inside the window and 1 outside. It was the mobility-loss Ron candidate ([[ron-increase]]).

**Not tied to these levers:** the local-field electron temperature for hot-electron capture uses its own `hotMu` 600 and `hotVsat` 1.9e7 (`model/GaN_modelfile_masterD`), whatever `mobModel` or the mob* levers say ([[hot-electron-capture]], [[model-caveats]]).

Effect on the collapse ([[field-mobility-trap-map]]): field mobility gives an **earlier, deeper and more uniform** collapse than static, partly because the trap-free baseline current is ~75% higher at low Vd.

Note for [[energy-balance]]: `lowfldmob` exists only with `mobModel field`.

Related: [[calibration]], [[levers]].
