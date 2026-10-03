#!/bin/bash
# Curve-tracer Id-Vd at Vg = -1 and 0 V (Ian, 2026-10-03) for four key devices:
# trap-free, the late-onset set (0.30 eV / 5e18 / hotTau 1e-14 / hotEb 1.0) at
# y = 1.0 and 2.4 um (deep collapse at 2.3 / 3.5 V at Vg = -2), and Run F.
# x = 0, sigma 40 nm, Vd 0-4 V / 0.1 V, field mobility, Te-ramp on.
#
# One line per task in params_curveTracer.txt:
#   Vg|devTag|trapPeak|trapSigma|trapLevel|hotTau|hotEb|trapMeanY
# Output: results/20261003_curveTracer/Vg<Vg>_<devTag>/
#
#SBATCH --job-name=pulsedIV_curveTracer
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=06:00:00
#SBATCH --array=0-7
#SBATCH --output=results/20261003_curveTracer/slurm_%A_%a.out
#SBATCH --error=results/20261003_curveTracer/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_curveTracer.txt")
IFS="|" read -r VG DEVTAG TRAPPEAK TRAPSIGMA TRAPLEVEL HOTTAU HOTEB TRAPMEANY <<< "$LINE"
TRAPMEANX=0
RUN_DIR=$REPO/results/20261003_curveTracer
TASK_DIR=$RUN_DIR/Vg${VG}_${DEVTAG}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

TAG="Vg${VG}_${DEVTAG}"

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl; do
    cp "$REPO/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/pulsedIV_task.tcl"
{
    echo "set trapPeak  $TRAPPEAK"
    echo "set trapSigma $TRAPSIGMA"
    echo "set Vg_meas   $VG"
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
  "trapSigma": $TRAPSIGMA,
  "Vg_meas": $VG,
  "trapLevel": $TRAPLEVEL,
  "hotEb": $HOTEB,
  "hotTau": $HOTTAU,
  "trapMeanX": $TRAPMEANX,
  "trapMeanY": $TRAPMEANY,
  "Vd_max": 4.0,
  "Vd_step": 0.1,
  "dampValue": 0.05,
  "mobModel": "field",
  "devTag": "$DEVTAG",
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
