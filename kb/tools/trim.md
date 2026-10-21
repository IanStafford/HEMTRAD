---
title: TRIM (SRIM-2013) under Wine
tags: [tools, radiation]
date: 2026-10-21
source: http://www.srim.org
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

**Template** `drivers/trim/TRIM_HEMT_template.IN`: the device stack, top down ([[device-structure]]):

| Layer | Thickness | Density |
|---|---|---|
| HfO2 | 100 nm | 9.68 g/cm³ |
| Si3N4 | 50 nm | 3.17 g/cm³ |
| Al0.22Ga0.78N | 15 nm | 5.51 g/cm³ (linear AlN/GaN) |
| GaN | 7.5 µm | 6.15 g/cm³ |

- Quick (Kinchin–Pease) cascades; writes RANGE and TRANSMIT.
- **The ion line (10 MeV Au, 20 ions) is a format-test placeholder.** The real ion species, energy and fluence come from Ian (pending, 2026-10-21).
- **To review before production runs:**
  - The displacement / lattice / surface binding energies are generic SRIM-style defaults. GaN literature values (e.g. Ga ~20 eV, N ~11 eV) would change the vacancy counts.
  - The SiN density depends on the deposition process.
  - Use Full cascade (type 2) if the cascade shape matters.

**Use in the model:** a TRIM vacancy profile could replace the Gaussian via a new `TrapConc_<name>` proc (`trapShape` lever, [[levers]]). First refine the access-region mesh ([[mesh]]). TRIM is 1D in depth plus lateral spread; the single-cascade 2D-vs-3D question is in [[critical-strike]].
