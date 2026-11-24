---
title: Why the 28 V strike curves step
tags: [results, rad-model, strikes, mechanism]
date: 2026-11-19
source: progress.md 2026-11-19 (pre-fix marker 2026-11-20); HPG jobs radStepDiag 51998840, radStepDiag5b 52018703, meshChkLoad_m5fix 51939192; fact-checked by three independent agents (workflow wf_0a18b21d-f13)
---
# Why the 28 V strike curves step (each drop is one damaged spot switching)

**Pre-fix.** Every run here loaded a 28 V stress state saved with the old FP contact box, so during the stress the drain edge of the T-gate head sat near 0 V instead of −10 V. The mechanism and numbers below are pre-fix; the stress and the key series are being rerun ([[fp-contact-fix]]).

**Setup.** Diagnostic reruns of the [[step-search-28v]] cases with `vdCuts=1` ([[levers]]). SiN deck, 28 V stress damage (scale 1.5e18), Vg +1 V, hotEb 1.0 eV. Strikes are 6e18 (σ 40 nm) at y 0.8 / 1.6 / 2.4 µm with trap level 0.30 eV, except E_lev0.4_N2 (0.40 eV) and C_n8e18_N2 (8e18). Case labels (C_N0, A_N1, B_N2, A_N3, row A) and the meshes (library, m5fix) are defined in the Labels section of [[step-search-28v]].

**Runs and what they cut.**
- radStepDiag 51998840: library mesh, 0-3 strikes. Cuts along the channel at every Id-Vd point, 1 nm below the AlGaN/GaN interface (x 0.016 µm): filled traps, electrons, lateral field, TeTrap.
- radStepDiag5b 52018703: the four 5 nm ("m5fix") cases plus the library 1-strike case. Also cuts mid-barrier (x 0.008 µm).
- Barrier filling is seen directly at 10 of the 14 first switches. For the 4 library-only ones (C_N0, B_N2 ×2, A_N3) it is inferred from the 2DEG cut.
- The cuts don't change the curves: they are identical to the original runs to the last digit.
- Tools: read the cuts with `analysis/vdcuts.py`, tabulate the drops with `analysis/vdcutsDropTable.py`, plot with `analysis/plot_pocketVolts.py`.
- **Cut resolution:** FLOOXS's `print1d` samples on a plot grid of at most 500 points per direction, merging the closest pairs ([[flooxs-gotchas]]). The library mesh has 520 y lines and m5fix 554, so some 5 nm cells are sampled at ~10 nm in the cuts. Pocket voltages are integrals and robust, but peak fields and widths below ~10-20 nm are approximate.

## The mechanism

1. **Each damaged spot is a partly depleted "pocket" in the 2DEG.**
   - The damage on the GaN side (x 0.016) is completely filled at rest and stays constant through the sweep (IonAcceptor = TrapN).
   - The same damage in the AlGaN barrier is only partly filled at rest. Mid-barrier at Vd 0.1 it is 4-5e17 cm⁻³ at trap level 0.30 eV (8.5-9.8e17 at 0.40 eV), against ~6e18 of damage at a strike centre. At the AlGaN top (x 0.001) it is ~1% (5e16 of 6e18 under the y 0.8 strike).
   - The pockets are the stress band (y 0.45-0.72 µm, under the field plate between the T-gate head edge at 0.485 and the field-plate edge at 0.725; it switches at y 0.57-0.60) and one per strike.
2. **The pockets sit in series along the channel and share the drain voltage.** The voltage across a pocket is measured as the integral of |Ey| over its y range (stress 0.45-0.72, strikes 0.72-1.1, 1.45-1.85, 2.25-2.65 µm).
   - This overcounts slightly: |Ey| counts the pocket's own built-in barrier on both flanks. That already gives 0.13-0.24 V at Vd 0.1, against 0.006-0.012 V over undamaged stretches.
3. **Each first switch came once ~0.5 V sat across the pocket.**
   - The |Ey| integral was 0.46-0.59 V at every one of the 14 first switches with a drop of at least 8 mA/mm (6 on the library mesh, 8 on the 5 nm mesh).
   - Counting field reversals inside the pocket as negative gives 0.36-0.59 V.
   - Reaching 0.5 V is necessary but not always enough. With 2 strikes (library), the stress band holds 0.50-0.54 V from Vd 10.6 to 12 V without switching: TeTrap stays at 365-379 K and there is no runaway.
