pdbSetDouble Math iterLimit 300
math device dim=2 col umf none scale

mater add name=Metal
mater add name=Nitride
mater add name=GaN
mater add name=AlGaN
mater add name=HighK alias=highk
mater add name=HighK alias=Highk

math diffuse dim=2 umf none col !scale 

set Gate_Length 0.250
set SourceGate 1.0
set DrainGate 3.16
set SourceT 0.200
set DrainT 0.360
set FP2 0.6
set FP_Offset 0.160

set SiN_Thick 0.05
set HPD_Thick 0.100
set FP_Thick 0.420
set Gate_Thick 0.200
set Al_Thick 0.015 ;# 15nm AlGaN thickness


proc HEMT_Struct { } {
    global Gate_Length Al_Thick SourceGate SourceT DrainGate DrainT FP2 FP_Offset FP_Thick Gate_Thick SiN_Thick HPD_Thick

    #Structure definition (AlGaN is 25nm thick.It is below the critical thickness for relaxation ~65nm Ambacher)
    set Mid_Point 0.0
    set Gtl [expr {$Mid_Point - ($Gate_Length/2.0)}]
    set Gtr [expr {$Mid_Point + ($Gate_Length/2.0)}]
  
    set bot 7.5
    line x loc=-1.0 spac=0.05 tag=toptop
    line x loc=[expr 0.0-$SiN_Thick-$HPD_Thick-$FP_Thick] spac=0.05 tag=topFP
    line x loc=[expr 0.0-$Gate_Thick-$HPD_Thick] spac=0.05 tag=bottomFP
    line x loc=[expr 0.0-$Gate_Thick] spac=0.025 tag=topT
    line x loc=[expr 0.0-$SiN_Thick] spac=0.01 tag=topGate
    line x loc=-0.005 spac=0.001 tag=topGateIns
    line x loc=0.0 spac=0.001 tag=AlGaNTop
    line x loc=$Al_Thick spac=0.001 tag=AlGaNBottom
    line x loc=0.1 spac=0.01
    line x loc=7.5 spac=0.25 tag=BBottom

    line y loc=[expr $Gtl-$SourceGate-0.125] spac=0.05 tag=left
    line y loc=[expr $Gtl-$SourceT] spac=0.03 tag=SourceT
    line y loc=[expr $Gtl] spac=0.01 tag=GateL
    line y loc=[expr $Gtr] spac=0.005 tag=GateR
    line y loc=[expr $Gtr+$FP_Offset] spac=0.01 tag=leftFP
    line y loc=[expr $Gtr+$DrainT] spac=0.01 tag=DrainT
    line y loc=[expr $Gtr+$FP2] spac=0.02 tag=rightFP
    line y loc=[expr $Gtr+$DrainGate] spac=0.05 
    line y loc=[expr $Gtr+$DrainGate+0.125] spac=0.05 tag=right

    #work layers top down, left to right
    region Metal xlo=topFP xhi=bottomFP ylo=leftFP yhi=rightFP

    region HighK xlo=bottomFP xhi=topT ylo=left yhi=right
    
    #t gate layer
    region HighK xlo=topT xhi=topGate ylo=left yhi=SourceT
    region Metal xlo=topT xhi=topGate ylo=SourceT yhi=DrainT
    region HighK xlo=topT xhi=topGate ylo=DrainT yhi=right

    #gate layer
    region Nitride xlo=topGate xhi=AlGaNTop ylo=left yhi=GateL
    region Metal   xlo=topGate xhi=topGateIns ylo=GateL yhi=GateR
    region Nitride xlo=topGateIns xhi=AlGaNTop ylo=GateL yhi=GateR
    region Nitride xlo=topGate xhi=AlGaNTop ylo=GateR yhi=right

    #AlGaN GaN under gate
    region AlGaN xlo=AlGaNTop xhi=AlGaNBottom ylo=left yhi=right
    region GaN xlo=AlGaNBottom xhi=BBottom ylo=left yhi=right

    init 

    set buf 0.001

    #Contacts
    contact name=FP Metal xlo=[expr 0.0-$SiN_Thick-$HPD_Thick-$FP_Thick-$buf] xhi=[expr 0.0-$SiN_Thick-$HPD_Thick] ylo=[expr $Gtr+$FP_Offset-$buf] yhi=[expr $Gtr+$FP_Offset+$FP2+$buf] add depth=1.0 width=1.0
    contact name=G Metal xlo=[expr 0.0-$SiN_Thick-$buf] xhi=[expr -0.005+$buf] ylo=[expr $Gtl] yhi=[expr $Gtr] add depth=1.0 width=1.0
    # contact name=G AlGaN xlo=[expr 0.0-$buf] xhi=0.001 ylo=[expr $Gtl+$buf] yhi=[expr $Gtr-$buf] add depth=1.0 width=1.0
    #contact name=G Nitride xlo=[expr -0.006] xhi=-0.001 ylo=[expr $Gtl+$buf] yhi=[expr $Gtr-$buf] add depth=1.0 width=1.0

    set l [expr $Gtl-$SourceGate-0.125] 
    contact name=S AlGaN ylo=[expr $l-$buf] yhi=[expr $l+$buf] xlo=[expr 0.0-$buf] xhi=[expr $Al_Thick-$buf] add depth=1.0 width=1.0
    set r [expr $Gtr+$DrainGate+0.125]
    contact name=D AlGaN ylo=[expr $r-$buf] yhi=[expr $r+$buf] xlo=[expr 0.0-$buf] xhi=[expr $Al_Thick-$buf] add depth=1.0 width=1.0
    contact name=B GaN xlo=[expr $bot-$buf]  xhi=[expr $bot+$buf] ylo=$l yhi=$r add depth=1.0 width=1.0

    contact name=G current=(Hole_Nitride-Elec_Nitride) voltage supply=0.0
    contact name=B current=(Hole_GaN-Elec_GaN) voltage supply=0.0
    contact name=D current=(Hole_GaN-Elec_GaN) voltage supply=0.0
    contact name=S current=(Hole_GaN-Elec_GaN) voltage supply=0.0
    contact name=FP voltage supply=0.0
      
    #doping definition-will use method from pfmos_qf deck for simplicity
    #GaN Doping-from Dessis file from Heller-acceptor-p-type
    sel z=-8e16*Mater(GaN) name=GaN_Doping

    #AlGaN Doping-from Dessis file from Heller-he puts equivalent donor and acceptor doping in region to signify traps
    sel z=1e12 name=AlGaN_Doping

    #Source and Drain contact doping-from contact to 2DEG like Heller-just to make contacts ohmic
    set le [expr $Gtl-$SourceGate]
    set re [expr $Gtr+$DrainGate]
    sel z=(1e18*(y>$re)+(y<=$re)*1.0e19*exp(-(y-$re)*(y-$re)/(1.5*0.02*0.02)))*(exp(-(x*x)/(2.0*0.03*0.03)))*(x>=0.0) name=Drain_Doping
    sel z=(1e18*(y<$le)+(y>=$le)*1.0e19*exp(-(y-$le)*(y-$le)/(1.5*0.02*0.02)))*(exp(-(x*x)/(2.0*0.03*0.03)))*(x>=0.0) name=Source_Doping

    #Total doping
    sel z=GaN_Doping+AlGaN_Doping+Drain_Doping+Source_Doping name=Doping

    sel z=0.22 name=AlN_Ratio
}
HEMT_Struct

