#!/bin/bash
# Cone vs Gaussian trap shape at settings that DO collapse (Ian): 4e18 cm^-3
# at trapLevel 0.55 eV (Run F; early, deep collapse everywhere) and 0.35 eV
# (onset moves strongly with position). trapShape=cone, apex at the AlGaN
# surface at trapMeanY; same 5 geometries (coneLen um | coneAngle deg):
# 0.05|30, 0.1|30, 0.2|30, 0.1|15, 0.1|45; x 10 contact-safe apex positions.
# Task 100: trap-free reference. Compare against the Gaussian 4e18/0.55 and
# 4e18/0.35 x=0 rows of job 43513462 (same Vd range, damping, retry driver).
#
# One line per task in params_trapConeCollapse.txt:
#   trapPeak|trapLevel|coneLen|coneAngle|trapMeanY
#
#SBATCH --job-name=pulsedIV_trapConeCollapse
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-100
#SBATCH --output=results/20260927_trapConeCollapse/slurm_%A_%a.out
#SBATCH --error=results/20260927_trapConeCollapse/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20260927_trapConeCollapse
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapConeCollapse.txt")
IFS='|' read -r TRAPPEAK TRAPLEVEL CONELEN CONEANGLE TRAPMEANY <<< "$LINE"
TRAPMEANX=0.0

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'cone_tl%.2f_L%.3f_a%02.0f_my%.3e' "$TRAPLEVEL" "$CONELEN" "$CONEANGLE" "$TRAPMEANY")
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
