---
title: Literature for a candidate paper claim (stepped collapse, passivation, biased ions)
tags: [results, literature, radiation, rad-model]
date: 2026-11-24
source: review workflow wf_20e6b15b-290 (six readers, two fact-checkers, one critic; 84 source entries, about 81 distinct, 39 read in full; 48 claims fact-checked: 35 confirmed, 12 partly, 1 unverifiable, none wrong), two readers on a local Zotero library (64 PDFs, 29 papers read), own spot-checks; scratch copies under scratchpad/lit and scratchpad/zot
---
# Literature for a candidate paper claim

Purpose: what the literature says about the effects we model, how new each part of the idea is, and what would disprove it. It extends [[rad-literature]] and [[rad-literature-steps]], which were built mostly from abstracts. Full text was the aim this time. Access tags: [F] full text read, [P] partly, [A] abstract, [S] search snippet. No measured data appear here. Searches ran to November 2026.

**Candidate claim.** After heavy-ion irradiation under off-state bias, Id–Vd of SiN-passivated AlGaN/GaN HEMTs drops in steps; high-k passivated ones don't. Model: acceptor damage placed by the stress field (E⁴) plus discrete strikes in the gate–drain gap; each damaged spot in the 2DEG switches when about 0.5 V sits across it, because hot electrons fill local AlGaN traps; spots in series share Vd ([[step-mechanism]]).

## 1. Bottom line

1. **No source reports a multi-step Vd-triggered drop of Id, or any abrupt drop after irradiation.** The search is "we found none", not a proof. The closest results:
   - **El Fatimy 2010 [F] shows a single abrupt drop of about a factor 2 in unirradiated T-gate HEMTs, one of them with a field plate (Lg 0.25 µm, Lgd 3.15 µm, SiO2/SiNx, gate field plate 0.6 µm): about 21 → 9 mA near 3.0-3.4 V at Vgs −1 V, and about 12 → 6.5 mA near 1.5 V at Vgs −3 V for a second device without a plate.** The authors link it to plasma-wave emission. It is nearly our geometry and is the strongest rival (§4).
   - Mace 2019 [P] Fig. 28 shows an upward step near Vd 14 V after Ge irradiation, undiscussed; Ig changes slope at the same Vd, so an artefact can't be excluded.
   - Every other published post-irradiation output curve viewed is smooth in Vd (Lin 2022, Lei 2015, Rasel 2023/2024, Lin 2026; most as [F]).
2. **Bias plus ions is already reported to collapse the channel, smoothly.** Lin D. 2026 [F]: p-GaN HEMT, 1e7 Ta/cm² (LET 76.3 in Si), Vgs 0, 360 V (burnout about 390 V). Max IDsat 17.1 → 1.2 A (−92.9%); ions alone "nearly unchanged"; 360 V for 1000 s alone, slight loss. Damage is placed under the p-GaN gate, not in the gap, and the curves have no steps.
3. **The E⁴ law has no literature support.** Published field laws have other forms (hot-carrier rates, Chynoweth, thermochemical, stored energy). Off-state proton irradiation with a field did no more than grounded.
4. **The passivation contrast has two explanations that the literature doesn't separate:** field (simulations only) and process/interface (measured, protons, no irradiation).
5. **The width problem is the weakest point** (§4, §5): a 0.05 µm track cannot by itself block a 200 µm channel, and the 2D model spreads each strike over the full width.

## 2. Novelty, part by part

