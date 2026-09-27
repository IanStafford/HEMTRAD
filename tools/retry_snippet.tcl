# Tested retry logic for the pulsedIV.tcl Vd loop (2026-09-27, task 64 of
# job 43373001). Not yet wired into pulsedIV.tcl - pending Ian's OK.
# --- retry test: attempt each Vd point in catch; on failure restore the
# solution (device store/restore) and trap memory, then bisect the Vd step.
set retryDepth 5
set dPrev 0.0
set nRetry 0
proc TryPoint {d} {
    global fillIters fillRelax
    if {[catch {
        contact name=D supply=$d
        device
        set ::te [FillStep $fillIters $fillRelax]
    } msg]} { return 0 }
    return 1
}
proc SaveState {} {
    sel z=TrapFrozen name=TFsave
    sel z=TeTrap name=TEsave
    device store
}
proc RestoreState {dPrev} {
    device restore
    sel z=TFsave name=TrapFrozen
    sel z=TEsave name=TeTrap
    contact name=D supply=$dPrev
}
# reach d from the current converged point dPrev, bisecting on failure
proc Reach {dPrev d depth} {
    SaveState
    if {[TryPoint $d]} { return 1 }
    incr ::nRetry
    puts "RETRY Vd $dPrev -> $d failed (depth $depth), bisecting"
    RestoreState $dPrev
    if {$depth <= 0} { return 0 }
    set mid [expr {0.5 * ($dPrev + $d)}]
    if {![Reach $dPrev $mid [expr {$depth - 1}]]} { return 0 }
    return [Reach $mid $d [expr {$depth - 1}]]
}
sel z=TrapFrozen name=TFsave
sel z=TeTrap name=TEsave

