---
title: Literature on stepped current collapse after heavy ions
tags: [results, literature, rad-model]
date: 2026-11-17
source: multi-agent literature workflow (28 sources fetched and checked; 26 unverified leads listed)
---
# Heavy-ion current collapse in AlGaN/GaN HEMTs: literature synthesis for the model

Related: [[rad-literature]], [[rad-model]], [[damage-region-map]], [[hot-electron-capture]].

> **2026-11-24:** this note is partly superseded by [[rad-literature-paper]], a full-text review that corrects several statements here (its §6). In particular: the "rises, never drops" statements hold only for the sources listed here (El Fatimy 2010 and Deng 2000 show drops, unirradiated); Rasel 2023/2024 OFF means unbiased; a biased-vs-unbiased heavy-ion comparison with output curves now exists (Lin 2026); published trap levels include 0.2-0.45 eV; Kuboyama 2011 is in our fluence and voltage range.

**Bottom line.** None of the verified sources reports what we are modelling: a permanent current collapse after heavy-ion irradiation under off-state bias, in which Id–Vd drops abruptly or in steps at small-to-moderate Vd, by orders of magnitude, in SiN-passivated devices but not high-k ones. The literature gives the pieces separately:
1. Heavy ions add traps and increase pulsed-IV collapse and gate-lag (Lin 2022; Lei 2015).
2. Biased strikes near our stress voltage leave localized, bias-dependent damage. A TCAD study proposes hot-electron, field-driven defect generation near the drain (Zhang 2024).
3. In simulations of unirradiated devices, high-k passivation lowers the drain-edge field and with it field-driven trapping and collapse (Satoh 2015; Hanawa 2015).
4. Threshold-like I–V features in unirradiated HEMTs come from three proposed mechanisms: hot-electron buffer trapping, a virtual gate with a critical lateral field, and discharge of a floating buffer (Wang 2011; Kaushik 2013; Singh 2018). In the sources listed here the reported features are current rises (kinks); drops in unirradiated HEMTs exist (El Fatimy 2010, Deng 2000; [[rad-literature-paper]]).

Our model combines stress-field-placed damage with hot-electron capture. It is consistent with this literature, but the literature does not establish it. Most sources could only be read as abstracts; access is marked in the reference list.

## 1. What is reported

### 1.1 Collapse and trapping after heavy ions (closest to our observation)
- **Lin 2022.** 2.1 GeV Ta ions. Vth moved positive by about 25% and saturation current fell by about 14%.
  - Pulsed output curves showed much more current collapse after irradiation.
  - There were more surface-state traps, with time constants mostly below 10 µs.
  - Defects in the band gap and at the gate/barrier interface act as tunnelling sites and raise gate current.
  - The abstract gives neither the fluence nor the bias during irradiation. Related work by overlapping authors used 1e8–1e10 cm⁻², which is not confirmed for this paper.
  - The collapse is described as a fractional loss. No abrupt drop or steps are reported.
  - This is the only verified heavy-ion source with pulsed-IV collapse. Whether traps faster than 10 µs show up depends on the curve tracer's pulse width and quiescent bias.
- **Lei 2015.** 256 MeV I ions up to 1e10 cm⁻², with the device off-state during irradiation.
  - Id and Ig rose during exposure.
  - Afterwards, saturation Id, reverse gate leakage and gate-lag all increased "dramatically" (the abstract gives no numbers).
  - Electroluminescence hot spots appeared in the gate area.
  - There was no obvious annealing after 1 day or 1 week at 300 K.
  - The proposed mechanism is latent-track defects that reduce 2DEG charge and mobility. That would lower Idsat, yet the abstract says Idsat rose. Check the full text.

### 1.2 Permanent DC degradation (no collapse reported)
- **800 MeV Bi, about 5e10 cm⁻²:**
  - Latent tracks act as gate-leakage paths, and NIEL defects reduce 2DEG density and mobility (Lei 2018; its numbers are unverified).
  - Idsat −13.1%, Vth −0.21 V, peak gm −26.6%, reverse Ig up more than 16×, forward Ig up more than 3× (Yue 2021). Room-temperature and 175 °C anneals partly recover every parameter except gate leakage.
  - In Yue 2021, conductive AFM on bare heterostructures hit with 1400 MeV Ta at 6.86e7 cm⁻² shows leakage rising in the AlGaN. The authors attribute HEMT gate leakage almost entirely to latent tracks (Yue 2021).
- **75 MeV S on AlInN/GaN, up to 5.5e13 cm⁻²:**
  - Simulations with irradiation-generated acceptor-like defects reproduce the degradation (Vega 2019).
  - A large positive Vth shift appears at higher fluence, and carrier density and mobility both fall (Challa 2021).
  - Thermally stimulated current levels sit at 0.78–0.82 and 0.91–0.98 eV, attributed to Ga vacancies and complexes acting as acceptors (Challa 2022).
- **2.8 MeV Au (nuclear stopping, 0.001–2 dpa).** At 0.1 dpa the ON-biased device's current density fell by about 2 orders of magnitude and the OFF-biased device stopped working. Leakage rose by about 6 orders. Defects and intermixing appeared at the AlGaN/GaN interface (Rasel 2023).
- **1.7 MeV Ge microbeam aimed at the gate–drain gap (about 1e11 cm⁻²).** Lower gm and Id, a changed gate diode, and no shift in Vth or Ron (Mace 2020). In the companion dissertation, 47 MeV Ge aimed at the gate raised Vth through charge trapping, and the change survived a 60-day anneal.
- **p-gate HEMTs.** Unbiased irradiated devices also degrade, with Ron up and breakdown voltage down. Latent tracks with N₂ bubbles run through the heterojunction into the GaN (Hu 2025).
- **Au⁴⁺, in-situ TEM.** Vacancies, interstitials and dislocations form. The authors hypothesize that trapped charge lowers the off-state breakdown voltage (Islam 2019).