| Part of the claim | Verdict | Closest source |
|---|---|---|
| (a) Stepped Id–Vd drop after heavy ions | **Not found** (multi-step drop after any radiation). One abrupt Vd drop: close precedent, unirradiated | El Fatimy 2010 [F] (one ~2× drop); Lin 2026, Lin 2022 [F] (smooth, biased ions) |
| (b) SiN vs high-k contrast after heavy ions | **Not found**. Other radiation: close precedent, mixed sign | Chang 2023 [F] (protons: semiconductor part equal, dielectric part differs), Dalapati 2024 [S] (X-ray), Li 2021 [P] and Satoh/Hanawa 2015 (unirradiated) |
| (c) Field-placed, bias-dependent damage | Bias dependence **already reported**. E⁴ **not found** | Lin 2026 [F], Zhang 2024 [F]; Mayberry 2026 [F, preprint] uses stored energy |
| (d) Spots in series sharing Vd | Generic physics **close precedent**; in an irradiated FET **not found** | Xu & Teitsworth 2010 [P], Bonilla & Grahn 2005 [P] (superlattices, sawtooth) |
| (e) Hot-electron trap filling as trigger | Principle **already reported**; barrier traps switching at ~0.5 V in an Id–Vd sweep **not found** | Ridley & Watkins 1961 [A], Braga 2004 [A], Hu & Hashizume 2012 [F] (buffer) |

None of the parts is new alone. The multi-step drop, its passivation dependence and the combination are the possible novelty. The observation is stronger than the mechanism.

## 3. Evidence by topic

### 3.1 Heavy ions and on-state current
- **Lin 2022 [F]:** Ta 2.1 GeV, unbiased, 1e8-1e10. Collapse at 500 ns, (−8, 10) V, rose from 2.24% to 10.01% at 1e10; DC Idsat −14%, gm −8%. Gate leakage *fell* at 1e8-1e9. Traps 500 ns-10 µs. Smooth curves.
- **Lei 2015 [F]:** I, 1e10, −3 V/20 V with 12-22 mA flowing, so barely off. Idsat rose almost 40% near threshold (Vgs −2.5 V), the initial slope and gm fell (gm −13%), Vth −2.78 → −2.91 V (authors: holes in AlGaN), gate-lag 1% → 2%. "Dramatic" in the abstract means that 1% → 2%.
- **Kim 2026 [A]:** Ar and Kr, 1e7, unbiased: below 10% loss of Id and gm, slight Vth shift. Kr degraded gate leakage and breakdown more.
- **Rasel 2023/2024 [F]:** the "OFF" devices were unbiased (2024: pins grounded), not off-state stressed; ON was only 2 V / −2 V. Rasel 2023 says the *biased* device was more tolerant. [[rad-literature-steps]] read this the other way.
- **Single-ion sites exist at our fluence.** Kuboyama 2011 [F, Zotero]: off-state HEMTs, about 1e7/cm² per step, Kr (LET 30.6) damage from Vd 20 V; seven abrupt leakage steps with seven emission sites ("might correspond"), one visible at the drain-side gate edge; step 161-246 µA. Id and RF otherwise unchanged. Gray 2026 [P]: about six discrete permanent leakage steps at 50 V in one run. Yu 2026 [F, Zotero]: 1713 MeV Au, same chip: gate leakage × about 100 biased at 50 V, falls unbiased; no on-state data.
- **Counterexample:** Tallarico 2026 [F] (p-GaN, 200 V off-state, Xe/Ag/Kr, 1e6): Vth, Ron and gm unchanged, leakage only. Measured only *after* verified recovery, so it can't rule out recoverable collapse; breakdown fell for Xe (about 550 → 500 V).
- **Trap location:** ISPSD 2025 [A]: dynamic Ron degrades, static Ron doesn't, with electron traps near the drain in the GaN *buffer*. The GaN (not barrier) location is also argued by Patrick 2014/15 [F, Zotero] for protons at moderate densities.

### 3.2 Bias during irradiation
- Protons and X-rays: off-state drain bias is about the same as grounded for proton gm loss (Chen, Vanderbilt dissertation, [P]: below 0.05 V and 5% gm for both; semi-ON 0.25 V and 20%). Gate-only (−7 V, Vd 0) gives nearly the same X-ray Vth shift as full off-state (−263 vs −280 mV at 10 Mrad, negative, Ion up; Bonaldo 2023 [P]). That matters for the unbiased control with the gate at −10 V ([[see-plan]]): no heavy-ion gate-only study was found.
- Lin 2026 [F] is the one direct heavy-ion comparison with output curves at 1e7 (§1). It contradicts "bias does nothing"; it doesn't place the damage where we do.
- Field laws found: hot-carrier rate, lucky electron, Chynoweth, thermochemical, stored energy threshold (Mayberry 2026 [F], a preprint, vertical diodes). Over the 0.5-1 MV/cm range E⁴ is only a local slope (our estimate: 2 for energy density, 4-7 thermochemical, 11-34 Chynoweth). A 3C-SiC simulation finds a field *reduces* disorder [F, arXiv:1901.01307].

