proc Poisson {Mat} {
    global VtRoom k q eps0
    pdbSetDouble $Mat DevPsi DampValue $VtRoom
    pdbSetDouble $Mat DevPsi Abs.Error 1.0e-1
    pdbSetDouble $Mat DevPsi Rel.Error 1.0e-1

    set eqn "- ($eps0 * [pdbDelayDouble $Mat DevPsi RelEps] * grad(DevPsi) / $q) + Doping - IonAcceptor - Elec + Hole"
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

# Static trap charge in an insulator (no carriers or Qfn there, so no Fermi or
# hot-electron occupancy): sign = -1 puts the traps in fully filled (-q*Ntrap),
# +1 as fixed positive charge (+q*Ntrap, e.g. trapped holes). Rebuilds the
# InsPoisson equation with the extra term.
proc InsTrapCharge {Mat Ntrap sign} {
    global q eps0
    set eqn "- ($eps0 * [pdbDelayDouble $Mat DevPsi RelEps] * grad(DevPsi) / $q) + Doping + ($sign) * ($Ntrap)"
    pdbSetString $Mat DevPsi Equation $eqn
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
    # When not frozen the charge is max(TrapFrozen, live): TrapFrozen is ~0 after
    # ThawTraps (pure live occupancy), or the charge already captured during a
    # fill-only sweep (FillStep), which the traps can't emit on that time scale.
    set live "(($Ntrap) * $occ)"
    set IonAcceptor "FrozenFlag * TrapFrozen + (1.0 - FrozenFlag) * 0.5 * (TrapFrozen + $live + abs(TrapFrozen - $live))"
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
    sel z=1.0e-30*(1.0+x*x) name=TrapFrozen
    ResetTe
}

# Record the present trapped charge as captured: from now on the traps can fill
# further but not empty (no emission) until ThawTraps.
proc CaptureTraps {} {
    sel z=IonAcceptor name=TrapFrozen
}

# Local-field electron temperature, Te = T + (2/3) tau v(E) E / (k/q), with
# v(E) = mu E / (1 + mu E / vsat). E is the driving field |grad Qfn| (V/cm), not
# |grad DevPsi|, so the built-in polarization field doesn't heat electrons at
# equilibrium.
# With the eTemp lever on, the target is the solved electron temperature ETemp
# instead (clamped at the lattice T, so cooled electrons don't raise the level).
proc HotTeExpr {} {
    global hotTau hotMu hotVsat kev eTemp hotEb capMode capField capBeta
    # Field-driven capture (capMode field, exploratory 2026-10-15): the capture
    # barrier is lowered by the local electric field instead of by hot electrons,
    # Poole-Frenkel-like: dE = capBeta*sqrt(F) (eV, F in V/cm), capped at 0.99*hotEb.
    # Returned as the equivalent TeTrap, T/(1 - dE/hotEb), so IonizedAcceptor,
    # FillStep and the Te ramp are unchanged. capField: lat = |dPsi/dy| (lateral,
    # no polarization field at rest), tot = |grad Psi|, qfn = |grad Qfn|.
    # Gate injection ("virtual gate", capMode gate, exploratory 2026-10-15): electrons
    # leak from the gate's drain edge into surface states and hop along the surface.
    # The supply is set by the peak lateral field at the gate drain edge, Fg (one
    # number per update, ~ Vd - Vg), and decays with distance from the edge:
    # dE = capBeta*sqrt(Fg)*exp(-(y - 0.125)/injLen) for y > 0.125, capped at 0.99*hotEb.
    global injLen
    if {$capMode eq "gate"} {
        set w "exp(-((y - 0.14) / 0.03)^2) * exp(-(x / 0.004)^2)"
        sel z=abs(grady(DevPsi))*$w name=FgTmp
        sel z=FgTmp
        set Fg [lindex [peak AlGaN] 1]
        set ::capFg $Fg
        set d "(0.5 * ((y - 0.125) + abs(y - 0.125)))"
        set dE "([expr {$capBeta * sqrt($Fg)}] * exp(-$d / $injLen))"
        set cap [expr {0.99 * $hotEb}]
        set dEc "(0.5 * ($dE + $cap - abs($dE - $cap)))"
        return "(Temp / (1.0 - $dEc / $hotEb))"
    }
    if {$capMode eq "field"} {
        switch -- $capField {
            lat { set F "abs(grady(DevPsi))" }
            tot { set F "sqrt(dot(DevPsi,DevPsi))" }
            qfn { set F "sqrt(dot(Qfn,Qfn))" }
            default { error "capField must be lat, tot or qfn" }
        }
        set dE "($capBeta * sqrt($F + 1.0e-6))"
        set cap [expr {0.99 * $hotEb}]
        set dEc "(0.5 * ($dE + $cap - abs($dE - $cap)))"
        return "(Temp / (1.0 - $dEc / $hotEb))"
    }
    if {$eTemp} { return "(Temp + 0.5 * (ETemp - Temp + abs(ETemp - Temp)))" }
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

# One pulse-train bias point of a fill-only sweep: iterate Te <-> device solve,
# keeping every electron captured along the way. Returns the final peak Te.
proc FillStep {{iters 4} {w 0.5}} {
    for {set i 1} {$i <= $iters} {incr i} {
        set te [UpdateTe $w]
        device
        CaptureTraps
    }
    return $te
}