**Sign of the Vth shift in the literature:**
- Positive: Lin 2022, Challa 2021, and Rasel 2024 (protons).
- Negative: Yue 2021, −0.21 V. That is the same size as our +0.2 V with the opposite sign.
- None: Mace 2020, for gap strikes.

### 1.3 Bias during irradiation
- **Zhang 2024** (full text) is the closest match to our conditions. Its HEMTs have Lgd = 3.5 µm and a 0.40 µm gate, in 8–12 GHz GaN-on-SiC MMIC power amplifiers.
  - Ions and bias: Ta at 1721.4 MeV, LET 78.1 MeV·cm²/mg, total fluence 1e6 cm⁻², Vg = −5 V, Vd stepped from 30 V in 10 V steps.
  - At 30 and 50 V, Ig and Id rose slightly and tracked each other, while the source current stayed more than 10× lower.
  - Photoemission showed faint spots in the HEMTs at 30 V, and more, brighter spots at 50 V.
  - At 60 V the device burned out (SEB).
  - The same 60 V bias without ions caused no rise.
  - There are no post-irradiation output curves at sub-burnout bias.
  - In short, individual biased strikes leave localized damage, and the damage grows with Vd near our 28 V.
- **Nakada 2018** (one-page report, read in full). A 600 V p-GaN commercial device at Vgs = 0.
  - With Xe (LET 36.2), leakage grew with fluence only between 300 and 360 V, and the device was destroyed at 380 V.
  - With Kr (LET 18), there was no rise up to 500 V and the device failed at 520 V.
  - At Vgs = +0.95 V the device survived to its rated voltage.
  - The authors suggest, with hedging, that each strike leaves its own localized damage site. Companion paper: Mizuta 2018.
- **The bias state that does most damage differs between studies:**
  - OFF worse than ON for 2.8 MeV Au (Rasel 2023).
  - ON worse than OFF for 300 keV protons: Vth +0.32 V ON against +0.09 V OFF; Idsat −12.4% and gm −19% in ON at the lowest fluence (Rasel 2024).
  - With the Ge microbeam, only ON and semi-on changed during irradiation, but the post-irradiation changes were similar in all bias states (Mace 2020).
  - Electrical stress speeds up failure in p-gate devices (Hu 2025).
- **Net.** An electric field during irradiation increases damage (Rasel 2023, 2024; Zhang 2024; Hu 2025). But no verified study compares biased and unbiased heavy-ion irradiation at a sub-burnout off-state bias, with output curves measured afterwards. Our "unbiased barely degrades" is neither confirmed nor contradicted. The one with/without-bias study (Hu 2025, p-gate) found that unbiased devices do degrade.

### 1.4 Passivation
- No verified heavy-ion study compares SiN with HfO2 or any other high-k passivation.
- **Satoh 2015** (simulation, unirradiated). A high-εr passivation weakens the field at the drain-side gate edge, lowers buffer leakage and raises off-state breakdown. A thick high-k layer reduces drain lag and current collapse because fewer electrons are injected into the buffer, which has deep acceptors.
- **Hanawa 2015** (full text, 2D drift-diffusion with impact ionization, no field plate).
  - At εr = 7 (labelled SiN), the added Vd drops almost entirely at the gate drain edge, and the gate breaks down near 80 V.
  - At εr = 20 the edge field stays moderate even at 100 V, and breakdown comes near 275 V.
  - At εr ≥ 40, buffer leakage sets the limit.
  - Mechanism: the voltage drops uniformly inside the insulator, which smooths the drop at the gate edge.
  - Limits: HfO2 is never named and 28 V is not a reported point.
- **Vetury 2001.** Collapse comes from a virtual gate: electrons trapped in surface states in the gate–drain access region. Passivated devices next to unpassivated ones on the same wafer showed almost no collapse.
- **Patrick 2013** (TRIM + FLOODS, protons). Negative traps in the buffer barely change the gate-edge field. Negative charge at the nitride/AlGaN interface, put in by hand, acts as a virtual gate: it lowers the gate-edge field (raising the critical voltage) while leaving I–V unchanged.

### 1.5 Threshold-like I–V features (unirradiated or other particles)
- **Hot-electron buffer trapping (Wang 2011).** The kink is caused by drain and gate "pumping". Hot 2DEG electrons are injected into the buffer and captured by donor-like traps, followed by field-assisted de-trapping. The kink grows with the highest Vd and Id reached. Activation energy 589 ± 67 meV, close to the GaN E2 trap.
- **Virtual gate with a critical field (Kaushik 2013, ATLAS).** A high-resistance region of the 2DEG under the virtual gate changes resistance abruptly at a critical lateral field set by Vds, and the change depends on channel temperature. The abstract does not say whether Id falls or rises.
- **Floating buffer (Singh 2018).** Carbon makes the buffer p-type and floating. Trap-assisted leakage across the junction between the 2DEG and the p-type buffer injects holes and discharges the buffer a few volts above the knee. This gives a bias threshold and hysteresis. Transients of both signs share a 0.9 eV activation energy.
- **Bias-activated barrier traps (Jiang 2026, Cl ions).**
  - A VN-related level near Ec−0.77 eV in the AlGaN switches on above a critical gate voltage and sharply increases capture.
  - Damage that varies with depth gives Vg-dependent Ids loss and a collapse of the transconductance peak.
  - FeGa–VN near Ec−0.5 eV in the GaN pins the Fermi level.
  - A donor, E1, near the interface saturates the Vth shift.