### 3.3 Passivation
- **Field route (simulations):** high-k lowers the drain-side gate-edge field (Hanawa/Satoh 2015 [F]). With a field plate the contrast shrinks at the plate edge: Kabemura 2018 [F] Fig. 6, at Vd 20 V the peak is about 1.4 MV/cm (εr 7) against 0.6 (εr 50), by eye, with a 0.3 µm plate, but the plate-edge peaks converge by 50-100 V. Kim 2024 [P]: T-gate with source plate, 5.16 → 3.83 MV/cm SiN → HfO2, at 500 V (E⁴ ratio about 3.3). None is at 28 V. Our own 28 V runs give SiN/HighK 8.8e5/5.1e5 V/cm at the head edge ([[see-plan]]), E⁴ ratio 9.
- **Process route (measured):** Koehler 2016 [F, Zotero]: 10 nm in-situ SiN under the PECVD SiN cuts the dynamic-Ron rise after protons from 2300% to 300% (Ron,dyn 4888 → 41.6 Ω·mm at 50 V); cause given as PECVD plasma damage. Two device types, so gate type and process are confounded. Also Li 2021 [P] (SiN vs AlON collapse without radiation), Yang 2021 [F] (Si-rich SiN), Yoon 2021 [F].
- **No difference expected:** proton displacement damage equal under HfO2 and Si3N4 (Chang 2023 [F]); SiN and AlN converge at high proton fluence (Gallagher 2017 [F]); sparse tracks in both dielectrics (coverage 1e-6 to 1e-5 at 1e7, our estimate).
- **Our decks differ only in permittivity, so the model cannot see the process route.**

