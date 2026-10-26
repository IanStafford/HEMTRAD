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
# damList (optional): several damage settings after ONE stress solve, e.g.
#   set damList {{d1 {damPeak 1e17 damM 2}} {d2 {damPeak 3e17 damM 3}}}
# each entry {suffix {lever value ...}} (damPeak/damM/damEref/damMax/damXmax/damY*/damIns*/Rgd/hotTau);
# (insTrapSign must be set before the model is sourced, i.e. as a task lever, not in damList)
# outputs get the prefix ${tag}_<suffix>. Traps are reset (ThawTraps) between entries.
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
if {![info exists Vd_stressMin]} { set Vd_stressMin 12.0 } ;# accept a stress Vd down to this if the solve fails above
if {![info exists damPeak]}   { set damPeak 0.0 }     ;# cm^-3 at E = damEref
if {![info exists damEref]}   { set damEref 1.0e6 }   ;# V/cm
if {![info exists damM]}      { set damM 2.0 }
if {![info exists damMax]}    { set damMax 1.0e19 }
if {![info exists damXmax]}   { set damXmax 0.05 }    ;# um below the AlGaN top
if {![info exists damYmin]}   { set damYmin -1.0e3 }  ;# um; damage window along y (diagnostic,
if {![info exists damYmax]}   { set damYmax 1.0e3 }   ;#   default = whole device)
# passivation damage (branch, 2026-10-24): fixed charge in the insulator layer
# damInsXmin <= x < 0 (um above the AlGaN top), density from the field there at the
# stress bias: N = min(damMax, damInsPeak*(E/damInsEref)^damInsM), charge sign
# insTrapSign (-1 = trapped electrons). damInsField / damField pick the stress field:
# lat = |dpsi/dy| (default for the semiconductor part, as before), tot = |grad psi|,
# ne = Elec*|dpsi/dy| at stress normalised to its semiconductor peak (use damEref 1).
if {![info exists damInsPeak]}  { set damInsPeak 0.0 }  ;# 0 = none (old behaviour)
if {![info exists damInsEref]}  { set damInsEref 1.0e6 }
if {![info exists damInsM]}     { set damInsM 2.0 }
if {![info exists damInsXmin]}  { set damInsXmin -0.05 } ;# um; -0.05 = the 50 nm SiN under the HfO2
if {![info exists damField]}    { set damField lat }
if {![info exists damInsField]} { set damInsField tot }
if {$damInsPeak > 0.0 && ![info exists insTrapSign]} { set insTrapSign -1 }
# second semiconductor damage site (branch, 2026-10-25): same law and depth as the
# first, own peak/exponent/y-window; e.g. a second ion-strike site farther toward
# the drain. dam2Peak 0 = none (old behaviour).
if {![info exists damNexp]}   { set damNexp 0.0 }   ;# first site also scales with (Elec/damNref)^damNexp at stress
if {![info exists damNref]}   { set damNref 1.0e17 } ;#   (hot-electron rate ~ n*E^m); 0 = field only (old behaviour)
if {![info exists dam2Peak]}  { set dam2Peak 0.0 }
if {![info exists dam2M]}     { set dam2M 0.0 }
if {![info exists dam2Ymin]}  { set dam2Ymin 0.65 }
if {![info exists dam2Ymax]}  { set dam2Ymax 1.0 }
if {![info exists dam2Field]} { set dam2Field "" }   ;# "" = same field/Eref as the first site
# third site (2026-10-26): uniform damage in a y window (discrete ion-strike site); 0 = none
if {![info exists dam3Peak]}  { set dam3Peak 0.0 }
if {![info exists dam3Ymin]}  { set dam3Ymin 1.0 }
if {![info exists dam3Ymax]}  { set dam3Ymax 1.6 }
if {![info exists dam2Eref]}  { set dam2Eref "" }
if {![info exists dam2Xmax]}  { set dam2Xmax "" }    ;# depth of the second site (um); "" = damXmax
if {![info exists Rgd]}       { set Rgd 0.0 }
if {![info exists damList]}   { set damList {} }
# trap / capture (sensitivity baseline)
if {![info exists trapLevel]} { set trapLevel 0.30 }
if {![info exists trapWidth]} { set trapWidth 0.1 }
if {![info exists hotEb]}     { set hotEb 1.0 }
if {![info exists hotTau]}    { set hotTau 1.0e-14 }
if {![info exists fillIters]} { set fillIters 4 }
if {![info exists fillRelax]} { set fillRelax 0.5 }

set useTraps [expr {$radState eq "post" && ($damPeak > 0.0 || $damInsPeak > 0.0 || $dam2Peak > 0.0 || $dam3Peak > 0.0 || [llength $damList] > 0)}]
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
        # The off-state solve stops converging near Vdg ~ 27 V (minority quasi-Fermi
        # levels in the depleted AlGaN, job 47311016). Use the highest converged Vd if it
        # is at least Vd_stressMin; the damage law's scale absorbs the field magnitude.
        set dS 0.0
        for {set d 1.0} {$d <= $Vd_stress + 1e-9} {set d [expr {$d + 1.0}]} {
            if {![Reach D $dS $d $retryDepth 0]} { break }
            set dS $d
        }
        if {$dS < $Vd_stressMin} { error "stress drain ramp failed at $dS" }
        sel z=abs(dot(DevPsi,y*1e-4)) name=Estress
        sel z=sqrt(dot(DevPsi,DevPsi)) name=EstressT
        # n*E at stress, normalised to its peak in the semiconductor (damField ne)
        sel z=Elec name=ElecStress
        sel z=Elec*Estress name=EstressNE
        set neMax [expr {max([lindex [peak GaN] 1], [lindex [peak AlGaN] 1])}]
        sel z=EstressNE/$neMax name=EstressNE
        puts $sf "stress n*Elat peak $neMax at [lrange [peak GaN] 2 3]"
        sel z=Estress
        puts $sf "stress Vg=$Vg_stress Vd=$dS (target $Vd_stress) peakElat(GaN)=[lindex [peak GaN] 1] at [lrange [peak GaN] 2 3] peakElat(AlGaN)=[lindex [peak AlGaN] 1]"
        flush $sf
        if {![Ramp D $dS 0.0 1.0]} { error "stress drain ramp-down failed" }
        if {![Ramp G $Vg_stress 0.0 0.5]} { error "stress gate ramp-down failed" }
    }
}
flush $sf

