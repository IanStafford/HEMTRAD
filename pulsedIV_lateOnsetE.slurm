#!/bin/bash
# Round E of the late-onset search (progress.md 2026-09-25, CLAUDE.md
# 10b). Round D showed a clean trend at fixed hotTau=2e-14: lowering
# trapPeak 8e18->6e18 delays onset (1.05V->1.8V) but weakens depth
# (231x->12x) - the two axes trade off directly along trapPeak alone.
#
# This round: push trapPeak down further AND raise hotTau at the same
# time, testing whether stronger heating can restore depth once the
# (delayed) runaway threshold is crossed.
#
# One line per task in params_lateOnsetE.txt: trapPeak|hotTau
#
#SBATCH --job-name=pulsedIV_lateOnsetE
#SBATCH --account=ee1
#SBATCH --qos=ee1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=01:30:00
#SBATCH --array=0-5%6
#SBATCH --output=results/20260925_lateOnsetE/slurm_%A_%a.out
#SBATCH --error=results/20260925_lateOnsetE/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260925_lateOnsetE
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_lateOnsetE.txt")
IFS='|' read -r TRAPPEAK HOTTAU <<< "$LINE"
TRAPLEVEL=0.35

TAG=$(printf 'tp%.2e_ht%.2e' "$TRAPPEAK" "$HOTTAU")

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
