---
title: Stress library (saved off-state stress states)
tags: [workflow, radiation, stress]
date: 2026-11-20
source: drivers/radIV.tcl (SaveAtBias, StructIn, StressInfo, CheckFpBox, the stress branch); sweeps/params_stressLib.txt, params_stressLibResume.txt, params_meshChkStress*.txt, params_fpFix*.txt; progress.md 2026-11-14 to 2026-11-20
---
# Stress library

The off-state stress solve (Vg -10 V, drain ramped to 28 V) is the slow part of a radIV post run. On the 93k-point strike mesh it climbs about 0.6-0.7 V/h, and the library's SiN stress needed about 47 h to reach 28 V. A saved state lets many damage variants share one stress: in radStressIO (2026-11-15, a 17 V SiN stress) the load run took 1 h 14 min against 9 h 07 min for the run that saved it, with identical Id-Vd, Vth, gm and peakN. Damage laws: [[damage-model]]. Levers: [[levers]].

## Levers (radIV, all off by default)

| Lever | What it does |
|---|---|
| `stressSave=<file>` | After the stress and the ramp back to rest, `struct outfile` writes the whole structure, plus `<file>.txt` with the stress settings (2026-11-14) |
| `stressSaveEvery` (V) | During the drain ramp, at every multiple of it, compute the stress fields and write the state at bias to `<stressSaveDir>/<stressSavePrefix>_Vd<Vd>.str.gz` plus `<...>.str.txt` (2026-11-15). Vd is printed as `%06.2f`, e.g. `sin_Vg-10_Vd028.00.str.gz`. `stressSavePrefix` "" = `tag`; `stressSaveDir` default "." |
| `stressLoad=<file>` | Build the deck, replace the structure with the file (a `.gz` is unpacked into the working directory first), re-issue the five contacts, start DevPsi/Qfn/Qfp from zero, skip the stress solve, then place damage as usual |
| `stressResume=<file>` | Continue a stress ramp from a state saved at bias: read its Vd from the settings file, restore its DevPsi/Qfn/Qfp, solve at (Vg_stress, that Vd), then ramp on in `stressStep` steps to `Vd_stress`. stressLoad and stressResume together stop with an error |
| `stressOnly 1` | Stop after the stress ramp (no ramp-down, damage or curves). A ramp that stalls first saves its last converged point, so it can be resumed. Ends with `RADIV DONE tag=<tag> (stress only)` |
| `stressStep`, `Vd_stressMin` | 1.0 V drain step (bisected on failure); in a full run a ramp that stops below 12 V is an error |

**Loading rules.**
- The mesh comes from the file. Mesh levers of the loading run (`meshY`, `yCoarse`, `bot2d`) are ignored; the generated load lines still carry the library's meshY.
- The settings file is checked: `Vd_stress`, `Vg_stress` and `deviceDeck` of the loading run must match it. `occSafe` and `meshY` are recorded but not checked.
- A load needs a damage lever (`useTraps`). With `stressSkip 1` the stress-skip branch runs first and zeroes the loaded fields.
- Written for the 2D decks. stressSaveEvery and stressResume were also checked on the 3D deck (2026-11-17: a 2 to 3 V resume matched the uninterrupted ramp; [[3d-plan]]).

**Settings file.** A state saved at bias carries one line: `stress file (at bias) written by tag=… deviceDeck=… Vg_stress=… Vd_stress=<Vd> field_at=<Vd> atBias=1 occSafe=… meshY=… fpBox=fixed|old`. The `stressSave` variant adds `Vd_reached`.

**FP box stamp (2026-11-20).** A saved state carries its own contacts (the `B FP Metal` lines in the .str file), so a state saved before the fix keeps the old FP contact box ([[fp-contact-fix]]). radIV now writes `fpBox=fixed|old` into every settings file. stressLoad and stressResume refuse a state whose box differs from the run's `fpBoxOld`, and a file without the entry counts as old. With the default `fpBoxOld 0` an old state is refused; set `fpBoxOld=1` only to reproduce a pre-fix run. Local smoke test: a fixed-box 1 V state loaded to RADIV DONE; the same load with `fpBoxOld=1` was refused.

**Checks of the machinery.** Local (SiN, 3 V): resuming from the 2 V state gave the same 3 V field (5.322858e5), and loading the 3 V state at bias gave the same peakN and Id-Vd as a normal 3 V run. HPG: radStressIO, above.

## States on HPG (`/blue/ee1/ianstafford/stress/`)

Not in the repo; each library state is about 13.7 MB gzipped. Paths: [[repo-locations]].