- **Bulk traps (Kalavagunta 2009, protons).** Bulk traps increase gate-lag. The companion dissertation found no substantial hot-electron current collapse from bulk traps.

Every feature in this subsection is either a current rise (de-trapping or discharge) or an effect driven by Vg. None is a drop triggered by Vd.

## 2. Proposed explanations

Key: Y = explains it, P = partly or only under conditions, N = does not, (inf) = our inference, not stated by the source.

| Mechanism | Abrupt drop | Multiple steps | Creep after drop | SiN vs high-k | Off-state bias needed | +Vth | Support for our case |
|---|---|---|---|---|---|---|---|
| A. Radiation acceptors deplete the 2DEG (static) | N | N | N | P, only if placement follows the field | N (field raises susceptibility) | Y, if under the gate | Strong for DC loss, none for collapse |
| B. Surface/interface traps form a virtual gate | P (critical lateral field) | P, if the virtual gate is segmented (inf) | P | Y | P (charge filled at stress) | P (not stated) | Strong for collapse generally; one abstract-level heavy-ion source |
| C. Field- or hot-electron-driven defect generation during the biased strike | N (sets where damage is) | P, through discrete per-strike sites | N | Y, through field concentration | Y | N, unless under the gate | Moderate: inferred from photoemission, SEM and TCAD; DFT for one route |
| D. Hot-electron capture that switches on with Vd, plus field-assisted de-trapping | Y | Y, if there are several trap regions | Y, through de-trapping | P | N | N | Moderate, but unirradiated, and the reported direction is a rise |
| E. Buffer charging, floating buffer, back-gating | Y (discharge threshold) | N reported | — | Y (less buffer injection with high-k) | P | Small | Moderate, unirradiated |
| F. Barrier traps activated by gate bias | Vg threshold only | P (non-uniform depth) | — | N | N | Y (through a donor) | Weak: abstract only, Cl ions, Vg not Vd |
| G. Latent tracks: leakage paths, N₂ bubbles, local defects | N | Supplies discrete sites | P, if leakage rises with Vd (inf) | Not tested | P (bias speeds failure) | Wrong sign in Yue 2021 | Strong for gate leakage |
| H. Single-event burnout or ion-induced conductive path | Destructive | N | N | — | Y | — | Different regime (≥ 60 V) |
| I. Strain, inverse piezoelectric effect | N | N | N | — | P | N | Weak |

**A. Acceptor damage that depletes the 2DEG.**
- Evidence: Vega 2019 and Challa 2021/2022 (simulations with acceptor-like defects; thermally stimulated current points to Ga-vacancy acceptors); Rasel 2024 (positive Vth from acceptor-like traps); Lei 2015 and Lei 2018 (track and NIEL defects reduce 2DEG density and mobility); Kalavagunta 2009 (band bending lowers 2DEG density).
- Explains the positive Vth shift and the loss of Idsat and gm.
- Cannot explain a Vd-triggered drop without a dynamic occupancy.

**B. Virtual gate.**
- Evidence: Vetury 2001 (the founding paper; passivation suppresses it); Lin 2022 (heavy ions add surface-state traps along with more pulsed collapse); Patrick 2013 (TCAD: negative charge at the nitride/AlGaN interface reshapes the field); Kaushik 2013 (the region under the virtual gate switches resistance abruptly at a critical lateral field that depends on temperature).
- This is the only published mechanism with an explicit field threshold inside an Id–Vd sweep, but its direction is unconfirmed.
- It explains a passivation dependence naturally, because the passivation interface hosts the charge.
- The heavy-ion traps in Lin 2022 are fast (below 10 µs), which matters for the pulse conditions.

**C. Defect generation during the biased strike.**
- Zhang 2024 gives a TCAD sequence:
  1. The ion track creates electron-hole pairs (about 1 ps).
  2. Holes pile up under the negatively biased gate and lower the barrier between the source and the buffer.
  3. Electrons inject from the source (from about 20 ps), forming a punch-through path.
  4. The gate–drain field heats these electrons, and they impact-ionize near the drain.
  5. Some create defects in the GaN buffer near the drain and are trapped there.
  6. The trapped charge raises the drain-side longitudinal field.
- Zhang 2024 also finds field-plate-edge strikes the most sensitive.
- Other support:
  - Hot electrons can activate defects by releasing hydrogen from passivated point defects (Puzyrev 2011, DFT, for degradation that does not recover spontaneously).
  - A related proton study reports reconfiguration and/or dehydrogenation of O-related defects (Chen 2013).
  - Fields increase susceptibility to damage (Rasel 2023, 2024).
- Explains the need for bias and gives damage that is localized per strike and sits where the field is high.
- The SiN vs high-k difference then follows from the field redistribution in Hanawa 2015 and Satoh 2015 (that link is our inference).
- Caveat: Zhang's defects are inferred, not measured, and the study is about burnout at 60 V.

