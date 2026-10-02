#!/bin/bash
# Critical-band edges for the critical-strike probability estimate (Ian).
# Finer lateral positions around where the Gaussian trap blob stops cutting
# Id >=10x (from the job 43513462 maps): gate-region edges for 2e18/0.55 and
# 2e18/0.75, and both edges for 4e18/0.35, at depths 0, 7.5, 15 nm. Same
# settings as job 43513462 (Run F hot-electron levers, trapSigma 0.04,
# Vd 0-3 V/0.1 V, dampValue 0.05, retry driver). Last task: trap-free ref.
#
# One line per task in params_critBand.txt:
#   trapPeak|trapLevel|trapMeanX|trapMeanY
#
#SBATCH --job-name=pulsedIV_critBand
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-99
#SBATCH --output=results/20260928_critBand/slurm_%A_%a.out
#SBATCH --error=results/20260928_critBand/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260928_critBand
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_critBand.txt")
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
  "trapMeanX": $TRAPMEANX,
  "trapMeanY": $TRAPMEANY,
  "Vd_max": 3.0,
  "Vd_step": 0.1,
  "dampValue": 0.05,
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
