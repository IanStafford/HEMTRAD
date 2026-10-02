#!/bin/bash
# 9-task grid searching for a late-onset (Vd~3V), dramatic (~1000x) current
# collapse like pulsedIV_F.csv, per progress.md 2026-09-24. Grid: trapPeak x
# hotTau, F's other trap/hot-electron levers held fixed (trapSigma=0.04,
# trapLevel=0.55, hotEb=0.5). Coarse Vd_step=0.15 to Vd_max=4.05 for the
# search; the winning combo gets a full-resolution follow-up run.
#
# One line per task in params_lateOnset.txt: trapPeak|hotTau
#
#SBATCH --job-name=pulsedIV_lateOnset
#SBATCH --account=ee1
#SBATCH --qos=ee1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=01:30:00
#SBATCH --array=0-8%9
#SBATCH --output=results/20260924_lateOnset/slurm_%A_%a.out
#SBATCH --error=results/20260924_lateOnset/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260924_lateOnset
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_lateOnset.txt")
IFS='|' read -r TRAPPEAK HOTTAU <<< "$LINE"

TAG=$(printf 'tp%.2e_ht%.2e' "$TRAPPEAK" "$HOTTAU")

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapSigma 0.04"
    echo "set trapLevel 0.55"
    echo "set hotEb     0.5"
    echo "set hotTau    $HOTTAU"
    echo "set Vd_max    4.05"
    echo "set Vd_step   0.15"
    echo "set ivCSV     \"pulsedIV_${TAG}.csv\""
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/pulsedIV.tcl"
} > "$DRIVER"

cat > "$TASK_DIR/params.json" <<JSON
{
  "trapPeak": $TRAPPEAK,
  "trapSigma": 0.04,
  "trapLevel": 0.55,
  "hotEb": 0.5,
  "hotTau": $HOTTAU,
  "Vd_max": 4.05,
  "Vd_step": 0.15,
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
