---
title: Field-driven trapping (candidates)
tags: [physics, open]
date: 2026-10-03
---
# Field-driven trapping mechanisms (not in the model)

Field-driven trapping: electrons reach traps by tunnelling/injection set by the local field, rather than by current heating ([[gate-bias]]).
1. **Gate injection into surface states ("virtual gate"):** off-state gate leakage tunnels and hops along the passivation/AlGaN interface into surface traps past the gate edge; scales with Vdg, worst at the most negative gate (Vetury et al., IEEE TED 2001).
2. **Tunnelling from the 2DEG into dielectric traps** (HfO2 has many bulk/border traps), driven by the vertical field under gate and field plate.
3. **Poole–Frenkel barrier lowering** at the trap (∝ √E) — structurally closest to the present capture term.
4. **Buffer trapping by the drain field** (drain lag; C/Fe or radiation defects).

| Signature | Hot-electron (model) | Field-driven |
|---|---|---|
| Onset vs higher Vg | earlier | later |
| Worst stress | semi-ON | off-state, high Vd − Vg |
| Higher T | weaker | usually stronger |
| Off-state pre-stress | little effect | strong collapse |

Caution: the measured collapse is at Vd 0.4–0.5 V, Vdg ≈ 2.5 V, far below typical injection voltages — the collapse may be largely set before the sweep (radiation-created charge or curve-tracer pulses).

**Proposed tests (awaiting Ian):** (c) off-state pre-stress with `drivers/stressFreeze.tcl` (no physics change) first; (a) a Poole–Frenkel capture option; (b) field-filled surface traps via `insTrapSign`/`surfCharge`. Measurement: onset vs Vg on the curve tracer.

**2026-10-15:** measured onset reported **later at higher Vg**, the field-driven signature. Tests (Poole–Frenkel, Fowler–Nordheim gate injection, virtual-gate surface sheet) in exploratory worktrees: [[vg-dependence]].
