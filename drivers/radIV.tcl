# Pre/post-irradiation device characterisation: the main driver of the rad-model work since
# 2026-10-23 (written on branch explore/rad-model, merged to main 2026-11-04). Run per task by
# sweeps/radIV.slurm. Notes: kb/results/rad-model.md (the model and its history),
# kb/results/step-search-28v.md (28 V strike steps), kb/model/levers.md (levers),
# kb/model/damage-model.md (damage laws), kb/workflow/stress-library.md (saved stresses).
# Coordinates: x = depth below the AlGaN top (um; x < 0 is the passivation and metal above it),
# y = along the channel (um; gate centre at 0, drain side positive).
#
# Measurements (proc Measure), the same before and after irradiation:
#   transfer Id-Vg at Vd = Vd_lin (0.1 V), Vg Vg_hi -> Vg_lo (doIdVg);
#   output Id-Vd at Vg = Vg_out (+1 V), Vd 0 -> Vd_max (doIdVd);
#   then one more Id-Vd curve per entry of VgFam, in list order.
#
# Stages:
#   radState pre : trap-free device (calibration): build the deck, then Measure.
#   radState post: 1. stress state at the irradiation bias (Vg_stress, Vd_stress), by one of
#                     - a stress solve: gate ramp, drain ramp in stressStep steps (bisected on
#                       failure; a ramp that stops is accepted if its last full step is
#                       >= Vd_stressMin, and the fields are taken at the furthest converged Vd),
#                       stress fields Estress / EstressT / EstressNE, ramp back to rest;
#                       stressSave / stressSaveEvery write the state, stressOnly 1 stops after
#                       the ramp;
#                     - stressLoad=<file>: load a saved state (mesh and stress fields);
#                     - stressResume=<file>: continue a stress ramp from a state saved at bias;
#                     - stressSkip 1: no stress, only for damage that does not read the field;
#                  2. DamageIn at rest (Vg = Vd = 0): build TrapN from the damage levers and
#                     switch it in at scales 0 -> 1;
#                  3. Measure;
#                  4. damList (optional): repeat 2-3 for several damage settings after ONE
#                     stress, e.g.
#                       set damList {{d1 {damPeak 1e17 damM 2}} {d2 {damPeak 3e17 damM 3}}}
#                     each entry {suffix {lever value ...}} (damPeak/damM/damEref/damMax/damXmax/
#                     damY*/damIns*/Rgd/hotTau); outputs get the prefix ${tag}_<suffix>, and the
#                     traps are reset (ThawTraps) between entries. insTrapSign must be set before
#                     the model is sourced, i.e. as a task lever, not in damList.
#
# Damage (post), summed into the acceptor trap density TrapN (cm^-3) unless noted:
#   - field damage (damPeak > 0): N = min(damMax, damPeak*(E/damEref)^damM*(n/damNref)^damNexp)
#     for 0 <= x <= damXmax and damYmin <= y <= damYmax, E = the stress field picked by damField
#     (lat |dpsi/dy|, tot |grad psi|, ne n*|dpsi/dy| normalised), n = Elec at stress
#     (damNexp 0 = field only);
#   - dam2*: a second law of the same form (dam2M 0 = a uniform site); dam3*: a uniform y window;
#   - damIns*: fixed charge in the passivation (damInsXmin <= x < 0), sign insTrapSign;
#   - damSites {ymin ymax xmin xmax N}: uniform boxes;
#   - damGauss / damGaussF {y x sigma N}: Gaussian strike sites, optionally field-scaled
#     (gaussFieldM; damGaussF always, with gaussFieldMF);
#   - 3D only (deviceDim 3, rfdevice3d.tcl): ion tracks damTube {y z sigma xmin xmax N}
#     (field-scaled with trackFieldM) and damRod {y x sigma zmin zmax N}.
#   Not in TrapN: surfCharge (fixed AlGaN/passivation charge, cm^-2, negative = acceptor-like,
#   read by the model file), mobDamFac (low-field mobility factor in a window), and Rgd, a
#   lumped gate-drain leakage (ohm*mm, 0 = none; the localized leakage paths ion strikes leave,
#   seen as steps in the irradiation monitor, are 3D, not in a 2D cut): Id_ext = Id_dev + (Vd - Vg)/Rgd.
# Traps fill but never empty after the rest point (fill-only, CaptureTraps), with a hot-electron
# FillStep at each Id-Vd point; emitRest releases a fraction at rest before each Id-Vd curve.
# Trap level and capture use this driver's own defaults (trapLevel 0.30, hotEb 1.0,
# hotTau 1e-14), not the model file's; trapEn and trapShape are set here, not by the caller.
#
# Outputs (prefix $tag; with damList, ${tag}_<suffix> for the damage-dependent files):
#   <tag>_summary.txt             every stage's settings and peaks; ends with "done";
#   <tag>_IdVg.csv                Vg, Id_dev, Id_ext (mA/mm);
#   <tag>_IdVd.csv                Vd, Id_dev, Id_ext (mA/mm), peak Te (K);
#   <tag>_IdVdG<Vg>.csv           one per VgFam entry, same columns;
#   <tag>_cuts.txt                Estress, EstressT, EstressNE, TrapN and IonAcceptor along y at
#                                 x = -0.04, -0.01, 0.001, 0.016 um (IonAcceptor at x >= 0 only;
#                                 3D at z = 0);
#   <tag>_vdcuts.txt              vdCuts 1: cuts at every Id-Vd point (see VdCuts);
#   <tag>_stressDiag.txt          stressDiag 1: one extra stress step and its Newton changes;
#   <stressSave>, <stressSave>.txt                 stressSave: state at rest after the stress;
#   <stressSaveDir>/<prefix>_Vd<Vd>.str.gz + .str.txt   stressSaveEvery / stressOnly: state at bias.
# Log: "RADIV DONE tag=<tag>" at the end. Failures print "RAMP GAVE UP", "IDVG GAVE UP",
# "IDVD GAVE UP" or "DAMAGE solve failed", or write "<tg> measurement failed" / "<tg> damage
# failed" to the summary (damList only); a failed stress, stress ramp-down or (without damList)
# damage stops the run with a Tcl error. A curve that gave up still ends in RADIV DONE, so check
# the log for the failure lines too.
#
# Layout of this file, in the order the run uses it:
#   1. levers, grouped by stage, all ahead of the model file; 2. model, deck, saved stress states, device init;
#   3. currents, solves and bias ramps; 4. stress; 5. damage (DamageIn); 6. measurement (Measure); 7. the run.

#======================================================================================================================
# 1. Levers. Each has an info-exists default here, ahead of `source GaN_modelfile_masterD`: the model file reads
#    mobModel, eTemp, trapEn, trapShape, trapLevel, trapWidth, hotEb, hotTau and insTrapSign when it is sourced.
#    All levers with their meaning: kb/model/levers.md.
#======================================================================================================================

