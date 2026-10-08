#!/bin/bash
# eTemp debug (2026-10-08): pulsedIV to Vd = 0 at Vg = -2, then the 0 -> 0.1 V
# step with Newton capped at 1 and 2 iterations, fields dumped after each
# (eTempDebug_tail.tcl). One line per task in params_eTempDebug.txt:
#   tag|extra lever settings (';'-separated)
#SBATCH --job-name=eTempDebug
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=01:00:00
#SBATCH --output=results/eTemp_logs/dbg_%A_%a.out
#SBATCH --error=results/eTemp_logs/dbg_%A_%a.err
set -euo pipefail
REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_eTempDebug.txt")
IFS="|" read -r TAG EXTRA <<< "$LINE"
TASK_DIR=$REPO/results/20261008_eTempDebug/$TAG
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
{
    echo "set trapEn 0"
    echo "set eTemp 1"
    echo "set etTau 1e-12"
    echo "set Vg_meas -2.0"
    echo "set Vd_max 0.0"
    echo "set dampValue 0.05"
    echo "set ivCSV dbg_iv.csv"
    if [ -n "${EXTRA:-}" ]; then echo "$EXTRA" | tr ';' '\n' | sed 's/^ */set /'; fi
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/pulsedIV.tcl"
    cat "$REPO/eTempDebug_tail.tcl"
} > "$TASK_DIR/dbg_task.tcl"
cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" dbg_task.tcl
