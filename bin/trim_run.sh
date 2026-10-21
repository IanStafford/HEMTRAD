#!/bin/bash
# Run SRIM-2013 TRIM in batch mode under Wine (workstation only; SRIM is not on HPG).
#   bin/trim_run.sh <TRIM.IN> <out_dir>
# Copies the TRIM.IN into the SRIM install (Wine prefix ~/.wine-srim, C:\SRIM), sets
# TRIMAUTO = 1 (no keyboard input, exit after the last ion), runs TRIM.exe, and copies the
# output tables (*.txt, SRIM Outputs/*) to <out_dir>. TRIM opens a window while it runs.
# One TRIM at a time: the install directory holds the in-progress files.
set -euo pipefail
IN=$1; OUT=$2
export WINEPREFIX=${WINEPREFIX:-$HOME/.wine-srim} WINEDEBUG=-all
S="$WINEPREFIX/drive_c/SRIM"
[ -f "$S/TRIM.exe" ] || { echo "SRIM not installed in $S (see kb/tools/trim.md)"; exit 1; }
if pgrep -x TRIM.exe >/dev/null; then echo "a TRIM run is already active"; exit 1; fi
mkdir -p "$OUT"
cp "$S/TRIM.IN" "$S/TRIM.IN.bak"
tr -d '\r' < "$IN" | sed 's/$/\r/' > "$S/TRIM.IN"       # TRIM expects CRLF
printf '1\r\n\r\n' > "$S/TRIMAUTO"
rm -f "$S"/*.txt "$S/SRIM Outputs"/*.txt
trap 'printf "0\r\n\r\n" > "$S/TRIMAUTO"; mv "$S/TRIM.IN.bak" "$S/TRIM.IN"' EXIT
t0=$(date +%s)
( cd "$S" && wine TRIM.exe >/dev/null 2>&1 )
cp "$S"/*.txt "$OUT"/ 2>/dev/null || true
cp "$S/SRIM Outputs"/*.txt "$OUT"/ 2>/dev/null || true
cp "$IN" "$OUT/TRIM.IN"
echo "TRIM done in $(( $(date +%s) - t0 )) s -> $OUT ($(ls "$OUT" | wc -l) files)"
