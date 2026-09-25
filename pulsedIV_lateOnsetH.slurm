#!/bin/bash
# Round H of the late-onset search (progress.md 2026-09-25, CLAUDE.md
# 10b). Round G found hotEb is a huge, mostly-independent depth lever:
# trapPeak=4e18/hotTau=5e-14/hotEb=0.7 gives ~750x depth at onset
# ~1.9-2.0V - the best combined late+deep match to F's ~1000x collapse
# so far. hotEb=0.8-0.9 overshoots to essentially fully-off.
#
# The crash rate (56% last round) didn't respond to the solver-side fix
# and doesn't correlate cleanly with hotEb - treating it as an
# unavoidable FLOOXS edge case for now, budgeting for losses rather than
# chasing it further.
#
# This round: extend the successful (trapPeak, hotTau, hotEb=0.7-0.8)
# region to lower trapPeak (3e18, 3.5e18, not yet tried) to keep pushing
# onset toward 3V while hotEb holds the depth up.
#
# One line per task in params_lateOnsetH.txt: trapPeak|hotTau|hotEb
#
#SBATCH --job-name=pulsedIV_lateOnsetH
#SBATCH --account=ee1
#SBATCH --qos=ee1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=02:30:00
#SBATCH --array=0-17%18
#SBATCH --output=results/20260925_lateOnsetH/slurm_%A_%a.out
#SBATCH --error=results/20260925_lateOnsetH/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260925_lateOnsetH
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_lateOnsetH.txt")
IFS='|' read -r TRAPPEAK HOTTAU HOTEB <<< "$LINE"
TRAPLEVEL=0.35

TAG=$(printf 'tp%.2e_ht%.2e_eb%.2e' "$TRAPPEAK" "$HOTTAU" "$HOTEB")

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapSigma 0.04"
    echo "set trapLevel $TRAPLEVEL"
    echo "set hotEb     $HOTEB"
    echo "set hotTau    $HOTTAU"
    echo "set Vd_max    4.05"
    echo "set Vd_step   0.1"
    echo "set dampValue 0.05"
    echo "set ivCSV     \"pulsedIV_${TAG}.csv\""
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/pulsedIV.tcl"
} > "$DRIVER"

cat > "$TASK_DIR/params.json" <<JSON
{
  "trapPeak": $TRAPPEAK,
  "trapSigma": 0.04,
  "trapLevel": $TRAPLEVEL,
  "hotEb": $HOTEB,
  "hotTau": $HOTTAU,
  "Vd_max": 4.05,
  "Vd_step": 0.1,
  "dampValue": 0.05,
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
