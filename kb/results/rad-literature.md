---
title: Literature review, irradiated GaN HEMTs (Vth, Ron, steps)
tags: [results, literature, radiation]
date: 2026-11-04
---
# Literature review: Vth shift and Ron rise in irradiated GaN HEMTs

Our conditions: about 2 GeV Au, LET ~67 MeV·cm²/mg, electronic stopping far above nuclear, fluence 1e7 cm⁻², off-state bias or none ([[rad-model]]). Two research agents ran this review on 2026-11-04. Many sources could only be read as abstracts or fetch summaries; each is marked. ScienceDirect, IEEE, MDPI, Springer and DTIC pages were often blocked, so important papers remain unread.

**Bottom line: nobody has reported what we need at this fluence.** No source found gives Vth at ~1e7 cm⁻² on a D-mode HEMT, a numerical Ron for biased vs unbiased heavy-ion irradiation, or abrupt Id–Vd steps onto a gate-independent line. Everything below is an analogue or inference for our regime.

## Vth shift: mechanisms proposed
| Mechanism | Sign | Reported size | Particle, fluence | Evidence | Src |
|---|---|---|---|---|---|
| Barrier or channel acceptors, 2DEG loss | + | +0.12 V; +25–85% | 2.8 MeV Au ≥1.7e10; Ta; 1.5 GeV Bi 1.7e11 | Shift measured, defects inferred | V6, V5, V4 |
| Same, protons | + | +25–28% | 2 MeV H, 6e14 | Measured, VGa inferred | V10 |
| Damage outside the gate | none | Ids falls only | Heavy ions | Measured and TCAD | V7 |
| Track leakage paths | none shown | Ig ×5 or more | Bi, 5e7–5e10 | EL and TEM measured | V1, V3 |
| Hole capture (total dose) | − | net −190 mV | X-ray, 100 Mrad | Measured, defects inferred | V11 |
| Donors (VN) | − | −0.13 V (snippet only) | 256 MeV I, 1e10; gamma | Inferred | V2, V9 |
| Schottky barrier change | not separated | ideality n ≈ 12 | Au, 2 dpa | I–V fit | V6 |
| Strain relaxation | not separated | Raman shift | Au, high dpa | Inferred | V6 |
| Surface traps | + implied | more collapse | 2.1 GeV Ta | Pulsed I–V, inferred | V5 |
| Buffer charge | + | not given | Simulation | TCAD | V12 |

**Closest match, not yet read in full:** 800 MeV Bi at 5e7 cm⁻² [V1]: Id −6.8%, gm −3.2%, Ig up over 5×. The abstract has no Vth. Get this full text first. A snippet attributes −0.21 V to it, unverified, and that sign would be opposite to ours.

**Recovery:** Bi output recovered in 3 months at room temperature, leakage didn't [V1]; iodine showed none in a week [V2]; X-ray Vth recovered at room temperature [V11].

## Size arguments (ours, not literature)
- A +0.1–0.2 V shift through a 15–18 nm barrier (the size the model uses) needs about 3–6e11 cm⁻² of charge, or 3–6e4 charges per ion at 1e7 cm⁻².
- A 4.5 nm × 18 nm track holds only about 2.5e4 atoms, so a per-track origin needs more than one charge per atom.
- TRIM's ~1e13 cm⁻³ vacancies gives about 2e7 cm⁻² in the barrier, 4 orders short.
- Track area coverage is about 2e-6, with ions ~3 µm apart, so current can flow around local damage.
- Uniform dose is about 11 krad, far below the Mrad range where total-dose shifts are seen [V11].
- **So no single reviewed mechanism reaches the size at this fluence.** Device-to-device spread, measurement drift and a missing control are live possibilities. The evidence ties tracks to **leakage**, not to Vth.

## Ion tracks at this electronic stopping
Our ~41 keV/nm is above the reported GaN track threshold: 23 keV/nm with diameter 1.6–4.5 nm for 23–46.9 keV/nm [V13, snippet], 15 keV/nm also quoted [V17]. At 33 keV/nm a melt radius of 4.4 nm was simulated and matched to TEM, with the crystal intact to 1e13 cm⁻² [V14]. Nitrogen nanobubbles appear in simulations at 40 keV/nm [V16]. Nanocrystalline Si₃N₄ has a threshold of 12–15 keV/nm [V18], and amorphous HfO₂ tracks change C–V and J–V [V19].

