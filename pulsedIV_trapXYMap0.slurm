#!/bin/bash
# Companion to pulsedIV_trapXYMap.slurm (job 44261474): same Run F trap blob,
# but insulator traps neutral (insTrapSign=0, the pre-10j model), at the
# near-surface depths x=-30..80 nm where the insulator charge dominated.
# Isolates the semiconductor-trap effect. Last task: trap-free reference.
#
# One line per task in params_trapXYMap0.txt: insTrapSign|trapMeanX|trapMeanY|trapPeak
#
#SBATCH --job-name=pulsedIV_trapXYMap0
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-90%120
#SBATCH --output=results/20261001_trapXYMap0/slurm_%A_%a.out
#SBATCH --error=results/20261001_trapXYMap0/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20261001_trapXYMap0
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapXYMap0.txt")
IFS="|" read -r INSSIGN TRAPMEANX TRAPMEANY TRAPPEAK <<< "$LINE"
TRAPLEVEL=0.55

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