# --- 1a. run and solver
if {![info exists radState]}  { set radState pre }
if {![info exists tag]}       { set tag $radState }
if {![info exists deviceDeck]} { set deviceDeck rfdevice.tcl }
if {![info exists fpBoxOld]} { set fpBoxOld 0 }  ;# 1 = the pre-2026-11-20 FP contact box (covers part of the T-gate head); 0 = fixed
# 3D slice (2026-11-12, kb/model/3d-plan.md): deviceDim 3 with deviceDeck=rfdevice3d.tcl. The contact current is
# divided by the slice width W3d (a deck lever).
if {![info exists deviceDim]}  { set deviceDim 2 }
if {![info exists mobModel]}  { set mobModel field }
if {![info exists eTemp]}     { set eTemp 0 }
if {![info exists dampValue]} { set dampValue 0.05 }   ;# Newton DampValue of DevPsi (GaN, AlGaN, Nitride) and of Qfn, Qfp (GaN)
if {![info exists retryDepth]} { set retryDepth 6 }    ;# bisection depth of a failed bias step (proc Reach)
# qfnAbs (no default; unset = the model's 1e-2): Qfn Abs.Error in GaN/AlGaN for the whole run, set before device init
# in section 2.

# --- 1b. measurements (proc Measure)
if {![info exists Vd_lin]}    { set Vd_lin 0.1 }
if {![info exists Vg_hi]}     { set Vg_hi 1.0 }
if {![info exists Vg_lo]}     { set Vg_lo -4.0 }
if {![info exists Vg_step]}   { set Vg_step 0.05 }
if {![info exists Vg_out]}    { set Vg_out 1.0 }
if {![info exists Vd_max]}    { set Vd_max 10.0 }
if {![info exists Vd_step]}   { set Vd_step 0.25 }
if {![info exists doIdVg]}    { set doIdVg 1 }
if {![info exists doIdVd]}    { set doIdVd 1 }
# VgFam: extra Id-Vd curves, one per Vg in the list, in that order (like the measured
# family; fill-only traps keep their state between curves), to <tag>_IdVdG<Vg>.csv. {} = none.
if {![info exists VgFam]}     { set VgFam {} }
if {![info exists noRampBack]} { set noRampBack 0 }    ;# 1: stop after the last curve, no ramp back to rest (nothing is measured after it; ignored with VgFam or damList)
# vdCuts (2026-11-19, default 0): at every Id-Vd point write cuts along y, 1 nm below the AlGaN/GaN interface
# (x 0.016 um), of the filled traps (IonAcceptor), the electron density, the lateral field and the hot-electron
# temperature to <tag>_vdcuts.txt, plus IonAcceptor and TeTrap mid-barrier (x 0.008 um, labels *_x0.008), to see which damage fills at each drop.
if {![info exists vdCuts]} { set vdCuts 0 }

# --- 1c. stress (post): irradiation bias, stress solve and saved stress states (kb/workflow/stress-library.md)
if {![info exists Vg_stress]} { set Vg_stress -10.0 }
if {![info exists Vd_stress]} { set Vd_stress 28.0 }
if {![info exists stressStep]} { set stressStep 1.0 }   ;# V, drain step of the stress ramp (bisected on failure)
if {![info exists Vd_stressMin]} { set Vd_stressMin 12.0 } ;# accept a stress Vd down to this if the solve fails above
# stressSkip 1: no stress solve, for damage that doesn't use the stress field (damSites,
# surfCharge, a uniform dam2/dam3 site). The stress fields are then ~0. 0 = old behaviour.
if {![info exists stressSkip]} { set stressSkip 0 }
# stressSave / stressLoad (2026-11-14, kb/flooxs/flooxs-commands.md): reuse one off-state stress for many
# damage variants. stressSave=<file>: after the stress and the ramp back to rest, write the whole structure
# (struct outfile) plus <file>.txt with the stress settings. stressLoad=<file>: build the deck, replace the
# structure with the file (mesh, Estress fields), skip the stress solve, then place damage as usual. The mesh
# comes from the file, so mesh levers of the loading run are ignored; the stress settings must match by
# design (checked against <file>.txt where possible). 2D decks only. "" = off (old behaviour).
if {![info exists stressSave]} { set stressSave "" }
if {![info exists stressLoad]} { set stressLoad "" }
# Stress library (2026-11-15). stressSaveEvery (V, 0 = off): during the stress drain ramp, at every Vd that is a
# multiple of it, compute the stress fields and write the state at bias to
# <stressSaveDir>/<stressSavePrefix>_Vd<Vd>.str.gz plus <...>.str.txt (Vd_stress = that Vd). Such a file serves
# stressLoad (damage placed from that Vd) and stressResume. stressResume=<file>: continue a stress ramp from a state
# saved at bias. stressOnly 1: stop after the stress ramp (no ramp-down, damage or curves); a ramp that stalls
# saves its last converged state first, so it can be resumed. Off by default.
if {![info exists stressSaveEvery]}  { set stressSaveEvery 0.0 }
if {![info exists stressSaveDir]}    { set stressSaveDir "." }
if {![info exists stressSavePrefix]} { set stressSavePrefix "" }
if {![info exists stressResume]}     { set stressResume "" }
if {![info exists stressOnly]}       { set stressOnly 0 }
# stressDiag 1: after the stress ramp stops, try one more drain step and write the
# fields and their Newton changes along cuts to <tag>_stressDiag.txt (then restore)
if {![info exists stressDiag]} { set stressDiag 0 }
if {![info exists stressDiagStep]} { set stressDiagStep 0.25 } ;# V, extra step tried by stressDiag

