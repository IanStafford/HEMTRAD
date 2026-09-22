# =============================================================================================================
# New metal code with schottky contact and option for thermionic emission current as well as ohmic pGaN contact
# =============================================================================================================

mater add name=Metal    

pdbSetDouble Metal Temp Abs.Error 0.1
pdbSetDouble Metal Temp Rel.Error 1.0e-2
pdbSetDouble Metal Temp DampValue 10.0

pdbSetDouble Metal DevPsi RelEps 1.0e12

#create a procedure for ohmic contacts
proc Ohmic {Mat Contact} {
    global Vt

    pdbSetDouble $Contact Qfp Rel.Error 1.0e-2
    pdbSetDouble $Contact Qfp Abs.Error 1.0e-2
    pdbSetDouble $Contact Qfp DampValue 0.025
    pdbSetDouble $Contact Qfn Rel.Error 1.0e-2
    pdbSetDouble $Contact Qfn Abs.Error 1.0e-2
    pdbSetDouble $Contact Qfn DampValue 0.025
    pdbSetDouble $Contact DevPsi Rel.Error 1.0e-2
    pdbSetDouble $Contact DevPsi Abs.Error 1.0e-2
    pdbSetDouble $Contact DevPsi DampValue 0.025

    #set all quantities fixed here
    pdbSetBoolean $Contact Qfn Fixed 1
    pdbSetBoolean $Contact Qfp Fixed 1
    pdbSetBoolean $Contact DevPsi Fixed 1

    #we'd like to keep fluxes around
    pdbSetBoolean $Contact Qfn Flux 1
    pdbSetBoolean $Contact Qfp Flux 1
    pdbSetBoolean $Contact DevPsi Flux 1

    pdbSetDouble $Contact Qfn Flux.Scale 1.602e-19
    pdbSetDouble $Contact Qfp Flux.Scale 1.602e-19
    pdbSetDouble $Contact DevPsi Flux.Scale 1.602e-19

    pdbSetString $Contact DevPsi Equation "Doping-Elec+Hole"
    pdbSetString $Contact Qfn Equation "Qfn+$Contact"
    pdbSetString $Contact Qfp Equation "Qfp+$Contact"
}

Ohmic AlGaN S
Ohmic AlGaN D
Ohmic GaN B

if {![info exists pGaN]} { set pGaN 0.0 }
set phiB 1.65; # Placeholder for field plate when using pGaN contact

if {!$pGaN} {
    # Ambacher's formula can be applied when we have AlGaN/Metal or potentially with a thin layer of Nitride,
    # but not with pGaN/Metal, so only set phiB if we don't have a pGaN contact
    # 1.3x+0.84, where x is the Al mole fraction, so with x=0.26, this gives 1.2255 eV, but I don't know if Ambacher's formula applies to GaN/Metal contacts,
    # so I'm using a higher value that is more consistent with the literature for GaN/Metal schottky contacts

    # Fieldplate electrostatics - Present in both the schottky and ohmic cases, but with different phiB

    # Using AlGaN Ec because we aren't getting current through it anyway.
    # If we used Nitride Ec we would have diff model for gate and FP
    pdbSetString FP DevPsi Equation "([pdbDelayDouble Nitride Elec Ec])+FP-$phiB"
    pdbSetBoolean FP DevPsi Fixed 1
    pdbSetDouble FP DevPsi Flux.Scale 1.602e-19

    # Schottky Contact - assume that the contact itself is in contact with the AlGaN or very close thru thin layer of SiN
    pdbSetString G DevPsi Equation "([pdbDelayDouble Nitride Elec Ec])+G-$phiB"
    pdbSetBoolean G DevPsi Fixed 1
    pdbSetDouble G DevPsi Flux.Scale 1.602e-19

    # Pin holes, leave Qfn floating
    pdbSetString G Qfp Equation "Qfp+G"
    pdbSetBoolean G Qfp Fixed 1
    #pdbSetDouble G Qfp Flux.Scale 1.602e-19
    #set eqn "200 * 5.0e12 * grad(Qfp)"
    #pdbSetString Metal Qfp Equation $eqn

} else {
    # We treat the pGaN contact as ohmic, so we pin both holes and electrons, and use the GaN Ec for the electrostatics since we are in direct contact with the GaN.
    Ohmic GaN G
}

proc InitMetal {} {
    global phiB
    sel z = "Mater(Metal) * ( ([pdbDelayDouble AlGaN Affinity])+$phiB)" name=MetalDevPsi
}

