#!/bin/bash
# Full x-y trap sensitivity map (Ian): Gaussian trap blob (Run F: 4e18 cm^-3,
# 0.55 eV, sigma 0.04 um, hotEb 0.5, hotTau 1.3e-13) centred from the top of
# the HighK (x=-0.275 um) to 0.5 um into the GaN (x=0.515), across the
# channel y=-0.4..2.5 um (contact-safe). Positions inside metal excluded.
# Insulator (Nitride/HighK) parts of the blob carry static charge
# (insTrapSign): grid A = -1 (fully filled, -q*N) at every position; grid B =
# +1 (fixed positive) at insulator-centred positions. Last task: trap-free
# reference. Vd 0-3 V/0.1 V, dampValue 0.05, retry driver.
#
# One line per task in params_trapXYMap.txt: insTrapSign|trapMeanX|trapMeanY
#
#SBATCH --job-name=pulsedIV_trapXYMap
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-247%160
#SBATCH --output=results/20261001_trapXYMap/slurm_%A_%a.out
#SBATCH --error=results/20261001_trapXYMap/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20261001_trapXYMap
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapXYMap.txt")
IFS='|' read -r INSSIGN TRAPMEANX TRAPMEANY <<< "$LINE"
TRAPLEVEL=0.55
TRAPPEAK=4e18
if [ "$INSSIGN" = "0" ]; then TRAPPEAK=1e10; fi

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'ins%+d_mx%.4e_my%.3e' "$INSSIGN" "$TRAPMEANX" "$TRAPMEANY")
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
  "trapSigma": 0.04,
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
