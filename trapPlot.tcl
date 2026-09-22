proc nearHalfVolt {V {tol 0.001}} {
    set scaled [expr {$V / 0.5}]
    set frac [expr {abs($scaled - round($scaled))}]
    return [expr {$frac < ($tol / 0.5)}]
}

proc trapPlot {ivCSV bias} {
    Initialize
    device init

    for {set g 0.0} {$g > -2.0} {set g [expr $g-0.1]} {
        contact name=G supply=$g
        device
    }   

    set f [open $ivCSV w]
    close $f
    set f2 [open "figures/AcceptorTrapOccupation_Vgm2.csv" w]

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
            #sel z=log10(abs(Acceptor)+1.0)
            #sel z=Acceptor
            #plot1d graph=Acceptor xv=0.018 ylab="AcceptorOccupation" title="Acceptor" name="Vds=$d"
            sel z=log10(abs(NeutralAcceptor)+1.0)

            set pstr [peak AlGaN]
            puts "$pstr"
            #sel z=NeutralAcceptor
            plot1d graph=Trap xv=0.018 xmin=-1.0 xmax=1.0 ylab="TrapConc" title="Traps" name="Vds=$d" log
            puts $f2 [print1d xv=0.018]

        } 
         
    }
    close $f2


if {0} {
    for {set d 3.45} {$d < [expr $bias + 0.001]} {set d [expr $d+0.0005]} {
        set f [open $ivCSV a]
        contact name=D supply=$d
        device
        set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}] 
        #FLOOXS GIVES A/um
        puts $f "$d, $cur"
        close $f
        chart graph=IV curve=DrainCur xval=$d yval=$cur leg.left
        if { 1.0 } {
            #sel z=log10(abs(Acceptor)+1.0)
            #sel z=Acceptor
            #plot1d graph=Acceptor xv=0.018 ylab="AcceptorOccupation" title="Acceptor" name="Vds=$d"
            sel z=log10(abs(Donor)+1.0)
            #sel z=Donor
            plot1d graph=Donor xv=0.010 xmax=0.5 xmin=0.0 ylab="DonorOccupation" title="Donor" name="Vds=$d" log

            #sel z=Acceptor-Donor name=NetTrap
            #plot1d graph=NetTrap xv=0.018 ylab="NetTrapOccupation" title="NetTrapOccupationLevel" name="Vds=$d"

            
            sel z=[expr {"Qfn"}]
            plot1d graph=Elec xv=0.018 ylab="Qfn(eV)" title="GaN" name="Vds=$d" 

            sel z=[expr {"Econd-Qfn-0.59"}]
            plot1d graph=Hole xv=0.018 xmax=0.5 xmin=0.0 ylab="Econd(eV)-Qfn-Etrap" title="GaN" name= "Vds=$d"
            #plot1d graph=Lateral yv=0.01 ylab="AcceptorTrapOccupation" title="TrapOccupationLevel" name="Vds=$d" penstyle=solid ymin=-0.5 ymax=0.5
        }        
    }
}
    if {0} {
        device time=300 t.ini=1.0e-13 userstep=1.0e-12 movie= {

            set d [expr 2.1 + (0.1 * $Time) / 1.0e-6]
            contact name=D supply=$d


            set cur [expr {abs([contact name=D sol=Qfn flux])*1.0e6}] 
            chart graph=IV curve=DrainCur xval=$d yval=$cur leg.left
            if { [nearHalfVolt $d 0.001] and [d >  2.0   ]} {
                sel z=log10(abs(Acceptor)+1.0)
                plot1d graph=Vertical xv=0.01 ylab="AcceptorTrapOccupation" title="TrapOccupationLevel" name="Vds=$d" log
                #plot1d graph=Lateral yv=0.01 ylab="AcceptorTrapOccupation" title="TrapOccupationLevel" name="Vds=$d" penstyle=solid ymin=-0.5 ymax=0.5
            }
        }
    }

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


trapPlot "figures/radPlot.csv" 10