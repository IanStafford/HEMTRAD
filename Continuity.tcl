# Thermoelectric coefficient of the electron current with a carrier temperature:
#   J = n mu grad(EFn) + n mu k Delta grad(Te),  Delta = 2.5 F3/2(eta)/F1/2(eta) - eta,
# eta = (EFn - Ec)/kTe (FLOOXS f12/f32 are normalized so F_j -> exp(eta)).
# Boltzmann limit: Delta = 5/2 - eta; degenerate 2DEG: Delta -> 0.
proc ElecDelta {} {
    global k q
    set eta "((Qfn-Econd)/($k*ETemp/$q))"
    return "(2.5*f32($eta)/f12($eta)-$eta)"
}

proc ElecContinuity {Mat} {
    global Vt eTemp etStats etThermo

    pdbSetDouble $Mat Qfn Rel.Error 1.0e-2
    pdbSetDouble $Mat Qfn Abs.Error 1.0e-2
    pdbSetDouble $Mat Qfn DampValue 0.1

    set eqn "ddt(Elec) + ([pdbDelayDouble $Mat Elec mob]) * (Elec+1.0e2) * grad(Qfn)"
    if {$eTemp && $etStats && $etThermo} {
        # thermal diffusion (Seebeck) part of the current, consistent with
        # electron statistics at ETemp
        append eqn " + ([pdbDelayDouble $Mat Elec mob]) * (Elec+1.0e2) * 8.617e-5 * [ElecDelta] * grad(ETemp)"
    }
    pdbSetString $Mat Qfn Equation $eqn

    set e "([pdbDelayDouble $Mat Elec Ec])"
    solution add name=Econd solve $Mat const val = ($e)

    # electron statistics at the electron temperature ETemp (constant 300 K
    # unless the eTemp lever solves it); etStats 0 keeps them at the lattice Temp
    global etStats k q
    if {$etStats} {
        set VtE "($k*ETemp/$q)"
        set Nc "([pdbDelayDouble $Mat Elec Nc]) * exp(1.5*log(ETemp/Temp))"
    } else {
        set VtE $Vt
        set Nc "([pdbDelayDouble $Mat Elec Nc])"
    }
    set e "$Nc * f12( -(Econd-Qfn) / ($VtE) )"
    solution add name=Elec solve $Mat const val = "($e)"
}

proc HoleContinuity {Mat} {
    global Vt

    pdbSetDouble $Mat Qfp Rel.Error 1.0e-2
    pdbSetDouble $Mat Qfp Abs.Error 1.0e-2
    pdbSetDouble $Mat Qfp DampValue 0.1

    set eqn "ddt(Hole) - ([pdbDelayDouble $Mat Hole mob]) * (Hole+1.0e2) * grad(Qfp)"
    pdbSetString $Mat Qfp Equation $eqn

    set e "([pdbDelayDouble $Mat Hole Ev])"
    solution add name=Eval solve $Mat const val = ($e)

    set e "([pdbDelayDouble $Mat Hole Nv]) * f12( -(Qfp - Eval) / ($Vt) )"
    solution name=Hole solve $Mat const val = "($e)"
}

