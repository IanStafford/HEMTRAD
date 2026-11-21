---
title: TRIM (SRIM-2013) under Wine
tags: [tools, radiation]
date: 2026-11-20
source: http://www.srim.org; drivers/trim/*.IN; bin/trim_run.sh; analysis/trimTrack.py; analysis/genRad3d.py; data/trim/*_track.json; progress.md 2026-10-21 and 2026-11-12
---
# TRIM (SRIM-2013) on the workstation

TRIM/SRIM (Ziegler) is a Windows program. HPG has no SRIM module (the `nxtrim` module there is unrelated), so it runs on the **workstation under Wine 10**.

**Install** (2026-10-21):
- **Package:** SRIM-2013-Pro, downloaded from srim.org (37,493,456 bytes, sha256 `07f7f46d…05cb40`). Kept in `~/opt/srim-2013/` (the original `.exe` and an unpacked copy in `src/`). It was extracted with `7z`, without running the self-extractor.
- **Wine prefix:** a separate `~/.wine-srim`, so `~/.wine` is untouched. SRIM lives in `C:\SRIM` = `~/.wine-srim/drive_c/SRIM`.
- **VB5 runtime:** `MSVBvm50.exe /Q`. The installer returned exit code 5, but `msvbvm50.dll` is in `syswow64`, which is what SRIM needs.
- **Controls:** the five OCX files from `SRIM-Setup/` (ComCtl32, ComDlg32, MSFlxGrd, RichTx32, TabCtl32) are copied to `syswow64` and registered with `regsvr32`.

**Batch runs:** `bin/trim_run.sh <TRIM.IN> <out_dir>`.
- It copies the input into `C:\SRIM` (converted to CRLF), sets `TRIMAUTO` = 1 (no keyboard input, exits after the last ion) and runs `TRIM.exe`. It then copies `*.txt` and `SRIM Outputs/*.txt` to `<out_dir>`, and restores `TRIM.IN`/`TRIMAUTO` afterwards.
- Only one TRIM runs at a time, because the install directory holds the in-progress files. The wrapper checks with `pgrep -x TRIM.exe`; `pgrep -f` would match the calling shell.
- TRIM opens a window on Ian's desktop (`DISPLAY=:0`) while it runs. Xvfb is not installed (that would need `sudo apt install xvfb`).
- **Checks:** the bundled B → W/SiO2/Si example (200 ions, 54 s; 956 vacancies/ion) and the HEMT template (20 ions, 6 s).
- **Outputs** go to an untracked folder such as `results/trim_SiN/` (`results/` is gitignored).

## Inputs (`drivers/trim/`)

| File | Stack, top down | Ion and cascades | Use |
|---|---|---|---|
| `TRIM_HEMT_template.IN` | HfO2 100 nm / Si3N4 50 nm / Al0.22Ga0.78N 15 nm / GaN 7.5 µm | Au 10 MeV, 20 ions, quick (Kinchin-Pease) cascades; writes RANGE and TRANSMIT | format test (2026-10-21); not a model-deck stack |
| `TRIM_HighK_Au2256.IN` | HfO2 250 nm / Si3N4 50 nm / AlGaN 15 nm / GaN 2 µm | Au 2256 MeV, 200 ions, full cascades, collision details with recoils (`COLLISON.txt`) | HighK deck track, `data/trim/HighK_track.json` |
| `TRIM_SiN_Au2256.IN` | Si3N4 300 nm / AlGaN 15 nm / GaN 2 µm | as the HighK file | SiN deck track, `data/trim/SiN_track.json` |
| `TRIM_HighK_Au2256_test20.IN`, `TRIM_SiN_Au2256_test20.IN` | as the 200-ion files | 20 ions, otherwise identical | smoke tests; nothing else refers to them |

- **The Au2256 stacks are the decks' passivation beside the T-gate head.** `rfdevice.tcl` has 250 nm of HighK (x −0.30 to −0.05 µm) on 50 nm of SiN. `rfdevice_SiN.tcl` has 300 nm of SiN ([[device-structure]]).
- **Densities in all five inputs:** HfO2 9.68, Si3N4 3.17, Al0.22Ga0.78N 5.51 (linear AlN/GaN), GaN 6.15 g/cm³.
- The SiN input declares six elements, including Hf and O, for a stack that contains neither. That is harmless.
- **Inputs that name a measured device stay out of git** (`drivers/trim/*NCY2*` is gitignored).
- **Open caveats, all inputs:**
  - The displacement, lattice and surface binding energies are generic SRIM-style defaults (displacement 25 / 28 / 15 / 28 / 25 / 25 eV for Hf / O / Si / N / Al / Ga). GaN literature values (e.g. Ga ~20 eV, N ~11 eV) would change the vacancy counts.
  - The SiN density depends on the deposition process.

## From TRIM to the model

1. **Run TRIM** on the workstation, e.g. `bin/trim_run.sh drivers/trim/TRIM_SiN_Au2256.IN results/trim_SiN` (22 s for 200 ions).
2. **Summarise the track:** `python3 analysis/trimTrack.py results/trim_SiN SiN data/trim/SiN_track.json`.
   - It reads `COLLISON.txt` and works per layer, with the GaN split into three sub-layers (top 50 nm, 50-500 nm, 0.5-2 µm).
   - Per ion it gives the vacancies per nm, the radial width sigma (from ⟨r²⟩ = 2 sigma²), the radii r50 and r90 that hold 50% and 90% of the vacancies, the on-axis density of that Gaussian and the electronic stopping Se.
   - Its totals agree with TRIM's `VACANCY.txt` within 3% (2026-11-12).
3. **3D params:** `analysis/genRad3d.py` (`tubes()`) turns the SiN JSON into the `damTube` columns of rad3dTrack1. Each AlGaN and GaN sub-layer gets a vacancy tube and an electronic-track core.
   - The vacancy tube has the TRIM vacancies per nm, with a radial sigma of max(TRIM sigma, 20 nm), times eta.
   - The core is a Gaussian of sigma 30 nm with a density of 5e15 × Se (eV/Å) × eta, about 2e19 cm⁻³ in GaN at eta 1.
   - rad3dTrack1 places one such track at y 0.5 µm on the SiN deck.
4. **Not from TRIM:** the rad3dRod `damRod` is the 2D strike spot (Gaussian, 3e18 cm⁻³, sigma 40 nm, y 0.8 µm) run along the gate width. The 2D strikes (`damGauss`) of the step search are set by hand ([[damage-model]]).

**Result of the Au 2256 MeV runs (2026-11-12, [[3d-plan]]).**
- In the top 50 nm of GaN an ion leaves 0.21 (SiN deck) to 0.27 (HighK deck) vacancies per nm, with a median radius of 1.5 to 2.1 nm.
- Most ions leave no vacancy in the 15 nm AlGaN.
- Se in GaN is about 4070 eV/Å (41 keV/nm).
- Nuclear displacements alone are below the collapse threshold, so the electronic track core carries the damage.

**The 3D track runs.** The first FLOOXS rad3dTrack1 runs used hot-electron capture on the stock 3D brick mesh, whose depth gradient is wrong, so they are not valid. The FANGS reruns with the brick fix and the patched FLOOXS copy are in [[3d-plan]]. TRIM gives depth plus lateral spread; the single-cascade 2D-vs-3D question is in [[critical-strike]].