# --- 1d. damage laws (post), summed into TrapN by DamageIn (section 5). Formulas and the studies that used each
#     law: kb/model/damage-model.md. damField picks the stress field F: lat = |dpsi/dy| (default), tot = |grad psi|,
#     ne = Elec*|dpsi/dy| at stress normalised to its semiconductor peak (use damEref 1).
# field damage, first site: N = min(damMax, damPeak*(F/damEref)^damM) for 0 <= x <= damXmax, damYmin <= y <= damYmax
if {![info exists damPeak]}   { set damPeak 0.0 }     ;# cm^-3 at E = damEref
if {![info exists damEref]}   { set damEref 1.0e6 }   ;# V/cm
if {![info exists damM]}      { set damM 2.0 }
if {![info exists damMax]}    { set damMax 1.0e19 }
if {![info exists damXmax]}   { set damXmax 0.05 }    ;# um below the AlGaN top
if {![info exists damYmin]}   { set damYmin -1.0e3 }  ;# um; y window of the field damage and of damIns*;
if {![info exists damYmax]}   { set damYmax 1.0e3 }   ;#   default = whole device. The final model sets damYmin 0.30 (no field damage at the gate edge)
if {![info exists damField]}    { set damField lat }
# dam2* (2026-10-25): a second semiconductor damage law of the same form as the first,
#   N = min(damMax, dam2Peak*(E/dam2Eref)^dam2M) for 0 <= x <= dam2Xmax, dam2Ymin <= y <= dam2Ymax,
# with its own field (dam2Field), peak, exponent and window. dam2M 0 makes it a uniform, field-independent site:
# the final model (kb/results/rad-model.md) uses it for fixed acceptors in the AlGaN under the gate (dam2Peak 5e17,
# y -0.125..0.125, dam2Xmax 0.014). The y defaults (0.65..1.0) are from its first use, a second
# ion-strike site toward the drain. dam2Peak 0 = none (old behaviour). dam2Eref was set only by radFinal,
# radFinal2 and radPhys1 (the n*E second site, 2026-10-25).
if {![info exists dam2Peak]}  { set dam2Peak 0.0 }
if {![info exists dam2M]}     { set dam2M 0.0 }
if {![info exists dam2Ymin]}  { set dam2Ymin 0.65 }
if {![info exists dam2Ymax]}  { set dam2Ymax 1.0 }
if {![info exists dam2Field]} { set dam2Field "" }   ;# "" = same field/Eref as the first site
if {![info exists dam2Eref]}  { set dam2Eref "" }    ;# V/cm; "" = damEref
if {![info exists dam2Xmax]}  { set dam2Xmax "" }    ;# depth of the second site (um); "" = damXmax
# damSites (2026-11-04): any number of uniform acceptor sites, each {ymin ymax xmin xmax N}
# (um, um, um below the AlGaN top, um, cm^-3), summed into TrapN. {} = none (old behaviour).
if {![info exists damSites]}  { set damSites {} }
if {![info exists damGauss]} { set damGauss {} }   ;# {y x sigma N} list: Gaussian acceptor sites (um, cm^-3), semiconductor only; {} = none
# gaussFieldM (2026-11-18): damGauss strike damage times (field/damEref)^m from the stored stress field (the same
# field as damField), capped at damMax: a strike leaves dense damage only where the field was high during the biased
# irradiation (field-driven defect generation; kb/results/rad-literature-steps.md). 0 = off (old behaviour).
if {![info exists gaussFieldM]} { set gaussFieldM 0.0 }
# damGaussF (2026-11-18, default {} = off): a second {y x sigma N} strike list that is always field-scaled,
# N * (field/damEref)^gaussFieldMF (capped at damMax), alongside an unscaled damGauss list (gaussFieldM 0), so one run
# can mix field-scaled strikes near the gate with plain strikes further out.
if {![info exists damGaussF]}    { set damGaussF {} }
if {![info exists gaussFieldMF]} { set gaussFieldMF 4.0 }   ;# field exponent of the damGaussF strikes
# 3D ion tracks (deviceDim 3, rfdevice3d.tcl). damTube: Gaussian columns along the depth, {y z sigma xmin xmax N}
# (um, cm^-3), e.g. ion tracks built from TRIM (analysis/genRad3d.py). trackFieldM: tube damage times
# (Estress/damEref)^m, capped at damMax (bias dependence inside a track); 0 = none.
if {![info exists damTube]}    { set damTube {} }
if {![info exists trackFieldM]} { set trackFieldM 0.0 }
# damRod (2026-11-17, 3D): ion tracks along the gate width ("into the page" of the 2D cross-section), each
# {y x sigma zmin zmax N} (um, cm^-3): Gaussian in (y, x) of width sigma centred at (y, x), uniform from zmin to
# zmax, semiconductor only (x >= 0). zmin 0 / zmax W3d spans the slice, which with reflecting walls is the 2D
# damGauss site {y x sigma N}; shorter rods cover part of the width. {} = none.
if {![info exists damRod]}     { set damRod {} }

# --- 1e. trap level and hot-electron capture. These are this driver's own defaults (the late-onset set of
#     kb/results/late-onset-search.md, also the trap-sensitivity baseline), not the model file's; the model file
#     reads them when it is sourced.
if {![info exists trapLevel]} { set trapLevel 0.30 }
if {![info exists trapWidth]} { set trapWidth 0.1 }
if {![info exists hotEb]}     { set hotEb 1.0 }
if {![info exists hotTau]}    { set hotTau 1.0e-14 }
if {![info exists fillIters]} { set fillIters 4 }    ;# FillStep at each Id-Vd point: Te <-> solve iterations,
if {![info exists fillRelax]} { set fillRelax 0.5 }  ;#   and the under-relaxation of TeTrap in each

# --- 1f. legacy levers, kept so old params files reproduce. Each entry names the params files
#     (sweeps/params_<name>.txt) that set the lever, with the date the file was added.
# stressQfnDamp, stressQfnAbs: no effect. They changed the Qfn DampValue and Abs.Error in GaN and AlGaN for the
# stress drain ramp only, but FLOOXS reads those pdb values only when it builds the solver (at device init), so the
# change was ignored; the two pdbSetDouble lines were removed on 2026-11-21. Use qfnAbs.
# radQDsmoke (stressQfnDamp, 2026-10-26), stressAbs1 (stressQfnAbs, 2026-10-28).
if {![info exists stressQfnDamp]} { set stressQfnDamp 0.1 }
if {![info exists stressQfnAbs]} { set stressQfnAbs 1.0e-2 }
# stressNoHoles 1 (Ian, 2026-10-26): solve the off-state stress bias without holes
# (Qfp frozen far above the bands so Hole ~ 0; restored and re-solved at rest before
# damage/measurement). Holes are negligible off-state; this was meant to remove the minority-Qfp
# divergence near Vdg ~ 27 V so the stress can reach Vd_stress, but the stress still stopped near 17 V
# with the same fields (kb/results/rad-model.md). 0 = old behaviour.
# Holes are removed only above stressNoHolesX (um below the AlGaN top); deeper, Qfp is frozen
# at its rest value 0 (the Fe buffer needs its equilibrium holes). 0 = freeze at 0 everywhere.
# radNHsmoke (2026-10-26), stressDiag2 (2026-10-28).
if {![info exists stressNoHoles]} { set stressNoHoles 0 }
if {![info exists stressNoHolesX]} { set stressNoHolesX 0.1 }
# damNexp, damNref: the first site also scales with (Elec/damNref)^damNexp at stress (hot-electron rate ~ n*E^m);
# damNexp 0 = field only (old behaviour). radPhys1 (2026-10-25).
if {![info exists damNexp]}   { set damNexp 0.0 }
if {![info exists damNref]}   { set damNref 1.0e17 }
# dam3* (2026-10-26): uniform damage in a y window (a discrete ion-strike site) for 0 <= x <= damXmax; 0 = none.
# Dropped from the model on 2026-11-11. radFinal6, radFinal8 (2026-10-26), radFinal9-11 (2026-10-27), radEB1 and
# radEB2 (2026-11-09), radFine (the 2026-11-05 study the file now holds), fpFixEB1 and fpFixEB1p (2026-11-20, the
# fixed-FP-box reruns of radEB1).
if {![info exists dam3Peak]}  { set dam3Peak 0.0 }
if {![info exists dam3Ymin]}  { set dam3Ymin 1.0 }
if {![info exists dam3Ymax]}  { set dam3Ymax 1.6 }
# damIns* (2026-10-24): fixed charge in the passivation, damInsXmin <= x < 0 (um above the AlGaN top), density from
# the field there at the stress bias: N = min(damMax, damInsPeak*(E/damInsEref)^damInsM), in the damYmin..damYmax
# window, charge sign insTrapSign (-1 = trapped electrons). damInsField picks the field: lat = |dpsi/dy|, any other
# value |grad psi| (default tot). radIns (2026-10-24), radFam, radRon, radVth, radVth2 (2026-11-04); damInsEref and
# damInsField were never set by a params file.
if {![info exists damInsPeak]}  { set damInsPeak 0.0 }  ;# 0 = none (old behaviour)
if {![info exists damInsEref]}  { set damInsEref 1.0e6 }
if {![info exists damInsM]}     { set damInsM 2.0 }
if {![info exists damInsXmin]}  { set damInsXmin -0.05 } ;# um; -0.05 = the 50 nm SiN under the HfO2
if {![info exists damInsField]} { set damInsField tot }
if {$damInsPeak > 0.0 && ![info exists insTrapSign]} { set insTrapSign -1 }
# low-field mobility factor in a window (with mobDamFac set, GaN.tcl multiplies by the
# data field MobDam). Unset = old behaviour. radRon (2026-11-04).
if {![info exists mobDamYmin]} { set mobDamYmin -1.0e3 }
if {![info exists mobDamYmax]} { set mobDamYmax 1.0e3 }
if {![info exists mobDamXmax]} { set mobDamXmax 0.05 }
# emitRest: radEmit, radEmit2 (2026-11-05), radEmit3 (2026-11-07).
if {![info exists emitRest]} { set emitRest 0.0 }  ;# fraction of the captured charge released at rest before each Id-Vd curve
# damList: several damage settings after one stress (see the header). radDam1, radDam2 (2026-10-23), radPost, radWin
# (2026-10-24), radFit1 (2026-10-25) and the Oct 24 radFine (commit 0fbf0ce). The stress library (stressSave /
# stressLoad) does the same job now.
if {![info exists damList]}   { set damList {} }
# Rgd: lumped gate-drain leakage (ohm*mm, 0 = none), Id_ext = Id_dev + (Vd - Vg)/Rgd. No committed params file sets it.
if {![info exists Rgd]}       { set Rgd 0.0 }

