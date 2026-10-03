#!/bin/bash
# Position maps at five trap level / concentration combinations (hot-electron
# levers fixed at the late-onset set: hotTau 1e-14 / hotEb 1.0, sigma 0.04):
# 5 sets x 65 positions (trapMeanX {0..15 nm} x trapMeanY {-0.4..2.4 um}). No
# reference task: reuse the trap-free CSV of 20261002_posMapLate (task_65). Vd 0-3 V / 0.1 V.
#
# One line per task in params_posMapLM.txt:
#   setTag|trapPeak|trapLevel|hotTau|hotEb|trapMeanX|trapMeanY
# Each set writes results/20261003_posMap_<setTag>/task_<0..64> (one plot_posVd.py run per set).
#
#SBATCH --job-name=pulsedIV_posMapLM
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=06:00:00
#SBATCH --array=0-324%170
#SBATCH --output=results/20261003_posMapLM_logs/slurm_%A_%a.out
#SBATCH --error=results/20261003_posMapLM_logs/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_posMapLM.txt")
IFS="|" read -r SETTAG TRAPPEAK TRAPLEVEL HOTTAU HOTEB TRAPMEANX TRAPMEANY <<< "$LINE"
RUN_DIR=$REPO/results/20261003_posMap_${SETTAG}
TASK_DIR=$RUN_DIR/task_$((SLURM_ARRAY_TASK_ID % 65))

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

TAG=$(printf 'mx%.3e_my%.3e' "$TRAPMEANX" "$TRAPMEANY")

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
    echo "set trapMeanX $TRAPMEANX"
    echo "set trapMeanY $TRAPMEANY"
    echo "set Vd_max    3.0"
    echo "set Vd_step   0.1"
    echo "set dampValue 0.05"
    echo "set mobModel  field"
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
  "trapMeanX": $TRAPMEANX,
  "trapMeanY": $TRAPMEANY,
  "Vd_max": 3.0,
  "Vd_step": 0.1,
  "dampValue": 0.05,
  "mobModel": "field",
  "setTag": "$SETTAG",
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
