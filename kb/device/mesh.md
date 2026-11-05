---
title: Mesh
tags: [device, numerics, caveat]
---
# Mesh

- Depth (`line x`): 1 nm through the AlGaN and the gate insulator, 10 nm to 0.1 µm, 0.25 µm in the deep buffer.
- Lateral (`line y`): **5 nm at the gate**, 10–20 nm at the field plate, **25–40 nm (spacing 0.02 → 0.05) from y ≈ 0.725 µm to the drain**.

**Known problem (static §10h, still applies):** traps narrower than a few cells in the access region are not resolved, even though their total charge is (±15%); the runaway depends on the local field, which a coarse mesh smears.

Local check, 4e18/0.55 at the surface, y = 1.25 µm, with `line y loc=1.25 spac=0.004`:
- A 0.1 µm/45° cone: no effect on the standard mesh, but collapses ~325× at 0.2 V on the 4 nm mesh, so the static-era cone results in the access region are mesh artifacts.
- Gaussian σ 40 nm: still collapses, but onset ~0.1 V earlier and the pre-collapse peak roughly halves on the fine mesh.

So access-region Gaussian results are **qualitatively robust, quantitatively mesh-sensitive** (onset ±0.1 V). Before shape or TRIM work: refine locally (`line y` at `trapMeanY`, ~4 nm) and do an 8/4/2 nm convergence check.

**Uniform sites are worse (2026-11-05, radMesh job 49606872):** a 0.3 µm, 4e18 site gives steps of 84–157 mA/mm on the standard mesh and under 8 at 10 and 5 nm, with Id at 10 V moving from 250–565 to 526–566 mA/mm. The final SiN two-step curve also lost its steps at 10 nm (radFine, job 49735196). Use `meshY` for any sharp-edged site before trusting a step, and 5 nm or finer above about 6e18 ([[damage-region-map]]).

Gotcha: `print1d yv=` exactly on a mesh line at the gate edge (y = −0.125) panics FLOOXS ("WTF in PlotMesh"); offset cuts by ~1 nm ([[flooxs-gotchas]]).

Related: [[device-structure]], [[static-era-lessons]].
