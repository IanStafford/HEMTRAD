proc Poisson {Mat} {
    global VtRoom k q eps0
    pdbSetDouble $Mat DevPsi DampValue $VtRoom
    pdbSetDouble $Mat DevPsi Abs.Error 1.0e-1
    pdbSetDouble $Mat DevPsi Rel.Error 1.0e-1

    set eqn "- ($eps0 * [pdbDelayDouble $Mat DevPsi RelEps] * grad(DevPsi) / $q) + Doping - NeutralAcceptor - Elec + Hole"
    #set eqn "- ($eps0 * [pdbDelayDouble $Mat DevPsi RelEps] * grad(DevPsi) / $q) + Doping - Elec + Hole"
    # To let the mobility model work with new acceptor term.
    solution name=Acceptor solve $Mat const val = 0.0
    solution name=NeutralAcceptor solve $Mat const val = 1.0
    pdbSetString $Mat DevPsi Equation $eqn
}

proc InsPoisson {Mat} {
    global VtRoom k q eps0

    pdbSetDouble $Mat DevPsi DampValue $VtRoom
    pdbSetDouble $Mat DevPsi Abs.Error 1.0e-2
    pdbSetDouble $Mat DevPsi Rel.Error 1.0e-2
    set eqn "- ($eps0 * [pdbDelayDouble $Mat DevPsi RelEps] * grad(DevPsi) / $q) + Doping" 
    pdbSetString $Mat DevPsi Equation $eqn
}

proc AcceptorTrapOld {Mat Ntrap Etrap Efwhm} {
    global k q

    set Acceptor [solution name=Acceptor $Mat print]
    set Vt ($k*Temp/$q)

    #do a switch so we can figure out testing...
    if {$Efwhm == 0.0} {
	set e1 0.0
	set e2 "(($Ntrap) / (1 + 4.0 * exp( (Eval + $Etrap - Qfp) / ($Vt) )))"
	set e3 0.0
    } else {
	#set the evaluation point for the Gaussian-Hermite Quadrature
	set Off [expr sqrt(12.0)*$Efwhm/2.0]
	set e1 "(($Ntrap/6.0) * ((1 / (1 + 4.0 * exp( (Eval + $Etrap + $Off - Qfp) / ($Vt) )))))"
	set e2 "((2.0*$Ntrap/3.0) * ((1 / (1 + 4.0 * exp( (Eval + $Etrap - Qfp) / ($Vt) )))))"
	set e3 "(($Ntrap/6.0) * ((1 / (1 + 4.0 * exp( (Eval + $Etrap - $Off - Qfp) / ($Vt) )))))"
    }
    set Acceptor "$Acceptor + $e1 + $e2 + $e3"
    solution name=Acceptor $Mat solve const val = "$Acceptor"
}

proc AcceptorTrap {Mat Ntrap Etrap Efwhm} {
    global k q eps0 sigma mean_x mean_y

    #set Acceptor [solution name=Acceptor $Mat print]
    set Vt ($k*Temp/$q)
    pdbSetDouble $Mat DevPsi DampValue $Vt
    pdbSetDouble $Mat DevPsi Abs.Error 1.0e-1
    pdbSetDouble $Mat DevPsi Rel.Error 1.0e-1
    #do a switch so we can figure out testing...
    #solution name=TrapConc solve $Mat const val = ($Ntrap)

    if {$Efwhm == 0.0} {
        set e1 0.0
        set e2 "(($Ntrap) / (1 + 4.0 * exp( (Eval + $Etrap - Qfn) / ($Vt) )))"
        set e3 0.0
    } else {
        #set the evaluation point for the Gaussian-Hermite Quadrature
        set sigma [expr $Efwhm/2.355]
        set Off   [expr sqrt(3.0)*$sigma]
        set e1 "((1.0/6.0) * ((1 / (1 + 4.0 * exp( (Eval + $Etrap + $Off - Qfp) / ($Vt) )))))"
        set e2 "((2.0/3.0) * ((1 / (1 + 4.0 * exp( (Eval + $Etrap - Qfp) / ($Vt) )))))"
        set e3 "((1.0/6.0) * ((1 / (1 + 4.0 * exp( (Eval + $Etrap - $Off - Qfp) / ($Vt) )))))"
        #set e1 "((1.0/6.0) * ((1 / (1 + 4.0 * exp( (Qfp - (Eval + $Etrap + $Off)) / ($Vt) )))))"
        #set e2 "((2.0/3.0) * ((1 / (1 + 4.0 * exp( (Qfp - (Eval + $Etrap)) / ($Vt) )))))"
        #set e3 "((1.0/6.0) * ((1 / (1 + 4.0 * exp( (Qfp - (Eval + $Etrap - $Off)) / ($Vt) )))))"
    }
    set Acceptor "$Ntrap * ($e1 + $e2 + $e3) + 1.0"
    solution name=Acceptor solve $Mat const val = ($Acceptor)

    #set eqn "- ($eps0 * [pdbDelayDouble $Mat DevPsi RelEps] * grad(DevPsi) / $q) + Doping - Acceptor - Elec + Hole"
    #pdbSetString $Mat DevPsi Equation $eqn
}

proc NeutralAcceptor {Mat Ntrap Etrap Efwhm} {
    global k q eps0 sigma mean_x mean_y

    #set Acceptor [solution name=Acceptor $Mat print]
    set Vt ($k*Temp/$q)
    pdbSetDouble $Mat DevPsi DampValue $Vt
    pdbSetDouble $Mat DevPsi Abs.Error 1.0e-1
    pdbSetDouble $Mat DevPsi Rel.Error 1.0e-1

    #do a switch so we can figure out testing...
    #solution name=TrapConc solve $Mat const val = ($Ntrap)

    if {$Efwhm == 0.0} {
        set e1 0.0
        set e2 "(($Ntrap) / (1 + 4.0 * exp( (Econd - $Etrap - Qfn) / ($Vt) )))"
        set e3 0.0
    } else {
        #set the evaluation point for the Gaussian-Hermite Quadrature
        set sigma [expr $Efwhm/2.355]
        set Off   [expr sqrt(3.0)*$sigma]
        if {1} {
            set e1 "((1.0/6.0) * ((1 / (1 + 2.0 * exp( (Econd - $Etrap + $Off - Qfn) / ($Vt) )))))"
            set e2 "((2.0/3.0) * ((1 / (1 + 2.0 * exp( (Econd - $Etrap - Qfn) / ($Vt) )))))"
            set e3 "((1.0/6.0) * ((1 / (1 + 2.0 * exp( (Econd - $Etrap - $Off - Qfn) / ($Vt) )))))"
        } else {
            set e1 "((1.0/6.0) * ((1 / (1 + 4.0 * exp( ($Etrap + $Off - Qfn) / ($Vt) )))))"
            set e2 "((2.0/3.0) * ((1 / (1 + 4.0 * exp( ($Etrap - Qfn) / ($Vt) )))))"
            set e3 "((1.0/6.0) * ((1 / (1 + 4.0 * exp( ($Etrap - $Off - Qfn) / ($Vt) )))))"
        }
    }
    set NeutralAcceptor "$Ntrap - $Ntrap * ($e1 + $e2 + $e3)"
    #set NeutralAcceptor "($e1 + $e2 + $e3)"
    solution name=NeutralAcceptor solve $Mat const val = ($NeutralAcceptor)
    
    #set eqn "- ($eps0 * [pdbDelayDouble $Mat DevPsi RelEps] * grad(DevPsi) / $q) + Doping + NeutralAcceptor - Elec + Hole"
    #pdbSetString $Mat DevPsi Equation $eqn
}