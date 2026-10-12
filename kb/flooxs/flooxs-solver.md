---
title: FLOOXS Newton solver
tags: [flooxs, numerics, reference]
source: ~/flooxs/src/diffuse/Newton.cc, BasePDE/Genpde.cc, math/MathParam.cc
---
# FLOOXS Newton solver

`device` assembles all `pde` solutions in all materials into one sparse system and runs Newton (`diffuse/Newton.cc`):

**Loop** (max `Math iterLimit`, default 20): assemble (time `tf`) → linear solve (`math device …`, default UMFPACK LU, time `tb`) → update every node (`Genpde.cc`) → check.

**Iteration table** printed per iteration:
`Iter | assembly s | solve s | linear residual | RHS norm (inf) | update norm (inf) | <sol> <mat> of max RHS | <sol> <mat> of max update`.
The "update" is the *scaled* error k = Δ / (Rel.Error·|value| + Abs.Error), not the raw change. (So `9.49e+01 ETemp GaN` means a scaled update of ~95.)

**Convergence:** update norm < `updateLimit` (1e-3), or RHS norm < `rhsLimit` (1e-8) × the first iteration's, or RHS < `rhsMax` (1e-12) after 3 iterations. Failure if the update or RHS norm exceeds 1e40 or is non-finite, or the limit is reached. `iterLimit 1` always "converges" (one step; used for debug dumps). `noimpLimit` (10) counts non-improving iterations.

**Per-material/solution error and damping parameters** (pdb `<Mat> <Sol> Abs.Error` default 1e-6, `Rel.Error` 0.01, `DampValue`, `Negative`), read in `Genpde.cc`:
- **Damping** (solution has the `damp` flag and a `DampValue` d): h = |Δ|/d; if h > 1, h → h^0.8 (h ≤ 5) or Cbreak·ln h (h > 5, Cbreak = 5^0.8/ln 5); Δ ← sign·h·d. So steps up to ~d pass unchanged and larger ones are compressed logarithmically. Without `DampValue` the `damp` flag is ignored with a warning; with `DampValue` but no `damp` flag nothing is damped.
- **Positivity** (`!negative` solutions): if a node's update would make it negative, the new value is old·e^(−h) with h = |Δ|/(old + Rel·Abs) capped near 10 — a multiplicative cut, down to ~old·4.5e-5 — and the node gets flagged as a "negative problem". **This branch runs instead of damping**, so a `!negative damp` solution is not damped on large downward steps. (Seen in the [[energy-balance]] debug: ETemp 300 K → 0.3 K ≈ 300·e^−7 after one iteration.)
- `negative` solutions (DevPsi, Qfn, Qfp here) are damped symmetrically.

**Exceptions:** a NaN/inf in an expression evaluation throws from `Values::TestProb`; `DevController` catches it ("Caught Exception!"), `device` returns a Tcl error. Retry only with `device store` / `device restore` ([[munmap-crash]], [[retry-bisection]]).

**Linear solvers** (`math`): `col umf none scale` (UMFPACK, the default for 2D device) — "Error in UMFPACK numeric factorization" means a singular/ill-conditioned matrix (e.g. near-empty equation rows). Alternatives: `row ilu bcgs|gmres tolerance= max.iter=`, Eigen `eigencol`/`eigenrow` (and a `cudss` flag for the Eigen row format).
