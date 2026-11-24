---
title: Single-event transient (ion strike): method and results
tags: [results, radiation, transient]
date: 2026-10-29
source: progress.md 2026-10-29 to 2026-11-19; drivers/seeIV.tcl; sweeps/params_see*.txt
---
# Single-event transient (ion strike): method and results

Goal (Ian, 2026-10-29): recreate in FLOOXS, as a transient, the single event seen in the Y2 current monitoring (`NC_HEMT_Y2_Rad_Summary.pptx`, slide 3, untracked). The driver is `drivers/seeIV.tcl`. It was developed on `explore/rad-model` and has been on main since the 2026-11-04 merge. This note gives model numbers only; the measured event is described in words.

## Method as run

- **The strike is a generation pulse** (`seeMethod gen`, the seeIV default since 2026-11-02; lever `seeGenExpr`, Ian OK'd 2026-11-02).
  - Pair generation G = ΔN(x, y)·exp(−((t − t0)/τ)²)/(τ√π) is added to both continuity equations (`model/Continuity.tcl`), with t0 = 3τ and τ = `seeGenTau` (1 ps; 2 ps for the maps).
  - The transient starts from the converged DC state at the strike bias, and the solver builds the plasma.
  - Track: ΔN is a vertical slab, Gaussian in y around `seeY0` with σ = `seeSigma` (0.05 µm), from x 0 to 1.4 µm (`seeXmax`, the GaN:Fe buffer; the SiC below is not in the deck). It carries 4.3e10 pairs/cm (`seePairs`) spread over an effective width `seeWeff` (1 µm).
- **`tranSign 1`** (the seeIV default; Ian OK'd 2026-11-02).
  - The deck's continuity transport term has the opposite sign to FLOOXS's own decks. In DC this is invisible, but any transient is anti-diffusive: with the old form the no-strike control can't take a 1 fs step.
  - `tranSign 1` flips the transport term to FLOOXS's form. DC runs are unchanged; recombination keeps the sign of ddt, generation the opposite, and the contact flux signs flip.
  - A first version flipped ddt with a unary minus. It failed because the time term's Jacobian ignores the unary minus.
- **DC numerics:** the trap model is on with an empty trap density (TrapN 1e-30, physically no traps) plus `occSafe`. With the trap model off, the off-state drain ramp stalls at Vd 7.5-10.5 V (seeSmoke2 48241815) or crawls (3 V after 5.7 h, seeIso1 48965552). Surface charge plays no part.
- **Why the quasi-Fermi route was dropped (2026-11-02).** Injecting the plasma at t = 0 by resetting Qfn / Qfp (`seeMethod qf`) never takes a first time step at any dt, down to 1e-75 s. That held even for a 1e-4 strike or a track starting 0.1 µm below the AlGaN.
  - Cause: FLOOXS's device transient is TR-BDF2, hard-coded. Its TR stage enforces F_new = −F_old on rows with no effective time term (carrier-free regions), so no first step converges from the reset state (seeIV header comment).
  - This can't be fixed from the deck. The qf code stays in seeIV as an option; the derivation is below.
- **Outputs:** `<tag>_see.csv` (t, then the Qfn / Qfp / DevPsi flux of each contact, A/µm), `<tag>_cuts_<k>.txt` (Elec, Hole, DevPsi along y at x 0.016 and 0.5 µm) and, with `seeMapTimes`, VTK maps (below). The output misses displacement current, so the contact columns only balance once the currents level off.

## Decisions

- **2D normalisation: taken** (2026-10-29; Ian asked for "good decisions" on the open items). A 2D cross-section turns the cylindrical track into a slab uniform along the 200 µm width, so the charge per µm of width had to be chosen.
  - The options were: (a) the real track's peak density, which overestimates the total charge ~W/2σ; (b) the total charge spread over the 200 µm width, far too dilute; (c) an effective width W_eff ~ 0.1-1 µm.
  - Taken: (c), lever `seeWeff`, 1 µm. Every SEE run so far uses 1 µm. **Open:** the planned bracket at 0.1 µm has not been run.
- **SRH recombination: taken** (2026-10-29; a physics change, approved). Lever `srhTau` in `model/Continuity.tcl` adds R = np/(τ(n + p)), default off. It was used once, at 1 ns (seeGen1). **Open:** it is still needed before trusting anything past ~1 ns.
- **Target: taken** (2026-10-29): the prompt strike first, the lasting leakage step later. **Open:** the lasting step needs a damage term that seeIV doesn't have.
- **R35 bias: taken for the strike runs** (2026-10-29): each device at its slide-legend irradiation bias, HPD at Vg −10 V and SiN at Vg −5 V, Vd 28 V (seeGen1, seeGen2). The seeMap28 maps use Vg −10 on both decks. **Open:** rerun the SiN rad-model stress at the R35 bias? The rad model stresses both decks at Vg −10 ([[rad-model]]).
- **Decay beyond ~1.3 ns: open.** A rerun of seeGen2 would need a maximum time step and would cost well over a day per task.

## The event (qualitative; numbers stay in the untracked data note)
- **R11 (HPD) under its irradiation bias:** one event gives a prompt spike in both drain and gate current (likely compliance- and sample-rate-limited), after which both currents stay at a higher level.
- Other leakage steps, in both devices, show no resolved spike.
- The monitor's sampling cannot resolve a ns transient. Compare collected charge / qualitative behaviour, not the peak.
- **R35 bias:** the slide legend gives a different gate bias for R35 than the −10 V the rad model assumed for both devices (see Decisions).

## Ion and track
- Au 2256 MeV, LET 66.8 MeV·cm²/mg → Se ≈ 41 keV/nm in GaN; ~9–10 eV per pair gives ~4.3e10 pairs/cm ≈ 0.7 pC/µm.
- Range ≫ the 1.5 µm stack, so normal incidence gives a uniform vertical track through passivation, AlGaN, GaN:Fe and on into the SiC.
- Radial Gaussian, σ ~ 20–50 nm (peak ~1e20 cm⁻³).
- **2D caveat:** a 2D cross-section turns the cylindrical track into a slab uniform along the 200 µm width; the charge per µm of width is set by `seeWeff` (see Decisions).

## Quasi-Fermi route (tried 2026-11-02, abandoned: TR-BDF2 first step fails)

The original plan (2026-10-29) was to inject the plasma by setting the quasi-Fermi levels (the solution variables), reverse-engineered from the carrier densities. The reasoning:
- Densities follow from the solution variables:
  - Elec = Nc·F½((Qfn − Econd)/Vt);
  - Hole = Nv·F½((Eval − Qfp)/Vt);
  - FLOOXS `f12` is normalised so that F½ → exp(η).
- Inverting: Qfn = Econd + Vt·F½⁻¹(n/Nc) and Qfp = Eval − Vt·F½⁻¹(p/Nv), with n = n_ss + ΔN and p = p_ss + ΔN.
- Adding the same ΔN to n and p is charge neutral, so Poisson (DevPsi) is unchanged at t = 0. The injected state is consistent and only the continuity equations relax it: drift/diffusion to the contacts, the strike current.
- FLOOXS has no inverse F½. Use the Joyce–Dixon series (u = n/Nc < ~8) or the Nilsson closed form (all u). The track core is ~1e20 cm⁻³ ≫ Nc (GaN 2.3e18), so it is degenerate. Check the expression against FLOOXS's own f12 polynomial (`src/math/Vector.cc`) before use.

What happened: Nilsson's closed form is within 0.5% of FLOOXS f12, and with two Newton steps on f12 the injection is exact (net charge 1e8 against 1e17 with Nilsson alone). The one-line F½⁻¹ expression overflowed FLOOXS's parser buffer and had to be built in stages. The injected state still never took a first time step (Method as run).

## The original plan (2026-10-29) and what came of it
0. **Mechanics smoke tests:** done (seeSmoke1-3, Oct 29 to Nov 2, and local tests on Nov 2). The DC ramp reaches 28 V once the empty trap model is on, and with `tranSign 1` the no-strike control steps normally. The plan also asked whether `sel … name=Qfn` / `name=Qfp` mid-run sets the state the next solve starts from, because freezing (`nosolve`) and pdb tolerances set mid-run do not take effect ([[flooxs-gotchas]]).
1. **Injection math:** done for the qf route (above); the gen route doesn't need it.
2. **Mesh around the strike:** not done. No SEE run refines the mesh at the strike (none sets the deck's `meshY`); all use the deck mesh.
3. **Transient driver** `drivers/seeIV.tcl`: done. DC at the strike bias (full drain bias with `occSafe 1`), then the strike, `device time=` with log-growing steps to `seeTend`, contact currents every step, field cuts at log times, maps on request.
4. **Validation:** partly. At the plateau S + D − B closes to ~1e-6 A/µm (0.03%), and net electrons out equal holes out (seeGen1). Not done: ambipolar spreading in a field-free region, time-step and σ convergence.
5. **Recombination:** the `srhTau` lever exists (Decisions); one 1 ns run.
6. **Position scan** (≤ ~30 tasks: source access, gate centre, gate drain edge, T-gate overhang, field-plate edge, drain access, near drain; both decks; both irradiation biases): not run. Strikes so far are at y 0.2, 0.5 and 1.0 µm.
7. **Link to the rad model** (where the transient puts the peak fields and currents could place the stress damage and strikes on a physical basis, and the lasting leakage step could be damage left by the event): not done ([[rad-model]], [[step-search-28v]]).

## First results: seeGen1 (job 49135298, 2026-11-04)
Generation-pulse strike (`seeMethod gen`, τ 1 ps, `tranSign 1`, W_eff 1 µm, 6.9e-13 C/µm deposited), Vd 28 V. Currents below are magnitudes; drain current flows in, source and bottom-hole current flow out.
- HighK, y 1.0, Vg −10: Id ~2.3 mA/µm, still near that plateau at 1 ns. Drain charge by 1 ns is 2.25e-12 C/µm, 3.3× deposited. Holes at the bottom contact are 54% of deposited.
- SiN, y 0.5, Vg −5: Id ~2.0 mA/µm, drain charge 2.9× deposited.
- SRH 1 ns: tracks the no-SRH run until a bad step at 0.70 ns, then stalls until the 24 h limit. Discard the last row.
- Control without a strike stays ≤ ~5e-13 A/µm.
- The output misses displacement current, so the columns only balance on the plateau.
- Mechanism (inferred from cuts at x 0.016 and 0.5 µm, HighK at 1 ns vs control): gate barrier gone (DevPsi 3.94 → 2.84, level with the source; Elec ~1e-27 → 1.1e19); buffer flooded (x 0.5 DevPsi 6.37 → 2.94, n ≈ p ≈ 1e18); peak lateral field moves from the gate edge (7e5 V/cm) to near the drain (1.4e6 V/cm at y 3.19). About 3.2e-13 C/µm of holes remain, ~0.9 ns at the 0.35 mA/µm bottom-contact current, so Id should fall over a few ns. seeGen2 then showed the current turning over (next section).
- Not reproduced yet: the lasting leakage step (no damage term) and the gate current (gate column stays at its DC value).

## seeGen2 (2026-11-05, job 49511531): decay has started, run stopped at about 1.3 ns

Same strikes as seeGen1, aimed at 10 ns. Both tasks accepted one bad step (HighK at 1.39 ns, SiN at 1.47 ns: currents about 1000× higher, sign flipped on SiN), and the time step then fell to nothing with no progress for 3 and 7 h. Cancelled with Ian's permission at 22.9 h; the bad last row is excluded.

| | Peak drain current | Peak at | At the end | Charge through the drain |
|---|---|---|---|---|
| HighK, y 1.0 | 2.37 mA/µm | 0.72 ns | 2.08 mA/µm at 1.32 ns | 2.96e-12 C/µm |
| SiN, y 0.5 | 2.02 mA/µm | 0.65 ns | 1.89 mA/µm at 1.38 ns | 2.70e-12 C/µm |

- **The current does turn over**, peaking near 0.7 ns. If the fall from 0.8 ns continued as an exponential, the time constant would be about 3.5 ns (HighK) and 7.6 ns (SiN), so it would take over 10 ns to end. That's an extrapolation from a short stretch.
- **Charge through the drain is already 4× the deposited 6.9e-13 C/µm.**
- The bad steps came at dt of 6e-11 to 9e-11 s. A rerun would need a maximum time step, and would cost well over a day per task.

## Current-density maps (2026-11-18, side project after Sun et al., IEEE EDL 46, 813 (2025), Fig. 5)

- seeIV levers `seeMapTimes` (s, list) and `seeMapDC` (default off) write the 2D state at those times as `<tag>_map_<k>.vtk` (XML VTK under a .vtk name, `struct vtk=`) plus `<file>.txt` with the time. Fields added before each dump: `JnX/JnY/JnMag`, `JpX/JpY/JpMag` = q·µ·n·∇Qfn and q·µ·p·∇Qfp in A/cm² (Qfn, Qfp are Fermi levels in V, so with `tranSign 1` these are the Continuity.tcl flux terms, same mobility expressions), and `MapN`, `MapP`, the carrier densities. `struct vtk` writes the const solutions Elec and Hole as placeholders (1.0), so use MapN/MapP.
- The mobility is built in stages (one `sel` per material): the field-dependent electron mobility for both materials in one expression overflows FLOOXS's parser buffer ("buffer overflow detected").
- `analysis/plot_seeMaps.py` (~/venvs/render): log10 |Jp| (or |Jn|) on the cross-section, one row per run, one panel per snapshot, white arrows for the direction (probed on the semiconductor cells with VTK; matplotlib's tri-finder rejects FLOOXS's repeated interface points).
- Smoke test (local, SiN, Vg −4 / Vd 2 V, strike y 0.2 µm, τ 2 ps, to 4 ps): snapshots and plot work. At 3.2 ps electrons in the channel flow to the drain and holes at the track move down toward the substrate contact. The |Jp| ~1e4 A/cm² across the whole buffer far from the track is real: the deck's GaN buffer is p-type (p ≈ 8e16 cm⁻³ in DC), and when the strike pulls the buffer potential down (by 1–4 V within 3 ps at Vd 10 V) its majority holes carry current toward the track and the substrate contact.
- Proof of concept (local, unirradiated SiN, Vg −5 / Vd 10 V, strike y 0.2 µm between the gate foot's drain edge and the field plate, τ 2 ps, W_eff 1 µm, snapshots DC, 3, 6, 12, 30, 100 ps; DC ramp 2 h and transient 80 min on the workstation). Figures `figures/see/poc_holeJ.png`, `poc_elecJ.png`.
  - Holes: the track carries up to ~1e6 A/cm² at 6-12 ps, then spreads sideways; by 100 ps the whole p-type buffer carries ~1e4-1e5 A/cm². All hole current leaves through the substrate contact B (0.19 / 0.31 / 0.34 mA/µm at 3 / 12 / 100 ps); none through the gate, which sits on a 5 nm insulator in this deck, and none through source or drain.
  - Electrons: swept out of the track within a few ps; by 100 ps the strike plasma fills the buffer under the off gate and the device conducts 1.68 mA/µm into the drain (1.34 out of the source).
  - So in this HEMT the analogue of the paper's hole path is the p-type buffer to the substrate; there is no hole build-up at the gate as in their Schottky control diode, because the gate can't take hole current. The 28 V off-state bias with SiN and HighK rows followed as seeMap28 (below); SRH (`srhTau`) for times beyond ~1 ns has not been run.

### seeMap28 (job 51945449, 2026-11-19): 28 V off-state, SiN vs HighK (pre-fix)

- **Setup:** both decks at Vg −10 / Vd 28 V, unirradiated, strike at y 0.2 µm, τ 2 ps, W_eff 1 µm, to 1 ns. Maps at DC and 3, 6, 12, 30, 100 and 300 ps and 1 ns (`sweeps/params_seeMap28.txt`, 2 tasks, 2-day limit). Figures `figures/see/map28_holeJ.png` and `map28_elecJ.png` (`analysis/plot_seeMaps.py`, one row per deck).
- **Result: SiN and HighK are nearly identical.**
  - Holes run down the track (~1e6 A/cm² at 6-12 ps) and out through the p-type buffer to the substrate contact: 0.34 mA/µm from 100 ps on in both decks. None reach the gate.
  - The drain current at 1 ns is 1.9-2.0 mA/µm in both (1.91 SiN, 1.96 HighK).
- **Pre-fix:** these runs had the old FP contact box. Their DC snapshot is where the bug showed up: the T-gate head's drain corner sat at −0.5 to −0.6 V against the FP instead of near −10 V ([[fp-contact-fix]]). The strike at y 0.2 µm lies under the head, so the maps may change with the fixed box. No fixed-box rerun is queued yet.

### The field during the strike, fixed contact (2026-11-24; fxSeeMap28 52357004, `figures/see/strike_field_28V.png`)

Lateral field |Ey| on the GaN row at x 16 nm, from the snapshot potentials (`analysis/plot_seeField.py`; triangle gradients, cross-checked against finite differences to under 1%). Vg −10 / Vd 28 V, strike at y 0.2 µm. The GaN region is the highest MatID (3 on SiN, 4 on HighK, which has an extra insulator).

| | SiN | HighK |
|---|---|---|
| Peak at the head drain edge, DC (y 0.53-0.56) | 8.8e5 (old contact 7.0e5) | 5.1e5 (old 3.5e5) |
| 3 ps | 9.8e5 | 6.1e5 |
| 6 / 12 / 31 ps | 6.0e5 / 3.4e5 / 4.1e4 | 4.3e5 / 3.0e5 / 7.6e4 |
| From 100 ps | about 4e3-5e3 | about 3e3-4e3 |
| Peak near the drain (y 3.2), DC | 1.1e4 | 1.1e4 |
| Peak near the drain, 31 ps / 105 ps / 1 ns | 4.7e5 / 6.1e5 / 6.8e5 | 4.2e5 / 6.9e5 / 7.3e5 |

- The strike adds 11% (SiN) and 19% (HighK) to the head-edge field for a few ps, then the plasma screens it away within about 30 ps. The high field moves to the drain end and stays there to 1 ns (the end of the run), with nearly the same size on both decks.
- The head-edge DC field ratio to the fourth power is (8.82/7.01)^4 = 2.5 between the fixed and old contact on SiN: the same factor by which the 28 V damage scale was refit (1.5e18 → about 6e17). HighK: 4.3. SiN/HighK: 9.0 with the fixed contact (15 with the old).
- The gate-foot peak (y 0.15) was as high as the head-edge peak with the old contact (7.4e5) and is 3.7e5 with the fix, so (foot/head)^4 is 3% on SiN and 23% on HighK. The `damYmin` 0.30 cutoff that keeps stress damage off the gate foot was a fitting choice; it may matter much less now. Not tested.
- **Caveats.** The strike is a 1 µm slab (`seeWeff`), so it screens the field over the whole simulated width, which a real track (about 0.1 µm wide) would not. No traps or damage in these runs. Only one strike position; no unbiased (0 V) strike has been run. The mesh is not refined at y 3.2 or at the head edge, so peak values there are approximate.
- If damage follows field to the fourth power times time, the drain end would outweigh the gate edge (E^4 about a third of the head peak, but lasting ~1 ns against ~10 ps). The present model takes the pre-strike DC field only.

Related: [[rad-model]], [[step-search-28v]], [[fp-contact-fix]], [[flooxs-gotchas]], [[levers]].