**D. Hot-electron capture that switches on with Vd.**
- Evidence: Wang 2011 (hot 2DEG electrons captured in the buffer, field-assisted de-trapping, E2-like 0.59 eV) and Zhang 2024 (trapping raises the local field, a positive-feedback loop).
- This is the only mechanism here that naturally gives an abrupt onset inside a single Vd sweep, plus creep through field-assisted de-trapping.
- Not reported after irradiation. In Wang 2011 the kink is a rise caused by earlier pumping, not a drop in the same sweep.

**E. Buffer charging.**
- Evidence: Satoh 2015 (injection into the buffer and trapping there; high-k reduces it); Singh 2018 (a floating buffer discharges at a leakage threshold, with hysteresis); Zhang 2024 (defects in the buffer near the drain).
- Gives a bias threshold. Singh's direction is a recovery, not a drop.

**F. Barrier traps activated by gate bias (Jiang 2026).**
- A precedent for radiation traps that turn on above a bias threshold, with non-uniform damage giving onsets that depend on the region.
- The threshold is in Vg and shows up as a collapse of the gm peak, not a 1000× Id drop.

**G. Latent tracks.**
- Evidence: Lei 2015, Lei 2018, Yue 2021 (gate leakage almost entirely through tracks; irreversible), Hu 2025 (N₂ bubbles; unbiased Ron up).
- Provides physically discrete damage sites, which is the basis for discrete strikes.
- No source links tracks to collapse.

**H, I.** Burnout and conductive paths (Zhang 2024, Nakada 2018, Mizuta 2018, Kuboyama 2011, Hu 2025) and strain (Mace 2020 dissertation; Rasel 2023, 2024) are outside our measured regime. The sub-burnout photoemission spots at 30–50 V in Zhang 2024 are what matters for us.

## 3. What our model could test

Lever names are from `drivers/radIV.tcl` and `kb/model/levers.md`. "Physics change" marks items that, under CLAUDE.md §5, must be proposed to Ian before they are implemented.

The Outcome column and the outcome lines under "Runs that distinguish them" record what had been run by 2026-11-20. Every strike run loaded a stress state saved with the old FP contact box, so those outcomes are pre-fix; being rerun, [[fp-contact-fix]].

