#!/bin/bash
# Late-onset search with field mobility, round 2 (after round 1, job 44359813:
# latest deep collapse 1.0 V at 0.35 eV / 4e18 / hotTau 3e-14 / hotEb 0.85).
# Run F position (trapMeanX 0, trapMeanY 0.2 um, trapSigma 0.04):
# trapLevel {0.30,0.35,0.40} x trapPeak {4,5,6}e18 x hotTau {1,1.5,2,3}e-14
# x hotEb {0.85,1.0} = 72, plus task 72: trap-free reference. Vd 0-4 V / 0.1 V, dampValue 0.05,
# retry driver, mobModel field (deck default).
#
# One line per task in params_onsetField2.txt:
#   trapPeak|trapLevel|hotTau|hotEb
#
#SBATCH --job-name=pulsedIV_onsetField2
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-72%80
#SBATCH --output=results/20261002_onsetField2/slurm_%A_%a.out
#SBATCH --error=results/20261002_onsetField2/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20261002_onsetField2
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_onsetField2.txt")
IFS='|' read -r TRAPPEAK TRAPLEVEL HOTTAU HOTEB <<< "$LINE"
TRAPMEANX=0.0
TRAPMEANY=0.2

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'tp%.2e_tl%.2f_ht%.2e_eb%.2f' "$TRAPPEAK" "$TRAPLEVEL" "$HOTTAU" "$HOTEB")
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
  "Vd_max": 4.0,
  "Vd_step": 0.1,
  "dampValue": 0.05,
  "mobModel": "field",
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
