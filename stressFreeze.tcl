# Stress-then-freeze (pulsed-IV style) current collapse simulation.
# For each quiescent (stress) bias: solve DC there so the traps equilibrate,
# freeze the trapped charge, then measure Id-Vd at Vg_meas with the traps held.
# Collapse = drop in the measured current relative to the (0,0) quiescent point.

window row=1 col=1
set trapEn 1

source GaN_modelfile_masterD
source rfdevice.tcl

pdbSetDouble GaN Qfn DampValue 0.10
pdbSetDouble GaN Qfp DampValue 0.10
pdbSetDouble GaN DevPsi DampValue 0.10
pdbSetDouble Nitride DevPsi DampValue 0.10
pdbSetDouble AlGaN DevPsi DampValue 0.10

set Vg_meas -2.0
set Vd_max 10.0
set Vd_step 0.25

# {VgQ VdQ csv}
set quiescent {
    {0.0   0.0  figures/stressIV_q0_0.csv}
    {-2.0 10.0  figures/stressIV_qm2_10.csv}
    {0.0  10.0  figures/stressIV_q0_10.csv}
    {-4.0 20.0  figures/stressIV_qm4_20.csv}
}

# step contact c from v0 to v1 in increments no larger than dv
proc ramp {c v0 v1 dv} {
    set n [expr {int(ceil(abs($v1 - $v0) / $dv))}]
    for {set i 1} {$i <= $n} {incr i} {
        contact name=$c supply=[expr {$v0 + ($v1 - $v0) * $i / double($n)}]
        device
    }
}

proc stressMeasure {VgQ VdQ csv} {
    global Vg_meas Vd_max Vd_step

    # stress: traps follow the Fermi level at the quiescent point
    ramp G 0.0 $VgQ 0.1
    ramp D 0.0 $VdQ 0.25
    HotStress
    FreezeTraps

    # measure with the trapped charge held fixed
    ramp D $VdQ 0.0 0.25
    ramp G $VgQ $Vg_meas 0.1

    set f [open $csv w]
    close $f
    set n [expr {int(round($Vd_max / $Vd_step))}]
    for {set i 0} {$i <= $n} {incr i} {
        set d [expr {$i * $Vd_step}]
        contact name=D supply=$d
        device
        set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
        #FLOOXS GIVES A/um
        set f [open $csv a]
        puts $f "$d, $cur"
        close $f
        chart graph=StressIV curve="Q($VgQ,$VdQ)" xval=$d yval=$cur leg.left
    }

    # back to (0,0) with the traps released
    ramp D $Vd_max 0.0 0.25
    ramp G $Vg_meas 0.0 0.1
    ThawTraps
    device
}

Initialize
device init

foreach q $quiescent {
    stressMeasure {*}$q
}