# Switch the damage in at rest (Vg = Vd = 0) for the present damage levers.
proc DamageIn {tg} {
    global damPeak damM damEref damMax damXmax damYmin damYmax sf
    global damInsPeak damInsM damInsEref damInsXmin damField damInsField
    global dam2Peak dam2M dam2Ymin dam2Ymax dam2Field dam2Eref dam2Xmax damNexp damNref dam3Peak dam3Ymin dam3Ymax
    ThawTraps
    set fld [expr {$damField eq "tot" ? "EstressT" : ($damField eq "ne" ? "EstressNE" : "Estress")}]
    set n "($damPeak*exp($damM*log($fld/$damEref+1.0e-30)))"
    if {$damNexp != 0.0} { set n "($n*exp($damNexp*log(ElecStress/$damNref+1.0e-30)))" }
    set n "(0.5*($n+$damMax-abs($n-$damMax)))*(x>=0.0)*(x<=$damXmax)*(y>=$damYmin)*(y<=$damYmax)"
    if {$dam2Peak > 0.0} {
        set f2 $fld
        if {$dam2Field ne ""} { set f2 [expr {$dam2Field eq "tot" ? "EstressT" : ($dam2Field eq "ne" ? "EstressNE" : "Estress")}] }
        set e2 [expr {$dam2Eref eq "" ? $damEref : $dam2Eref}]
        set n2 "($dam2Peak*exp($dam2M*log($f2/$e2+1.0e-30)))"
        set x2 [expr {$dam2Xmax eq "" ? $damXmax : $dam2Xmax}]
        set n "$n+(0.5*($n2+$damMax-abs($n2-$damMax)))*(x>=0.0)*(x<=$x2)*(y>=$dam2Ymin)*(y<=$dam2Ymax)"
    }
    if {$dam3Peak > 0.0} {
        set n "$n+$dam3Peak*(x>=0.0)*(x<=$damXmax)*(y>=$dam3Ymin)*(y<=$dam3Ymax)"
    }
    if {$damInsPeak > 0.0} {
        set fi [expr {$damInsField eq "lat" ? "Estress" : "EstressT"}]
        set ni "($damInsPeak*exp($damInsM*log($fi/$damInsEref+1.0e-30)))"
        set n "$n+(0.5*($ni+$damMax-abs($ni-$damMax)))*(x<0.0)*(x>=$damInsXmin)*(y>=$damYmin)*(y<=$damYmax)"
    }
    foreach s {0.0 0.01 0.03 0.1 0.3 0.6 1.0} {
        sel z=$s*($n)+1.0e-30*(1.0+x*x) name=TrapN
        SaveState
        if {[catch {device}]} { RestoreState; puts "DAMAGE solve failed at scale $s"; return 0 }
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
    set c [open ${tg}_cuts.txt w]
    foreach fld {Estress EstressT EstressNE TrapN IonAcceptor} {
        sel z=$fld
        foreach xc {-0.04 -0.01 0.001 0.016} {
            if {$xc < 0.0 && $fld eq "IonAcceptor"} { continue }
            puts $c "# $fld along y at x = $xc"; puts $c [print1d xv=$xc]
        }
    }
    close $c
    return 1
}

proc Measure {tg} {
    global doIdVg doIdVd Vd_lin Vg_hi Vg_lo Vg_step Vg_out Vd_max Vd_step retryDepth useTraps te
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
        if {![Ramp G 0.0 $Vg_out 0.1]} { return 0 }
        if {$useTraps} { CaptureTraps }
        set f [open ${tg}_IdVd.csv w]
        puts $f "0.0, [IdDev], [IdExt 0.0 $Vg_out], 300.0"
        set dPrev 0.0
        set n [expr {int(round($Vd_max / $Vd_step))}]
        for {set i 1} {$i <= $n} {incr i} {
            set d [expr {$i * $Vd_step}]
            if {![Reach D $dPrev $d $retryDepth 1]} { puts "IDVD GAVE UP at Vd=$d"; break }
            set dPrev $d
            puts $f "$d, [IdDev], [IdExt $d $Vg_out], $te"
            flush $f
            puts "IDVD $tg Vd=$d Id=[IdDev] peakTe=$te"
        }
        close $f
        # back to rest for the next damage setting
        if {![Ramp D $dPrev 0.0 0.5]} { return 0 }
        if {![Ramp G $Vg_out 0.0 0.1]} { return 0 }
    }
    return 1
}

if {$useTraps && [llength $damList] > 0} {
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
        SaveState
        if {[catch {device}]} { RestoreState; puts $sf "reset solve failed"; break }
    }
} else {
    if {$useTraps && ![DamageIn $tag]} { error "damage" }
    Measure $tag
}
puts $sf "done"
close $sf
puts "RADIV DONE tag=$tag"
