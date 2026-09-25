#!/bin/bash
# Round B of the late-onset search (progress.md 2026-09-24/25, CLAUDE.md
# 10b). Round A (trapPeak x hotTau) showed trapPeak=4e18 never collapses
# once hotTau is cut, while trapPeak=6e18/8e18 instead pinch the channel
# at rest (cold trapLevel=0.55eV occupancy too high at that density).
#
# This round: trapLevel x trapPeak, hotTau fixed at 1e-14 (weakest tested
# that still shows any hot effect), trapSigma=0.04, hotEb=0.5. Testing
# whether a shallower trapLevel empties more at cold/zero-field
# equilibrium, buying headroom for higher trapPeak without an at-rest
# pinch.
#
# One line per task in params_lateOnsetB.txt: trapLevel|trapPeak
#
#SBATCH --job-name=pulsedIV_lateOnsetB
#SBATCH --account=ee1
#SBATCH --qos=ee1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=01:30:00
#SBATCH --array=0-5%6
#SBATCH --output=results/20260925_lateOnsetB/slurm_%A_%a.out
#SBATCH --error=results/20260925_lateOnsetB/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260925_lateOnsetB
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_lateOnsetB.txt")
IFS='|' read -r TRAPLEVEL TRAPPEAK <<< "$LINE"
HOTTAU=1e-14

TAG=$(printf 'tl%.2e_tp%.2e' "$TRAPLEVEL" "$TRAPPEAK")

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
