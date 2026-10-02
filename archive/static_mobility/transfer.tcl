source run_measurements.tcl
window row=1 col=1

if {1} {
    set trapEn 0
    source rfdevice.tcl
    source GaN_modelfile_masterD
    run_measurements "figures/rfDeviceHFO2_Simulated.csv" "null" fieldplate
}