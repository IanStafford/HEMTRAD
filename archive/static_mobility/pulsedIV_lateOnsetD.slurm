#!/bin/bash
# Round D of the late-onset search (progress.md 2026-09-25, CLAUDE.md
# 10b). Round C found the first F-like depth: trapPeak=8.5e18/hotTau=2e-14
# gave a ~300x collapse (54.6->0.174 mA/mm), but onset only ~0.9-1.2V.
# Raising trapPeak OR hotTau moves the collapse both earlier and deeper
# together (looks like a runaway trap/Te threshold, not two independent
# knobs). trapPeak=1.05e19/hotTau=2e-14 crashed (solver abort, not
# Newton/NaN) - not retried.
#
# This round: lower trapPeak at the SAME hotTau=2e-14 that crossed the
# runaway threshold in round C, to see if the threshold can be pushed
# later in Vd while keeping the depth.
#
# One line per task in params_lateOnsetD.txt: trapPeak
#
#SBATCH --job-name=pulsedIV_lateOnsetD
#SBATCH --account=ee1
#SBATCH --qos=ee1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=01:30:00
#SBATCH --array=0-4%5
#SBATCH --output=results/20260925_lateOnsetD/slurm_%A_%a.out
#SBATCH --error=results/20260925_lateOnsetD/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260925_lateOnsetD
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

TRAPPEAK=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_lateOnsetD.txt")
TRAPLEVEL=0.35
HOTTAU=2e-14

TAG=$(printf 'tp%.2e' "$TRAPPEAK")

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