4. **What happens at the switch.**
   - As a pocket's voltage rises, the barrier traps over its drain flank fill gradually. When the drop starts they are already at 1.4-3.1e18, i.e. 27-73% of the rise at the peak cell.
   - The local-field electron temperature there (TeTrap, set by |∇Qfn|: [[hot-electron-capture]]) rises from ~330-370 K to 550-700 K. This lowers the trap level by hotEb·(1 − T/TeTrap).
   - During the 0.3-0.8 V of Vd that the drop takes, the fill front completes. Those cells reach full occupancy (3.3-4.5e18, 90-100% of the local damage) in a 10-35 nm band, 10-20 nm at the strike edges on the 5 nm mesh.
   - The 2DEG beneath falls 2-10× and the peak lateral field in the pocket rises 2-4× (about 1e5 → 2.4-4.1e5 V/cm).
   - Partial filling also happens without a drop. On the 5 nm E and C runs the y 0.8 pocket fills to 2.1-2.6e18 and stops there once the y 1.6 pocket switches.
   - TeTrap is computed from the local field, so the heating is not independent evidence. It is the model's field → capture → depletion loop.
5. **After it switches, a pocket takes most of any further drain voltage.** One strike, library mesh: the y 0.8 pocket goes from 0.52 V at Vd 1.9 to 1.35 V at 2.2 and 4.3 V at 6.1. Over the same switch the stress band's share falls from 0.44 to 0.29 V, and it reaches 0.5 V again only at Vd 5.9. That is what separates the steps.
6. **Second-stage drops** (library 1 strike, 10.0-10.8 V; 5 nm 8e18, 11.4-11.8 V) come from a pocket that has already switched and carries 6.0 and 7.3 V.
   - Its high-field region spreads toward the drain into nearly undamaged channel: n falls 2-10× at y 0.94 and 1.74, where TrapN is ~1e16.
   - Some extra fill happens in one core cell (y 0.81: 1.5 → 5.3e18; y 1.62: 4.6 → 6.1e18).

## What switches in the deliverable's row A (library mesh, `figures/rad/step28/diag/pocket_volts.png`)

| Strikes | Drops (≥ 8 mA/mm) | What switches |
|---|---|---|
| 0 | 1.6-2.0 V, 395 → 281 | stress band (0.52 V at 1.6 V) |
| 1 | 1.9-2.2 V, 388 → 283; 6.1-6.6 V, 401 → 348; 10.0-10.8 V, 398 → 222 | y 0.8 strike (0.52 V); stress band (0.59 V); the y 0.8 pocket's second stage (6.0 → 9.1 V across it) |
| 2 | 2.1-2.4 V, 379 → 371; 3.0-3.3 V, 390 → 307 | y 1.6 strike (0.54 V); y 0.8 strike (0.52 V) |
| 3 | 4.4-4.8 V, 389 → 324 | y 0.8 strike (0.52 V). The y 2.4 and y 1.6 pockets cross 0.5 V earlier (Vd 2.4 and 3.0 V). The y 2.4 crossing gives one 5 mA/mm dip (373 → 368 at 2.4-2.6 V); the y 1.6 crossing only flattens Id. |

- **The y 0.8 strike in every curve.** The first large drop in the 1-, 2- and 3-strike curves is the y 0.8 strike pocket switching each time. It switches at the same ~0.52 V across it but at Vd 1.9 / 3.0 / 4.4 V, because the strikes further out take a growing share of the drain voltage.
- **The stress band's drop disappears with 2 and 3 strikes.** With 2 strikes it reaches 0.5 V only at Vd 10.6 and doesn't switch (a 7.7 mA/mm dip at 10.8-11.3 V). With 3 strikes it never does (at most 0.43 V).
- **Switches and drops are not one-to-one.** Every drop of at least 8 mA/mm is one spot switching, but not every switch is a drop: in row A the far strikes' switches cost 0-8 mA/mm. So it is neither one drop per strike nor one drop per spot (3 strikes: three switches, one drop; 1 strike: two spots, three drops).
- **Drop size varies.** It depends on the spot, the strike density and the mesh, and is not yet understood. In row A the far strikes' switches cost under 10 mA/mm. With 8e18 strikes on the 5 nm mesh the y 1.6 strike's switch costs 106 mA/mm (263 → 156).
- **Order of switching.** In every case run, the pocket nearest the drain switched first (barrier-confirmed in 4 runs). The margin can be small: on the 5 nm E and C runs the y 0.8 pocket was filling alongside y 1.6 until y 1.6 switched. Much of the drain-side pockets' lead in |Ey| integral is already there at Vd 0.1. Why the drain side leads is not established.

