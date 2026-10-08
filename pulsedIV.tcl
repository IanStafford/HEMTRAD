# Pulsed curve-tracer Id-Vd sweep with trap memory: reproduces radiation-induced
# current collapse (device works normally, then shuts off past some Vd).
#
# Physics: at each Vd point, hot electrons (local-field Te) are captured into the
# radiation-induced acceptor traps. Emission from 0.6-0.8 eV traps takes seconds
# or longer, so across the pulse train the traps only fill, never empty. Once
# trapped charge depletes the 2DEG at the drain-side gate edge, the field (and
# Te) there rises, trapping more: the current collapses and stays off.
#
# Assumptions, all adjustable below:
#  - traps start at steady state at (Vg_meas, 0) (device rested before the sweep)
#  - no emission during the sweep (fill-only); fillIters Te/solve iterations per
#    Vd point stand in for the pulses at that step
#  - trap location/density/level and hot-electron parameters as set here

window row=1 col=1

#=================== levers ===================
# Each has an `info exists` default so a driver copy or array task can
# override it (`set <lever> <value>`) before sourcing this file.
# trap distribution (radiation damage)
if {![info exists trapEn]}    { set trapEn    1 }
if {![info exists trapPeak]}  { set trapPeak  4e18 }   ;# peak trap density (cm^-3)
if {![info exists trapMeanX]} { set trapMeanX 0.0 }    ;# Gaussian center, depth (um; 0 = AlGaN top, 0.015 = 2DEG)
if {![info exists trapMeanY]} { set trapMeanY 0.20 }   ;# Gaussian center, lateral (um; gate drain edge = 0.125)
if {![info exists trapSigma]} { set trapSigma 0.025 }  ;# Gaussian spatial sigma (um)
if {![info exists trapLevel]} { set trapLevel 0.68 }   ;# trap depth below Ec (eV)
if {![info exists trapWidth]} { set trapWidth 0.1 }    ;# energy FWHM (eV)

# hot-electron capture
if {![info exists hotEb]}  { set hotEb  0.3 }     ;# capture barrier (eV); larger = hot electrons out-capture cold ones more (earlier, deeper collapse)
if {![info exists hotTau]} { set hotTau 1.0e-13 } ;# energy relaxation time (s); larger = hotter at a given field

# sweep (curve tracer)
if {![info exists Vg_meas]}   { set Vg_meas   -2.0 }
if {![info exists Vd_max]}    { set Vd_max    1.6 }
if {![info exists Vd_step]}   { set Vd_step   0.1 }
if {![info exists fillIters]} { set fillIters 4 }   ;# Te/solve/capture iterations per Vd point
if {![info exists fillRelax]} { set fillRelax 0.5 } ;# Te under-relaxation per iteration

if {![info exists ivCSV]} { set ivCSV "figures/pulsedIV.csv" } ;# columns: Vd, Id (mA/mm), peak Te (K)
if {![info exists dampValue]} { set dampValue 0.10 } ;# Newton damping on Qfn/Qfp/DevPsi; smaller = more damped/stable, slower

# retry on solver failure (Newton limit or NaN): restore the last converged
# solution + trap memory and bisect the Vd step. No effect if nothing fails.
if {![info exists retryDepth]}   { set retryDepth 5 }   ;# max bisection levels per Vd point (0 = no retry)
if {![info exists retrySubFill]} { set retrySubFill 1 } ;# 1: full FillStep at bisection substeps; 0: plain device solve there
# Te ramp fallback (2026-10-02): if a point still fails after bisection, hold Vd
# at the target and move Te toward its local-field target in adaptive steps
# (halve on failure, grow on success), capturing after each converged solve,
# until max|TeTarget-Te|/Te < teRampTol. Same operations as FillStep, smaller
# Te steps: a continuation in Te through the runaway, where one w = 0.5 jump is
# too big for Newton. Only runs where the sweep would otherwise give up.
if {![info exists teRamp]}    { set teRamp    1 }      ;# 0 = off (old behaviour: give up)
if {![info exists teRampW0]}  { set teRampW0  0.1 }    ;# first Te relaxation fraction
if {![info exists teRampMin]} { set teRampMin 0.002 }  ;# give up below this fraction
if {![info exists teRampTol]} { set teRampTol 0.01 }   ;# stop when Te is within 1% of target
if {![info exists teRampMax]} { set teRampMax 300 }    ;# max ramp sub-steps per point
#==============================================

source GaN_modelfile_masterD
# Electron-temperature profiles (eTemp lever): at each Vd in this list, write
# ETemp along cuts at the AlGaN top (x = 0, the trap row) and in the 2DEG
# (x = 0.016 um) to <ivCSV root>_Te_Vd<Vd>.txt. Empty = none.
if {![info exists teProfile]} { set teProfile {} }
if {![info exists deviceDeck]} { set deviceDeck rfdevice.tcl } ;# device structure deck (rfdevice_SiN.tcl: SiN instead of HighK)
source $deviceDeck

