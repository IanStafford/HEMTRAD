# Field-plate / dielectric check, trap-free (port of archive/static_mobility/
# fieldPlateTest.tcl, 2026-10-16, with the calibrated field-dependent mobility).
# Vg = -2 V, Vd 0.5-20 V in 0.5 V steps, on one device deck:
#   set deviceDeck rfdevice_SiN.tcl ; set tag sin ; source drivers/fieldPlate.tcl
# Writes fp_<tag>.csv (Vd, Id mA/mm, peak |grad Qfn| in the channel region V/cm,
# position of that peak, local-field Te) and, at Vd = 3/10/20 V, print.1d cuts
# along the 2DEG (x = 0.016 um) of |grad Qfn| (cutE_<tag>_<Vd>.txt) and DevPsi
# (cutPsi_<tag>_<Vd>.txt). analysis/plot_fieldPlate.py makes the figures.
if {![info exists deviceDeck]} { set deviceDeck rfdevice.tcl }
if {![info exists tag]}        { set tag highk }
if {![info exists mobModel]}   { set mobModel field }
if {![info exists eTemp]}      { set eTemp 0 }
if {![info exists dampValue]}  { set dampValue 0.05 }
if {![info exists retryDepth]} { set retryDepth 5 }
set trapEn 0
# Te column only (no traps): the late-set local-field values
if {![info exists hotTau]} { set hotTau 1.0e-14 }
if {![info exists hotEb]}  { set hotEb 1.0 }

if {![info exists modelDir]} {
    if {[file exists GaN_modelfile_masterD]} { set modelDir . } elseif {[file isdirectory model]} { set modelDir model } else { set modelDir [file join [file dirname [info script]] .. model] }
}
source [file join $modelDir GaN_modelfile_masterD]
source [file join $modelDir $deviceDeck]
foreach m {GaN AlGaN Nitride} { pdbSetDouble $m DevPsi DampValue $dampValue }
pdbSetDouble GaN Qfn DampValue $dampValue
pdbSetDouble GaN Qfp DampValue $dampValue
puts "RELEPS HighK=[pdbGetDouble HighK DevPsi RelEps] Nitride=[pdbGetDouble Nitride DevPsi RelEps] mobModel=$mobModel"
Initialize
device init
for {set g -0.1} {$g > -2.001} {set g [expr {$g - 0.1}]} { contact name=G supply=$g; device }

# Reach Vd = d from the converged dPrev, bisecting on failure (device store /
# restore around every attempt, CLAUDE.md section 6).
proc Reach {dPrev d depth} {
    device store
    if {![catch { contact name=D supply=$d; device }]} { return 1 }
    puts "RETRY Vd $dPrev -> $d failed (depth $depth), bisecting"
    device restore
    contact name=D supply=$dPrev
    if {$depth <= 0} { return 0 }
    set mid [expr {0.5 * ($dPrev + $d)}]
    if {![Reach $dPrev $mid [expr {$depth - 1}]]} { return 0 }
    return [Reach $mid $d [expr {$depth - 1}]]
}

set mask "(x>0.0)*(x<0.05)*(y>-0.5)*(y<3.0)"
set f [open fp_$tag.csv w]; puts $f "Vd,Id,Epk_Vcm,Epk_y,Te_pk"; close $f
set dPrev 0.0
for {set d 0.5} {$d < 20.01} {set d [expr {$d + 0.5}]} {
    if {![Reach $dPrev $d $retryDepth]} { puts "FP GAVE UP at Vd=$d"; break }
    set dPrev $d
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
puts "FP DONE tag=$tag last Vd=$dPrev"
