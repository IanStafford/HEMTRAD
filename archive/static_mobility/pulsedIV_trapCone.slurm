#!/bin/bash
# Cone-shaped (displacement-cascade-like) trap distribution vs the 2D
# Gaussian, at trapPeak=2e18 cm^-3, trapLevel=0.75 eV (Ian's choice).
# trapShape=cone, apex at the AlGaN surface (trapMeanX=0) at lateral
# position trapMeanY; 5 geometries (coneLen um | coneAngle deg):
# 0.05|30, 0.1|30, 0.2|30, 0.1|15 (~same in-material charge as the surface
# Gaussian), 0.1|45; x 10 contact-safe apex positions. Task 50: trap-free
# reference. Compare against the Gaussian 2e18/0.75 x=0 row of job 43513462
# (same Vd range, damping, retry driver).
#
# One line per task in params_trapCone.txt: trapPeak|coneLen|coneAngle|trapMeanY
#
#SBATCH --job-name=pulsedIV_trapCone
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-50
#SBATCH --output=results/20260927_trapCone/slurm_%A_%a.out
#SBATCH --error=results/20260927_trapCone/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260927_trapCone
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapCone.txt")
IFS='|' read -r TRAPPEAK CONELEN CONEANGLE TRAPMEANY <<< "$LINE"
TRAPLEVEL=0.75
TRAPMEANX=0.0

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'cone_L%.3f_a%02.0f_my%.3e' "$CONELEN" "$CONEANGLE" "$TRAPMEANY")
fi

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapShape cone"
    echo "set coneLen   $CONELEN"
    echo "set coneAngle $CONEANGLE"
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
  "trapShape": "cone",
  "coneLen": $CONELEN,
  "coneAngle": $CONEANGLE,
  "coneW0": 0.01,
  "coneEdge": 0.01,
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
