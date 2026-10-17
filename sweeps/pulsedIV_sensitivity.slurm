#!/bin/bash
# One-at-a-time sensitivity of the trap model (2026-10-17, Ian): each task
# changes ONE lever from the baseline, all else fixed. Baseline = late-onset set
# at y = 1.0 um (round 3: deep collapse at 2.3 V): trapPeak 5e18, trapSigma 0.04,
# trapMeanX 0, trapMeanY 1.0 (Gaussian + placement fixed), trapLevel 0.30,
# trapWidth 0.1, hotEb 1.0, hotTau 1e-14, hotMu 600, hotVsat 1.9e7, fillIters 4,
# fillRelax 0.5. Local-field model (eTemp 0), field mobility, Vg -2, Vd 0-4 / 0.1.
# Task 0 = baseline, task 1 = trap-free reference (trapPeak 1e10).
#
# One line per task in params_sensitivity.txt:
#   label|trapLevel|trapWidth|hotEb|hotTau|hotMu|hotVsat|fillIters|fillRelax|trapPeak
#
#SBATCH --job-name=pulsedIV_sensitivity
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=10:00:00
#SBATCH --array=0-33%34
#SBATCH --output=results/20261017_sensitivity/slurm_%A_%a.out
#SBATCH --error=results/20261017_sensitivity/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20261017_sensitivity
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/sweeps/params_sensitivity.txt")
IFS='|' read -r LABEL TRAPLEVEL TRAPWIDTH HOTEB HOTTAU HOTMU HOTVSAT FILLITERS FILLRELAX TRAPPEAK <<< "$LINE"
TAG=$(echo "$LABEL" | tr '=' '_')

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/model/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapEn    1"
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapSigma 0.04"
    echo "set trapMeanX 0.0"
    echo "set trapMeanY 1.0"
    echo "set trapLevel $TRAPLEVEL"
    echo "set trapWidth $TRAPWIDTH"
    echo "set hotEb     $HOTEB"
    echo "set hotTau    $HOTTAU"
    echo "set hotMu     $HOTMU"
    echo "set hotVsat   $HOTVSAT"
    echo "set fillIters $FILLITERS"
    echo "set fillRelax $FILLRELAX"
    echo "set eTemp     0"
    echo "set Vg_meas   -2.0"
    echo "set Vd_max    4.0"
    echo "set Vd_step   0.1"
    echo "set dampValue 0.05"
    echo "set mobModel  field"
    echo "set ivCSV     \"pulsedIV_${TAG}.csv\""
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/drivers/pulsedIV.tcl"
} > "$DRIVER"

cat > "$TASK_DIR/params.json" <<JSON
{
  "label": "$LABEL",
  "trapPeak": $TRAPPEAK,
  "trapSigma": 0.04,
  "trapMeanX": 0.0,
  "trapMeanY": 1.0,
  "trapLevel": $TRAPLEVEL,
  "trapWidth": $TRAPWIDTH,
  "hotEb": $HOTEB,
  "hotTau": $HOTTAU,
  "hotMu": $HOTMU,
  "hotVsat": $HOTVSAT,
  "fillIters": $FILLITERS,
  "fillRelax": $FILLRELAX,
  "eTemp": 0,
  "Vg_meas": -2.0,
  "Vd_max": 4.0,
  "Vd_step": 0.1,
  "dampValue": 0.05,
  "mobModel": "field",
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