| Directory | Contents | Job | FP box |
|---|---|---|---|
| `sin_Vg-10/`, `hk_Vg-10/` | SiN and HighK decks, Vg -10 V, a state every 1 V to 84 V, library mesh | stressLib 51459840 (`params_stressLib.txt`). HighK finished in that job; SiN hit the 4-day limit and was resumed from its Vd 60 state (stressLibResume 51998839, `params_stressLibResume.txt`), completed to 84 V | old (pre-fix) |
| `meshchk/sin_m10/`, `meshchk/sin_m5fix/` | SiN, 28 V, the m10 and m5fix meshes | meshChkStress 51883722 | old (pre-fix) |
| `meshchk/sin_m2p5/` | SiN, 2.5 nm patches | meshChkStress2p5 52044407, cancelled at Vd 20 after 21.6 h | old, incomplete |
| `fpfix/sin_Vg-10/`, `fpfix/hk_Vg-10/` | Both decks, a state every 1 V to 28 V, library mesh, prefix `fpfix_<deck>_Vg-10` | fpFixStress 52134552 (`params_fpFixStress.txt`), running | fixed |
| `fpfix/meshchk/sin_m5fix/`, `fpfix/meshchk/sin_m2p5/` | SiN, 28 V, m5fix and 2.5 nm | fpFixMesh 52135538 (`params_fpFixMesh.txt`), queued 2026-11-20 | fixed |

- **Old library (pre-fix; being rerun, [[fp-contact-fix]]).** Rounds A-K, rad28strikeL, radStepDiag and one radStepDiag5 task loaded its states (28 V; round E also 24 and 30 V). meshChkLoad_m10 / m5fix, radStepM / M2 and the other radStepDiag5 tasks loaded the mesh-check states. The mesh check, [[step-mechanism]] and [[step-search-28v]] rest on these old-box states.
- **Fixed-box library.** fpFixLoad (19 tasks) loads the fixed 28 V states once fpFixStress saves them.
- **Other saved states.** rad28strike tasks 0 and 1 saved their own 28 V states with `stressSave` (`stress_sin28.str`, `stress_hk28.str` in the run's task directories); the other rad28strike tasks loaded them.

**Making or extending a library.** A stress-only line sets `stressOnly=1;stressSaveEvery=1.0;stressSaveDir=<dir>;stressSavePrefix=<prefix>;Vd_stress=28.0;stressStep=1.0;occSafe=1` on top of the rad baseline block, `radState=post`, the mesh (`meshY`, `deviceDeck`) and at least one damage lever. Without a damage lever `useTraps` is 0 and radIV skips the stress branch. The library lines carry the 28 V base-line damage levers (`params_fpFixStress.txt`); they don't change the stress solve, because TrapN stays ~0 until `DamageIn`. `occSafe 1` is needed above Vd ~17.7 V ([[levers]]). To continue a stalled or timed-out ramp, add `stressResume=<last state>` with the same directory and prefix (`params_stressLibResume.txt`). A load line sets `stressLoad=<state>` and the matching `Vd_stress`. Submit through `sweeps/radIV.slurm` ([[sweep-pattern]], [[hpg-workflow]]).

## Mesh

- **Library mesh.** `meshY={0.3 0.01 2.6 0.01 0.64 0.005 0.96 0.005 1.44 0.005 1.76 0.005 2.24 0.005 2.56 0.005}` on top of the deck: 10 nm over y 0.3-2.6 µm, with 5 nm patches around the strike sites at 0.8, 1.6 and 2.4. It has 93,080 points (179 x 520), the same for SiN and HighK.
- **True spacing.** From a VTK export of locally built meshes, the library has 520 y lines: 9.5-17.2 nm at y 0.76-0.90 and 5 nm at 1.6 and 2.4. The deck's rightFP line (y 0.725, 20 nm) breaks the 0.64-0.96 patch, so the strike at 0.8 sits on ~15 nm ([[levers]], meshY).
- **Check meshes.** m5fix adds helper lines at 0.72 and 0.73 (5 nm): 554 y lines, a clean 5 nm over 0.64-0.96, identical elsewhere. m10 is 10 nm uniform over 0.3-2.6 with helper lines at 0.715 / 0.735 (~64k points). m2p5 uses 2.5 nm patches with m5fix's helper lines (157k points).
- **print1d caveat.** `print1d` resamples to at most 500 points per direction. Spacings read from cuts are therefore wrong on these meshes, and the rows of `_cuts.txt` / `_vdcuts.txt` are not mesh nodes ([[flooxs-gotchas]]).
- **Cost of a mesh change.** The mesh is part of the state, so a new mesh needs a new stress. Estimates were ~22 h (m10), ~51 h (m5fix) and ~90 h (2.5 nm). In practice m5fix took about 24 h, and the 157k-point 2.5 nm stress reached Vd 20 in 21.6 h.
- **Refine before saving.** A strike variant loaded from a stress saved without refinement round the strike differs near the ~2 V drop (399 vs 426 mA/mm at 2.3 V, radStressIO `sin_load_g0.8` against radStrikeN). Save the stress on a mesh already refined at every strike position.

Related: [[levers]], [[damage-model]], [[step-search-28v]], [[fp-contact-fix]], [[flooxs-commands]], [[mesh]], [[drivers]].