### 3.4 Transients and width
- **The strike removes the gate-edge field and raises the drain-end field, in TCAD** (Zhang 2024 [F] Fig. 6b; Zerarka 2017 [F, Zotero] has the field falling everywhere because buffer traps empty; they disagree at the drain end). Our 28 V runs show the same pattern: a short rise of 11-19% at the head edge, then collapse in about 30 ps, with about 7e5 V/cm near the drain from 100 ps to 1 ns ([[see-plan]]).
- The static field map predicts where a strike couples (field-plate edge, Khachatrian 2019 [F], though its figure shows a broad maximum 2-3 µm away); it doesn't predict where hot carriers do damage.
- **Width.** TCAD tracks are 0.05-0.06 µm; nearly all studies are 2D slabs. Our arithmetic with the published disc-percolation threshold (filling 1.128): at 1e7/cm² a damaged radius of about 1.9 µm per ion is needed to block a sheet, against 0.3% coverage for 0.1 µm. Supporting the "small spots don't block" side: Sun 2014 [F] (about one 100 nm site per µm, no apparent Id loss, data not shown). Against it: a site can influence up to about a micron (surface chemistry, reader's report).
- Cester/Cimino (Si MOSFETs, SEDC2, [A]) is the closest "one ion collapses drain current", and the effect fades as W grows. The name clash should be cited.

### 3.5 Trap filling, levels and time constants
- Kink papers (Gao 2023 [F], Singh 2018 [F], Faqir 2010 [F, Zotero]) are *rises* on one sweep direction. In Faqir, barrier traps release electrons above a field, the opposite sign to our filling. A drop that is not a trap effect is published: Deng 2000 [F] (real-space transfer, peak/valley at most 1.5, Vg > 1.5 V).
- **Trap levels:** 0.17, 0.3 and 0.45 eV in electron-irradiated devices (Pearton 2015 [F, Zotero]), about 0.2 eV noise levels growing with protons (Vanderbilt theses [P]), O DX about 0.25 eV in AlGaN (Fleetwood 2022 [F, Zotero]), implanted GaN 0.40, 0.59, 0.74 eV (Kamiński 2024 [F, Zotero]). "Published levels are 0.5-0.98 eV" in [[rad-literature-steps]] is too narrow. But noise and interface energies are not level depths, and GaN and AlGaN levels do not share one depth (Lyons 2021 [F, Zotero]).
- **Emission problem (our estimate):** 0.30 eV with σ 1e-15 cm² empties in about 2 µs at 300 K, so a fill-only trap needs a metastable centre or a tiny cross-section, which makes capture slow (Ridley-Watkins warns that long time constants rule out short pulses).
- **Buffer rival:** Uren 2012 [F, Zotero]: 2.3e12 cm⁻² under mid-gate gives about +0.2 V Vth and current recovery with rising Vd, in pulsed measurements. It matches our +Vth and the creep, not steps.

## 4. Rivals and how to tell them apart

| Rival | Signature that separates it |
|---|---|
| **Device plus curve-tracer instability, self-excitation or plasma wave** (El Fatimy 2010 [F]; Knap 2004 [P]; Belhadj 1990 [A]). The strongest rival: unirradiated, same geometry class, abrupt, Vd-triggered | Steps move or vanish with cable, drain load, gate resistor or ferrites; RF on the drain; no trap-like dependence on pulse width, temperature or light. It must also explain why unirradiated and unbiased SiN parts on the same fixture don't step |
| Process/interface damage in SiN | A thin in-situ SiN or a different SiN recipe changes the collapse without changing the permittivity |
| Real-space transfer, transferred electrons | Smooth, one Vds window, needs high positive Vg |
| Buffer charging | Ron and Vth both move, very slow, depends on the carbon level |
| Self-heating | Scales with power, high Vds only |
| SMU range change or compliance | Steps at fixed current decades or limit values, gone on a fixed range |
| Random telegraph noise | Random in time, two fixed levels |
| Bias-only damage | Al-Mamun 2024 [F]: 48 h at −5 V/5 V gives 14-46% lower Idsat and twice the Ron without radiation. A bias-only control of the same duration is needed |

**Most informative experiment (no new irradiation):** an irradiated SiN device that steps and its unirradiated twin, in an RF-stabilised, Kelvin, fixed-range setup. Sweep up and down, first and repeated (about 100 sweeps), varying in turn cable or load, pulse width, temperature 25-125 °C and illumination. Next: SiN/high-k × (ions + bias, ions only, bias only). **Most informative simulation:** a 3D strike of finite width with realistic Poisson positions, output step height against spot radius ([[3d-plan]]).

## 5. What a referee attacks first (the critic's ranking)

1. Width and strike count: about 32 ions per 100 µm of gate in a 3.2 µm gap (our arithmetic); if each blocked the full width there would be tens of rows, not 2-3 steps. Steps come from hand-placed strikes.
2. No circuit-artefact exclusion.
3. Missing controls: same-device pre/post, bias only, ions only, unirradiated SiN and high-k.
4. E⁴ is a local slope with no literature exponent.
5. A fill-only 0.30 eV barrier trap against pulse timing, and the model's Te at the switch (550-700 K) against Monte Carlo electron temperatures (about 2800 K at 200 kV/cm, reader's report, not rechecked): if literature heating applied, undamaged regions would switch too.
6. SiN vs high-k attributed to permittivity rather than process.
7. A descending staircase against the sawtooth that series-NDR theory predicts; it needs latching.
8. Size of the effect at 1e7, against unbiased losses below 10%.

## 6. Corrections to the older notes

Checked against full text by the fact-checkers unless noted.

