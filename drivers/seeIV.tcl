# Single-event transient (heavy-ion strike) on the calibrated HEMT deck (branch
# explore/rad-model; plan kb/results/see-plan.md).
#
# 1. DC steady state at the strike bias (Vg_bias, then Vd_bias; traps off).
# 2. Inject a charge-neutral electron-hole plasma along a vertical ion track at y = seeY0
#    by resetting the quasi-Fermi levels (the solution variables):
#      n = n_ss + dN, p = p_ss + dN,  Qfn = Econd + Vt*F12inv(n/Nc), Qfp = Eval - Vt*F12inv(p/Nv)
#    F12inv is Nilsson's closed form (<0.5% vs FLOOXS f12 for eta -30..25). Equal dN keeps
#    the charge neutral, so Poisson is consistent at t = 0.
#    dN(x,y) = seePairs/(seeWeff*sqrt(2 pi)*seeSigma) * exp(-(y-y0)^2/(2 sigma^2)) for
#    seeXmin <= x <= seeXmax in GaN/AlGaN: a 2D slab of the track's charge per unit
#    depth spread over an effective width seeWeff (the 2D-normalisation lever).
# 3. Transient to seeTend with log-growing steps; terminal currents every step.
#
# Outputs (prefix $tag): <tag>_see.csv (t, then Qfn/Qfp/DevPsi flux per contact, A/um),
# <tag>_summary.txt, <tag>_cuts_<k>.txt (Elec, Hole, DevPsi along y at x 0.016 / 0.5 um).
# seeStrike 0 runs the same transient without injection (control).

if {![info exists tag]}        { set tag see }
if {![info exists deviceDeck]} { set deviceDeck rfdevice.tcl }
if {![info exists mobModel]}   { set mobModel field }
if {![info exists eTemp]}      { set eTemp 0 }
if {![info exists dampValue]}  { set dampValue 0.05 }
if {![info exists retryDepth]} { set retryDepth 6 }
if {![info exists Vg_bias]}    { set Vg_bias -10.0 }
if {![info exists Vd_bias]}    { set Vd_bias 28.0 }
if {![info exists Vd_rampStep]} { set Vd_rampStep 1.0 }
# strike
if {![info exists seeStrike]}  { set seeStrike 1 }
if {![info exists seeY0]}      { set seeY0 1.0 }      ;# um, strike position along the channel
if {![info exists seeSigma]}   { set seeSigma 0.05 }  ;# um, track radius (Gaussian sigma)
if {![info exists seeWeff]}    { set seeWeff 1.0 }    ;# um, effective width of the 2D slab
if {![info exists seePairs]}   { set seePairs 4.3e10 } ;# pairs/cm along the track (Au 2256 MeV, ~41 keV/nm, ~9.5 eV/pair)
if {![info exists seeXmin]}    { set seeXmin 0.0 }    ;# um, track starts at the AlGaN top
if {![info exists seeXmax]}    { set seeXmax 1.4 }    ;# um, GaN:Fe buffer thickness (SiC below is not in the deck)
if {![info exists seeTinit]}   { set seeTinit 1.0e-15 }
if {![info exists seeTend]}    { set seeTend 1.0e-9 }
if {![info exists seeUserStep]} { set seeUserStep 0.0 } ;# 0 = no cap on the time step
if {![info exists seeCutTimes]} { set seeCutTimes {1e-13 1e-12 1e-11 1e-10 1e-9 1e-8 1e-7} }
set trapEn 0

if {![info exists modelDir]} {
    if {[file exists GaN_modelfile_masterD]} { set modelDir . } elseif {[file isdirectory model]} { set modelDir model } else { set modelDir [file join [file dirname [info script]] .. model] }
}
source [file join $modelDir GaN_modelfile_masterD]
source [file join $modelDir $deviceDeck]
foreach m {GaN AlGaN Nitride} { pdbSetDouble $m DevPsi DampValue $dampValue }
pdbSetDouble GaN Qfn DampValue $dampValue
pdbSetDouble GaN Qfp DampValue $dampValue
if {[info exists qfnAbs]} { foreach m {GaN AlGaN} { pdbSetDouble $m Qfn Abs.Error $qfnAbs } }
# radIV gets these DevPsi tolerances from IonizedAcceptor (trap model on); with traps off
# they stay at FLOOXS's 1e-6 default and the drain ramp crawls (job 48227316), so set
# them here as radIV has them (read when the solver is built, i.e. before device init)
foreach m {GaN AlGaN} { pdbSetDouble $m DevPsi Abs.Error 1.0e-1; pdbSetDouble $m DevPsi Rel.Error 1.0e-1 }
Initialize
device init

proc TryBias {c v} {
    if {[catch { contact name=$c supply=$v; device }]} { return 0 }
    return 1
}
proc Reach {c vPrev v depth} {
    device store
    if {[TryBias $c $v]} { return 1 }
    puts "RETRY $c $vPrev -> $v failed (depth $depth)"
    device restore
    contact name=$c supply=$vPrev
    if {$depth <= 0} { return 0 }
    set mid [expr {0.5 * ($vPrev + $v)}]
    if {![Reach $c $vPrev $mid [expr {$depth - 1}]]} { return 0 }
    return [Reach $c $mid $v [expr {$depth - 1}]]
}
proc Ramp {c a b st} {
    set n [expr {max(1, int(ceil(abs($b - $a) / $st - 1e-9)))}]
    set prev $a
    for {set i 1} {$i <= $n} {incr i} {
        set v [expr {$a + ($b - $a) * $i / double($n)}]
        if {![Reach $c $prev $v $::retryDepth]} { puts "RAMP GAVE UP $c at $v"; return 0 }
        set prev $v
    }
    return 1
}
proc Flux {c s} {
    if {[catch {set f [contact name=$c sol=$s flux]}]} { return nan }
    return $f
}

