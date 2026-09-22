proc run_measurements {ivCSV peakCSV label} {
    # Source the provided Tcl file and the GaN model file
    Initialize
    device init

    if {1} {
    for {set d 0.0} {$d <10.05} {set d [expr $d+0.25]} {
    contact name=D supply=$d
    device 
    }

    # Wipes the  file before the loop
    set f [open $ivCSV w]
    close $f

    # Loop over gate voltage values from  10.0 down to -4.0 (approximately)
    # window row=1 col=2 make window declaration seperately to avoid new window for each run
    for {set g 0.0} {$g > -4.05} {set g [expr $g-0.1]} {
        contact name=G supply=$g
        device
        set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e3}] 
        #FLOOXS GIVES A/um

        #Appends the file and closes it every iteration to avoid data loss in case of crash
        set f [open $ivCSV a]
        puts $f "$g, $cur"
        close $f

        chart graph=IV curve=$label xval=$g yval=$cur leg.left title= "Vd=6V"
    }
    }

    if {0} {
    for {set g 0.0} {$g > -4.05} {set g [expr $g-0.5]} {
        contact name=G supply=$g
        device
    }
    set f [open $peakCSV w]

    # Loop over Vds values from 0.0 to 20.0 (approximately)
    for {set vds 0.0} {$vds < 25.1} {set vds [expr $vds+0.5]} {
        contact name=D supply=$vds
        device
        sel z=abs(dot(DevPsi,y))*1.0e-4*(y<1)*(y>-0.5)*(x<0.5)*(x>-0.5) name=PeakField
        set pstr [peak GaN]
        puts [peak GaN]
        set peakfield [lindex $pstr 1]

        set f [open $peakCSV a]
        puts $f "$vds, $peakfield"
        close $f

        chart graph=PeakField curve=$label xval=$vds yval=$peakfield leg.left ylab= "Electric Field (V/cm)" title= "Peak Field GaN"

        set pstr [peak AlGaN]
        puts [peak AlGaN]
        set peakfield [lindex $pstr 1]
        chart graph=PeakField_AlGaN curve=$label xval=$vds yval=$peakfield leg.left ylab= "Electric Field (V/cm)" title= "Peak Field AlGaN"
    }
    sel z=PeakField
    plot2d levels=40 graph=levelPlot title="PeakField" xlab="x(um)" ylab="y(um)" xmin=-0.5 xmax=0.5 ymin=-0.5 ymax=1.0
    }
}