## Ron: mechanisms proposed
| Mechanism | Effect | Particle or stress | Bias | Evidence | Src |
|---|---|---|---|---|---|
| Displacement loss of n and µ, split by Hall | µ −28.9%, n −12.1% | 2 MeV H, 6e14 | Not biased | Strong, wrong fluence regime | R7, R8 |
| New acceptor traps near the 2DEG | Dynamic Ron 21→4888 Ω·mm at 50 V, quasi-static only 9.1→14.7 | 2 MeV H | Depends on the measurement bias | Strong measurement, location inferred | R8, R9 |
| Damage aimed at the gate–drain gap | Id and gm fall, no Ron or Vth change | 1.7 MeV Ge, 1e11 | On: immediate; semi-on: delayed; off: none in situ | Medium, low voltage | R5 |
| Single-ion local damage, leak paths, N₂ bubbles | Ron up unbiased, no numbers | Heavy ions | High voltage gives sharp leakage or burnout | Weak for Ron | R1, R10, R11 |
| Field-driven defects (no radiation) | Rd up above a critical voltage | Off-state stress | Field-driven | Contested | R13, R20 |
| Hot-electron trapping in the gate–drain access (no radiation) | Non-recoverable Ron change | On or semi-on stress | Tracks electroluminescence | Abstracts only | R14, R15 |
| Surface or passivation traps | Sets dynamic Ron size | Protons | Quiescent drain bias | Strong within source | R9 |
| Ohmic contacts | Rc unchanged | Gamma | Not tested | Indirect null | R16 |

- **R9 is the closest analogue:** a small DC change coexists with a very large Ron rise after off-state priming.
- **Field plates can move damage, not only reduce it:** longer drain field plates worsened semi-on current loss, through trapping at the plate edge [R15].
- **Fields don't change carrier removal much** at typical HEMT fields [R12]. So a bias effect is more likely after defect creation, in filling or field-driven growth (our inference). This fits a fill-only trap model.
- **No heavy-ion Hall or TLM separation of n and µ, and no source vs drain access comparison, was found.**

## Steps and a gate-independent line
- **No report of abrupt Id–Vd steps.** The nearest: post-irradiation sweeps "hit compliance" [R5], and irrecoverable leakage jumps during irradiation [R11].
- **Series-limit idea:** an access-region ceiling I = Q_acc·v_sat [R22, snippet] would make a damaged or depleted gate–drain section set a Vg-independent current. A filled trap acts as a local floating gate [R19]. That this explains our line is our inference; [[ron-increase]] tests it.
- **Kinks in the literature** are usually current rises (impact ionization, Fe detrapping) [R21, snippets], not drops.
- **Instrument effects:** nothing GaN-specific. Range changes and compliance-skip logic can distort sweeps in negative-differential regions [R23]. Repeating a sweep on a fixed range is an obvious test.

## SiN vs high-k
No heavy-ion comparison, and no irradiation data on HfO₂ passivation of an otherwise standard HEMT, were found. Proton work finds PECVD SiN far worse than ALE AlN for dynamic Ron [R9]. Gamma work finds a 5 nm HfO₂ gate dielectric better than SiN [R16].

## What this means for the model
Every Vth or Ron lever in our model stays **phenomenological**. The studies test which damage geometry reproduces measured signatures, not which defect is responsible. Worth obtaining through library access: V1, V3 and V6's companion R6 in full, R1 (biased vs unbiased heavy ions, the most relevant paper found, not read beyond the abstract), and Chen et al., IEEE TNS 62(6) 2015 (seen only as a citation).

## Sources
Access: **F** full or most read, **P** partial or fetch summary, **A** abstract, **S** search snippet only, unverified.

