# Pre/post-irradiation device characterisation (branch explore/rad-model, 2026-10-23).
# Reproduces the measured set in kb/results/measured-rad-y2.md (local note):
#   transfer Id-Vg at Vd = Vd_lin (0.1 V), Vg Vg_hi -> Vg_lo;
#   output Id-Vd at Vg = Vg_out (+1 V), Vd 0 -> Vd_max.
# radState pre : trap-free device (calibration).
# radState post: radiation damage, then the same measurements:
#   - bias-independent part: fixed charge at the AlGaN/passivation surface
#     (lever surfCharge, cm^-2, set by the caller; negative = acceptor-like);
#   - biased-irradiation part (damPeak > 0): acceptor traps whose density follows the
#     lateral field |dEpsi/dy| at the irradiation bias (Vg_stress, Vd_stress):
#       N = min(damMax, damPeak * (E/damEref)^damM)   for 0 <= x <= damXmax (um)
#     Trap level / hot-electron capture as in the trap model (trapLevel, hotEb, ...).
#   - lumped gate-drain leakage Rgd (ohm*mm, 0 = none): the localized leakage paths
#     ion strikes leave (steps in the irradiation monitor) are 3D, not in a 2D cut;
#     Id_ext = Id_dev + (Vd - Vg)/Rgd.
# Traps fill but never empty after the rest point (fill-only, CaptureTraps), with
# hot-electron FillStep at each Id-Vd point.
# Outputs (prefix $tag): <tag>_IdVg.csv (Vg, Id_dev, Id_ext mA/mm),
# <tag>_IdVd.csv (Vd, Id_dev, Id_ext, peak Te), <tag>_cuts.txt (Estress, TrapN,
# IonAcceptor along x = 0.001 / 0.016 um), <tag>_summary.txt.

if {![info exists radState]}  { set radState pre }
if {![info exists tag]}       { set tag $radState }
if {![info exists deviceDeck]} { set deviceDeck rfdevice.tcl }
if {![info exists mobModel]}  { set mobModel field }
if {![info exists eTemp]}     { set eTemp 0 }
if {![info exists dampValue]} { set dampValue 0.05 }
if {![info exists retryDepth]} { set retryDepth 6 }
# measurements
if {![info exists Vd_lin]}    { set Vd_lin 0.1 }
if {![info exists Vg_hi]}     { set Vg_hi 1.0 }
if {![info exists Vg_lo]}     { set Vg_lo -4.0 }
if {![info exists Vg_step]}   { set Vg_step 0.05 }
if {![info exists Vg_out]}    { set Vg_out 1.0 }
if {![info exists Vd_max]}    { set Vd_max 10.0 }
if {![info exists Vd_step]}   { set Vd_step 0.25 }
if {![info exists doIdVg]}    { set doIdVg 1 }
if {![info exists doIdVd]}    { set doIdVd 1 }
# irradiation bias and damage
if {![info exists Vg_stress]} { set Vg_stress -10.0 }
if {![info exists Vd_stress]} { set Vd_stress 28.0 }
if {![info exists damPeak]}   { set damPeak 0.0 }     ;# cm^-3 at E = damEref
if {![info exists damEref]}   { set damEref 1.0e6 }   ;# V/cm
if {![info exists damM]}      { set damM 2.0 }
if {![info exists damMax]}    { set damMax 1.0e19 }
if {![info exists damXmax]}   { set damXmax 0.05 }    ;# um below the AlGaN top
if {![info exists Rgd]}       { set Rgd 0.0 }
# trap / capture (sensitivity baseline)
if {![info exists trapLevel]} { set trapLevel 0.30 }
if {![info exists trapWidth]} { set trapWidth 0.1 }
if {![info exists hotEb]}     { set hotEb 1.0 }
if {![info exists hotTau]}    { set hotTau 1.0e-14 }
if {![info exists fillIters]} { set fillIters 4 }
if {![info exists fillRelax]} { set fillRelax 0.5 }

set useTraps [expr {$radState eq "post" && $damPeak > 0.0}]
set trapEn $useTraps
set trapShape field

if {![info exists modelDir]} {
    if {[file exists GaN_modelfile_masterD]} { set modelDir . } elseif {[file isdirectory model]} { set modelDir model } else { set modelDir [file join [file dirname [info script]] .. model] }
}
source [file join $modelDir GaN_modelfile_masterD]
source [file join $modelDir $deviceDeck]
foreach m {GaN AlGaN Nitride} { pdbSetDouble $m DevPsi DampValue $dampValue }
pdbSetDouble GaN Qfn DampValue $dampValue
pdbSetDouble GaN Qfp DampValue $dampValue

Initialize
device init

