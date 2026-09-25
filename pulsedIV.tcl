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
#==============================================

source GaN_modelfile_masterD
source rfdevice.tcl

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
set n [expr {int(round($Vd_max / $Vd_step))}]
for {set i 0} {$i <= $n} {incr i} {
    set d [expr {$i * $Vd_step}]
    contact name=D supply=$d
    device
    set te [FillStep $fillIters $fillRelax]
    set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
    #FLOOXS GIVES A/um
    puts "PULSED Vd=$d Id=$cur peakTe=$te"
    set f [open $ivCSV a]
    puts $f "$d, $cur, $te"
    close $f
    chart graph=PulsedIV curve=Id xval=$d yval=$cur leg.left
}
