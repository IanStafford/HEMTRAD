---
title: Damage model (radIV damage laws)
tags: [model, radiation, damage]
date: 2026-11-20
source: drivers/radIV.tcl (StressFields, DamageIn), model/GaN_modelfile_masterD (TrapConc_field), model/Poisson.tcl, sweeps/params_*.txt, progress.md
---
# Damage model (`drivers/radIV.tcl`)

In a post run (`radState post`) radIV writes the radiation damage into the data field **TrapN** at rest (Vg = Vd = 0), after the stress solve or after loading a saved stress state ([[stress-library]]). The trap model reads it through `trapShape field` (`TrapConc_field` returns `TrapN`). In GaN and AlGaN it becomes acceptor traps at `trapLevel` (radIV default 0.30 eV) with hot-electron fill-only capture ([[trap-model]], [[hot-electron-capture]]). In Nitride and HighK it is fixed charge `insTrapSign`·q·TrapN when `insTrapSign` is not 0; radIV sets -1 when `damInsPeak` > 0 ([[insulator-traps]]). Levers and defaults: [[levers]].

Coordinates are in µm. x is depth: 0 = AlGaN top, the AlGaN is 0 to 0.015, x < 0 is the passivation (the 50 nm SiN layer is -0.05 to 0). y runs along the channel: the gate foot is -0.125 to 0.125.

**FP contact fix.** Every law that reads the stress field depends on the T-gate head potential during the stress, which the 2026-11-20 fix changed. Damage built on a stress state saved before then is pre-fix; being rerun, [[fp-contact-fix]].

## Stress fields

`StressFields` stores four data fields at the stress bias (`Vg_stress`, and `Vd_stress` or the highest converged Vd at or above `Vd_stressMin`):

| Field | Expression | Selected by |
|---|---|---|
| `Estress` | lateral field \|∂ψ/∂y\| (V/cm) | `damField lat` (default), `damInsField lat` |
| `EstressT` | total field \|∇ψ\| (V/cm) | `tot`; the default for `damInsField` |
| `EstressNE` | Elec·Estress, divided by its peak in GaN/AlGaN (dimensionless; use `damEref 1`) | `ne` |
| `ElecStress` | Elec at the stress bias (cm⁻³) | `damNexp` |

With `stressSkip 1` all four are ~0 (1e-30). On the stock FLOOXS 3D brick mesh every gradient with a depth component is wrong (a brick-gradient bug), and a stored 3D Estress also came out wrong in the 2026-11-17 test, so field-placed damage can't be used in 3D on stock FLOOXS ([[3d-plan]]).

## The laws (`DamageIn`)

TrapN is the sum of the terms below. F is the field picked by `damField`, and min(a, damMax) is written 0.5(a + damMax - |a - damMax|).