proc IdDev {} { return [expr {abs([contact name=D sol=Qfn flux]) * 1.0e6}] }
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
# One solve at contact c = v; fill = 1 runs the hot-electron FillStep.
proc TryBias {c v fill} {
    if {[catch {
        contact name=$c supply=$v
        device
        if {$fill && $::useTraps} { set ::te [FillStep $::fillIters $::fillRelax] }
    }]} { return 0 }
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
set te 300.0
set sf [open ${tag}_summary.txt w]

#---------------- irradiation (post) ----------------
if {$radState eq "post"} {
    if {[info exists surfCharge]} { puts $sf "surfCharge $surfCharge" }
    if {$useTraps} {
        if {![Ramp G 0.0 $Vg_stress 0.5]} { error "stress gate ramp failed" }
        if {![Ramp D 0.0 $Vd_stress 0.5]} { error "stress drain ramp failed" }
        sel z=abs(dot(DevPsi,y*1e-4)) name=Estress
        puts $sf "stress Vg=$Vg_stress Vd=$Vd_stress peakElat(GaN)=[lindex [peak GaN] 1] at [lrange [peak GaN] 2 3] peakElat(AlGaN)=[lindex [peak AlGaN] 1]"
        if {![Ramp D $Vd_stress 0.0 1.0]} { error "stress drain ramp-down failed" }
        if {![Ramp G $Vg_stress 0.0 0.5]} { error "stress gate ramp-down failed" }
        # damage, switched in gradually at rest (live occupancy)
        set n "($damPeak*exp($damM*log(Estress/$damEref+1.0e-30)))"
        set n "(0.5*($n+$damMax-abs($n-$damMax)))*(x>=0.0)*(x<=$damXmax)"
        foreach s {0.01 0.03 0.1 0.3 0.6 1.0} {
            sel z=$s*$n+1.0e-30*(1.0+x*x) name=TrapN
            SaveState
            if {[catch {device}]} { RestoreState; puts "DAMAGE solve failed at scale $s"; error "damage" }
        }
        sel z=TrapN
        puts $sf "damage peakN(GaN)=[lindex [peak GaN] 1] at [lrange [peak GaN] 2 3] peakN(AlGaN)=[lindex [peak AlGaN] 1]"
        CaptureTraps
        set c [open ${tag}_cuts.txt w]
        foreach fld {Estress TrapN IonAcceptor} {
            sel z=$fld
            foreach xc {0.001 0.016} { puts $c "# $fld along y at x = $xc"; puts $c [print.1d x.value=$xc] }
        }
        close $c
    }
}
flush $sf

#---------------- transfer at Vd_lin ----------------
if {$doIdVg} {
    if {![Ramp D 0.0 $Vd_lin 0.05]} { error "Vd_lin ramp failed" }
    if {![Ramp G 0.0 $Vg_hi 0.1]} { error "Vg_hi ramp failed" }
    if {$useTraps} { CaptureTraps }
    set f [open ${tag}_IdVg.csv w]
    set gPrev $Vg_hi
    set n [expr {int(round(($Vg_hi - $Vg_lo) / $Vg_step))}]
    for {set i 0} {$i <= $n} {incr i} {
        set g [expr {$Vg_hi - $i * $Vg_step}]
        if {$i > 0 && ![Reach G $gPrev $g $retryDepth 0]} { puts "IDVG GAVE UP at Vg=$g"; break }
        if {$useTraps} { CaptureTraps }
        set gPrev $g
        puts $f "$g, [IdDev], [IdExt $Vd_lin $g]"
        flush $f
        puts "IDVG Vg=$g Id=[IdDev]"
    }
    close $f
    if {![Ramp G $gPrev 0.0 0.1]} { error "gate return failed" }
    if {![Ramp D $Vd_lin 0.0 0.05]} { error "drain return failed" }
}

#---------------- output at Vg_out ----------------
if {$doIdVd} {
    if {![Ramp G 0.0 $Vg_out 0.1]} { error "Vg_out ramp failed" }
    if {$useTraps} { CaptureTraps }
    set f [open ${tag}_IdVd.csv w]
    puts $f "0.0, [IdDev], [IdExt 0.0 $Vg_out], 300.0"
    set dPrev 0.0
    set n [expr {int(round($Vd_max / $Vd_step))}]
    for {set i 1} {$i <= $n} {incr i} {
        set d [expr {$i * $Vd_step}]
        if {![Reach D $dPrev $d $retryDepth 1]} { puts "IDVD GAVE UP at Vd=$d"; break }
        set dPrev $d
        puts $f "$d, [IdDev], [IdExt $d $Vg_out], $te"
        flush $f
        puts "IDVD Vd=$d Id=[IdDev] peakTe=$te"
    }
    close $f
}
puts $sf "done"
close $sf
puts "RADIV DONE tag=$tag"