set sf [open ${tag}_summary.txt w]
puts $sf "deck $deviceDeck Vg $Vg_bias Vd $Vd_bias strike $seeStrike y0 $seeY0 sigma $seeSigma Weff $seeWeff pairs/cm $seePairs x $seeXmin..$seeXmax"
flush $sf

# 1. DC steady state at the strike bias
if {![Ramp G 0.0 $Vg_bias 0.5]} { puts $sf "gate ramp failed"; close $sf; error "gate ramp" }
if {![Ramp D 0.0 $Vd_bias $Vd_rampStep]} { puts $sf "drain ramp failed"; close $sf; error "drain ramp" }
set contacts {S D G FP B}
set line "DC"
foreach c $contacts { foreach s {Qfn Qfp} { append line " $c.$s=[Flux $c $s]" } }
puts $sf $line; flush $sf

# 2. inject the plasma
if {$seeStrike} {
    set sem "(Material(GaN)+Material(AlGaN))"
    set other "(1.0-$sem)"
    set Nc "(([pdbDelayDouble GaN Elec Nc])*Material(GaN)+([pdbDelayDouble AlGaN Elec Nc])*Material(AlGaN)+$other)"
    set Nv "(([pdbDelayDouble GaN Hole Nv])*Material(GaN)+([pdbDelayDouble AlGaN Hole Nv])*Material(AlGaN)+$other)"
    set s_cm [expr {$seeSigma * 1.0e-4}]
    set N0 [expr {$seePairs / ($seeWeff * 1.0e-4 * sqrt(2.0 * 3.14159265358979) * $s_cm)}]
    set dN "($N0*exp(-((y-($seeY0))*(y-($seeY0)))/(2.0*$seeSigma*$seeSigma))*(x>=$seeXmin)*(x<=$seeXmax)*$sem)"
    sel z=$dN name=SeeDN
    # Nilsson inverse of the normalised F1/2: eta(u) = ln u/(1-u^2) + v/(1+(0.24+1.08 v)^-2), v = (3 sqrt(pi) u/4)^(2/3)
    proc F12inv {u} {
        set v "exp((2.0/3.0)*log(1.329340388*($u)))"
        return "(log($u)/(1.0-($u)*($u)+1.0e-9)+($v)/(1.0+1.0/((0.24+1.08*($v))*(0.24+1.08*($v)))))"
    }
    set un "((Elec+SeeDN)/$Nc+1.0e-280)"
    set up "((Hole+SeeDN)/$Nv+1.0e-280)"
    sel z=Qfn name=QfnSS
    sel z=Qfp name=QfpSS
    sel z=Elec name=ElecSS
    sel z=Hole name=HoleSS
    set Vt "($k*Temp/$q)"
    sel z=($sem*(Econd+$Vt*[F12inv $un])+$other*QfnSS) name=Qfn
    sel z=($sem*(Eval-$Vt*[F12inv $up])+$other*QfpSS) name=Qfp
    sel z=Elec-ElecSS name=dElecChk
    sel z=SeeDN name=z
    puts $sf "injected peak dN [lindex [peak GaN] 1] /cm3 (N0 $N0)"
    sel z=dElecChk
    puts $sf "check: peak Elec - Elec_ss after reset [lindex [peak GaN] 1] /cm3 (should be ~ peak dN)"
    flush $sf
}

# 3. transient
set cf [open ${tag}_see.csv w]
set hdr "t"
foreach c $contacts { foreach s {Qfn Qfp DevPsi} { append hdr ",$c.$s" } }
puts $cf $hdr
set ::cutTimes [lsort -real $seeCutTimes]
set ::cutK 0
proc LogStep {} {
    global cf contacts tag
    sel z=Time
    set t [lindex [peak GaN] 1]
    set line $t
    foreach c $contacts { foreach s {Qfn Qfp DevPsi} { append line ",[Flux $c $s]" } }
    puts $cf $line; flush $cf
    while {$::cutK < [llength $::cutTimes] && $t >= [lindex $::cutTimes $::cutK]} {
        set c2 [open ${tag}_cuts_$::cutK.txt w]
        puts $c2 "# t = $t"
        foreach fld {Elec Hole DevPsi} {
            sel z=$fld
            foreach xc {0.016 0.5} { puts $c2 "# $fld along y at x = $xc"; if {[catch {puts $c2 [print1d xv=$xc]}]} { puts $c2 "{ cut failed }" } }
        }
        close $c2
        incr ::cutK
    }
}
if {$seeUserStep > 0.0} {
    set rc [catch {device time=$seeTend t.init=$seeTinit userstep=$seeUserStep movie= {LogStep}} msg]
} else {
    set rc [catch {device time=$seeTend t.init=$seeTinit movie= {LogStep}} msg]
}
if {$rc} {
    puts $sf "transient stopped: $msg"
} else {
    puts $sf "transient done to $seeTend"
}
close $cf
puts $sf "done"
close $sf
puts "SEEIV DONE tag=$tag"
