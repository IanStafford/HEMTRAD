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
# trap distribution (radiation damage)
set trapEn    1
set trapPeak  4e18    ;# peak trap density (cm^-3)
set trapMeanX 0.0     ;# Gaussian center, depth (um; 0 = AlGaN top, 0.015 = 2DEG)
set trapMeanY 0.20    ;# Gaussian center, lateral (um; gate drain edge = 0.125)
set trapSigma 0.025   ;# Gaussian spatial sigma (um)
set trapLevel 0.68    ;# trap depth below Ec (eV)
set trapWidth 0.1     ;# energy FWHM (eV)

# hot-electron capture
set hotEb   0.3       ;# capture barrier (eV); larger = hot electrons out-capture cold ones more (earlier, deeper collapse)
set hotTau  1.0e-13   ;# energy relaxation time (s); larger = hotter at a given field

# sweep (curve tracer)
set Vg_meas   -2.0
set Vd_max    1.6
set Vd_step   0.1
set fillIters 4       ;# Te/solve/capture iterations per Vd point
set fillRelax 0.5     ;# Te under-relaxation per iteration

set ivCSV "figures/pulsedIV.csv"   ;# columns: Vd, Id (mA/mm), peak Te (K)
#==============================================

source GaN_modelfile_masterD
source rfdevice.tcl

pdbSetDouble GaN Qfn DampValue 0.10
pdbSetDouble GaN Qfp DampValue 0.10
pdbSetDouble GaN DevPsi DampValue 0.10
pdbSetDouble Nitride DevPsi DampValue 0.10
pdbSetDouble AlGaN DevPsi DampValue 0.10

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
