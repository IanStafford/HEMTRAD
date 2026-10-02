#!/bin/bash
# Trap concentration x energy level x lateral position, burst QOS.
# Goal: how trapPeak and trapLevel shape the collapse in this model (not a
# radPlot1 fit). Traps kept >=0.7 um from the source/drain contact doping
# (edges at y=-1.125 and 3.285), since the 50-point map suggested contact
# proximity gives unreliable results.
#
# Fixed: trapMeanX=0 (AlGaN surface), trapSigma=0.04, trapWidth=0.1,
# hotEb=0.5, hotTau=1.3e-13 (Run F), Vg=-2, Vd 0-3.0V in 0.1V,
# dampValue=0.05.
# Swept: trapPeak {2e18,4e18,8e18} x trapLevel {0.35,0.55,0.75} x
# trapMeanY {-0.4,-0.125,0,0.125,0.285,0.5,0.725,1.25,1.75,2.4} = 90,
# plus task 90: effectively trap-free reference (trapPeak=1e10).
#
# One line per task in params_trapConcLevel.txt: trapPeak|trapLevel|trapMeanY
#
#SBATCH --job-name=pulsedIV_trapConcLevel
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=01:30:00
#SBATCH --array=0-90
#SBATCH --output=results/20260926_trapConcLevel/slurm_%A_%a.out
#SBATCH --error=results/20260926_trapConcLevel/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260926_trapConcLevel
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapConcLevel.txt")
IFS='|' read -r TRAPPEAK TRAPLEVEL TRAPMEANY <<< "$LINE"

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'tp%.2e_tl%.2f_my%.3e' "$TRAPPEAK" "$TRAPLEVEL" "$TRAPMEANY")
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
    echo "set trapMeanX 0.0"
    echo "set trapMeanY $TRAPMEANY"
    echo "set Vd_max    3.0"
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
  "hotEb": 0.5,
  "hotTau": 1.3e-13,
  "trapMeanX": 0.0,
  "trapMeanY": $TRAPMEANY,
  "Vd_max": 3.0,
  "Vd_step": 0.1,
  "dampValue": 0.05,
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