# --- 1g. checks, and settings derived from the levers (trapEn and trapShape are set here whatever the caller gave)
if {$stressLoad ne "" && $stressResume ne ""} { error "stressLoad and stressResume together" }
# useTraps: any damage lever set (2026-11-20: damGaussF added; a damGaussF-only run used to get no traps at all)
set useTraps [expr {$radState eq "post" && ($damPeak > 0.0 || $damInsPeak > 0.0 || $dam2Peak > 0.0 || $dam3Peak > 0.0 || [llength $damList] > 0 || [llength $damSites] > 0 || [llength $damGauss] > 0 || [llength $damGaussF] > 0 || [llength $damTube] > 0 || [llength $damRod] > 0)}]
set trapEn $useTraps
set trapShape field

#======================================================================================================================
# 2. Model and deck. With stressLoad / stressResume a saved state then replaces the deck's structure. Device init.
#======================================================================================================================
if {![info exists modelDir]} {
    if {[file exists GaN_modelfile_masterD]} { set modelDir . } elseif {[file isdirectory model]} { set modelDir model } else { set modelDir [file join [file dirname [info script]] .. model] }
}
source [file join $modelDir GaN_modelfile_masterD]
source [file join $modelDir $deviceDeck]

# Saved stress states. <file> is a struct outfile (.str, or .str.gz); beside it, <file>.txt (for a .gz, the name
# without .gz plus .txt) holds one line of the stress settings, which a loading run checks.
# struct infile for a .str or .str.gz file (a .gz is unpacked into the working directory first)
proc StructIn {f} {
    if {[string match *.gz $f]} {
        set tmp [file join [pwd] [file rootname [file tail $f]]]
        exec gzip -dc $f > $tmp
        struct infile=$tmp
        file delete $tmp
    } else {
        struct infile=$f
    }
}
# the settings file written beside a saved state ("" if none)
proc StressInfo {f} {
    set b [expr {[string match *.gz $f] ? [file rootname $f] : $f}]
    if {![file exists $b.txt]} { return "" }
    set c [open $b.txt]; set t [read $c]; close $c
    return $t
}
# the end of every settings line: occSafe, meshY and the FP contact box of the saving run
proc StateStamp {} {
    return "occSafe=[expr {[info exists ::occSafe] ? $::occSafe : 0}] meshY=[expr {[info exists ::meshY] ? [join $::meshY ,] : {none}}] fpBox=[expr {$::fpBoxOld ? {old} : {fixed}}]"
}
proc WriteStateInfo {path line} {
    set c [open $path w]
    puts $c $line
    close $c
}
# FP contact box of a saved state (the state file carries its own contacts). Settings files written before the
# 2026-11-20 fix have no fpBox= entry and hold the old box, which also covers part of the T-gate head.
proc CheckFpBox {what info} {
    set st [expr {[regexp {fpBox=(\S+)} $info -> v] ? $v : "old"}]
    set want [expr {$::fpBoxOld ? "old" : "fixed"}]
    if {$st ne $want} { error "$what: state has the $st FP contact box, this run expects $want (fpBoxOld=$::fpBoxOld; kb/results/fp-contact-fix.md)" }
}
# Refuse a saved state stressed at another bias, built with another deck or with the other FP contact box.
# what = stressLoad (also checks Vd_stress) or stressResume (continues from the file's Vd_stress).
proc CheckStateInfo {what info} {
    global Vg_stress Vd_stress deviceDeck
    if {$what eq "stressLoad"} {
        if {[regexp {Vd_stress=(\S+)} $info -> v] && abs($v - $Vd_stress) > 1e-9} { error "stressLoad: file stressed at Vd_stress=$v, this run has $Vd_stress" }
        if {[regexp {Vg_stress=(\S+)} $info -> v] && abs($v - $Vg_stress) > 1e-9} { error "stressLoad: file stressed at Vg_stress=$v, this run has $Vg_stress" }
    } else {
        if {[regexp {Vg_stress=(\S+)} $info -> v] && abs($v - $Vg_stress) > 1e-9} { error "$what: file at Vg_stress=$v, this run has $Vg_stress" }
    }
    if {[regexp {deviceDeck=(\S+)} $info -> v] && $v ne $deviceDeck} { error "$what: file built with $v, this run has $deviceDeck" }
    CheckFpBox $what $info
}

set loadFile [expr {$stressLoad ne "" ? $stressLoad : $stressResume}]
if {$loadFile ne ""} {
    # the 2D decks and rfdevice3d.tcl use the same contact names and current expressions (re-issued below)
    if {![file exists $loadFile]} { error "stressLoad/stressResume: no file $loadFile" }
    StructIn $loadFile
    # struct infile clears the device setup: the contact biases of the 2D decks again
    contact name=G current=(Hole_Nitride-Elec_Nitride) voltage supply=0.0
    contact name=B current=(Hole_GaN-Elec_GaN) voltage supply=0.0
    contact name=D current=(Hole_GaN-Elec_GaN) voltage supply=0.0
    contact name=S current=(Hole_GaN-Elec_GaN) voltage supply=0.0
    contact name=FP voltage supply=0.0
    # Initialize resets the solution; keep the saved one for stressResume
    if {$stressResume ne ""} { foreach v {DevPsi Qfn Qfp} { sel z=$v name=${v}Res } }
    # A state saved at a high stress bias has DevPsi of tens of volts near the drain; Initialize computes carrier
    # densities from it with Qfn = 0 and overflows (exp(38.7*30), "computed a nan or infinite", rad28strikeL
    # 51762900). Start from zero potentials, as a freshly built deck does.
    foreach v {DevPsi Qfn Qfp} { sel z=0.0 name=$v }
}
if {[info exists mobDamFac]} {
    sel z=1.0-(1.0-$mobDamFac)*(x>=0.0)*(x<=$mobDamXmax)*(y>=$mobDamYmin)*(y<=$mobDamYmax)+1.0e-30*(1.0+x*x) name=MobDam
}
foreach m {GaN AlGaN Nitride} { pdbSetDouble $m DevPsi DampValue $dampValue }
pdbSetDouble GaN Qfn DampValue $dampValue
pdbSetDouble GaN Qfp DampValue $dampValue

