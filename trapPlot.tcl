proc nearHalfVolt {V {tol 0.001}} {
    set scaled [expr {$V / 0.5}]
    set frac [expr {abs($scaled - round($scaled))}]
    return [expr {$frac < ($tol / 0.5)}]
}

proc trapPlot {ivCSV} {
    Initialize
    device init

    for {set g 0.0} {$g > -2.0} {set g [expr $g-0.1]} {
        contact name=G supply=$g
        device
    }   

    set f [open $ivCSV w]
    close $f
    set f2 [open "figures/trapOccupation2.csv" w]

    for {set d 0.0} {$d < [expr 10.0 + 0.001]} {set d [expr $d+0.1]} {
        set f [open $ivCSV a]
        contact name=D supply=$d
        device
        device
        set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}] 
        #FLOOXS GIVES A/um
        puts $f "$d, $cur"
        close $f
        chart graph=IV curve=DrainCur xval=$d yval=$cur leg.left
        if { [nearHalfVolt $d 0.001]} {
            sel z=log10(abs(IonAcceptor)+1.0)

            set pstr [peak AlGaN]
            puts "$pstr"
            plot1d graph=Trap xv=0.018 xmin=-1.0 xmax=1.0 ylab="TrapConc" title="Traps" name="Vds=$d" log
            puts $f2 [print1d xv=0.018]
        }
    }
    close $f2
}

window row=1 col=2
set trapEn 1

source GaN_modelfile_masterD
source rfdevice.tcl

pdbSetDouble GaN Qfn DampValue 0.10
pdbSetDouble GaN Qfp DampValue 0.10
pdbSetDouble GaN DevPsi DampValue 0.10
pdbSetDouble Nitride DevPsi DampValue 0.10
pdbSetDouble AlGaN DevPsi DampValue 0.10


trapPlot "figures/radPlot2.csv"