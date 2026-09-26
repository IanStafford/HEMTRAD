#!/bin/bash
# 50-location trap map: where along/through the channel does the (single)
# Gaussian trap blob hurt the device most? One trap location per device.
# Run on the burst QOS (ee1-b: 171 CPUs, lower priority) so all tasks run
# at once instead of queuing behind the 19-CPU ee1 cap.
#
# Baseline: Run F's levers (trapPeak=4e18, trapSigma=0.04, trapLevel=0.55,
# hotEb=0.5, hotTau=1.3e-13), Vg=-2, Vd 0-1.6V in 0.1V steps.
# Grid: trapMeanX in {0, 0.00375, 0.0075, 0.01125, 0.015} (AlGaN surface
# to 2DEG) x trapMeanY in {-0.5, 0, 0.125, 0.285, 0.5, 0.725, 1.25, 2.0,
# 2.5, 3.0} (source side, under gate, gate edge, field plate, access
# region, near drain). Task 50 is an effectively trap-free reference
# (trapPeak=1e10; trapEn=0 would break CaptureTraps, which needs IonAcceptor).
#
# One line per task in params_trapMap.txt: trapPeak|trapMeanX|trapMeanY
#
#SBATCH --job-name=pulsedIV_trapMap
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=00:45:00
#SBATCH --array=0-50
#SBATCH --output=results/20260926_trapMap/slurm_%A_%a.out
#SBATCH --error=results/20260926_trapMap/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260926_trapMap
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapMap.txt")
IFS='|' read -r TRAPPEAK TRAPMEANX TRAPMEANY <<< "$LINE"

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'mx%.3e_my%.3e' "$TRAPMEANX" "$TRAPMEANY")
fi

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapPeak  $TRAPPEAK"
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
  "trapPeak": $TRAPPEAK,
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