# qfnAbs: Qfn Abs.Error (V) in GaN/AlGaN for the whole run (solver tolerance; model
# default 1e-2). FLOOXS reads Abs.Error/Rel.Error/DampValue only when it builds the
# solver (first solve after device init), so it has to be set here. In the fully
# depleted region under the gate Qfn does not affect the solution and Newton's updates
# there wander by 1e-3..4e-2 V; with 1e-2 (~1e-5 V effective at updateLimit 1e-3) the
# off-state stress cannot converge above Vd ~17 V (job 48125435).
if {[info exists qfnAbs]} { foreach m {GaN AlGaN} { pdbSetDouble $m Qfn Abs.Error $qfnAbs } }
Initialize
device init

#======================================================================================================================
# 3. Currents, solves and bias ramps
#======================================================================================================================
proc IdDev {} {
    set i [expr {abs([contact name=D sol=Qfn flux]) * 1.0e6}]
    if {$::deviceDim == 3} { set i [expr {$i / $::W3d}] }
    return $i
}
proc IdExt {vd vg} {
    set id [IdDev]
    if {$::Rgd > 0.0} { set id [expr {$id + ($vd - $vg) / $::Rgd * 1.0e3}] }
    return $id
}
proc SaveState {} {
    if {$::useTraps} { sel z=TrapFrozen name=TFsave; sel z=TeTrap name=TEsave }
    device store
}
proc RestoreState {} {
    device restore
    if {$::useTraps} { sel z=TFsave name=TrapFrozen; sel z=TEsave name=TeTrap }
}
# One solve at the present bias and data fields; a failed solve restores the state before it. 1 = converged.
proc SolveOK {} {
    SaveState
    if {[catch {device}]} { RestoreState; return 0 }
    return 1
}
# One solve at contact c = v; fill = 1 runs the hot-electron FillStep.
proc TryBias {c v fill} {
    if {[catch {
        contact name=$c supply=$v
        device
        if {$fill && $::useTraps} { set ::te [FillStep $::fillIters $::fillRelax] }
    }]} { return 0 }
    set ::lastOK($c) $v
    return 1
}
# Reach contact c = v from the converged vPrev, bisecting on failure.
proc Reach {c vPrev v depth fill} {
    SaveState
    if {[TryBias $c $v $fill]} { return 1 }
    puts "RETRY $c $vPrev -> $v failed (depth $depth)"
    RestoreState
    contact name=$c supply=$vPrev
    if {$depth <= 0} { return 0 }
    set mid [expr {0.5 * ($vPrev + $v)}]
    if {![Reach $c $vPrev $mid [expr {$depth - 1}] $fill]} { return 0 }
    return [Reach $c $mid $v [expr {$depth - 1}] $fill]
}
# Ramp contact c from a to b in steps of at most st (plain solves).
proc Ramp {c a b st} {
    set n [expr {max(1, int(ceil(abs($b - $a) / $st - 1e-9)))}]
    set prev $a
    for {set i 1} {$i <= $n} {incr i} {
        set v [expr {$a + ($b - $a) * $i / double($n)}]
        if {![Reach $c $prev $v $::retryDepth 0]} { puts "RAMP GAVE UP $c at $v"; return 0 }
        set prev $v
    }
    return 1
}
# One cut of the selected field to channel c: the header line, then print1d at the given position(s), or
# "{ cut failed }" if print1d fails.
proc Cut {c hdr args} {
    puts $c $hdr
    if {[catch {puts $c [print1d {*}$args]}]} { puts $c "{ cut failed }" }
}