| Mechanism | Model change | Signature that identifies it | Steps without hand-placed sites? | Outcome (2026-11-20) |
|---|---|---|---|---|
| C (static field) | Exponent `damM` 2–6; depth `damXmax` from 50 nm down to 0.1–0.3 µm into the buffer (Zhang puts defects in the buffer near the drain); `damField` lat vs tot; stress Vd series from the stress library (`stressLoad`, 1–84 V) | HighK/SiN damage ratio ≈ (E_HK/E_SiN)^m. With 5.5e5 vs 2.9e5 V/cm at y 0.5 µm (17 V stress), HighK gets 3.6× less damage at m = 2, 13× less at m = 4, 47× less at m = 6. Find the smallest m that keeps HighK flat. | Only if the field has several separate peaks (see the second-field-plate row below) | Stress-Vd series run (radStepE 51801897): stress damage alone gives one drop at each stress voltage (24 V: 1.2-1.6 V; 28 V: 1.6-2.0 V; 30 V: 1.8-2.3 V, each at its own scale), no separate field-peak steps. `damM` and `damXmax` not varied in the step search ([[step-search-28v]]). |
| C (hot-electron flux) | `damNexp` > 0 or `damField ne` (damage ∝ n·E^m), as a proxy for the hot-electron flux in Zhang 2024 and Puzyrev 2011. Better: weight damage by n·E or the impact-ionization rate integrated over the `seeIV` strike transient. That means new placement code: a model change, propose to Ian. Our seeIV run already shows the peak field moving to the drain edge, as in Zhang 2024. | Damage moves from the gate-edge field peak toward the drain-side depletion edge or the drain. The onset then moves to the Vd at which Te there crosses the capture threshold. | Possibly two: the gate edge and the drain side | n·E⁴ weighting had no effect at the 17 V stress (radPhys1 47725314, [[rad-model]]). At 28 V the stress-time n·E favours SiN only near y 0.8 (no runs, [[step-search-28v]]). Strike-transient weighting not built. |
| C + G (discrete strikes) | `damGauss` density (4–8e18), sigma (20–100 nm), depth x, y positions including the field-plate edges; `trackFieldM` so that strike damage scales with the stress field (makes unbiased strikes weak, after Zhang 2024); 3D `damRod` covering full, half or quarter width | Removing one strike ("knock-out") moves only its own step. Step Vd follows the strike's y and density. | Yes: one step per site with a distinct onset | Run (rounds S, A-K, M). Trap 0.30 / 8e18 strikes give 2 / 3 / 3 drops on three meshes. Not one step per site: the pockets share the drain voltage ([[step-mechanism]]); knock-out moves the remaining steps by ≤ 0.3 V. Field-scaled strikes (`gaussFieldM`, rounds H-J) keep HighK flat but give SiN one drop. 3D `damRod` stopped by the brick-gradient bug ([[3d-plan]]). |
| C (geometry) | Add a second, source-connected field plate next to the gate plate (the deck has one). This is a deck change: commit first and agree it with Ian, because the deck is calibrated. | E^m damage gets separate maxima at the gate edge and each field-plate edge. The step count is set by the number of field peaks, not the number of strikes. High-k smooths each peak. | Yes, and it is the most natural route to 2–3 steps | Not run (deck change). |
| B (virtual gate) | Field-driven surface trap sheet with lateral-field capture (branch `explore/field-capture`), with its density placed by the stress field at the passivation interface (`damInsPeak`, `damInsM`, `damInsXmin`). Fixed `insTrapSign` −1 charge only as a static control. | Onset moves later at higher Vg, the opposite of hot-electron capture. Fast traps (Lin 2022, below 10 µs) empty between pulses with `emitRest 1`. | Only if the trap sheet is segmented (gate edge, FP edges) | Not run in the rad model. The Oct virtual-gate sheet gave the measured Vg ordering but a switch-like shift ([[vg-dependence]]). |
| D (creep) | `emitFrac`, `emitRest`. Field-assisted (Poole–Frenkel) emission, after Wang 2011, is a physics change. | Emission-driven creep: trapped charge falls as Vd rises. Electrostatic creep: trapped charge stays constant while Id rises because the drain field punches through the depleted section. Log occupancy against Vd to tell them apart. | No (shapes the plateau) | Crude emission tested on single sites (radEmit 49834170, radEmit2 49853997, radEmit3 50128200): no clean step ([[damage-region-map]]). Not tried on the 28 V strike curves. Occupancy is logged per Vd by `vdCuts` ([[step-mechanism]]); with fill-only capture (the default) trapped charge cannot fall, so any creep there is electrostatic by construction. |
| E (buffer) | `damSites` acceptors at x 0.05–0.5 µm under the drain-side access region or near the drain. A buffer-specific level (Fe/E2-like, 0.5–0.6 eV) needs a second trap species, because `trapLevel` is one level shared by GaN and AlGaN. Floating-buffer hole injection (Singh 2018) needs trap-assisted leakage, a physics change. | Vth hardly moves; knee and Ron change. Our back-gating runs needed about 1e13 cm⁻² for +0.1 V. | Unlikely | Not run. |
| F (barrier traps) | Damage confined to the AlGaN barrier (x < 0.015 µm) under or near the gate, at a deeper level (0.77 eV, Jiang 2026); `VgFam` | The collapse switches on above a critical Vg rather than a critical Vd | No | Not run. The step switch itself is AlGaN-barrier trap filling, but driven by Vd through hot-electron capture ([[step-mechanism]]). |
| A (static) | `mobDamFac` windows; under-gate acceptors; `surfCharge`; `polWinFac` | Ron and gm change with no Vd-triggered drop. Use as controls and to fit +0.2 V (our runs: all of these reach +0.2 V, and Ron and gm tell them apart). Also test the coupling: mobility loss at a strike raises the local field and Te, so its step should come at lower Vd. | No | Not run in the step search. The static Vth routes were run earlier (radVth 49570570, [[rad-model]]). |
| Trap level | `trapLevel`, `hotEb`, `hotTau` | Published radiation levels are 0.5–0.98 eV (Jiang 2026; Wang 2011; Challa 2022), deeper than our 0.30 eV (radStepB tries 0.35–0.45). Deeper levels collapse early and uniformly in our maps, so report the effective level, trapLevel − hotEb(1 − T/Te), next to the literature values. | — | radStepB (5e18, 3 strikes): 0.35 / 0.40 / 0.45 eV give two drops each, the first earlier and deeper at deeper levels (1.9-2.3 V 320 → 211; 1.5-1.9 V 253 → 128; 1.2-1.6 V 191 → 63 mA/mm). Trap 0.40 with 7e18 gives one drop per strike on m5fix only. Levels above 0.45 eV not tried in the strike search ([[step-search-28v]]; 0.55 eV single Gaussians in [[damage-region-map]]). |

### Mechanisms that naturally give multiple discrete steps
1. **Independent sites with different capture onsets.** Strikes or tracks at different y, density or depth each reach the capture threshold at their own Vd. Our runs already show this: in radStepA (2026-11-17), three 8e18 strikes give drops near 1.6–2.0, 3.7–4.0 and 6.7–6.9 V.
2. **Separate field peaks from the structure.** With the gate edge and each field-plate edge, stress-field damage forms discrete peaks without any hand placement. This is supported by the field-plate-edge sensitivity in Zhang 2024 and the field-concentration argument in Hanawa 2015.
3. **A cascade through field redistribution.** Trapping at one site depletes the 2DEG, concentrates the lateral field and heats electrons at the next site. This is the trapping-raises-field loop of Zhang 2024.
4. **Partial-width tracks (3D only).** Each track pinches part of the width. At 1e7 cm⁻² (0.1 µm⁻², ions about 3 µm apart), a 200 µm-wide device gets about 2 hits in every 0.1 µm-wide band along the channel and about 70 in a 3.5 µm gate–drain gap. Many small pinches add up to a droop unless the trapping runaway spreads sideways.
5. **A segmented virtual gate.** Successive surface segments fill, each switching at its own critical field (Kaushik 2013, inferred).

Uniform 2DEG depletion, mobility loss, fixed charge and single buffer back-gating do not naturally give steps.

### Runs that distinguish them
- **Knock-out test.** Delete one site and rerun. If the other steps stay at the same Vd, the sites are independent (route 1). If later steps move or vanish, the steps cascade (route 3).
  - **Outcome (radStepD 51801163):** removing strike 0.8 or 1.6 of three 8e18 strikes moves the first drop from 1.6-2.0 to 1.4-1.7 V and the step near 4 V from 3.7-4.0 to 3.5-4.1 V. The strikes are partly independent: the pockets sit in series and share the drain voltage, so each strike shifts the others slightly ([[step-search-28v]], [[step-mechanism]]).
