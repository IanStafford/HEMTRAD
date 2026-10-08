#!/bin/bash
# Electron energy balance (ETemp.tcl, eTemp lever) tests, 2026-10-08.
# One line per task in $PARAMS (default params_eTemp1.txt):
#   tag|eTemp|etTau|etMob|etStats|trapEn|trapPeak|trapLevel|hotTau|hotEb|trapMeanY|Vg|Vd_max|teProfile[|extra]
# extra (optional): more lever settings, ';'-separated, e.g. 'etThermoJ 0;etThermoE 1'
# teProfile: comma-separated Vd list for ETemp cut dumps (or "-").
# Output: results/$RUN/<tag>/ (RUN default 20261008_eTemp1). Submit with
#   sbatch --array=0-N --export=ALL,PARAMS=params_x.txt,RUN=<run> pulsedIV_eTemp.slurm
#
#SBATCH --job-name=pulsedIV_eTemp
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=06:00:00
#SBATCH --output=results/eTemp_logs/slurm_%A_%a.out
#SBATCH --error=results/eTemp_logs/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
PARAMS=${PARAMS:-params_eTemp1.txt}
RUN=${RUN:-20261008_eTemp1}
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/$PARAMS")
IFS="|" read -r TAG ETEMP ETTAU ETMOB ETSTATS TRAPEN TRAPPEAK TRAPLEVEL HOTTAU HOTEB TRAPMEANY VG VDMAX TEPROF EXTRA <<< "$LINE"
TASK_DIR=$REPO/results/$RUN/$TAG

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"
for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl ETemp.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

PROF=""
[ "$TEPROF" != "-" ] && PROF=$(echo "$TEPROF" | tr ',' ' ')

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set eTemp     $ETEMP"
    echo "set etTau     $ETTAU"
    echo "set etMob     $ETMOB"
    echo "set etStats   $ETSTATS"
    echo "set trapEn    $TRAPEN"
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapSigma 0.04"
    echo "set trapLevel $TRAPLEVEL"
    echo "set hotEb     $HOTEB"
    echo "set hotTau    $HOTTAU"
    echo "set trapMeanX 0.0"
    echo "set trapMeanY $TRAPMEANY"
    echo "set Vg_meas   $VG"
    echo "set Vd_max    $VDMAX"
    echo "set Vd_step   0.1"
    echo "set dampValue 0.05"
    echo "set mobModel  field"
    echo "set teProfile {$PROF}"
    if [ -n "${EXTRA:-}" ]; then echo "$EXTRA" | tr ';' '\n' | sed 's/^ */set /'; fi
    echo "set ivCSV     \"pulsedIV_${TAG}.csv\""
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/pulsedIV.tcl"
} > "$DRIVER"

cat > "$TASK_DIR/params.json" <<JSON
{
  "tag": "$TAG", "eTemp": $ETEMP, "etTau": $ETTAU, "etMob": "$ETMOB", "etStats": $ETSTATS,
  "trapEn": $TRAPEN, "trapPeak": $TRAPPEAK, "trapSigma": 0.04, "trapLevel": $TRAPLEVEL,
  "hotEb": $HOTEB, "hotTau": $HOTTAU, "trapMeanX": 0.0, "trapMeanY": $TRAPMEANY,
  "Vg_meas": $VG, "Vd_max": $VDMAX, "Vd_step": 0.1, "dampValue": 0.05, "mobModel": "field",
  "teProfile": "$TEPROF", "extra": "${EXTRA:-}", "job": "${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