#======================================================================================================================
# 4. Stress (post): the state at the irradiation bias, by a stress solve, a loaded state, or none (stressSkip)
#======================================================================================================================
# stress fields from the present solution; returns the n*E peak used for normalising EstressNE
proc StressFields {} {
    sel z=abs(dot(DevPsi,y*1e-4)) name=Estress
    sel z=sqrt(dot(DevPsi,DevPsi)) name=EstressT
    # n*E at stress, normalised to its peak in the semiconductor (damField ne)
    sel z=Elec name=ElecStress
    sel z=Elec*Estress name=EstressNE
    set neMax [expr {max([lindex [peak GaN] 1], [lindex [peak AlGaN] 1])}]
    sel z=EstressNE/$neMax name=EstressNE
    return $neMax
}
# write the state at the present stress bias (stressSaveEvery, stressOnly)
proc SaveAtBias {d} {
    global stressSaveDir stressSavePrefix tag deviceDeck Vg_stress sf
    StressFields
    set p [expr {$stressSavePrefix eq "" ? $tag : $stressSavePrefix}]
    file mkdir $stressSaveDir
    set b [file join $stressSaveDir [format "%s_Vd%06.2f.str" $p $d]]
    struct outfile=$b
    WriteStateInfo $b.txt "stress file (at bias) written by tag=$tag deviceDeck=$deviceDeck Vg_stress=$Vg_stress Vd_stress=$d field_at=$d atBias=1 [StateStamp]"
    exec gzip -f $b
    sel z=Estress
    puts $sf "stress state saved at Vd=$d to $b.gz peakElat(GaN)=[lindex [peak GaN] 1]"
    flush $sf
}
# stressSave: write the state at rest after the stress (dS = last full drain step, dReal = Vd of the fields)
proc SaveAtRest {dS dReal} {
    global stressSave tag deviceDeck Vg_stress Vd_stress sf
    struct outfile=$stressSave
    WriteStateInfo $stressSave.txt "stress file written by tag=$tag deviceDeck=$deviceDeck Vg_stress=$Vg_stress Vd_stress=$Vd_stress Vd_reached=$dS field_at=$dReal [StateStamp]"
    puts $sf "stress saved to $stressSave"
}
# stressDiag: from the converged drain bias dS try one more step, write the fields and their Newton changes along
# cuts to <tag>_stressDiag.txt, then restore the state at dS
proc StressDiagWrite {dS} {
    global stressDiagStep tag
    sel z=Qfn name=QfnPrev
    sel z=DevPsi name=PsiPrev
    sel z=Elec name=ElecPrev
    SaveState
    contact name=D supply=[expr {$dS + $stressDiagStep}]
    set ok [expr {![catch {device} msg]}]
    sel z=abs(Qfn-QfnPrev) name=dQfn
    sel z=abs(DevPsi-PsiPrev) name=dPsi
    set c [open ${tag}_stressDiag.txt w]
    puts $c "# stressDiag: converged Vd=$dS, attempt Vd=[expr {$dS + $stressDiagStep}] ok=$ok"
    foreach fld {dQfn dPsi QfnPrev PsiPrev ElecPrev Econd Elec Hole Qfn Qfp DevPsi} {
        sel z=$fld
        foreach xc {0.001 0.008 0.016 0.03 0.2 1.0 3.0 6.0} { Cut $c "# $fld along y at x = $xc" xv=$xc }
        foreach yc {-0.6 0.0 0.2 0.4 0.6 1.0 2.0 3.0} { Cut $c "# $fld along x at y = $yc" yv=$yc }
    }
    close $c
    RestoreState
    contact name=D supply=$dS
}
# 1 if a damage law reads the stored stress field (2026-11-20: field-scaled strikes and tracks added)
proc NeedsStressField {} {
    global damPeak damInsPeak damInsM dam2Peak dam2M damList damGauss gaussFieldM damGaussF damTube damRod trackFieldM
    return [expr {$damPeak > 0.0 || ($damInsPeak > 0.0 && $damInsM != 0.0) || ($dam2Peak > 0.0 && $dam2M != 0.0) || [llength $damList] > 0
        || ([llength $damGauss] > 0 && $gaussFieldM != 0.0) || [llength $damGaussF] > 0
        || (([llength $damTube] > 0 || [llength $damRod] > 0) && $trackFieldM != 0.0)}]
}
# stressSkip 1: stress fields ~0, no stress solve
proc StressSkipped {} {
    global sf
    if {[NeedsStressField]} { error "stressSkip with a damage law that needs the stress field" }
    foreach f {Estress EstressT EstressNE ElecStress} { sel z=1.0e-30*(1.0+x*x) name=$f }
    puts $sf "stress skipped"
}
# stressLoad: the stress fields came with the loaded state (section 2); check and report them
proc StressLoaded {} {
    global stressLoad sf
    if {[catch {sel z=Estress}]} { error "stressLoad: $stressLoad has no Estress field" }
    puts $sf "stress loaded from $stressLoad"
    set info [StressInfo $stressLoad]
    if {$info ne ""} { puts -nonewline $sf $info }
    CheckStateInfo stressLoad $info
    puts $sf "stress (loaded) peakElat(GaN)=[lindex [peak GaN] 1] at [lrange [peak GaN] 2 3] peakElat(AlGaN)=[lindex [peak AlGaN] 1]"
}
# The stress solve: gate ramp to Vg_stress (or stressResume), drain ramp in stressStep steps to Vd_stress, the
# stress fields at the furthest converged Vd, ramp back to rest. stressOnly ends the run after the drain ramp.
proc StressSolve {} {
    global stressNoHoles stressNoHolesX stressResume stressStep stressSaveEvery stressOnly stressDiag stressSave
    global Vg_stress Vd_stress Vd_stressMin retryDepth tag sf
    if {$stressNoHoles} {
        solution name=Qfp nosolve
        sel z=50.0*(x<$stressNoHolesX)+1.0e-12*(1.0+x*x) name=Qfp
        if {![SolveOK]} { error "no-holes rest solve failed" }
        puts $sf "stress without holes above x=$stressNoHolesX um (Qfp frozen: +50 V there, 0 below)"
    }
    if {$stressResume ne ""} {
        set info [StressInfo $stressResume]
        if {![regexp {Vd_stress=(\S+)} $info -> vR]} { error "stressResume: no Vd_stress in the settings file of $stressResume" }
        CheckStateInfo stressResume $info
        foreach v {DevPsi Qfn Qfp} { sel z=${v}Res name=$v }
        contact name=G supply=$Vg_stress
        contact name=D supply=$vR
        if {![SolveOK]} { error "stressResume: solve at Vg=$Vg_stress Vd=$vR failed" }
        puts $sf "stress resumed from $stressResume at Vd=$vR"
        flush $sf
    } elseif {![Ramp G 0.0 $Vg_stress 0.5]} { error "stress gate ramp failed" }
    # The off-state solve stops converging near Vdg ~ 27 V (minority quasi-Fermi
    # levels in the depleted AlGaN, job 47311016). Use the highest converged Vd if it
    # is at least Vd_stressMin; the damage law's scale absorbs the field magnitude.
    set dS [expr {$stressResume ne "" ? $vR : 0.0}]
    set ::lastOK(D) $dS
    # drain targets: multiples of stressStep, then Vd_stress itself if it isn't one (2026-11-13)
    set dList {}
    for {set d [expr {$dS + $stressStep}]} {$d <= $Vd_stress + 1e-9} {set d [expr {$d + $stressStep}]} { lappend dList $d }
    if {[llength $dList] == 0 || abs([lindex $dList end] - $Vd_stress) > 1e-9} { lappend dList $Vd_stress }
    foreach d $dList {
        if {![Reach D $dS $d $retryDepth 0]} { break }
        set dS $d
        if {$stressSaveEvery > 0.0 && abs($d / $stressSaveEvery - round($d / $stressSaveEvery)) < 1e-6} { SaveAtBias $d }
    }
    # A failed Reach leaves the device at its furthest converged bisection point, not at dS
    # (2026-11-13: the old final runs stopped at 17.66 V and were labelled 17.0). Report it.
    set dReal $::lastOK(D)
    if {$stressOnly} {
        # the state is at dReal (the furthest converged point); keep it for stressResume if not saved yet
        if {abs($dReal - $dS) > 1e-9 || $stressSaveEvery <= 0.0} { SaveAtBias $dReal }
        puts $sf "stress only: target $Vd_stress, last step $dS, last converged Vd=$dReal"
        puts $sf "done"
        close $sf
        puts "RADIV DONE tag=$tag (stress only)"
        exit
    }
    if {$dS < $Vd_stressMin} { error "stress drain ramp failed at $dS" }
    if {$stressDiag} { StressDiagWrite $dS }
    set neMax [StressFields]
    puts $sf "stress n*Elat peak $neMax at [lrange [peak GaN] 2 3]"
    sel z=Estress
    puts $sf "stress Vg=$Vg_stress Vd=$dS (target $Vd_stress, field taken at Vd=$dReal) peakElat(GaN)=[lindex [peak GaN] 1] at [lrange [peak GaN] 2 3] peakElat(AlGaN)=[lindex [peak AlGaN] 1]"
    flush $sf
    if {![Ramp D $dS 0.0 1.0]} { error "stress drain ramp-down failed" }
    if {![Ramp G $Vg_stress 0.0 0.5]} { error "stress gate ramp-down failed" }
    if {$stressNoHoles} {
        sel z=0.0+1.0e-12*(1.0+x*x) name=Qfp
        solution name=Qfp solve
        if {![SolveOK]} { error "holes back: rest solve failed" }
        puts $sf "holes restored at rest"
    }
    if {$stressSave ne ""} { SaveAtRest $dS $dReal }
}

#======================================================================================================================
# 5. Damage (post): TrapN from the damage levers, switched in at rest (Vg = Vd = 0)
#======================================================================================================================
# Pieces of the sel expressions (strings in FLOOXS's expression syntax):
# the stored stress field for a damField / dam2Field value: tot EstressT, ne EstressNE, anything else Estress
proc StressFieldName {kind} {
    return [expr {$kind eq "tot" ? "EstressT" : ($kind eq "ne" ? "EstressNE" : "Estress")}]
}
# (q/ref)^m, written exp(m*log(q/ref+1e-30))
proc PowerOf {q ref m} { return "exp($m*log($q/$ref+1.0e-30))" }
# min(a, damMax), written 0.5*(a+damMax-|a-damMax|)
proc CapMax {a} { return "0.5*($a+$::damMax-abs($a-$::damMax))" }
# a Gaussian of width sg centred at (u0, v0) in the coordinates u, v
proc Gauss2 {u u0 v v0 sg} { return "exp(-(($u-$u0)*($u-$u0)+($v-$v0)*($v-$v0))/(2.0*$sg*$sg))" }

