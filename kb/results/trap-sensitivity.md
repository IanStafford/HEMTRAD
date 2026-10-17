---
title: Trap-model sensitivity (one lever at a time)
tags: [results, model]
date: 2026-10-17
---
# Trap-model sensitivity, one lever at a time

Ian asked to see how each trap-model lever acts on its own, with the Gaussian and its placement fixed.
- **Job:** 46462234 (`sweeps/pulsedIV_sensitivity.slurm`, `sweeps/params_sensitivity.txt`), 34 tasks, all reached 4 V, no give-ups, 19–40 min each.
- **Analysis:** `analysis/plot_sensitivity.py` → `figures/sensitivity.png` (onset, deepest drop and drop at 4 V, Id just before the onset vs trap-free), `figures/sensitivity_IdVd.png`, `figures/sensitivity_metrics.csv`.
- **Baseline:** the late set at y = 1.0 µm ([[late-onset-search]]):
  - Gaussian (fixed): 5e18 cm⁻³, σ 40 nm, x 0.
  - Trap and capture levers: level 0.30 eV, width 0.1, `hotEb` 1.0, `hotTau` 1e-14, `hotMu` 600, `hotVsat` 1.9e7.
  - Fill: `fillIters` 4, `fillRelax` 0.5.
  - Sweep: `eTemp` 0, field mobility, Vg −2, Vd 0–4 V in 0.1 V steps.
  - It collapses deep at **2.3 V** (same as round 3), down to 1.85e4× below trap-free at 2.6 V. It then **recovers to 23× by 4 V** (Id 0.01 → 8 mA/mm).

| Lever | Values (baseline ★) | Onset (V) | Deepest drop | Notes |
|---|---|---|---|---|
| `trapLevel` (eV) | 0.20, 0.25, **0.30★**, 0.35, 0.40, 0.50 | none, none, 2.3, 1.3, 0.9, 0.4 | 1.1, 1.1, 1.9e4, 3.6e7, 1.1e8, 7e8 | Strongest lever. A cliff between 0.25 and 0.30: nothing, then deep. Deeper levels sag Id before the collapse (0.78 / 0.57 / 0.37 of trap-free) and stay down with a creep. |
| `hotEb` (eV) | 0.5, 0.75, **1.0★**, 1.25, 1.5 | none, 3.2 (medium), 2.3, 1.8, 1.6 | 1.2, 3, 1.9e4, 2e6, 3e11 | Strongest depth lever. At 1.5 Id is already at 12% of trap-free before the drop. |
| `hotTau` (s) | 5e-15, 7e-15, **1e-14★**, 1.5e-14, 2e-14, 3e-14 | none, 3.3 (medium), 2.3, 1.6, 1.3, 1.1 | 1.2, 3.8, 1.9e4, 1.8e8, 8e8, 4e9 | Onset ≈ ∝ 1/√τ; ≥ 1.5e-14 stays collapsed (no recovery). |
| `hotVsat` (cm/s) | 1e7, 1.5e7, **1.9e7★**, 2.5e7, 3e7 | 3.6 (medium), 2.7 (medium), 2.3, 2.0, 1.9 | 2, 10, 1.9e4, 6e4, 1.2e6 | Sets the saturated drift velocity in Te; as strong as `hotMu` on the onset. |
| `hotMu` (cm²/Vs) | 300, 450, **600★**, 900, 1200 | 3.2 (medium), 2.7 (medium), 2.3, 1.9, 1.8 | 7, 18, 1.9e4, 1.2e5, 8e5 | Te only; weaker above 600 because v saturates. |
| `trapWidth` (eV) | 0.02, 0.05, **0.1★**, 0.2, 0.3 | 2.6, 2.5, 2.3, 2.0, 2.0 | 41, 280, 1.9e4, 7e3, 1.7e4 | Weak on onset; narrow widths give shallow drops. |
| `fillIters` | 1, 2, **4★**, 8 | 2.8, 2.6, 2.3, 2.2 | 33, 890, 1.9e4, 1.8e4 | 4 → 8 moves the onset only 0.1 V: the fills per point are near-converged at the baseline. |
| `fillRelax` | 0.25, **0.5★**, 0.75, 1.0 | 2.5, 2.3, 2.3, 2.2 | 6.6e3, 1.9e4, 1.0e4, 1.0e4 | Weakest lever. |

## Reading
- **Three groups:**
  - **Trap/capture physics** (`trapLevel`, `hotEb`, `hotTau`) sets onset and depth together. It moves the onset by 1–2 V and the depth by orders of magnitude.
  - **Te-model inputs** (`hotMu`, `hotVsat`) move the onset 1.4–1.7 V across a 4× (`hotMu`) or 3× (`hotVsat`) range. Their effect on depth is smaller.
  - **Numerics of the fill** (`fillIters`, `fillRelax`) and the **energy width** move it ≤ 0.6 V.
- **There is a threshold.** Below a critical capture strength the collapse disappears, or turns medium (2–20×) and late: level ≤ 0.25 eV, `hotEb` ≤ 0.75, `hotTau` ≤ 7e-15, `hotMu` ≤ 450, `hotVsat` ≤ 1.5e7. The baseline sits just above it. That is why it collapses late (2.3 V) and why it recovers.
- **Depth and recovery are linked.** Sets just over the threshold collapse 1e2–1e4× and then recover strongly with Vd. Stronger sets go to ≤ 1e-5 mA/mm and stay there with a slight creep. The measured ~1000× drop with creep sits between the two.
- **No single lever gives the measured onset (0.4–0.5 V, ~1000×) from this baseline.** `trapLevel` 0.50 collapses at 0.4 V, but 7e8× deep and from a current already sagged to 37% of trap-free.
- `fillIters` 4 vs 8 agree within one step. Here the fill per Vd point is close to converged, unlike the virtual-gate FN capture ([[vg-dependence]]).

Related: [[levers]], [[hot-electron-capture]], [[trap-model]], [[collapse-classification]].
