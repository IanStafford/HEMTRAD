window row=1 col=3
source run_measurements.tcl

set trapEn 0
pdbSetDouble HighK DevPsi RelEps 6.3
source rfdevice.tcl
source GaN_modelfile_masterD
run_measurements "figures/SiN_rf_IV.csv" "figures/50V_plot_HighK.csv" HighK