# Sum a {y x sigma N} strike list (semiconductor only) into the data field sum, one strike per sel, and write each
# strike to the summary as "<tg> <label> y=... N=...".
proc StrikeSum {sum strikes label tg} {
    sel z=0.0*x name=$sum
    foreach g $strikes {
        lassign $g y0 x0 sg ng
        sel z=$sum+$ng*[Gauss2 y $y0 x $x0 $sg]*(x>=0.0) name=$sum
        puts $::sf "$tg $label y=$y0 x=$x0 sigma=$sg N=$ng"
    }
}
# Multiply the data field sum by (fld/damEref)^m and cap it at damMax (field-scaled strikes and tracks).
proc ScaleByField {sum fld m} {
    sel z=$sum*[PowerOf $fld $::damEref $m] name=$sum
    sel z=[CapMax $sum] name=$sum
}
# The TrapN expression (cm^-3) for the present damage levers, in the order of kb/model/damage-model.md. Sums over
# many sites are built in data fields (SiteSum, GaussSum, GaussFSum, TubeSum, RodSum), one site per sel, because
# FLOOXS's parser has a fixed buffer; each site goes to the summary.
proc DamageExpr {tg} {
    global damPeak damM damEref damMax damXmax damYmin damYmax damField damNexp damNref
    global dam2Peak dam2M dam2Ymin dam2Ymax dam2Field dam2Eref dam2Xmax dam3Peak dam3Ymin dam3Ymax
    global damInsPeak damInsM damInsEref damInsXmin damInsField
    global damSites damGauss gaussFieldM damGaussF gaussFieldMF damTube trackFieldM damRod sf
    set fld [StressFieldName $damField]
    # field damage, first site (damPeak 0 adds zero)
    set n "($damPeak*[PowerOf $fld $damEref $damM])"
    if {$damNexp != 0.0} { set n "($n*[PowerOf ElecStress $damNref $damNexp])" }
    set n "([CapMax $n])*(x>=0.0)*(x<=$damXmax)*(y>=$damYmin)*(y<=$damYmax)"
    if {$dam2Peak > 0.0} {
        set f2 $fld
        if {$dam2Field ne ""} { set f2 [StressFieldName $dam2Field] }
        set e2 [expr {$dam2Eref eq "" ? $damEref : $dam2Eref}]
        set n2 "($dam2Peak*[PowerOf $f2 $e2 $dam2M])"
        set x2 [expr {$dam2Xmax eq "" ? $damXmax : $dam2Xmax}]
        set n "$n+([CapMax $n2])*(x>=0.0)*(x<=$x2)*(y>=$dam2Ymin)*(y<=$dam2Ymax)"
    }
    if {$dam3Peak > 0.0} {
        set n "$n+$dam3Peak*(x>=0.0)*(x<=$damXmax)*(y>=$dam3Ymin)*(y<=$dam3Ymax)"
    }
    if {$damInsPeak > 0.0} {
        set fi [expr {$damInsField eq "lat" ? "Estress" : "EstressT"}]
        set ni "($damInsPeak*[PowerOf $fi $damInsEref $damInsM])"
        set n "$n+([CapMax $ni])*(x<0.0)*(x>=$damInsXmin)*(y>=$damYmin)*(y<=$damYmax)"
    }
    if {[llength $damSites] > 0} {
        sel z=0.0*x name=SiteSum
        foreach site $damSites {
            lassign $site y0 y1 x0 x1 ns
            sel z=SiteSum+$ns*(x>=$x0)*(x<=$x1)*(y>=$y0)*(y<=$y1) name=SiteSum
            puts $sf "$tg site y=$y0..$y1 x=$x0..$x1 N=$ns"
        }
        set n "$n+SiteSum"
    }
    if {[llength $damGauss] > 0} {
        StrikeSum GaussSum $damGauss gauss $tg
        if {$gaussFieldM != 0.0} {
            ScaleByField GaussSum $fld $gaussFieldM
            sel z=GaussSum
            puts $sf "$tg gauss damage times ($fld/$damEref)^$gaussFieldM: peak [lindex [peak GaN] 1] at [lrange [peak GaN] 2 3]"
        }
        set n "$n+GaussSum"
    }
    if {[llength $damGaussF] > 0} {
        StrikeSum GaussFSum $damGaussF gaussF $tg
        ScaleByField GaussFSum $fld $gaussFieldMF
        sel z=GaussFSum
        puts $sf "$tg gaussF damage times ($fld/$damEref)^$gaussFieldMF: peak [lindex [peak GaN] 1] at [lrange [peak GaN] 2 3]"
        set n "$n+GaussFSum"
    }
    if {[llength $damTube] > 0} {
        sel z=0.0*x name=TubeSum
        foreach t $damTube {
            lassign $t y0 z0 sg x0 x1 nt
            sel z=TubeSum+$nt*[Gauss2 y $y0 z $z0 $sg]*(x>=$x0)*(x<=$x1) name=TubeSum
            puts $sf "$tg tube y=$y0 z=$z0 sigma=$sg x=$x0..$x1 N=$nt"
        }
        if {$trackFieldM != 0.0} {
            ScaleByField TubeSum $fld $trackFieldM
            puts $sf "$tg tube damage times ($fld/$damEref)^$trackFieldM"
        }
        set n "$n+TubeSum"
    }
    if {[llength $damRod] > 0} {
        sel z=0.0*x name=RodSum
        foreach r $damRod {
            lassign $r y0 x0 sg z0 z1 nr
            sel z=RodSum+$nr*[Gauss2 y $y0 x $x0 $sg]*(x>=0.0)*(z>=$z0)*(z<=$z1) name=RodSum
            puts $sf "$tg rod y=$y0 x=$x0 sigma=$sg z=$z0..$z1 N=$nr"
        }
        set n "$n+RodSum"
    }
    return $n
}
# <tg>_cuts.txt: the stress fields, TrapN and the filled traps (IonAcceptor, x >= 0 only) along y
proc DamageCuts {tg} {
    global deviceDim
    set c [open ${tg}_cuts.txt w]
    foreach fld {Estress EstressT EstressNE TrapN IonAcceptor} {
        sel z=$fld
        foreach xc {-0.04 -0.01 0.001 0.016} {
            if {$xc < 0.0 && $fld eq "IonAcceptor"} { continue }
            if {$deviceDim == 3} {
                Cut $c "# $fld along y at x = $xc, z = 0" xv=$xc zv=0.0
            } else {
                # the one print1d in this driver without a catch: a failed 2D cut here stops the run
                puts $c "# $fld along y at x = $xc"; puts $c [print1d xv=$xc]
            }
        }
    }
    close $c
}
# Switch the damage in at rest (Vg = Vd = 0) for the present damage levers: TrapN = s*N for s = 0 ... 1, one solve
# each; then record the filled charge (CaptureTraps) and write the cuts. Returns 0 if a solve failed.
proc DamageIn {tg} {
    global damPeak damM damEref damField damNexp damNref damXmax damYmin damYmax
    global dam2Peak dam2M dam2Field dam2Eref dam2Ymin dam2Ymax dam3Peak dam3Ymin dam3Ymax
    global damInsPeak damInsM damInsEref damInsField damInsXmin sf
    ThawTraps
    set n [DamageExpr $tg]
    foreach s {0.0 0.01 0.03 0.1 0.3 0.6 1.0} {
        sel z=$s*($n)+1.0e-30*(1.0+x*x) name=TrapN
        if {![SolveOK]} { puts "DAMAGE solve failed at scale $s"; return 0 }
    }
    sel z=TrapN
    puts $sf "$tg damPeak=$damPeak damM=$damM damEref=$damEref damField=$damField damNexp=$damNexp damNref=$damNref damXmax=$damXmax damY=$damYmin..$damYmax peakN(GaN)=[lindex [peak GaN] 1] at [lrange [peak GaN] 2 3] peakN(AlGaN)=[lindex [peak AlGaN] 1]"
    if {$dam3Peak > 0.0} { puts $sf "$tg dam3Peak=$dam3Peak dam3Y=$dam3Ymin..$dam3Ymax" }
    if {$dam2Peak > 0.0} {
        puts $sf "$tg dam2Peak=$dam2Peak dam2M=$dam2M dam2Field=$dam2Field dam2Eref=$dam2Eref dam2Y=$dam2Ymin..$dam2Ymax"
    }
    if {$damInsPeak > 0.0} {
        puts $sf "$tg damInsPeak=$damInsPeak damInsM=$damInsM damInsEref=$damInsEref damInsField=$damInsField damInsXmin=$damInsXmin insTrapSign=$::insTrapSign peakN(Nitride)=[lindex [peak Nitride] 1] at [lrange [peak Nitride] 2 3]"
    }
    CaptureTraps
    DamageCuts $tg
    return 1
}

