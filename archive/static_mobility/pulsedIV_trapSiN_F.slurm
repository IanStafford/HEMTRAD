#!/bin/bash
# SiN-passivated device (rfdevice_SiN.tcl: every HighK region -> Nitride),
# repeating the 10f Run F 4e18 cm^-3 / 0.55 eV trap map (job 43513462) to see what
# the HighK dielectric does. Same grid: trapMeanX {0,3.75,7.5,11.25,15 nm} x
# trapMeanY {-0.4..2.4 um} = 50, plus task 50: trap-free SiN reference.
# Fixed: trapSigma=0.04, hotEb=0.5, hotTau=1.3e-13, Vg=-2, Vd 0-3.0V/0.1V,
# dampValue=0.05, retry driver.
#
# One line per task in params_trapSiN_F.txt:
#   trapPeak|trapLevel|trapMeanX|trapMeanY
#
#SBATCH --job-name=pulsedIV_trapSiN_F
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=03:00:00
#SBATCH --array=0-50%60
#SBATCH --output=results/20261001_trapSiN_F/slurm_%A_%a.out
#SBATCH --error=results/20261001_trapSiN_F/slurm_%A_%a.err

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD
RUN_DIR=$REPO/results/20261001_trapSiN_F
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/params_trapSiN_F.txt")
IFS='|' read -r TRAPPEAK TRAPLEVEL TRAPMEANX TRAPMEANY <<< "$LINE"

if [ "$TRAPPEAK" = "1e10" ]; then
    TAG="notrap"
else
    TAG=$(printf 'tp%.2e_tl%.2f_mx%.3e_my%.3e' "$TRAPPEAK" "$TRAPLEVEL" "$TRAPMEANX" "$TRAPMEANY")
fi

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl rfdevice_SiN.tcl; do
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
    echo "set deviceDeck rfdevice_SiN.tcl"
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
  "deviceDeck": "rfdevice_SiN.tcl",
  "task_id": $SLURM_ARRAY_TASK_ID
}
JSON

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" pulsedIV_task.tcl
