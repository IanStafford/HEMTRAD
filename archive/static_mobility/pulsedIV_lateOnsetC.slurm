#!/bin/bash
# Round C of the late-onset search (progress.md 2026-09-25, CLAUDE.md
# 10b). Round B (trapLevel x trapPeak, trapLevel=0.35 fixed) showed a
# real normal-rise-then-knee shape for the first time: trapPeak=8e18 gave
# the latest onset so far (~1.5-1.8V) but only ~2.8x depth; trapPeak=1.2e19
# gave ~10x depth but an earlier onset (~0.6-0.9V). Neither close to F's
# ~1000x.
#
# This round: bracket the trapPeak gap {8.5e18, 9.5e18, 1.05e19} x raise
# hotTau {1e-14, 2e-14} for more heating/depth, trapLevel=0.35 fixed,
# trapSigma=0.04, hotEb=0.5.
#
# One line per task in params_lateOnsetC.txt: trapPeak|hotTau
#
#SBATCH --job-name=pulsedIV_lateOnsetC
#SBATCH --account=ee1
#SBATCH --qos=ee1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=01:30:00
#SBATCH --array=0-5%6
#SBATCH --output=results/20260925_lateOnsetC/slurm_%A_%a.out
#SBATCH --error=results/20260925_lateOnsetC/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260925_lateOnsetC
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_lateOnsetC.txt")
IFS='|' read -r TRAPPEAK HOTTAU <<< "$LINE"
TRAPLEVEL=0.35

TAG=$(printf 'tp%.2e_ht%.2e' "$TRAPPEAK" "$HOTTAU")

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapSigma 0.04"
    echo "set trapLevel $TRAPLEVEL"
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
  "trapLevel": $TRAPLEVEL,
  "hotEb": 0.5,
  "hotTau": $HOTTAU,
  "Vd_max": 4.05,
  "Vd_step": 0.15,
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