#======================================================================================================================
# 6. Measurement (the same before and after irradiation)
#======================================================================================================================
# vdCuts 1: cuts at one Id-Vd point, appended to <tg>_vdcuts.txt
proc VdCuts {tg d} {
    set c [open ${tg}_vdcuts.txt a]
    foreach {lab ex} {IonAcceptor IonAcceptor Elec Elec Ey "abs(dot(DevPsi,y*1.0e-4))" TeTrap TeTrap} {
        sel z=$ex
        Cut $c "# Vd=$d $lab" xv=0.016
    }
    # the AlGaN barrier (x 0.008 um, mid-barrier): its damage traps are nearly empty at rest and fill with hot electrons
    foreach lab {IonAcceptor TeTrap} {
        sel z=$lab
        Cut $c "# Vd=$d ${lab}_x0.008" xv=0.008
    }
    close $c
}
# One Id-Vd curve at gate voltage vg, from rest and back, to file fn.
proc IdVdCurve {tg vg fn} {
    global Vd_max Vd_step retryDepth useTraps te emitRest
    if {$useTraps && $emitRest > 0.0} {
        # cold electrons at rest: a stale hot TeTrap would refill the traps at the next capture
        ResetTe
        sel z=(1.0-$emitRest)*TrapFrozen+1.0e-30*(1.0+x*x) name=TrapFrozen
        if {![SolveOK]} { puts "emitRest solve failed"; return 0 }
    }
    if {![Ramp G 0.0 $vg 0.1]} { return 0 }
    if {$useTraps} { CaptureTraps }
    set f [open $fn w]
    puts $f "0.0, [IdDev], [IdExt 0.0 $vg], 300.0"
    set dPrev 0.0
    set n [expr {int(round($Vd_max / $Vd_step))}]
    for {set i 1} {$i <= $n} {incr i} {
        set d [expr {$i * $Vd_step}]
        if {![Reach D $dPrev $d $retryDepth 1]} { puts "IDVD GAVE UP at Vd=$d"; break }
        set dPrev $d
        puts $f "$d, [IdDev], [IdExt $d $vg], $te"
        flush $f
        puts "IDVD $tg Vg=$vg Vd=$d Id=[IdDev] peakTe=$te"
        if {$::vdCuts} { VdCuts $tg $d }
    }
    close $f
    if {$::noRampBack && [llength $::VgFam] == 0 && [llength $::damList] == 0} { return 1 }
    # back to rest for the next curve or damage setting
    if {![Ramp D $dPrev 0.0 0.5]} { return 0 }
    if {![Ramp G $vg 0.0 0.1]} { return 0 }
    return 1
}
proc Measure {tg} {
    global doIdVg doIdVd Vd_lin Vg_hi Vg_lo Vg_step Vg_out VgFam useTraps retryDepth
    if {$doIdVg} {
        if {![Ramp D 0.0 $Vd_lin 0.05]} { return 0 }
        if {![Ramp G 0.0 $Vg_hi 0.1]} { return 0 }
        if {$useTraps} { CaptureTraps }
        set f [open ${tg}_IdVg.csv w]
        set gPrev $Vg_hi
        set n [expr {int(round(($Vg_hi - $Vg_lo) / $Vg_step))}]
        for {set i 0} {$i <= $n} {incr i} {
            set g [expr {$Vg_hi - $i * $Vg_step}]
            if {$i > 0 && ![Reach G $gPrev $g $retryDepth 0]} { puts "IDVG GAVE UP at Vg=$g"; break }
            if {$useTraps} { CaptureTraps }
            set gPrev $g
            puts $f "$g, [IdDev], [IdExt $Vd_lin $g]"
            flush $f
            puts "IDVG $tg Vg=$g Id=[IdDev]"
        }
        close $f
        if {![Ramp G $gPrev 0.0 0.1]} { return 0 }
        if {![Ramp D $Vd_lin 0.0 0.05]} { return 0 }
    }
    if {$doIdVd} {
        if {![IdVdCurve $tg $Vg_out ${tg}_IdVd.csv]} { return 0 }
    }
    foreach vg $VgFam {
        if {![IdVdCurve $tg $vg ${tg}_IdVdG$vg.csv]} { return 0 }
    }
    return 1
}

#======================================================================================================================
# 7. The run: stress and damage (post), measurements
#======================================================================================================================
set te 300.0
set sf [open ${tag}_summary.txt w]
if {$radState eq "post"} {
    if {[info exists surfCharge]} { puts $sf "surfCharge $surfCharge" }
    if {$useTraps && $stressSkip} {
        StressSkipped
    } elseif {$useTraps && $stressLoad ne ""} {
        StressLoaded
    } elseif {$useTraps} {
        StressSolve
    }
}
flush $sf

if {$useTraps && [llength $damList] > 0} {
    # damList (legacy, 1f): damage and measurements for each entry after the one stress
    foreach e $damList {
        foreach {k v} [lindex $e 1] { set $k $v }
        set tg ${tag}_[lindex $e 0]
        if {![DamageIn $tg]} { puts $sf "$tg damage failed"; flush $sf; continue }
        flush $sf
        if {![Measure $tg]} { puts $sf "$tg measurement failed"; flush $sf; break }
        puts $sf "$tg measured"; flush $sf
        # traps out again before the next setting
        ThawTraps
        sel z=1.0e-30*(1.0+x*x) name=TrapN
        if {![SolveOK]} { puts $sf "reset solve failed"; break }
    }
} else {
    if {$useTraps && ![DamageIn $tag]} { error "damage" }
    Measure $tag
}
puts $sf "done"
close $sf
puts "RADIV DONE tag=$tag"
