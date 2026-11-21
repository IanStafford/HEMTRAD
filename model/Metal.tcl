# =============================================================================================================
# New metal code: Schottky gate and field plate, ohmic source/drain/body, and an ohmic pGaN gate option
# =============================================================================================================

mater add name=Metal    

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
if {![info exists phiB]} { set phiB 1.65 } ;# effective gate/FP barrier vs Nitride Ec (eV); sets Vth. With pGaN 1 it only enters InitMetal

if {!$pGaN} {
    # Ambacher's formula can be applied when we have AlGaN/Metal or potentially with a thin layer of Nitride,
    # but not with pGaN/Metal, so only set phiB if we don't have a pGaN contact
    # 1.3x+0.84 eV, where x is the Al mole fraction: 1.178 eV at x = 0.26, 1.126 eV at the deck's AlN_Ratio 0.22.
    # I don't know if Ambacher's formula applies to GaN/Metal contacts, so I'm using a higher value that is more
    # consistent with the literature for GaN/Metal schottky contacts (phiB is a calibration lever, kb/device/calibration.md)

    # Fieldplate electrostatics - set only in this (Schottky) branch; with pGaN 1 this file gives the FP no DevPsi equation

    # The FP and the gate (below) both use the Nitride Ec, so phiB is the effective barrier against the
    # Nitride Ec and the gate and FP share one model.
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

} else {
    # We treat the pGaN contact as ohmic (proc Ohmic): Qfn and Qfp are pinned to the contact bias and DevPsi follows
    # from charge neutrality (Doping-Elec+Hole), as at S, D and B; phiB does not enter the gate equations.
    Ohmic GaN G
}

proc InitMetal {} {
    global phiB
    sel z = "Mater(Metal) * ( ([pdbDelayDouble AlGaN Affinity])+$phiB)" name=MetalDevPsi
}

