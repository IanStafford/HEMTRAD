#!/bin/bash
# Retry of the 19 round-3 tasks (job 44435511) that stopped with PULSED GAVE UP
# before Vd_max (runaway stall, CLAUDE.md 10.5). Solver-side only, as for the
# static-era 10f retry: dampValue 0.02 (was 0.05), retryDepth 7 (was 5).
# Physics and levers unchanged. analyze_onset.py reads <run>Retry automatically
# and keeps whichever run got further.
#
# One line per task in params_onsetField3Retry.txt:
#   trapPeak|trapLevel|hotTau|hotEb|trapMeanY
#
#SBATCH --job-name=pulsedIV_onsetField3Retry
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-18%20
#SBATCH --output=results/20261002_onsetField3Retry/slurm_%A_%a.out
#SBATCH --error=results/20261002_onsetField3Retry/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20261002_onsetField3Retry
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_onsetField3Retry.txt")
IFS='|' read -r TRAPPEAK TRAPLEVEL HOTTAU HOTEB TRAPMEANY <<< "$LINE"
TRAPMEANX=0.0

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'tp%.2e_tl%.2f_ht%.2e_eb%.2f_my%.3e' "$TRAPPEAK" "$TRAPLEVEL" "$HOTTAU" "$HOTEB" "$TRAPMEANY")
fi

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
    echo "set Vd_max    4.0"
    echo "set Vd_step   0.1"
    echo "set dampValue 0.02"
    echo "set retryDepth 7"
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
  "Vd_max": 4.0,
  "Vd_step": 0.1,
  "dampValue": 0.02,
  "retryDepth": 7,
  "mobModel": "field",
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
