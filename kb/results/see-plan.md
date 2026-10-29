---
title: Single-event transient plan (ion strike in FLOOXS)
tags: [plan, radiation, transient]
date: 2026-10-29
---
# Single-event transient: plan

Goal (Ian, 2026-10-29): recreate in FLOOXS the single event seen in the Y2 current monitoring (`NC_HEMT_Y2_Rad_Summary.pptx`, slide 3, untracked) as a transient. The ion's electron-hole plasma is injected by setting the quasi-Fermi levels (the solution variables), reverse-engineered from the carrier densities.

## The event (qualitative; numbers stay in the untracked data note)
- **R11 (HPD) under its irradiation bias:** one event gives a prompt spike in both drain and gate current (likely compliance- and sample-rate-limited), after which both currents stay at a higher level.
- Other leakage steps, in both devices, show no resolved spike.
- The monitor's sampling cannot resolve a ns transient. Compare collected charge / qualitative behaviour, not the peak.
- **R35 bias:** the slide legend gives a different gate bias for R35 than the −10 V the rad model assumed for both devices. To be confirmed by Ian.

## Why the quasi-Fermi route works
- Densities follow from the solution variables:
  - Elec = Nc·F½((Qfn − Econd)/Vt);
  - Hole = Nv·F½((Eval − Qfp)/Vt);
  - FLOOXS `f12` is normalised so that F½ → exp(η).
- Inverting: Qfn = Econd + Vt·F½⁻¹(n/Nc) and Qfp = Eval − Vt·F½⁻¹(p/Nv), with n = n_ss + ΔN and p = p_ss + ΔN.
- Adding the same ΔN to n and p is charge neutral, so Poisson (DevPsi) is unchanged at t = 0. The injected state is consistent and only the continuity equations relax it: drift/diffusion to the contacts, the strike current.
- FLOOXS has no inverse F½. Use the Joyce–Dixon series (u = n/Nc < ~8) or the Nilsson closed form (all u). The track core is ~1e20 cm⁻³ ≫ Nc (GaN 2.3e18), so it is degenerate. Check the expression against FLOOXS's own f12 polynomial (`src/math/Vector.cc`) before use.

## Ion and track
- Au 2256 MeV, LET 66.8 MeV·cm²/mg → Se ≈ 41 keV/nm in GaN; ~9–10 eV per pair gives ~4.3e10 pairs/cm ≈ 0.7 pC/µm.
- Range ≫ the 1.5 µm stack, so normal incidence gives a uniform vertical track through passivation, AlGaN, GaN:Fe and on into the SiC.
- Radial Gaussian, σ ~ 20–50 nm (peak ~1e20 cm⁻³).
- **2D caveat:** a 2D cross-section turns the cylindrical track into a slab uniform along the 200 µm width. The charge per µm of width must be chosen (decision below).

## Steps
0. **Mechanics smoke tests** (2–3 tasks):
   - a transient with no strike stays steady;
   - `sel … name=Qfn` / `name=Qfp` mid-run really changes the state the next solve starts from. Freezing (`nosolve`) and pdb tolerances mid-run do not, see [[flooxs-gotchas]], so this must be checked.
1. **Injection math:** Tcl proc that builds F½⁻¹ and the track profile ΔN(x, y; y0, σ) as expressions. Python round-trip check n → Qfn → n to < 1% from 1e10 to 1e21 cm⁻³.
2. **Mesh:** a deck lever adds y mesh lines around the strike position y0 (spacing ≤ σ/2) and keeps x resolution through the GaN. Check the injected charge (∫ΔN) against the target.
3. **Transient driver** `drivers/seeIV.tcl` (branch):
   - DC steady state at the strike bias (possible at full drain bias now with `occSafe 1`);
   - inject at t = 0;
   - `device time=` in log-spaced segments 1e-15 → 1e-6 s;
   - log Id, Ig, Is, Ib vs t and the collected charge ∫I dt;
   - dump n, p, ψ, |E| maps at a few times.
4. **Validation:**
   - charge conservation (collected vs injected, when no recombination);
   - a strike in a field-free region spreads by ambipolar diffusion;
   - time-step and σ convergence.
5. **Recombination (needs Ian):** the model has **no** G–R term, so plasma left in the buffer never decays. Add SRH (τn, τp ~ 0.1–1 ns, lever, default off) before trusting anything past ~1 ns.
6. **Scan** (≤ ~30 tasks):
   - strike position: source access, gate centre, gate drain edge, T-gate overhang (y 0.5), field-plate edge, drain access (1.0–1.6), near drain;
   - both decks; the R11 and R35 irradiation biases.
7. **Link to the rad model:** where the transient puts the peak fields/currents (and heat) says where an event damages the device. That could give the stress-damage placement and the hand-placed second SiN strike site ([[rad-model]]) a physical basis, and model the lasting post-event leakage step as damage left by the event.

## Decisions for Ian
- **2D normalisation:** charge per µm of width for the slab track. (a) Same peak density as the real track (overestimates total charge ~W/2σ); (b) same total charge spread over the 200 µm width (far too dilute); (c) an effective width W_eff ~ 0.1–1 µm. Proposed: (c), as a lever, bracketed.
- **SRH recombination term** (physics change).
- **Target:** the prompt transient only, or also the lasting leakage step after it?
- **R35 bias:** confirm the gate bias from the slide legend. If it differs from −10 V, rerun the SiN rad-model stress at that bias.
