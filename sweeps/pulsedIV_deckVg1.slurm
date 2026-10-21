#!/bin/bash
# HighK vs SiN passivation with traps at Vg +1 V, Vd 0-10 V (2026-10-21, Ian).
# Does the trap model collapse the SiN deck at high Vd but not the HighK deck?
# Earlier HighK/SiN comparisons stopped at 3 V ([[highk-vs-sin]]).
# Trap set = sensitivity baseline (5e18, sigma 0.04, x 0, level 0.30, width 0.1,
# hotEb 1.0, hotTau 1e-14, hotMu 600, hotVsat 1.9e7, fillIters 4, fillRelax 0.5),
# at y = 0.3 / 1.0 / 2.4 um, plus a trap-free reference per deck (trapPeak 1e10).
# Local-field model (eTemp 0), field mobility, Vd step 0.1.
#
# One line per task in params_deckVg1.txt:
#   label|deviceDeck|trapMeanY|trapPeak
#
#SBATCH --job-name=pulsedIV_deckVg1
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=24:00:00
#SBATCH --array=0-7%8
#SBATCH --output=results/20261021_deckVg1/slurm_%A_%a.out
#SBATCH --error=results/20261021_deckVg1/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20261021_deckVg1
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/sweeps/params_deckVg1.txt")
IFS='|' read -r LABEL DECK TRAPMEANY TRAPPEAK <<< "$LINE"
TAG=$(echo "$LABEL" | tr '=' '_')

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl rfdevice_SiN.tcl; do
    cp "$REPO/model/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapEn    1"
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapSigma 0.04"
    echo "set trapMeanX 0.0"
    echo "set trapMeanY $TRAPMEANY"
    echo "set deviceDeck $DECK"
    echo "set trapLevel 0.30"
    echo "set trapWidth 0.1"
    echo "set hotEb     1.0"
    echo "set hotTau    1e-14"
    echo "set hotMu     600"
    echo "set hotVsat   1.9e7"
    echo "set fillIters 4"
    echo "set fillRelax 0.5"
    echo "set eTemp     0"
    echo "set Vg_meas   1.0"
    echo "set Vd_max    10.0"
    echo "set Vd_step   0.1"
    echo "set dampValue 0.05"
    echo "set mobModel  field"
    echo "set ivCSV     \"pulsedIV_${TAG}.csv\""
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/drivers/pulsedIV.tcl"
} > "$DRIVER"

cat > "$TASK_DIR/params.json" <<JSON
{
  "label": "$LABEL",
  "trapPeak": $TRAPPEAK,
  "trapSigma": 0.04,
  "trapMeanX": 0.0,
  "trapMeanY": $TRAPMEANY,
  "deviceDeck": "$DECK",
  "trapLevel": 0.30,
  "trapWidth": 0.1,
  "hotEb": 1.0,
  "hotTau": 1e-14,
  "hotMu": 600,
  "hotVsat": 1.9e7,
  "fillIters": 4,
  "fillRelax": 0.5,
  "eTemp": 0,
  "Vg_meas": 1.0,
  "Vd_max": 10.0,
  "Vd_step": 0.1,
  "dampValue": 0.05,
  "mobModel": "field",
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
