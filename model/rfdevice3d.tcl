# 3D slice of the HEMT in rfdevice.tcl (2026-11-12, kb/model/3d-plan.md): the same 2D cross-section
# extruded along z (the gate-width direction) over 0..W3d um. Every region spans the full z range
# (a plain extrusion, which avoids FLOOXS's MakeInterfaces failure for uneven 3-material corners).
# The side walls z = 0 and z = W3d are reflecting (zero normal flux), so a track at z = 0 stands for a
# row of tracks spaced 2*W3d apart along the width. Contact current is the total through the slice;
# the driver divides by W3d (deviceDim 3).
# Levers (info exists defaults):
#   passMat   HighK | Nitride   passivation above the gate nitride (HighK deck or SiN deck)
#   W3d       slice width (um)
#   zSpac0    z spacing at the track wall z = 0 (um); zSpac1 at z = W3d
#   bot3d     buffer depth (um); the 2D deck uses 7.5
#   yCoarse   factor on the y spacing away from the gate, field plate and drain edge
#   init3d    init options ("quad nogas": bricks, no gas region)
#   meshY     as in rfdevice.tcl
if {![info exists passMat]} { set passMat HighK }
if {![info exists W3d]}     { set W3d 0.5 }
if {![info exists zSpac0]}  { set zSpac0 0.02 }
if {![info exists zSpac1]}  { set zSpac1 0.1 }
if {![info exists bot3d]}   { set bot3d 7.5 }
if {![info exists yCoarse]} { set yCoarse 1.0 }
if {![info exists init3d]}  { set init3d "quad nogas" }

pdbSetDouble Math iterLimit 300
math device dim=3 col umf none scale

mater add name=Metal
mater add name=Nitride
mater add name=GaN
mater add name=AlGaN
mater add name=HighK alias=highk
mater add name=HighK alias=Highk

math diffuse dim=3 umf none col !scale

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
set Al_Thick 0.015