## Why the steps move with the mesh

**What the 5 nm check mesh actually changes** (true node positions, from a VTK export of locally built meshes):
- m5fix is a clean 5 nm over y 0.64-0.96, where the library mesh has 4.8-19.6 nm (9.5-17.2, mean 13, at 0.76-0.90).
- Elsewhere the two meshes are the same, including 5 nm at y 1.6 and 2.4.
- So every m5fix comparison isolates the refinement at the y 0.8 strike.
- m10 is 10 nm uniform, so it is finer than the library at y 0.8 but coarser at 1.6 and 2.4.
- A cut-based spacing check suggested m5fix was coarser at y 1.6. That was the 500-point resampling of `print1d`, not the mesh.

**The first-switch threshold.** It agrees within 0.04 V for the three pockets run on both meshes (C_N0 stress band 0.52 / 0.53 V; A_N1 y 0.8 0.52 / 0.50 V; A_N1 stress band 0.59 / 0.55 V).

**The switched region.** After the y 0.8 switch it is about 22-35 nm wide (FWHM of |Ey| in the cuts) on both meshes. On the library mesh that is about 2 cells (spacing ~12 nm at y 0.84-0.87), and it holds a higher peak field and more voltage: 4.5e5 vs 3.6e5 V/cm and 1.93 vs 1.57 V at Vd 3.1.
- So on the 5 nm mesh the stress band reaches its threshold sooner (0.55 V at Vd 3.1 against 0.36 V) and switches at 3.1-3.6 V instead of 6.1-6.6 V.
- The y 0.8 drop itself shrinks from 105 to 20 mA/mm. The stress-band drop keeps its size (56 vs 53 mA/mm).

**The second-stage switch near 10.5 V doesn't happen on 5 nm, and the voltage share doesn't explain why.** The 5 nm y 0.8 pocket carries 5.76 V at Vd 10.0 (6.00 on the library mesh), passes 6 V at 10.4 and reaches 7.5 V at 12 V without switching. This is open.

## Corrected geometry, stress band only (2026-11-24, verified from the fpFixScale28/28b cuts)

SiN, stress damage only, fixed FP contact, per-Vd cuts (`vdCuts=1`, jobs 52385669 and 52585664), N0 5e17 to 7e17 cm⁻³:
- **The ∫|Ey| over the damaged band (y 0.45-0.72 µm) when the first drop starts is 0.57 / 0.56 / 0.51 / 0.46 / 0.46 V** for N0 5 / 5.5 / 6 / 6.5 / 7e17 (0.12-0.15 V already at Vd 0.1). So the ~0.5 V threshold seen on the old geometry holds on the corrected one for the stress band, over a scale range where the drop itself changes from 60 to 212 mA/mm. At 1e18 and 1.5e18, where the curve collapses, it is 0.41 and 0.45 V.
- At N0 6e17 the drop runs 398 → 266 mA/mm between 1.6 and 2.0 V. The GaN-side damage (5.3e18 cm⁻³) is full throughout; the barrier traps (x 0.008) at y 0.58 fill from 5.3e17 to 3.7e18, and the 2DEG there falls from 1.0e19 to 2.4e18.
- Max TeTrap in the band: 362 K at 1.6 V, 709 K at 2.0 V, 1313 K at 12 V.
- Not checked on the corrected geometry: discrete strikes (no cuts), the second-stage drops and the series order of switching.

## Open

- Drop size per switch (some ~100 mA/mm, some under 10).
- Why reaching ~0.5 V is sometimes not enough (2-strike stress band).
- Why the drain-side pocket switches first.
- Why the second-stage switch is missing on the 5 nm mesh.
- Whether the steps converge at 2.5 nm. The old-box 2.5 nm stress (meshChkStress2p5 52044407) was cancelled at Vd 20 on Nov 20; fixed-box 5 nm and 2.5 nm stresses are queued (fpFixMesh 52135538). The 5 nm m5fix B_N2 and A_N3 cases have no vdCuts run.

Related: [[step-search-28v]], [[hot-electron-capture]], [[trap-model]], [[rad-literature-steps]], [[fp-contact-fix]].
