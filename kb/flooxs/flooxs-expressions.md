---
title: FLOOXS expression language
tags: [flooxs, reference]
source: ~/flooxs/src/BasePDE/lexical.cc, math/Vector.cc
---
# FLOOXS expression language

Equations, `const` solutions and `sel` all take **expression strings** built from solution/field names, numbers and the functions below. They are parsed once (at `device init` for equations) and differentiated symbolically for the Newton Jacobian.

- **Operators:** `+ - * /`, `^` (power), comparisons `< > <= >= == !=`, `&& ||`, ternary `?:`. Comparisons and `?:` are step functions (zero derivative): fine in `sel`/doping (`(y>$re)` in `model/rfdevice.tcl`), bad inside Newton equations.
- **Math:** `exp log log10 sqrt sin cos tan asin acos atan erf erfc abs sign randn`. There is **no `min`/`max`/`pow` function**: the decks write max as `0.5*(a+b+abs(a-b))` (kinked — Newton can cycle on it, [[flooxs-gotchas]]) and powers as `exp(log(a)*b)` or `^`.
- **Fermi integrals:** `f12`/`F12`/`fermi_1/2`, `f32`, `fn12`, `fn32`. Normalised so F_j(η) → e^η for η → −∞ (Blakemore form; f12 ≈ η^1.5/Γ(2.5), f32 ≈ 0.3009 η^2.5 for large η), piecewise series in `math/Vector.cc` (η < 0, 0…4, > 4). `exp` of a large argument overflows → "computed a nan or infinite".
- **Differential operators:** `grad(S)` in an equation is the flux term of S (assembled over element edges, i.e. the divergence of `coef·∇S` in the box method), e.g. continuity `ddt(Elec) + mob*(Elec+1e2)*grad(Qfn)`. `ddt(S)` time derivative (0 in a steady `device`). `dot(A,B)` = ∇A·∇B (so `sqrt(dot(DevPsi,DevPsi))` = |E| in V/cm); `dot(DevPsi, y*1e-4)` projects on y. `gradx/grady/gradz`, `maggrad`, `sgrad`, `delta`.
- **Geometry and globals:** `x`, `y`, `z` (µm in the decks' expressions, e.g. trap Gaussians in µm; gradients are per cm and `peak` prints cm), `Mater(<M>)`/`NotMater(<M>)` (indicator), `Temp`, `time`.
- **Tcl interplay:** the string is built by Tcl first, so `$var` substitutes numbers and `[pdbDelayDouble …]` inlines stored expressions ([[flooxs-pdb]]). Build long expressions in a Tcl variable and pass `val = ($e)` to avoid the word-splitting error.
- **Constant folding:** a `sel` field that is spatially constant at `device init` is folded in as a literal (use `1e-30*(1+x*x)` to keep it live); redefining a `const` solution after `device init` doesn't reach the assembled equations ([[flooxs-gotchas]]).
