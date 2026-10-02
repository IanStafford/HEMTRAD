#!/bin/bash
# RETRY of the 10 trap-map-set tasks that gave up at their collapse point
# (job 43513462): solver-side only - dampValue 0.02, retryDepth 7.
# 3D trap maps at several trap concentrations/levels (burst QOS).
# Sets (trapPeak/trapLevel): 2e18/0.55, 2e18/0.75, 4e18/0.35, 4e18/0.55
# (Run F), 8e18/0.35 - one per regime from the conc x level study.
# Each: trapMeanX {0,3.75,7.5,11.25,15 nm} x trapMeanY {-0.4,-0.125,0,0.125,
# 0.285,0.5,0.725,1.25,1.75,2.4} um (>=0.7 um from contact doping), 50/set,
# plus task 250: trap-free reference (trapPeak=1e10).
# Fixed: trapSigma=0.04, hotEb=0.5, hotTau=1.3e-13, Vg=-2, Vd 0-3.0V/0.1V,
# dampValue=0.05. pulsedIV.tcl now retries failed points (store/restore +
# bisection), so no separate retry job should be needed.
#
# One line per task in params_trapMapSetsRetry.txt:
#   trapPeak|trapLevel|trapMeanX|trapMeanY
#
#SBATCH --job-name=pulsedIV_trapMapSetsRetry
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-9
#SBATCH --output=results/20260927_trapMapSetsRetry/slurm_%A_%a.out
#SBATCH --error=results/20260927_trapMapSetsRetry/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260927_trapMapSetsRetry
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapMapSetsRetry.txt")
IFS='|' read -r TRAPPEAK TRAPLEVEL TRAPMEANX TRAPMEANY <<< "$LINE"

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'tp%.2e_tl%.2f_mx%.3e_my%.3e' "$TRAPPEAK" "$TRAPLEVEL" "$TRAPMEANX" "$TRAPMEANY")
fi

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapSigma 0.04"
    echo "set trapLevel $TRAPLEVEL"
    echo "set hotEb     0.5"
    echo "set hotTau    1.3e-13"
    echo "set trapMeanX $TRAPMEANX"
    echo "set trapMeanY $TRAPMEANY"
    echo "set Vd_max    3.0"
    echo "set Vd_step   0.1"
    echo "set dampValue 0.02"
    echo "set retryDepth 7"
    echo "set ivCSV     \"pulsedIV_${TAG}.csv\""
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/pulsedIV.tcl"
} > "$DRIVER"

cat > "$TASK_DIR/params.json" <<JSON
{
  "trapPeak": $TRAPPEAK,
  "trapSigma": 0.04,
  "trapLevel": $TRAPLEVEL,
  "hotEb": 0.5,
  "hotTau": 1.3e-13,
  "trapMeanX": $TRAPMEANX,
  "trapMeanY": $TRAPMEANY,
  "Vd_max": 3.0,
  "Vd_step": 0.1,
  "dampValue": 0.02,
  "retryDepth": 7,
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
