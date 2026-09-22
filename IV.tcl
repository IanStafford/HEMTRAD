# =========================================================
# IV.tcl
# Script to generate IV curves for different gate voltages
# with field plate structure.
# =========================================================

# Load the field plate structure and libraries
source powerdevice.tcl
source GaN_modelfile_masterD

# Open a plot window
window row=1 col=1

# ========================================================
# First IV curve at Vg = 0V
# ========================================================

# Call initialization procedure to solve the initial conditions
Initialize
device init

# Data file to store IV results
set f [open "figures/fpIV0.csv" w]

# Sweep Drain voltage from 0V to 6V in steps of 0.1V
for {set d 0.0} {$d < 6.05} {set d [expr $d+0.1]} {
    contact name=D supply=$d 
    device
    # Calculate current in mA/mm (flooxs calculated A/um)
    set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
    # Save data to file
    puts $f "$d, $cur"
    # Plot the IV curve
    chart graph=IV curve="Vg=0" xval=$d yval=$cur leg.left
}
close $f

# ========================================================
# Second IV curve at Vg = -1V
# ========================================================

source powerdevice.tcl
source GaN_modelfile_masterD

Initialize
device init
#set g -1.0
#contact name=G supply=$g
for {set g 0.0} {$g > -1.05} {set g [expr $g-0.5]} {
    contact name=G supply=$g
    device
}

set f [open "figures/fpIV1.csv" w]

for {set d 0.0} {$d < 6.05} {set d [expr $d+0.1]} {
    contact name=D supply=$d 
    device
    set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
    puts $f "$d, $cur"
    chart graph=IV curve="Vg=-1" xval=$d yval=$cur leg.left
}
close $f

# ========================================================
# Third IV curve at Vg = -2V
# ========================================================

source powerdevice.tcl
source GaN_modelfile_masterD

Initialize
device init
#set g -2.0
#contact name=G supply=$g
for {set g 0.0} {$g > -2.05} {set g [expr $g-0.5]} {
    contact name=G supply=$g
    device
}

set f [open "figures/fpIV2.csv" w]

for {set d 0.0} {$d < 6.05} {set d [expr $d+0.1]} {
    contact name=D supply=$d 
    device
    set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
    puts $f "$d, $cur"
    chart graph=IV curve="Vg=-2" xval=$d yval=$cur leg.left
}
close $f

# ========================================================
# Fourth IV curve at Vg = -3V
# ========================================================

source powerdevice.tcl
source GaN_modelfile_masterD

Initialize
device init
#set g -3.0
#contact name=G supply=$g
for {set g 0.0} {$g > -3.05} {set g [expr $g-0.5]} {
    contact name=G supply=$g
    device
}

set f [open "figures/fpIV3.csv" w]

for {set d 0.0} {$d < 6.05} {set d [expr $d+0.1]} {
    contact name=D supply=$d 
    device
    set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
    puts $f "$d, $cur"
    chart graph=IV curve="Vg=-3" xval=$d yval=$cur leg.left
}
close $f