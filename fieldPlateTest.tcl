# Field-plate / dielectric check (2026-10-01, CLAUDE.md 10l): trap-free, Vg=-2,
# Vd 0.5-20 V in 0.5 V steps. Run once per device deck from a wrapper that sets
# deviceDeck and tag, then sources this file, e.g.
#   set deviceDeck rfdevice_SiN.tcl
#   set tag sin
#   source fieldPlateTest.tcl
# Writes fp_<tag>.csv (Vd, Id mA/mm, peak |grad Qfn| in the channel region V/cm,
# position of that peak, local-field Te with Run F hotTau) and, at Vd = 3/10/20 V,
# print.1d cuts along the 2DEG (x=0.016 um) of |grad Qfn| (cutE_<tag>_<Vd>.txt)
# and DevPsi (cutPsi_<tag>_<Vd>.txt). plot_fieldPlate.py makes figures/fieldPlate*.
if {![info exists deviceDeck]} { set deviceDeck rfdevice.tcl }
if {![info exists tag]} { set tag highk }
set trapEn 0
set hotTau 1.3e-13
set hotEb 0.5
source GaN_modelfile_masterD
source $deviceDeck
foreach m {GaN AlGaN Nitride} { pdbSetDouble $m DevPsi DampValue 0.05 }
pdbSetDouble GaN Qfn DampValue 0.05
pdbSetDouble GaN Qfp DampValue 0.05
puts "RELEPS HighK=[pdbGetDouble HighK DevPsi RelEps] Nitride=[pdbGetDouble Nitride DevPsi RelEps] Metal=[pdbGetDouble Metal DevPsi RelEps]"
Initialize
device init
for {set g -0.1} {$g > -2.001} {set g [expr {$g - 0.1}]} { contact name=G supply=$g; device }
set mask "(x>0.0)*(x<0.05)*(y>-0.5)*(y<3.0)"
set f [open fp_$tag.csv w]; puts $f "Vd,Id,Epk_Vcm,Epk_y,Te_pk"; close $f
for {set d 0.5} {$d < 20.01} {set d [expr {$d + 0.5}]} {
    contact name=D supply=$d
    device
    set id [expr {abs([contact name=D sol=Qfn flux])*1.0e6}]
    sel z=sqrt(dot(Qfn,Qfn))*$mask name=Ech
    set p [peak GaN]
    set pa [peak AlGaN]
    set ep [lindex $p 1]; set ey [lindex $p 3]
    if {[lindex $pa 1] > $ep} { set ep [lindex $pa 1]; set ey [lindex $pa 3] }
    sel z=[HotTeExpr]*$mask name=TeC
    set te [lindex [peak GaN] 1]
    set f [open fp_$tag.csv a]; puts $f "$d,$id,$ep,$ey,$te"; close $f
    puts "FP Vd=$d Id=$id Epk=$ep at=$ey Te=$te"
    if {abs($d-3.0)<1e-6 || abs($d-10.0)<1e-6 || abs($d-20.0)<1e-6} {
        set dd [format %g $d]
        sel z=sqrt(dot(Qfn,Qfn))
        set c [open cutE_${tag}_$dd.txt w]; puts $c [print.1d x.value=0.016]; close $c
        sel z=DevPsi
        set c [open cutPsi_${tag}_$dd.txt w]; puts $c [print.1d x.value=0.016]; close $c
    }
}
