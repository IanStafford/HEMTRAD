# Transfer-curve calibration against figures/rfDeviceHFO2_Experimental.csv
# (Id-Vg at Vds = 10 V, 25 C, 100 nm HfO2, std field plate; measured in A for a 200 um gate width;
# compared in mA/mm = A * 1e3 / 0.2).
# Trap-free, field mobility by default. Ramp Vd to Vd_cal at Vg=0, ramp the gate up to
# Vg_max, then sweep it down to Vg_min, writing Vg, Id (mA/mm) to calCSV.
# Any lever below can be set by a wrapper before sourcing this file.
if {![info exists deviceDeck]} { set deviceDeck rfdevice.tcl }
if {![info exists calCSV]}     { set calCSV figures/calib_IdVg.csv }
if {![info exists Vd_cal]}     { set Vd_cal 10.0 } ;# measured at Vds = 10 V (raw data RF_100nmHfOx_IdVgs_Example1.xlsx)
if {![info exists Vg_max]}     { set Vg_max 1.0 }
if {![info exists Vg_min]}     { set Vg_min -4.0 }
if {![info exists Vg_step]}    { set Vg_step 0.1 }
# Lumped ohmic contact resistances (ohm*mm), applied at the external terminals:
# internal source = Id*Rs, internal drain = Vd - Id*Rd (gate referenced to the
# external source, as measured). 0 = ideal contacts (the deck as before).
if {![info exists Rs_contact]} { set Rs_contact 0.0 }
if {![info exists Rd_contact]} { set Rd_contact 0.0 }
set trapEn 0
if {![info exists mobModel]}   { set mobModel field }

source GaN_modelfile_masterD
source $deviceDeck
# Optional post-load overrides (a Tcl script string), e.g. pdbSetDouble calls.
if {[info exists calHook]} { eval $calHook }

Initialize
device init

# Drain current in A/mm (FLOOXS flux is A/um of depth).
proc IdAmm {} { return [expr {abs([contact name=D sol=Qfn flux]) * 1.0e3}] }
# Solve at external Vd = vd with the contact resistances, by fixed-point
# iteration on the internal terminal voltages (converges fast: gm*R << 1).
proc SolveRc {vd} {
    global Rs_contact Rd_contact
    if {$Rs_contact == 0.0 && $Rd_contact == 0.0} {
        contact name=D supply=$vd
        device
        return
    }
    set id [IdAmm]
    for {set it 0} {$it < 20} {incr it} {
        set vs [expr {$id * $Rs_contact}]
        set vdi [expr {$vd - $id * $Rd_contact}]
        contact name=S supply=$vs
        contact name=D supply=$vdi
        device
        set idn [IdAmm]
        if {abs($idn - $id) * ($Rs_contact + $Rd_contact) < 1.0e-4} { return }
        set id $idn
    }
    puts "RC WARNING: contact-resistance iteration did not converge at Vd=$vd"
}

for {set d 0.25} {$d < $Vd_cal + 0.001} {set d [expr {$d + 0.25}]} {
    SolveRc $d
}
for {set g $Vg_step} {$g < $Vg_max + 0.001} {set g [expr {$g + $Vg_step}]} {
    contact name=G supply=$g
    SolveRc $Vd_cal
}
set f [open $calCSV w]
for {set g $Vg_max} {$g > $Vg_min - 0.001} {set g [expr {$g - $Vg_step}]} {
    set g [expr {round($g * 1000.0) / 1000.0}]
    contact name=G supply=$g
    SolveRc $Vd_cal
    set cur [expr {abs([contact name=D sol=Qfn flux]) * 1.0e6}]
    puts $f "$g, $cur"
    flush $f
    puts "CAL Vg=$g Id=$cur"
}
close $f
