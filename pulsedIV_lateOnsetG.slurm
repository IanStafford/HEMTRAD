#!/bin/bash
# Round G of the late-onset search (progress.md 2026-09-25, CLAUDE.md
# 10b). Round F found a real tension: the deepest collapses (~760-830x,
# close to F's ~1000x target) sit at onset ~1.0-1.35V; pushing onset
# later (lower trapPeak/hotTau) costs nearly all the depth (~1.8x by
# onset ~2.4-2.55V). It also crashed 6/18 tasks (33%, same
# munmap_chunk() abort as round C) right around the collapse transition.
#
# Two changes this round, both approved by Ian:
# 1. Solver-side stability fix (not a physics change): finer Vd_step
#    (0.1 instead of 0.15) and more Newton damping (dampValue=0.05
#    instead of 0.10, now a lever in pulsedIV.tcl) through the sweep, to
#    reduce the crash rate near the transition.
# 2. New axis: hotEb (fixed at F's 0.5 in every round so far). Testing
#    whether raising it restores depth at the "late onset, weak depth"
#    trapPeak/hotTau combos from round F, without needing more charge -
#    hotEb directly lowers the effective trap level for a given Te, so
#    might deepen the collapse independent of when it starts.
#
# Anchor points (trapPeak, hotTau) from round E/F, each swept over
# hotEb: A=4e18/5e-14 (onset ~2.25-2.4V, ~2.3x @ hotEb=0.5), B=4.5e18/
# 3e-14 (onset ~2.4-2.55V, ~1.8x), C=4.5e18/5e-14 (onset ~1.95-2.1V,
# ~9.9x), D=5e18/3e-14 (onset ~2.1-2.25V, ~6.8x). Plus 2 extra on the
# best-depth control point 6e18/5e-14 (~833x @ hotEb=0.5) to see how
# hotEb affects an already-deep, early-onset case.
#
# One line per task in params_lateOnsetG.txt: trapPeak|hotTau|hotEb
#
#SBATCH --job-name=pulsedIV_lateOnsetG
#SBATCH --account=ee1
#SBATCH --qos=ee1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=02:30:00
#SBATCH --array=0-17%18
#SBATCH --output=results/20260925_lateOnsetG/slurm_%A_%a.out
#SBATCH --error=results/20260925_lateOnsetG/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260925_lateOnsetG
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_lateOnsetG.txt")
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