proc HEMT_Struct3d { } {
    global Gate_Length Al_Thick SourceGate SourceT DrainGate DrainT FP2 FP_Offset FP_Thick Gate_Thick SiN_Thick HPD_Thick
    global passMat W3d zSpac0 zSpac1 bot3d yCoarse init3d
    set P $passMat
    set c $yCoarse
    set Mid_Point 0.0
    set Gtl [expr {$Mid_Point - ($Gate_Length/2.0)}]
    set Gtr [expr {$Mid_Point + ($Gate_Length/2.0)}]
    set bot $bot3d

    line x loc=-1.0 spac=0.05 tag=toptop
    line x loc=[expr 0.0-$SiN_Thick-$HPD_Thick-$FP_Thick] spac=0.05 tag=topFP
    line x loc=[expr 0.0-$Gate_Thick-$HPD_Thick] spac=0.05 tag=bottomFP
    line x loc=[expr 0.0-$Gate_Thick] spac=0.025 tag=topT
    line x loc=[expr 0.0-$SiN_Thick] spac=0.01 tag=topGate
    line x loc=-0.005 spac=0.001 tag=topGateIns
    line x loc=0.0 spac=0.001 tag=AlGaNTop
    line x loc=$Al_Thick spac=0.001 tag=AlGaNBottom
    line x loc=0.1 spac=0.01
    line x loc=$bot spac=0.25 tag=BBottom

    line y loc=[expr $Gtl-$SourceGate-0.125] spac=[expr 0.05*$c] tag=left
    line y loc=[expr $Gtl-$SourceT] spac=0.03 tag=SourceT
    line y loc=[expr $Gtl] spac=0.01 tag=GateL
    line y loc=[expr $Gtr] spac=0.005 tag=GateR
    line y loc=[expr $Gtr+$FP_Offset] spac=0.01 tag=leftFP
    line y loc=[expr $Gtr+$DrainT] spac=0.01 tag=DrainT
    line y loc=[expr $Gtr+$FP2] spac=0.02 tag=rightFP
    line y loc=[expr $Gtr+$DrainGate] spac=[expr 0.05*$c]
    line y loc=[expr $Gtr+$DrainGate+0.125] spac=0.05 tag=right
    if {[info exists ::meshY]} { foreach {yl sl} $::meshY { line y loc=$yl spac=$sl } }

    line z loc=0.0 spac=$zSpac0 tag=zlo
    line z loc=$W3d spac=$zSpac1 tag=zhi
    if {[info exists ::meshZ]} { foreach {zl sl} $::meshZ { line z loc=$zl spac=$sl } }

    set Z "zlo=zlo zhi=zhi"
    eval region Metal xlo=topFP xhi=bottomFP ylo=leftFP yhi=rightFP $Z
    eval region $P xlo=bottomFP xhi=topT ylo=left yhi=right $Z
    eval region $P xlo=topT xhi=topGate ylo=left yhi=SourceT $Z
    eval region Metal xlo=topT xhi=topGate ylo=SourceT yhi=DrainT $Z
    eval region $P xlo=topT xhi=topGate ylo=DrainT yhi=right $Z
    eval region Nitride xlo=topGate xhi=AlGaNTop ylo=left yhi=GateL $Z
    eval region Metal   xlo=topGate xhi=topGateIns ylo=GateL yhi=GateR $Z
    eval region Nitride xlo=topGateIns xhi=AlGaNTop ylo=GateL yhi=GateR $Z
    eval region Nitride xlo=topGate xhi=AlGaNTop ylo=GateR yhi=right $Z
    eval region AlGaN xlo=AlGaNTop xhi=AlGaNBottom ylo=left yhi=right $Z
    eval region GaN xlo=AlGaNBottom xhi=BBottom ylo=left yhi=right $Z

    eval init $init3d

    set buf 0.001
    set zb "zlo=[expr -$buf] zhi=[expr $W3d+$buf]"
    eval contact name=FP Metal xlo=[expr 0.0-$SiN_Thick-$HPD_Thick-$FP_Thick-$buf] xhi=[expr 0.0-$SiN_Thick-$HPD_Thick] ylo=[expr $Gtr+$FP_Offset-$buf] yhi=[expr $Gtr+$FP_Offset+$FP2+$buf] $zb add
    eval contact name=G Metal xlo=[expr 0.0-$SiN_Thick-$buf] xhi=[expr -0.005+$buf] ylo=[expr $Gtl] yhi=[expr $Gtr] $zb add
    set l [expr $Gtl-$SourceGate-0.125]
    eval contact name=S AlGaN ylo=[expr $l-$buf] yhi=[expr $l+$buf] xlo=[expr 0.0-$buf] xhi=[expr $Al_Thick-$buf] $zb add
    set r [expr $Gtr+$DrainGate+0.125]
    eval contact name=D AlGaN ylo=[expr $r-$buf] yhi=[expr $r+$buf] xlo=[expr 0.0-$buf] xhi=[expr $Al_Thick-$buf] $zb add
    eval contact name=B GaN xlo=[expr $bot-$buf] xhi=[expr $bot+$buf] ylo=$l yhi=$r $zb add

    contact name=G current=(Hole_Nitride-Elec_Nitride) voltage supply=0.0
    contact name=B current=(Hole_GaN-Elec_GaN) voltage supply=0.0
    contact name=D current=(Hole_GaN-Elec_GaN) voltage supply=0.0
    contact name=S current=(Hole_GaN-Elec_GaN) voltage supply=0.0
    contact name=FP voltage supply=0.0

    sel z=-8e16*Mater(GaN) name=GaN_Doping
    sel z=1e12 name=AlGaN_Doping
    set le [expr $Gtl-$SourceGate]
    set re [expr $Gtr+$DrainGate]
    sel z=(1e18*(y>$re)+(y<=$re)*1.0e19*exp(-(y-$re)*(y-$re)/(1.5*0.02*0.02)))*(exp(-(x*x)/(2.0*0.03*0.03)))*(x>=0.0) name=Drain_Doping
    sel z=(1e18*(y<$le)+(y>=$le)*1.0e19*exp(-(y-$le)*(y-$le)/(1.5*0.02*0.02)))*(exp(-(x*x)/(2.0*0.03*0.03)))*(x>=0.0) name=Source_Doping
    sel z=GaN_Doping+AlGaN_Doping+Drain_Doping+Source_Doping name=Doping
    sel z=0.22 name=AlN_Ratio
}
HEMT_Struct3d
