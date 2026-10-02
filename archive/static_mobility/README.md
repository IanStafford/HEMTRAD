# Static-mobility archive (2026-09-23 to 2026-10-01)

Everything here was simulated with the old default `mobModel static` (constant
GaN electron mobility 600 cm²/V·s). On 2026-10-01 the deck was calibrated against
the measured HfO2 transfer curve (CLAUDE.md §10.1) and the field-dependent mobility
(`mobModel field`) replaced it. Results in this folder are kept for reference but
are superseded.

- **Write-ups:** `RESULTS.md` here (the old CLAUDE.md §10-§10l, verbatim). File
  names there refer to this folder. CLAUDE.md §10.4 summarizes the lessons.
- **Snapshot:** branch `static-mobility` (commit d2eda77) has every file in its
  original place, if anything here needs to be rerun exactly as it was.
- **Contents:** sweep `pulsedIV_*.slurm` / `params_*.txt` (late-onset rounds A-I,
  trap placement, 50-location map, conc × level × position, 10f map sets, cone,
  critical-strike band, x-y map + sign-0 companion, deep traps, HighK vs SiN),
  their analysis scripts (`analyze_*.py`, `critical_strike.py`,
  `plot_*.py`), old drivers (`fieldpeak.tcl` — note its HighK εr bug,
  `transfer.tcl`, `run_measurements.tcl`, `mobilityCompare.tcl`, `IV.tcl` — which
  sources a missing `powerdevice.tcl`), and `figures/` with all their outputs.
- **Raw results** (not in git): `results/archive_static_mobility/` on the
  workstation; the HPG copies are still under `results/` there. The analysis
  scripts here read the workstation archive paths; run them from the repo root
  (`python3 archive/static_mobility/analyze_trapCone.py ...`). They write into
  the root `figures/`, so move any regenerated output back here.
- `figures.ipynb` cells that load `figures/pulsedIV_F.csv`, `hotStressIV_*`,
  `mobility_*` or `rfDeviceHFO2_Simulated.csv` now need the
  `archive/static_mobility/figures/` prefix.