| Statement | Correction |
|---|---|
| [[rad-literature-steps]] bottom line item 4 and §1.5 ("rises, never drops") | Wrong: El Fatimy 2010 and Deng 2000 drop (unirradiated). Say "in the sources read" |
| Rasel 2023 "OFF worse than ON"; "fields increase susceptibility" | OFF meant no field, and the biased device was more tolerant. Only Rasel 2024 (protons, 2 V) and Lin 2026, Zhang 2024 support it |
| "No biased vs unbiased heavy-ion comparison with output curves" (gap 2, §1.3) | Lin 2026 does it at 1e7 (p-GaN, 360 V, gate region, smooth) |
| "Nobody works at 1e7" (gap 4, and the bottom line of [[rad-literature]]) | Lin 2026, Kim 2026 [A], Gray 2026 [P] and Chen 2026 [P] (Kr, p-GaN, leakage only) do, and Kuboyama 2011 gives the single-ion steps |
| "Published levels 0.5-0.98 eV, deeper than 0.30" (gap 6, trap level row) | Too narrow: see §3.5 |
| "The one published mechanism with a field threshold is Kaushik 2013"; "the only abrupt mechanism in a Vd sweep is D" | Too strong: Faqir 2010 and Gao 2023 give thresholds of other kinds; plasma-wave or circuit instability is another |
| Kuboyama 2011 listed as outside our regime (§2 H/I) | About 1e7 per step, 20 V for Kr, seven sites |
| [[rad-literature]]: "Uniform dose about 11 krad, far below the Mrad range where total-dose shifts are seen" | 3 krad(SiO2) X-ray gave −0.35 V (Schottky), −1 V (MOS) at Vgs −4 V (Sun 2013, via Fleetwood 2022). Negative and recovering, so it doesn't explain our shift, but the threshold is not Mrad |
| Dynamic Ron 21 → 4888 and R8 ("quasi-static"); "acceptor" | It is Koehler EDL 2016 (PECVD-SiN part, floating), donor-like traps, and the pulsed-0 V value 9.1 → 14.7 is not quasi-static |
| [[rad-literature]] "fields don't change carrier removal much" | Initial proton/electron statements only; Vth and gm are bias-dependent (Fleetwood 2022, Pearton 2021) |
| Islam 2019, Rasel: fluence/energy details | Islam: 1.5 MeV Au, ex situ, 6.5e13-e15; the 2.8 MeV lamella was an unbiased imaging test; off-state refers to the later electrical test |
| Sun et al., EDL 46, 813 (2025) as a GaN HEMT (topic brief, [[see-plan]]) | It is a β-Ga2O3 junction barrier diode; don't cite it as a HEMT precedent |

## 7. Not reached (library list)
Song 2024 (the only 3D GaN strike study found, 10.1063/5.0185373); Dalapati 2024 (HfO2 vs SiN X-ray collapse, 10.1016/j.apsusc.2024.161532); Hu 2025 and Hu 2018; Kinoshita 1985; Grupen 2019; Kaushik 2013 (direction of the change); Braga 2004; El Fatimy thesis; Cester 2004 (10.1109/TNS.2004.839203); Sonia 2006 (10.1109/TNS.2006.885006). Zhang Ka-band TED 2026 (10.1109/TED.2026.3678900) was seen only as a title.