- **Stress-Vd series from the library.** Field-peak steps (route 2) move with `Vd_stress` and FP geometry. Strike steps (route 1) move with strike y and density.
  - **Outcome (radStepE 51801897):** stress damage alone gives one drop at each stress voltage (24 / 28 / 30 V: 1.2-1.6 / 1.6-2.0 / 1.8-2.3 V), with no separate field-peak steps. FP geometry was not varied ([[step-search-28v]]).
- **3D rod fraction** (rad3dRod: full, half and quarter width). If step height scales with rod length, there is no lateral spread and a 2D strike overstates each step. If step height saturates, the runaway spreads sideways and discrete steps survive in 3D.
  - **Outcome:** stopped. Stock FLOOXS gets the depth gradient wrong on the 3D brick mesh, so the rad3dRod 3D tasks (51784348) were cancelled. A patched FLOOXS (`~/flooxs-brickfix`) matches 2D and has been used only for a local render ([[3d-plan]]).
- **Vg family** (`VgFam`). In our hot-electron capture, which is current-driven, a higher Vg moves the onset earlier. Field-driven capture (route 5, the virtual gate) moves it later. That later shift is what the measured pulsed curves showed (`kb/results/vg-dependence.md`).
  - **Outcome:** VgFam {0 −1} ran for three library cases (radStepE 51801898; the 8e18 3-strike case has no Vg −1 curve). The curves are in `results/20261117_radStepE` but have not been analysed. With fill-only capture, each curve after the first carries the earlier curves' trapped charge.
- **HighK counterparts with identical levers.** These must stay flat (radStepC). If HighK steps once the damage is scaled by (E_SiN/E_HK)^m, the passivation contrast rests entirely on m.
  - **Outcome (radStepC 51799742, radStepG 51823696, radStepK 51939558):** HighK does not stay flat. Plain 4e18 strikes give it small drops at trap 0.30 eV and a clear one at 0.40 eV (414 → 388 mA/mm); 5e18 or more gives clear drops. Field-scaled strikes (m 4, rounds H-J) keep HighK flat but give SiN only one drop. So in the strike model the passivation contrast rests on m ([[step-search-28v]]).
- **Hysteresis and memory.** Sweep up and back down, and vary `emitRest`. Trapping-based steps show hysteresis; fixed damage does not.
  - **Outcome:** not run in the step search.
- **Occupancy and Te maps at each step.** Identify which region crosses the capture threshold.
  - **Outcome (radStepDiag 51998840, radStepDiag5b 52018703, `vdCuts`):** each drop is one damaged pocket switching once ~0.5 V sits across it, as the AlGaN barrier traps over its drain flank fill with hot electrons ([[step-mechanism]]).
- **Convergence.** A step counts only if it survives a 5 nm mesh around the site and a halved Vd step. Earlier model steps turned out to be mesh and step artifacts.
  - **Outcome:** halving the Vd step keeps the step counts (positions move by up to ~0.7-1 V; steps under ~15 mA/mm are not robust). With 5 nm at y 0.8, row A (6e18) keeps only 2 / 1 / 0 drops for 1 / 2 / 3 strikes, while trap 0.30 / 8e18 keeps 2 / 3 / 3 drops on all three meshes. The 2.5 nm check is being redone with the fixed FP box ([[step-search-28v]]).

## 4. Gaps
1. **No direct precedent.** No verified report of an abrupt or stepped Id–Vd collapse after heavy ions, and none of a roughly 1000× drop at sub-volt Vd. The closest is Lin 2022, where the collapse is stated qualitatively and the fluence, bias and pulse conditions are not in the abstract.
2. **No biased vs unbiased comparison at sub-burnout bias with output curves.** Zhang 2024 at 30–50 V reports only slight leakage and photoemission spots. Hu 2025 found that unbiased p-gate devices degrade. Studies disagree on whether ON or OFF bias is worse (Rasel 2023 vs Rasel 2024; Mace 2020).
3. **No heavy-ion passivation comparison.** The high-k argument rests on simulations of unirradiated devices without field plates, comparing εr only. HfO2 is never named and 28 V is not a reported point (Satoh 2015; Hanawa 2015).
4. **Fluence gap.** Our 1e7 cm⁻² falls between the burnout studies (1e6 cm⁻²; 3e5 cm⁻²) and the degradation studies (1e10 cm⁻² and up). At our fluence the discreteness of individual tracks matters, and nobody addresses it.
5. **The damage law is ours.** No source gives a damage–field exponent or measures how damage grows with stress Vd, apart from the qualitative growth of spots from 30 to 50 V (Zhang 2024). Per-strike defect creation below burnout bias is inferred, never confirmed by spectroscopy.
6. **Trap levels and time constants are unconstrained for our geometry.** Literature levels are 0.5–0.98 eV. Lin 2022's traps are faster than 10 µs, so the curve tracer's pulse width and quiescent bias need to be known.
7. **Creep after the drop.** No irradiation source explains it. Only the kink literature's field-assisted de-trapping applies (Wang 2011).
8. **Sign of the Vth shift.** Positive (Lin 2022, Challa 2021, Rasel 2024), negative (Yue 2021) and none (Mace 2020) are all reported.
9. **Access.** Most sources were read as abstracts only. Full texts worth getting: Lin 2022 (fluence, bias, pulse conditions), Lei 2015 (direction of the Idsat change, gate-lag conditions), Kaushik 2013 (whether Id falls or rises at the critical field), Satoh 2015 (field-plate geometry) and Singh 2018.

