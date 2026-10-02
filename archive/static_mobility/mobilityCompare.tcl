# Device performance for one electron mobility model (no traps), same bias sequence
# as transfer.tcl: output curve Id-Vd at Vg=0 (ramping to Vd=10V), then transfer
# curve Id-Vg at Vd=10V.
# Select the model with the MOBMODEL environment variable (static | field):
#   MOBMODEL=field flooxs mobilityCompare.tcl
# Writes figures/mobility_<model>_IdVd.csv and figures/mobility_<model>_IdVg.csv (mA/mm).

window row=1 col=1

set mobModel static
if {[info exists env(MOBMODEL)]} { set mobModel $env(MOBMODEL) }
set trapEn 0

source rfdevice.tcl
source GaN_modelfile_masterD

Initialize
device init

set f [open "figures/mobility_${mobModel}_IdVd.csv" w]
for {set i 0} {$i <= 40} {incr i} {
    set d [expr {$i * 0.25}]
    contact name=D supply=$d
    device
    set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
    #FLOOXS GIVES A/um
    puts $f "$d, $cur"
    flush $f
    chart graph=IdVd curve=$mobModel xval=$d yval=$cur leg.left title="Vg=0V"
}
close $f

set f [open "figures/mobility_${mobModel}_IdVg.csv" w]
for {set i 0} {$i <= 40} {incr i} {
    set g [expr {-$i * 0.1}]
    contact name=G supply=$g
    device
    set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
    puts $f "$g, $cur"
    flush $f
    chart graph=IdVg curve=$mobModel xval=$g yval=$cur leg.left title="Vd=10V"
}
close $f