## 8. References (access in brackets)
**Irradiated HEMTs.** Lin Z.-Z. 2022, Chin. Phys. B 31, 036103, 10.1088/1674-1056/ac11e4 [F]. Lei 2015, Chin. Phys. B 24, 056103, 10.1088/1674-1056/24/5/056103 [F]. Lin D. 2026, IEEE TED, 10.1109/TED.2026.3714370 [F]. Kim D.-S. 2026, JJAP, 10.35848/1347-4065/aec344 [A]. Rasel 2023, J. Phys. D 56, 305104 [F]; 2024, 57, 295102 [F]. Mace 2019, AFIT dissertation 2462 [P]. Islam 2019, Microelectron. Reliab. 102, 113493 [F]. Tallarico 2026, IEEE Access 14, 10.1109/ACCESS.2026.3735852 [F]. Gray 2026, IEEE TNS, 10.1109/TNS.2026.3750044 [P]. Kuboyama 2011, IEEE TNS 58, 2734, 10.1109/TNS.2011.2171504 [F, Zotero]. Yu 2026, pssa 223, e202500589, 10.1002/pssa.202500589 [F, Zotero]. Koehler 2016, IEEE EDL 37, 545, 10.1109/LED.2016.2537050 [F, Zotero]. Fleetwood 2022, IEEE TNS 69, 1105, 10.1109/TNS.2022.3147143 [F, Zotero]. Pearton 2015, 10.1149/2.0251602jss [F, Zotero, parts]. Weaver 2016, 10.1149/2.0281607jss [F, Zotero]. Patrick 2014/2015, 10.1149/06417.0035ecst, 10.1149/2.0181503jss [F, Zotero].
**Bias, fields, strikes.** Zhang 2024, APL 124, 082105, 10.1063/5.0185332 [F]. Zerarka 2017, IEEE TNS 64, 2242, 10.1109/TNS.2017.2710629 [F]. Khachatrian 2019, 10.1109/TNS.2019.2910493 [F] and 2018, 10.1109/TNS.2018.2885824 [F]. Sun H. 2014, 10.1016/j.microrel.2014.09.020 [F]. Mayberry 2026, engrXiv 7656 [F, preprint]. Chen, Vanderbilt dissertation 2016 [P]; Bonaldo 2023, 10.1109/TNS.2023.3237179 [P]. Wang 2023, 10.3390/mi14101948; Zhang 2024, 10.3390/mi15080950 [F]. Cester/Cimino (SEDC2), 10.1016/S0026-2714(03)00179-3 [A].
**Passivation.** Kabemura 2018, 10.1109/TED.2018.2857774 [F]; Komoto 2021 [F]; Hanawa 2015 and Satoh 2016 TechConnect [F]; Kim 2024, 10.3390/mi15091126 [P]; Chang 2023, 10.3390/nano13050898 [F]; Gallagher 2017, 10.1149/2.0151711jss [F]; Yoon 2021, 10.3390/mi12080864 [F]; Li 2021, 10.1109/TPEL.2020.3031680 [P]; Yang 2021, 10.1088/1361-6641/ac16c3 [F].
**Collapse and threshold-like features.** El Fatimy 2010, JAP 107, 024504, 10.1063/1.3291101 [F]. Dyakonov 2008, arXiv:0802.3780 [P]. Knap 2004, APL 84, 2331, 10.1063/1.1689401 [P]. Deng 2000, 10.1557/S1092578300004506 [F]. Braga 2004, 10.1063/1.1719262 [A]. Binder 2019, 10.1016/j.microrel.2019.113495 [A]. Gao 2023, 10.1109/TED.2023.3326781 [F]. Singh 2018, 10.1109/TED.2018.2860902 [F]. Kaushik 2013, 10.1109/TED.2013.2279158 [A]. Hu & Hashizume 2012, 10.1063/1.4704393 [F]. Faqir 2010, 10.1016/j.microrel.2010.07.020 [F, Zotero]. Uren 2012, 10.1109/TED.2012.2216535 [F, Zotero]. Kamiński 2024, 10.1038/s41598-024-65142-w [F, Zotero]. Lyons 2021, 10.1063/5.0041506 [F, Zotero, parts]. Zou 2023 review, 10.3390/mi14112044 [F, Zotero, parts].
**Series elements.** Xu & Teitsworth 2010, 10.1063/1.3475988 [P]. Bonilla & Grahn 2005, 10.1088/0034-4885/68/3/R03 [P]. Ridley & Watkins 1961, 10.1088/0370-1328/78/5/309 [A].
**Other.** Al-Mamun 2024, 10.1063/5.0179809 [F, stress sections]. ECS MA2026-01 1483, 10.1149/MA2026-01331483mtgabs [A]: a public abstract on collapse that grows with fluence and field after DC-biased irradiation; part of (c) is already disclosed there.

Related: [[rad-literature]], [[rad-literature-steps]], [[step-mechanism]], [[see-plan]], [[fp-contact-fix]], [[3d-plan]], [[rad-model]].
