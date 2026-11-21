# Appended after pulsedIV.tcl (run with Vd_max 0): attempt the 0 -> $dbgVd step
# with Newton capped at 1 and then 2 iterations, and dump fields after each, to
# find where the ETemp update goes wrong. Output: dbg_<it>_<field>.txt cuts and
# DBGPEAK lines (peak = max over the material, peakneg = max of -field).
if {![info exists dbgVd]} { set dbgVd 0.1 }
proc DbgDump {tag} {
    global eTemp
    set fields {ETemp Qfn Elec DevPsi}
    if {$eTemp} { lappend fields Delta }
    foreach fld $fields {
        if {$fld eq "Delta"} {
            if {[catch {sel z=[ElecDelta]} e]} { puts "DBG Delta sel failed: $e"; continue }
        } else {
            sel z=$fld
        }
        foreach m {GaN AlGaN} {
            puts "DBGPEAK $tag $fld $m peak=[peak $m]"
        }
        set f [open "dbg_${tag}_${fld}.txt" w]
        foreach xc {0.0 0.008 0.016 0.03 0.1 0.5 1.0} {
            puts $f "# $fld along y at x = $xc um"
            puts $f [print1d xv=$xc]
        }
        foreach yc {-0.401 -0.124 0.001 0.126 0.201 0.501 1.001 2.001} {
            puts $f "# $fld along x at y = $yc um"
            puts $f [print1d yv=$yc]
        }
        close $f
        if {$fld ne "Delta"} {
            sel z=-1.0*$fld
            foreach m {GaN AlGaN} { puts "DBGPEAK $tag $fld $m peakneg=[peak $m]" }
        }
    }
}
DbgDump it0
device store
foreach it {1 2} {
    contact name=D supply=$dbgVd
    pdbSetDouble Math iterLimit $it
    set rc [catch {device} msg]
    puts "DBG device iterLimit=$it rc=$rc msg=[string range $msg 0 200]"
    DbgDump it$it
    device restore
    contact name=D supply=0.0
}
pdbSetDouble Math iterLimit 20
puts "DBG done"
