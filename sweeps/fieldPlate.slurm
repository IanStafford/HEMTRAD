#!/bin/bash
# HighK vs SiN field check with the field-dependent mobility (2026-10-16):
# trap-free, Vg = -2 V, Vd 0.5-20 V. Task 0 = HighK (rfdevice.tcl),
# task 1 = SiN (rfdevice_SiN.tcl). drivers/fieldPlate.tcl.
#
#SBATCH --job-name=fieldPlate
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=06:00:00
#SBATCH --array=0-1
#SBATCH --output=results/20261016_fieldPlate/slurm_%A_%a.out
#SBATCH --error=results/20261016_fieldPlate/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20261016_fieldPlate
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"
if [ "$SLURM_ARRAY_TASK_ID" = "0" ]; then DECK=rfdevice.tcl; TAG=highk; else DECK=rfdevice_SiN.tcl; TAG=sin; fi

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl rfdevice_SiN.tcl; do
    cp "$REPO/model/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/fieldPlate_task.tcl"
{
    echo "set deviceDeck $DECK"
    echo "set tag        $TAG"
    echo "set mobModel   field"
    echo "set eTemp      0"
    echo "set dampValue  0.05"
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/drivers/fieldPlate.tcl"
} > "$DRIVER"

cat > "$TASK_DIR/params.json" <<JSON
{
  "deviceDeck": "$DECK",
  "tag": "$TAG",
  "mobModel": "field",
  "eTemp": 0,
  "dampValue": 0.05,
  "Vg": -2.0,
  "Vd": "0.5-20 step 0.5",
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" fieldPlate_task.tcl
