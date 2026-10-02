#!/bin/bash
# Trap-placement study: how does the location of the (single) Gaussian
# trap distribution along the channel affect the radiation-induced
# collapse? Each task is one device with the trap blob at one
# (trapMeanX, trapMeanY) location - no multi-location devices.
#
# Baseline is Run F's tuned levers (CLAUDE.md section 10), matching the
# project's primary target (radPlot1, ~0.4-0.5V onset):
# trapPeak=4e18, trapSigma=0.04, trapLevel=0.55, hotEb=0.5,
# hotTau=1.3e-13, Vg_meas=-2, Vd 0-1.6V in 0.1V steps.
#
# Geometry landmarks (rfdevice.tcl): gate spans y=[-0.125,0.125]
# (Gate_Length=0.25), field plate spans y=[0.285,0.725]
# (leftFP/rightFP), drain contact at y=3.41. AlGaN top (surface) is
# x=0, the 2DEG/AlGaN-GaN interface is x=0.015 (Al_Thick).
#
# Grid: trapMeanX in {0.0, 0.0075, 0.015} (surface, mid-AlGaN, 2DEG
# interface) x trapMeanY in {0.125, 0.20, 0.285, 0.725, 2.0} (gate edge,
# the value used throughout tuning, field-plate-left edge,
# field-plate-right edge, deep access near drain).
#
# One line per task in params_trapPlacement.txt: trapMeanX|trapMeanY
#
#SBATCH --job-name=pulsedIV_trapPlacement
#SBATCH --account=ee1
#SBATCH --qos=ee1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=00:45:00
#SBATCH --array=0-14%15
#SBATCH --output=results/20260925_trapPlacement/slurm_%A_%a.out
#SBATCH --error=results/20260925_trapPlacement/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260925_trapPlacement
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapPlacement.txt")
IFS='|' read -r TRAPMEANX TRAPMEANY <<< "$LINE"

TAG=$(printf 'mx%.3e_my%.3e' "$TRAPMEANX" "$TRAPMEANY")

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapPeak  4e18"
    echo "set trapSigma 0.04"
    echo "set trapLevel 0.55"
    echo "set hotEb     0.5"
    echo "set hotTau    1.3e-13"
    echo "set trapMeanX $TRAPMEANX"
    echo "set trapMeanY $TRAPMEANY"
    echo "set Vd_max    1.6"
    echo "set Vd_step   0.1"
    echo "set ivCSV     \"pulsedIV_${TAG}.csv\""
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/pulsedIV.tcl"
} > "$DRIVER"

cat > "$TASK_DIR/params.json" <<JSON
{
  "trapPeak": 4e18,
  "trapSigma": 0.04,
  "trapLevel": 0.55,
  "hotEb": 0.5,
  "hotTau": 1.3e-13,
  "trapMeanX": $TRAPMEANX,
  "trapMeanY": $TRAPMEANY,
  "Vd_max": 1.6,
  "Vd_step": 0.1,
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
