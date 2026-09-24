proc Poisson {Mat} {
    global VtRoom k q eps0
    pdbSetDouble $Mat DevPsi DampValue $VtRoom
    pdbSetDouble $Mat DevPsi Abs.Error 1.0e-1
    pdbSetDouble $Mat DevPsi Rel.Error 1.0e-1

    set eqn "- ($eps0 * [pdbDelayDouble $Mat DevPsi RelEps] * grad(DevPsi) / $q) + Doping - IonAcceptor - Elec + Hole"
    #set eqn "- ($eps0 * [pdbDelayDouble $Mat DevPsi RelEps] * grad(DevPsi) / $q) + Doping - Elec + Hole"
    # To let the mobility model work with new acceptor term.
    solution name=Acceptor solve $Mat const val = 0.0
    solution name=IonAcceptor solve $Mat const val = 0.0
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

# Acceptor trap: neutral when empty, -q when filled with an electron.
# IonAcceptor = Ntrap * f, where f is the electron occupancy of a level Etrap
# below Econd (Gaussian energy spread Efwhm via 3-point Gauss-Hermite).
# The Poisson equation subtracts IonAcceptor as negative charge.
proc IonizedAcceptor {Mat Ntrap Etrap Efwhm {g 2.0}} {
    global k q hotEb

    set Vt ($k*Temp/$q)
    pdbSetDouble $Mat DevPsi DampValue $Vt
    pdbSetDouble $Mat DevPsi Abs.Error 1.0e-1
    pdbSetDouble $Mat DevPsi Rel.Error 1.0e-1

    # Hot-electron capture over a barrier hotEb: capture ~ exp(-hotEb/kTe) while
    # emission stays at the lattice T, which is the same as lowering the trap
    # level by hotEb*(1 - T/Te). TeTrap is a data field set by UpdateTe; with
    # TeTrap = T this is plain Fermi-level occupancy.
    set Et "(Econd - $Etrap - $hotEb * (1.0 - Temp / TeTrap))"

    # f(E) = 1 / (1 + g*exp((E - Qfn)/Vt)), trap level E = Et
    if {$Efwhm == 0.0} {
        set occ "(1.0 / (1.0 + $g * exp( ($Et - Qfn) / ($Vt) )))"
    } else {
        set esig [expr $Efwhm/2.355]
        set Off  [expr sqrt(3.0)*$esig]
        set e1 "((1.0/6.0) / (1.0 + $g * exp( ($Et + $Off - Qfn) / ($Vt) )))"
        set e2 "((2.0/3.0) / (1.0 + $g * exp( ($Et - Qfn) / ($Vt) )))"
        set e3 "((1.0/6.0) / (1.0 + $g * exp( ($Et - $Off - Qfn) / ($Vt) )))"
        set occ "($e1 + $e2 + $e3)"
    }
    # TrapFrozen / FrozenFlag are data fields (read at solve time), so the
    # trapped charge can be switched between live and frozen without device init.
    set IonAcceptor "FrozenFlag * TrapFrozen + (1.0 - FrozenFlag) * ($Ntrap) * $occ"
    solution name=IonAcceptor solve $Mat const val = ($IonAcceptor)
}

# Freeze the trapped charge at its present value. Deep traps (0.6-0.8 eV) emit
# on a ~s-100s time scale, so after a stress bias the occupancy is fixed for a
# measurement much faster than that (pulsed IV / quick DC sweep).
proc FreezeTraps {} {
    sel z=IonAcceptor name=TrapFrozen
    sel z=1.0+1.0e-30*x*x name=FrozenFlag
}

# Let the traps follow the local Fermi level again (steady state), cold electrons.
proc ThawTraps {} {
    sel z=1.0e-30*(1.0+x*x) name=FrozenFlag
    ResetTe
}

# Local-field electron temperature, Te = T + (2/3) tau v(E) E / (k/q), with
# v(E) = mu E / (1 + mu E / vsat). E is the driving field |grad Qfn| (V/cm), not
# |grad DevPsi|, so the built-in polarization field doesn't heat electrons at
# equilibrium.
proc HotTeExpr {} {
    global hotTau hotMu hotVsat kev
    set E "sqrt(dot(Qfn,Qfn))"
    set v "($hotMu * $E / (1.0 + $hotMu * $E / $hotVsat))"
    return "(Temp + (2.0/3.0) * $hotTau * $v * $E / $kev)"
}

# Move TeTrap a fraction w of the way to the local-field Te (under-relaxed so
# the trap charge change per solve stays small). Returns the peak Te.
proc UpdateTe {{w 0.5}} {
    sel z=[HotTeExpr] name=TeTarget
    sel z=TeTrap+$w*(TeTarget-TeTrap) name=TeTrap
    sel z=TeTrap
    return [lindex [peak GaN] 1]
}

proc ResetTe {} {
    sel z=Temp+1.0e-12*(1.0+x*x) name=TeTrap
}

# At the present bias, iterate Te <-> device solve until the traps settle.
proc HotStress {{iters 8} {w 0.5}} {
    for {set i 1} {$i <= $iters} {incr i} {
        set te [UpdateTe $w]
        device
        puts "HotStress iter $i peak Te(GaN) = $te K"
    }
}
