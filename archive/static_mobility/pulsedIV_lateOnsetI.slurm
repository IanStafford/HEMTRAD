#!/bin/bash
# Round I of the late-onset search (progress.md 2026-09-25, CLAUDE.md
# 10b). Round H found the best matches yet on the hotTau=6e-14/hotEb=0.8
# line: trapPeak=3e18 gives onset ~2.3-2.4V at ~336x depth (closest shape
# match to F so far), trapPeak=3.5e18 gives ~1277x depth (near F's
# ~1000x target) at onset ~2.0-2.1V. Lower trapPeak keeps buying later
# onset without the depth collapsing to nothing, unlike at hotEb=0.5.
#
# This round: push trapPeak lower still {2.5e18, 2.75e18, 3e18, 3.25e18}
# x hotTau {6e-14, 7e-14} x hotEb {0.8, 0.85, 0.9} (skipping the 3 cells
# already known from round H), aiming for onset ~2.7-3V while keeping
# depth in the hundreds-x range.
#
# One line per task in params_lateOnsetI.txt: trapPeak|hotTau|hotEb
#
#SBATCH --job-name=pulsedIV_lateOnsetI
#SBATCH --account=ee1
#SBATCH --qos=ee1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=02:30:00
#SBATCH --array=0-17%18
#SBATCH --output=results/20260925_lateOnsetI/slurm_%A_%a.out
#SBATCH --error=results/20260925_lateOnsetI/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260925_lateOnsetI
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_lateOnsetI.txt")
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
