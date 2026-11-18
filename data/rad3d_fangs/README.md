Id-Vd curves (Vd, Id_dev, Id_ext, peak Te) copied 2026-11-18 from the HEMTRAD-FANGS session's HPG results
(/blue/ee1/ianstafford/HEMTRAD-FANGS/repo/results/20261117_*) (the old HPG checkout; the reorganised FANGS project is .../HEMTRAD-FANGS/proj, where the Tcl results moved to runs/tcl/), rad3dRod tasks on the FANGS port. Model output only.
- before_full: rod_full, stock brick gradients (job 51784599, STRUMPACK)
- after_full: rod_full with the brick-gradient fix (51824509, STRUMPACK); after_full_bcgs (51824508_0, BiCGSTAB, partial)
- after_half, after_quarter: rods over half / a quarter of the slice width, with the fix (51824508_1/_2, partial)
- ref2d: 2D reference (rad3dRod task 3, damGauss at the same spot; agrees with FLOOXS 51784349 to 2e-5)
