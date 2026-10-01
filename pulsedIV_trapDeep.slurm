#!/bin/bash
# Deep-trap test (Ian): is the collapse from traps deep in the GaN, or from the
# blob's tail at the 2DEG? Run F traps (0.55 eV, hotEb 0.5, hotTau 1.3e-13) in a
# blob narrow in depth (trapSigma 0.01 um) but 40 nm wide laterally
# (trapSigmaY 0.04, resolvable on the access-region mesh), centred 0-65 nm below
# the 2DEG. Two peak densities: 4e18 (same local density as the sigma-40 nm
# maps) and 1.6e19 (same total charge). Insulator traps neutral.
# Last task: trap-free reference.
#
# One line per task in params_trapDeep.txt: trapMeanX|trapMeanY|trapPeak
#
#SBATCH --job-name=pulsedIV_trapDeep
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-70%100
#SBATCH --output=results/20261001_trapDeep/slurm_%A_%a.out
#SBATCH --error=results/20261001_trapDeep/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20261001_trapDeep
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapDeep.txt")
IFS="|" read -r TRAPMEANX TRAPMEANY TRAPPEAK <<< "$LINE"
INSSIGN=0
TRAPLEVEL=0.55

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'tp%.2e_mx%.4e_my%.3e' "$TRAPPEAK" "$TRAPMEANX" "$TRAPMEANY")
fi

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapSigma 0.01"
    echo "set trapSigmaY 0.04"
    echo "set trapLevel $TRAPLEVEL"
    echo "set hotEb     0.5"
    echo "set hotTau    1.3e-13"
    echo "set insTrapSign $INSSIGN"
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
  "trapSigma": 0.01,
  "trapSigmaY": 0.04,
  "trapLevel": $TRAPLEVEL,
  "hotEb": 0.5,
  "hotTau": 1.3e-13,
  "insTrapSign": $INSSIGN,
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
