# Electron energy balance (hydrodynamic-like electron temperature ETemp).
# Enabled with the eTemp lever in GaN_modelfile_masterD; with eTemp 0, ETemp is
# a constant 300 K solution and nothing here is used.
#
#   1.5 k n dTe/dt - div(1.5 k Te n mu grad(Qfn))      convective energy flux (r = 0.6)
#                  - div(1.5 k Te n mu grad(k Te))     heat conduction
#                  - n mu |grad Qfn|^2                 Joule heating (J.E)
#                  + 1.5 k n (Te - T) / tau            energy relaxation to the lattice
#   (etThermo 1: J includes the thermoelectric grad(Te) part, see Continuity.tcl)
#
# Same form as Sentaurus' hydrodynamic electron energy equation with Qfn,Qfn as
# the heat source. Levers (GaN_modelfile_masterD): etTau (tau), etMob (which
# mobility the heating and flux terms use: low = low-field mobility, field = the
# same field-dependent mobility as the current, so J.E is consistent).
proc ElecTemperature {Mat} {
    global etTau etMob mobModel
    set keV 8.625e-5
    set tau $etTau

    if {$etMob eq "field" || $mobModel ne "field"} {
        # static mobility model has no lowfldmob; use the continuity mobility
        set mob ([pdbDelayDouble $Mat Elec mob])
    } else {
        set mob ([pdbDelayDouble $Mat Elec lowfldmob])
    }

    pdbSetDouble $Mat ETemp Rel.Error 1.0e-2
    pdbSetDouble $Mat ETemp Abs.Error 1.0e-2
    pdbSetDouble $Mat ETemp DampValue 5.0
    set Ele "(Elec+1.0)"

    #Sentaurus version with Qfn,Qfn as heat source
    #                   eV     cm-3   /s          cm2 (integration in 2D) = ev / cm s
    set HeatCap "(1.5 * $keV * $Ele * ddt(ETemp))"
    #                     eV             cm-3   cm2/Vs  (V Gauss's Law in 2D) =  ev / cm s
    set HeatFlux1 "(1.5 * $keV * ETemp * $Ele * $mob * grad(Qfn))"
    #                     eV             cm-3   cm2/Vs  (V Gauss's Law in 2D) = ev / cm s
    set HeatFlux2 "(1.5 * $keV * ETemp * $Ele * $mob * $keV * grad(ETemp))"
    #              cm-3   cm2/Vs   V/cm V/cm * cm2  eV / cm s
    set HeatGen  "($Ele * $mob * dot(Qfn,Qfn))"
    #                       eV     cm-3                  / s  cm2 (integration in 2D) eV/ cm s
    set EnergyRelax "(1.5 * $keV * $Ele * (ETemp - Temp) / $tau)"

    global etStats etThermo
    if {$etStats && $etThermo} {
        # the current now has a grad(Te) part (Continuity.tcl ElecDelta); carry
        # it into the convective energy flux and the Joule heating J.grad(EFn)
        set D [ElecDelta]
        set HeatFlux1 "(1.5 * $keV * ETemp * $Ele * $mob * grad(Qfn)) + (1.5 * $keV * ETemp * $Ele * $mob * $keV * $D * grad(ETemp))"
        set HeatGen  "($Ele * $mob * (dot(Qfn,Qfn) + $keV * $D * dot(Qfn,ETemp)))"
    }
    set eqn "$HeatCap - $HeatFlux1 - $HeatFlux2 - $HeatGen + $EnergyRelax"
    pdbSetString $Mat ETemp Equation "$eqn"
}

# Ohmic contacts inject electrons at the lattice temperature.
proc ETempContact {Contact} {
    pdbSetDouble $Contact ETemp Rel.Error 1.0e-2
    pdbSetDouble $Contact ETemp Abs.Error 1.0e-2
    pdbSetBoolean $Contact ETemp Fixed 1
    pdbSetString $Contact ETemp Equation "ETemp-300.0"
}