**Vth review**
- V1 Lei et al., Heavy ions irradiation effects on AlGaN/GaN HEMTs, RADECS 2016, 10.1109/radecs.2016.8093107. A
- V2 Lei et al., Influence of heavy ion irradiation on DC and gate-lag, Chin. Phys. B 2015, 10.1088/1674-1056/24/5/056103. A
- V3 Lei et al., Degradation mechanisms, 800 MeV Bi, Microelectron. Reliab. 2018, 10.1016/j.microrel.2017.07.086. S
- V4 Hu et al., Role of latent tracks, NIM B 2018, 10.1016/j.nimb.2018.06.011. S
- V5 Lin et al., Effect of heavy ion irradiation on interface traps, Chin. Phys. B 2022, 10.1088/1674-1056/ac11e4. A
- V6 Rasel et al., Heavy ion irradiation induced failure with in-situ biasing, J. Phys. D 2023, 10.1088/1361-6463/accfa7. F
- V7 Jiang et al., Heavy ion radiation in the non-gate region, IEEE TNS 2025, 10.1109/tns.2025.3591512. A
- V8 Mace et al., Targeted heavy-ion radiation, JRERE 2020, scholar.afit.edu/facpub/688. A
- V9 Pearton et al., Review: ionizing radiation damage effects on GaN devices, ECS JSS 2016, 10.1149/2.0251602jss. P
- V10 Weaver et al., Radiation tolerance of AlGaN/GaN HEMTs, ECS JSS 2016, 10.1149/2.0281607jss. F
- V11 Bonaldo et al., TID effects at ultra-high doses, IEEE TNS 2023, 10.1109/TNS.2023.3237179. P
- V12 Patrick et al., Fundamental modeling of radiation effects, ECS 2014, ecs.confex.com/ecs/225/webprogram/Paper31096.html. A
- V13 Hu et al., Latent tracks in gallium nitride, NIM B 2025, 10.1016/j.nimb.2025.165855. S
- V14 Sequeira et al., Commun. Phys. 2021, 10.1038/s42005-021-00550-2. P
- V15 Kucheyev et al., Lattice damage produced in GaN, JAP 2004, 10.1063/1.1703826. A
- V16 Liang et al., Atomistic mechanisms of ion track formation, arXiv:2604.24288. P
- V17 Moskalets et al., Dynamical screening effects, arXiv:2602.14066. P
- V18 Janse van Vuuren et al., Tracks in nanocrystalline silicon nitride, Crystals 2022, 10.3390/cryst12101410. A
- V19 Li et al., Latent reliability degradation, amorphous HfO₂, IEEE EDL 2019, 10.1109/led.2019.2939002. A

**Ron review**
- R1 Hu et al., Failure mechanisms of AlGaN/GaN HEMTs irradiated by high-energy heavy ions with and without bias, Nucl. Sci. Tech. 36, 13 (2025), 10.1007/s41365-024-01567-2. A
- R4 Islam et al., Heavy ion irradiation effects on HEMT failure at off-state, Microelectron. Reliab. 2019, osti.gov/servlets/purl/1650173. F
- R5 = V8, plus slides SAND2019-3048C, osti.gov/servlets/purl/1639470. P
- R6 Rasel et al., J. Phys. D 57, 295102 (2024), 10.1088/1361-6463/ad3f29. A
- R7 Greenlee et al., Degradation mechanisms of 2 MeV proton irradiated HEMTs, APL 107, 083504 (2015), 10.1063/1.4929583. P
- R8 Anderson et al., Failure mechanisms, 2 MeV protons, CS MANTECH 2015, csmantech.org. F
- R9 Koehler et al., Surface passivation and current collapse of proton-irradiated HEMTs, CS MANTECH 2016, csmantech.org. F
- R10 Nakada et al., Single-event effect in GaN-HEMT, RIKEN APR 51 (2018), nishina.riken.jp/researcher/APR/APR051/pdf/192.pdf. F
- R11 Zhang et al., Single event effects of enhanced GaN HEMT devices, Micromachines 15, 950 (2024), 10.3390/mi15080950. P
- R12 = V9. R13 Joh, Physics of electrical degradation in GaN HEMTs, MIT thesis 2009, dspace.mit.edu/handle/1721.1/55116. A
- R14 Zanoni et al., MRS 2012, 10.1557/opl.2012.1137. A
- R15 Minetto et al., IEEE TED 68, 5003 (2021), 10.1109/TED.2021.3101182. A
- R16 Chang et al., TID effects in MIS-HEMTs, Nanomaterials 10, 2175 (2020), 10.3390/nano10112175. P
- R17 Double-gate HEMT and current collapse, Semiconductor Today 2013, reporting Yu et al., IEEE EDL 34, 217. P
- R18 Meneghini et al., Ron collapse in d-mode MIS-HEMTs, ICNS 2013, hdl.handle.net/11577/2718149. A
- R19 Armstrong & Kaplar, Deep level characterization, SAND2016-1978B, osti.gov/servlets/purl/1574639. P
- R20 Gao et al. 2014, MIT RJ-145. S
- R21 Kink papers: Chin. Phys. B 23, 027302 (2014); Appl. Phys. A 2020. S
- R22 MIT MTL annual report 2012, virtual-source access model. S
- R23 SweepMe wiki, wiki.sweep-me.net/wiki/SMU. P

Related: [[rad-model]], [[damage-region-map]], [[ron-increase]], [[trim]], [[critical-strike]].