**Unverified leads (not checked; titles only):**
- **Passivation and high-k:**
  - "Analysis of Lag Phenomena and Current Collapse in Field-Plate AlGaN/GaN HEMTs with High-k Passivation Layer" (2021, techconnectworld.com/World2021/a.php?i=115)
  - "Operational Characteristics of AlGaN/GaN HEMTs with Various Dielectric Passivation Structures…" (2024, doi:10.3390/mi15091126)
  - "Role of ex-situ HfO2 passivation… X-ray-induced degradation… MIS-HEMTs" (year unconfirmed)
  - "Impact of process-dependent SiNx passivation on proton-induced degradation in GaN MIS-HEMTs" (2021)
  - "Latent tracks of swift Bi ions in Si3N4" (2020, doi:10.1088/2053-1591/ab72d3): tracks forming in the SiN itself could be a route to the SiN vs high-k difference.
- **Threshold-like I–V:**
  - "Part I: Physical Insights into Dynamic RON Behavior and a Unique Time-Dependent Critical Stress Voltage" (2021, doi:10.1109/TED.2021.3109847)
  - "Dynamic Behavior of Threshold Voltage and ID-VDS Kink… Due to Poole-Frenkel Effect" (2023, doi:10.1109/TED.2023.3326781)
  - "Negative Differential Conductivity in AlGaN/GaN HEMTs: Real Space Charge Transfer…" (2000, doi:10.1557/S1092578300004506)
  - "Investigation of Trapping and Hot-Electron Effects… Combined Electrooptical Method" (2011, doi:10.1109/TED.2011.2160547)
- **Ion-damage TCAD and radiation effects:**
  - "(Invited) Simulation of Radiation Effects in AlGaN/GaN HEMTs" (2015)
  - "Effect of Heavy Ion Radiation on Electrical Performance… in Non-Gate Region" (2025, 10.1109/TNS.2025.3591512)
  - "TCAD Simulation of the Single Event Effects in Normally-off GaN Transistors…" (2017, 10.1109/TNS.2017.2710629)
  - "Radiation Effects in AlGaN/GaN HEMTs" review (2022, 10.1109/TNS.2022.3147143)
  - "Radiation response of AlGaN-Channel HEMTs" (2019)
  - "Impact of Gamma Radiation on Dynamic RDSON…" (2019, 10.3390/ma12172760)
  - Total-dose studies (2020, doi:10.3390/nano10112175; 2023, doi:10.1109/TNS.2023.3237179)
  - Proton MIS-HEMT study (2023, doi:10.3390/nano13050898)
  - Enhancement-mode single-event study (2024, 10.3390/mi15080950)
- **Tracks in GaN:**
  - 2004 (doi:10.1063/1.1703826)
  - 2015 (doi:10.1007/s10853-015-9069-y)
  - 2017 (doi:10.1063/1.4995491)
  - 2018 (doi:10.1038/s41598-018-22321-w)
  - 2021 (doi:10.1038/s42005-021-00550-2)
  - 2025 (doi:10.3390/mi16030288)
  - 2026 (arXiv:2604.24288)

## References
Access: [F] full text read, [P] partial (companion documents), [A] abstract or metadata only.

