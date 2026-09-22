source run_measurements_E.tcl
window row=1 col=1

if {1} {
    set trapEn 0
    set ::pGaN 1.0
    source powerdevice.tcl
    source GaN_modelfile_masterD
    run_measurements_E "figures/powerIV.csv" "null" fieldplate
}

if {0} {
    set trapEn 0
    set ::pGaN 1.0
    source powerdevice.tcl
    source GaN_modelfile_masterD
    run_measurements_E "figures/SiNpowerIV.csv" "null" fieldplate
}

if {0} {
    set trapEn 1
    set trapLevel 3.0
    source fieldplate.tcl
    source GaN_modelfile_masterD
    run_measurements "figures/null.csv" "null" fieldplate
}