1. **Field damage, first site.** N₁ = min(damMax, damPeak·(F/damEref)^damM·(ElecStress/damNref)^damNexp) for 0 ≤ x ≤ damXmax and damYmin ≤ y ≤ damYmax. `damNexp 0` (default) means field only. Defaults: damPeak 0, damEref 1e6 V/cm, damM 2, damMax 1e19, damXmax 0.05, the whole device in y.
2. **Second site** (`dam2Peak > 0`). N₂ = min(damMax, dam2Peak·(F₂/E₂)^dam2M) for 0 ≤ x ≤ dam2Xmax and dam2Ymin ≤ y ≤ dam2Ymax (default 0.65 to 1.0). F₂ is `dam2Field` and E₂ is `dam2Eref`; their "" defaults mean damField and damEref, and dam2Xmax "" means damXmax. `dam2M 0` makes the site uniform.
3. **Third site** (`dam3Peak > 0`). A uniform dam3Peak for 0 ≤ x ≤ damXmax and dam3Ymin ≤ y ≤ dam3Ymax (default 1.0 to 1.6). Not capped.
4. **Insulator damage** (`damInsPeak > 0`). N_ins = min(damMax, damInsPeak·(F_i/damInsEref)^damInsM) for damInsXmin ≤ x < 0 (default -0.05) and damYmin ≤ y ≤ damYmax. F_i is Estress with `damInsField lat` and EstressT otherwise (default `tot`). The charge sign is `insTrapSign`, -1 by default when damInsPeak > 0.
5. **`damSites`.** Each `{ymin ymax xmin xmax N}` adds a uniform N inside its box. The sites are summed one at a time into the data field SiteSum, because FLOOXS's parser has a fixed buffer. Not field dependent, not capped.
6. **`damGauss`.** Each `{y x sigma N}` adds N·exp(-((y-y₀)² + (x-x₀)²)/(2σ²)) for x ≥ 0. With `gaussFieldM` m ≠ 0 the summed strikes are multiplied by (F/damEref)^m and capped at damMax, so a strike leaves dense damage only where the field was high during the biased irradiation ([[rad-literature-steps]]).
7. **`damGaussF`.** The same `{y x sigma N}` form, always multiplied by (F/damEref)^gaussFieldMF (default 4) and capped at damMax. It can run next to an unscaled damGauss list.
8. **`damTube`** (3D). Each `{y z sigma xmin xmax N}` adds N·exp(-((y-y₀)² + (z-z₀)²)/(2σ²)) for xmin ≤ x ≤ xmax: a column along the depth. With `trackFieldM` m ≠ 0 the sum is multiplied by (F/damEref)^m and capped at damMax.
9. **`damRod`** (3D). Each `{y x sigma zmin zmax N}` adds N·exp(-((y-y₀)² + (x-x₀)²)/(2σ²)) for x ≥ 0 and zmin ≤ z ≤ zmax: a track along the gate width. A rod over the whole slice (zmin 0, zmax W3d) is the 2D damGauss site. Not field-scaled; trackFieldM acts on damTube only.

**Switching it in.** TrapN = s·N for s = 0, 0.01, 0.03, 0.1, 0.3, 0.6 and 1.0, with one solve per step (device store / restore around each). A failed step prints `DAMAGE solve failed at scale <s>`. Then `CaptureTraps` records the filled charge, and `<tag>_cuts.txt` gets Estress, EstressT, EstressNE, TrapN and IonAcceptor along y at x -0.04, -0.01, 0.001 and 0.016. The summary file gets the peak of TrapN in GaN and AlGaN.

**`damList`.** Several damage settings after one stress solve. Each entry `{suffix {lever value ...}}` sets its levers, places the damage and measures, with outputs `<tag>_<suffix>`. The traps are thawed and TrapN reset between entries.

**Not part of TrapN** but set with the damage: `surfCharge` (fixed charge at the AlGaN/passivation surface, model file), `mobDamFac` (low-field mobility factor in a window, GaN.tcl; radRon, [[ron-increase]]), `polWinFac` (polarization charge factor in a y window; radVth), `emitRest` / `emitFrac` (release of captured charge; radEmit, radEmit2, radEmit3), and `Rgd` (lumped gate-drain leakage, post-processing only; no committed params file sets it).

## Which studies used which law

