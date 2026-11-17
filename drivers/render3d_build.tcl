# Build the 3D SiN slice (W3d 1 um) with one Gaussian ion track at y 0.5 um and write VTK for analysis/render3d.py.
# Run from the repo root: flooxs drivers/render3d_build.tcl  (no solve; about 1 min, 45 MB file).
set modelDir model
source model/GaN_modelfile_masterD
set passMat Nitride
set W3d 1.0
set bot3d 1.5
set yCoarse 2.0
set zSpac0 0.02
set zSpac1 0.1
source model/rfdevice3d.tcl
# one ion track: Gaussian column (sigma 30 nm) at y 0.5 um, z 0, through the channel and buffer
sel z=2.0e19*exp(-((y-0.5)*(y-0.5)+z*z)/(2.0*0.03*0.03))*(x>=0.0) name=Track
sel z=log10(abs(Doping)+1.0) name=LogDoping
struct vtk=sin3d.vtk
puts "VTK WRITTEN"