pdbSetDouble GaN Qfn DampValue $dampValue
pdbSetDouble GaN Qfp DampValue $dampValue
pdbSetDouble GaN DevPsi DampValue $dampValue
pdbSetDouble Nitride DevPsi DampValue $dampValue
pdbSetDouble AlGaN DevPsi DampValue $dampValue

Initialize
device init

# rest at the measurement gate bias with the traps in steady state
for {set g -0.1} {$g > $Vg_meas - 0.001} {set g [expr {$g - 0.1}]} {
    contact name=G supply=$g
    device
}
CaptureTraps

set f [open $ivCSV w]
close $f
# One attempt at Vd=d. fill=1 runs the hot-electron FillStep (a measured
# point); fill=0 is a plain solve (a bisection substep with retrySubFill=0).
proc TryPoint {d fill} {
    global fillIters fillRelax
    if {[catch {
        contact name=D supply=$d
        device
        if {$fill} { set ::te [FillStep $fillIters $fillRelax] }
    }]} { return 0 }
    return 1
}
# `device store`/`device restore` save/restore the solution; restore also
# clears the solver's element queues a thrown NaN leaves behind (a bare
# catch + retry would re-assemble those elements - see CLAUDE.md section 6).
proc SaveState {} {
    sel z=TrapFrozen name=TFsave
    sel z=TeTrap name=TEsave
    device store
}
proc RestoreState {dPrev} {
    device restore
    sel z=TFsave name=TrapFrozen
    sel z=TEsave name=TeTrap
    contact name=D supply=$dPrev
}
# Reach d from the converged point dPrev, bisecting the step on failure.
proc Reach {dPrev d depth fill} {
    SaveState
    if {[TryPoint $d $fill]} { return 1 }
    incr ::nRetry
    puts "RETRY Vd $dPrev -> $d failed (depth $depth), bisecting"
    RestoreState $dPrev
    if {$depth <= 0} { return 0 }
    set mid [expr {0.5 * ($dPrev + $d)}]
    if {![Reach $dPrev $mid [expr {$depth - 1}] $::retrySubFill]} { return 0 }
    return [Reach $mid $d [expr {$depth - 1}] $fill]
}

# Te continuation at fixed Vd = d, starting from the converged point dPrev.
proc TeRampPoint {dPrev d} {
    global teRampW0 teRampMin teRampTol teRampMax
    RestoreState $dPrev
    SaveState
    if {[catch { contact name=D supply=$d; device }]} {
        RestoreState $dPrev
        return 0
    }
    set w $teRampW0
    for {set k 1} {$k <= $teRampMax} {incr k} {
        SaveState
        if {[catch {
            set ::te [UpdateTe $w]
            device
            CaptureTraps
        }]} {
            device restore
            sel z=TFsave name=TrapFrozen
            sel z=TEsave name=TeTrap
            set w [expr {$w / 2.0}]
            puts "TERAMP Vd=$d step $k failed, w -> $w"
            if {$w < $teRampMin} { return 0 }
            continue
        }
        sel z=[HotTeExpr] name=TeTarget
        sel z=abs(TeTarget-TeTrap)/TeTrap
        set r [lindex [peak GaN] 1]
        puts "TERAMP Vd=$d step $k w=$w Id=[expr {abs([contact name=D sol=Qfn flux])*1.0e6}] peakTe=$::te mismatch=$r"
        if {$r < $teRampTol} { return 1 }
        set w [expr {min(0.5, $w * 1.5)}]
    }
    return 1
}

set nRetry 0
set nRamp 0
set dPrev 0.0
set n [expr {int(round($Vd_max / $Vd_step))}]
for {set i 0} {$i <= $n} {incr i} {
    set d [expr {$i * $Vd_step}]
    if {![Reach $dPrev $d $retryDepth 1]} {
        if {!$teRamp || ![TeRampPoint $dPrev $d]} {
            puts "PULSED GAVE UP at Vd=$d after $retryDepth bisection levels"
            break
        }
        incr nRamp
        puts "PULSED TERAMP rescued Vd=$d"
    }
    set dPrev $d
    set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
    #FLOOXS GIVES A/um
    puts "PULSED Vd=$d Id=$cur peakTe=$te retries=$nRetry ramps=$nRamp"
    if {$eTemp} {
        sel z=ETemp
        puts "ETEMP Vd=$d peakETemp(GaN)=[lindex [peak GaN] 1] peakETemp(AlGaN)=[lindex [peak AlGaN] 1]"
    }
    foreach v $teProfile {
        if {abs($v - $d) < 1.0e-6} {
            set pf [open "[file rootname $ivCSV]_Te_Vd[format %.2f $d].txt" w]
            sel z=ETemp
            foreach xc {0.0 0.016} {
                puts $pf "# ETemp (K) along y (um) at x = $xc um, Vd = $d V"
                puts $pf [print1d xv=$xc]
            }
            close $pf
        }
    }
    set f [open $ivCSV a]
    puts $f "$d, $cur, $te"
    close $f
    chart graph=PulsedIV curve=Id xval=$d yval=$cur leg.left
}