- Challa 2021: S. R. Challa et al., "Understanding High-Energy 75-MeV Sulfur-Ion Irradiation-Induced Degradation in GaN-Based Heterostructures: The Role of the GaN Channel Layer," IEEE TED 68(1), 24–28 (2021), doi:10.1109/TED.2020.3037259. [A]
- Challa 2022: S. R. Challa et al., "Defect characterization of heavy-ion irradiated AlInN/GaN on Si high-electron-mobility transistors," J. Phys. D 55(11), 115107 (2022), doi:10.1088/1361-6463/ac40b8. [A]
- Chen 2013: J. Chen, Y. S. Puzyrev et al., "Proton-induced dehydrogenation of defects in AlGaN/GaN HEMTs," IEEE TNS 60(6), 4080–4086 (2013), doi:10.1109/TNS.2013.2281771. [A]
- Hanawa 2015: H. Hanawa, Y. Satoh, K. Horio, "Simulation of High-k Passivation-Layer Effects on Breakdown Voltage in AlGaN/GaN HEMTs," TechConnect Briefs 2015 vol. 4, 266–269, https://briefs.techconnect.org/wp-content/volumes/TCB2015v4/pdf/644.pdf. [F]
- Hu 2025: P.-P. Hu et al., "Failure mechanisms of AlGaN/GaN HEMTs irradiated by high-energy heavy ions with and without bias," Nucl. Sci. Tech. 36(1), 13 (2025), doi:10.1007/s41365-024-01567-2. [A]
- Islam 2019: Z. Islam et al., "Heavy ion irradiation effects on GaN/AlGaN high electron mobility transistor failure at off-state," Microelectron. Reliab. 102, 113493 (2019), doi:10.1016/j.microrel.2019.113493. [A]
- Jiang 2026: H. Jiang et al., "The Impact of Non-Uniform Distribution of Radiation-Induced Defects on the Electrical Performance of AlGaN/GaN HEMTs," IEEE TNS 73(2), 314–322 (2026), doi:10.1109/TNS.2025.3597348. [A]
- Kalavagunta 2009: A. Kalavagunta et al., "Impact of Proton Irradiation-Induced Bulk Defects on Gate-Lag in GaN HEMTs," IEEE TNS 56(6), 3192–3195 (2009), doi:10.1109/TNS.2009.2034156; dissertation https://ir.vanderbilt.edu/handle/1803/11752. [A]
- Kaushik 2013: J. K. Kaushik et al., "On the Origin of Kink Effect in Current–Voltage Characteristics of AlGaN/GaN HEMTs," IEEE TED 60(10), 3351–3357 (2013), doi:10.1109/TED.2013.2279158. [A]
- Kuboyama 2011: S. Kuboyama et al., "Single-Event Damages Caused by Heavy Ions Observed in AlGaN/GaN HEMTs," IEEE TNS 58(6), 2734–2738 (2011), doi:10.1109/TNS.2011.2171504. [A]
- Lei 2015: Z.-F. Lei et al., "Influence of heavy ion irradiation on DC and gate-lag performance of AlGaN/GaN HEMTs," Chin. Phys. B 24(5), 056103 (2015), doi:10.1088/1674-1056/24/5/056103. [A]
- Lei 2018: Z. F. Lei et al., "Degradation mechanisms of AlGaN/GaN HEMTs under 800 MeV Bi ions irradiation," Microelectron. Reliab. 80, 312–316 (2018), doi:10.1016/j.microrel.2017.07.086. [A, secondary summaries]
- Lin 2022: Z.-Z. Lin et al., "Effect of heavy ion irradiation on the interface traps of AlGaN/GaN high electron mobility transistors," Chin. Phys. B 31(3), 036103 (2022), doi:10.1088/1674-1056/ac11e4. [A]
- Mace 2020: M. E. Mace et al., "Targeted Heavy-Ion Radiation of Aluminum Gallium Nitride/Gallium Nitride HEMTs," J. Radiat. Eff. Res. Eng. 38(1), 132–141 (2020), https://scholar.afit.edu/facpub/688; poster SAND2019-3048C https://www.osti.gov/servlets/purl/1639470; dissertation https://scholar.afit.edu/etd/2462. [P]
- Mizuta 2018: E. Mizuta et al., "Single-Event Damage Observed in GaN-on-Si HEMTs for Power Control Applications," IEEE TNS 65(8), 1956–1963 (2018), doi:10.1109/TNS.2018.2819990. [A]
- Nakada 2018: Y. Nakada et al., "Investigation of single-event effect observed in GaN-HEMT," RIKEN Accel. Prog. Rep. 51, 192 (2018), https://www.nishina.riken.jp/researcher/APR/APR051/pdf/192.pdf. [F]
- Patrick 2013: E. Patrick et al., "Modeling Proton Irradiation in AlGaN/GaN HEMTs: Understanding the Increase of Critical Voltage," IEEE TNS 60(6), 4103–4108 (2013), doi:10.1109/TNS.2013.2286115. [A]
- Puzyrev 2011: Y. S. Puzyrev et al., "Dehydrogenation of defects and hot-electron degradation in GaN high-electron-mobility transistors," J. Appl. Phys. 109(3), 034501 (2011), doi:10.1063/1.3524185. [A]
- Rasel 2023: M. A. J. Rasel et al., "Heavy ion irradiation induced failure of gallium nitride high electron mobility transistors: effects of in-situ biasing," J. Phys. D 56(30), 305104 (2023), doi:10.1088/1361-6463/accfa7. [A]
- Rasel 2024: M. A. J. Rasel et al., "Influence of electrical field on the susceptibility of gallium nitride transistors to proton irradiation," J. Phys. D 57(29), 295102 (2024), doi:10.1088/1361-6463/ad3f29. [A]
- Satoh 2015: Y. Satoh et al., "Analysis of high-k passivation-layer effects on buffer-related breakdown and current collapse in AlGaN/GaN HEMTs," Jpn. J. Appl. Phys. 54(3), 031002 (2015), doi:10.7567/JJAP.54.031002. [A]
- Singh 2018: M. Singh et al., "'Kink' in AlGaN/GaN-HEMTs: Floating Buffer Model," IEEE TED 65(9), 3746–3753 (2018), doi:10.1109/TED.2018.2860902. [A]
- Vega 2019: N. A. Vega et al., "Outstanding Reliability of Heavy-Ion-Irradiated AlInN/GaN on Silicon HFETs," IEEE TNS 66(12), 2417–2421 (2019), doi:10.1109/TNS.2019.2954216. [A]
- Vetury 2001: R. Vetury et al., "The impact of surface states on the DC and RF characteristics of AlGaN/GaN HFETs," IEEE TED 48(3), 560–566 (2001), doi:10.1109/16.906451. [A]
- Wang 2011: M. Wang, K. J. Chen, "Kink Effect in AlGaN/GaN HEMTs Induced by Drain and Gate Pumping," IEEE EDL 32(4), 482–484 (2011), doi:10.1109/LED.2011.2105460. [A]
- Yue 2021: S.-Z. Yue et al., "Single-Event Damage-Induced Gate-Leakage Mechanisms in AlGaN/GaN High-Electron-Mobility Transistors," IEEE TED 68(6), 2667–2672 (2021), doi:10.1109/TED.2021.3075667. [A]
- Zhang 2024: H. Zhang et al., "Study on the single-event burnout mechanism of GaN MMIC power amplifiers," Appl. Phys. Lett. 124(8), 082105 (2024), doi:10.1063/5.0185332; accepted manuscript https://researchonline.ljmu.ac.uk/id/eprint/22690/. [F]