| Law | Settings | Studies (params files) | Notes |
|---|---|---|---|
| 1, lateral field | damM 2 (radCal1), 1 / 2 / 4 (radDam1, 2026-10-23), 4 / 6 (radDam2, radPost), then 4 in nearly every study from radWin and radFine (2026-10-24) on (radIns also 6; radStress, 2026-11-04, 1 / 2 / 4); damEref 5e5 everywhere except radCal1 and radDam1 (the 1e6 default) | Nearly every post study: radCal1, radDam1/2, radWin, radPost, radFit1/2, radFinal-radFinal12, radEB1/2, rad28*, radExp*, radStrike*, radStep*, meshChk*, fpFix*. Also the Oct 24 radFine (job 47562303, params at commit 0fbf0ce) | The final setting is damYmin 0.30, damXmax 0.05, damMax 1e20, m 4 ([[rad-model]]) |
| 1, `damField ne` | damEref 1.0, damM 1-2 | radNE1, radNE2, radNEsmoke | n·E damage in the access region ([[rad-model]]) |
| 1 with `damNexp` | damNexp 1 | radPhys1 | Hot-electron rate ~ n·E^m |
| 2, n·E | dam2Field ne, dam2M 1, dam2Eref 1.0 | radFinal, radFinal2, radPhys1 | Ron-like loss that recovers toward high Vd |
| 2, uniform under the gate | dam2M 0, y -0.125 to 0.125; 1e18 / 3e18 to damXmax in radFinal3, 1.5e17-4e17 in radFinal4-6, 5e17 to x 0.014 (AlGaN only) from radFinal7 on | radFinal3-radFinal12, the Nov 11 model (radEB1/2, fpFixEB1) and the strike-era base line (radExp*, radStrike*, rad28*, radStep*, meshChkLoad*, fpFixLoad) | Hand-placed site under the gate |
| 2, uniform drain-side site | dam2M 0 (default), y 0.65-1.0 or 1.0-1.6, 1e18 / 3e18 | radFit2 | The first use of dam2, a second strike site toward the drain (the source of the 0.65-1.0 defaults) |
| 3, uniform | dam3Peak 2e18-6e18 | radFinal6, radFinal8-radFinal11; the SiN final-set tasks of radEB1, radEB2, fpFixEB1 and the Nov 5 radFine (4.5e18) | The hand-placed second SiN site at y 1.0-1.6 (plus one HighK task in radFinal6); dropped from the final model on Nov 11 ([[rad-model]]) |
| 4, insulator | damInsM 2 / 4 (radIns); damInsM 0 = uniform charge in the 50 nm SiN layer (radFam, radRon, radVth, radVth2); insTrapSign -1 | radIns, radFam, radRon, radVth, radVth2 | [[insulator-traps]], [[ron-increase]] |
| 5, `damSites` | uniform boxes, with `stressSkip 1` | radChk, radEmit/2/3, radFam, radMap1/2, radMesh, radMulti, radRon, radVth/2/3, and the Nov 5 radFine (job 49735196) | [[damage-region-map]] |
| 6, plain strikes | Mostly σ 40 nm at the AlGaN top (radStepB, E and J also vary σ or depth), with the E⁴ stress damage | radStrike2, radStrikeN, rad28strike, rad28strikeL, radExp1, radExp2, radStressIO, radStepA-G, radStepDiag/5, radStepM/M2/M3, meshChkLoad_m10/m5fix, fpFixLoad; rad3dRod (2D reference) | [[step-search-28v]], [[step-mechanism]] |
| 6, field-scaled | gaussFieldM 2 / 4 | radStepH (2, 4), radStepI, radStepJ, fpFixLoad (band b) | One SiN drop per curve, HighK flat ([[step-search-28v]]) |
| 7, `damGaussF` | gaussFieldMF 4 near the gate, plain far strikes | radStepK | The hybrid: no extra steps from the far strikes |
| 8, `damTube` | TRIM-built tracks from `analysis/genRad3d.py` | rad3dTrack1 | [[3d-plan]], [[trim]] |
| 9, `damRod` | y 0.8, σ 40 nm, 3e18, z 0 to 0.125 / 0.25 / 0.5 | rad3dRod | [[3d-plan]] |
| `trackFieldM` | | no committed params file | |

The two radFine studies share a name: the Oct 24 one (job 47562303, field damage via damList, m 4 at 4e18-7.5e18) lives only in git history at commit 0fbf0ce; `sweeps/params_radFine.txt` now holds the Nov 5 damSites study (job 49735196).

Related: [[levers]], [[stress-library]], [[trap-model]], [[rad-model]], [[fp-contact-fix]].
