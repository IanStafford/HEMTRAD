#!/bin/bash
# Pre/post-irradiation characterisation sweeps with drivers/radIV.tcl (branch
# explore/rad-model). One line per task in sweeps/$PARAMS:
#   label|lever=value;lever=value;...
# DRV (env, default radIV) picks drivers/$DRV.tcl, e.g. DRV=seeIV.
# Submit from the worktree root, e.g.
#   RUN=20261023_radCal1 PARAMS=params_radCal1.txt; mkdir -p results/$RUN
#   sbatch --array=0-7%8 --export=ALL,RUN=$RUN,PARAMS=$PARAMS \
#          --output=results/$RUN/slurm_%A_%a.out --error=results/$RUN/slurm_%A_%a.err sweeps/radIV.slurm
#
#SBATCH --job-name=radIV
#SBATCH --account=ee1
#SBATCH --qos=ee1-b
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=24:00:00

set -euo pipefail

REPO=/home/ianstafford/blue/ee1/ianstafford/HEMTRAD-wt/rad-model
RUN_DIR=$REPO/results/$RUN
TASK_DIR=$RUN_DIR/task_${SLURM_ARRAY_TASK_ID}

module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs

export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find "$CONDA_PREFIX/share" -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH

mkdir -p "$TASK_DIR"

LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$REPO/sweeps/$PARAMS")
LABEL=${LINE%%|*}
PAIRS=${LINE#*|}

for f in GaN_modelfile_masterD GaN.tcl AlGaN.tcl Insulator.tcl Metal.tcl Continuity.tcl Poisson.tcl rfdevice.tcl rfdevice_SiN.tcl; do
    cp "$REPO/model/$f" "$TASK_DIR/$f"
done

DRIVER="$TASK_DIR/radIV_task.tcl"
JSON="\"label\": \"$LABEL\", \"task_id\": $SLURM_ARRAY_TASK_ID, \"params\": \"$PARAMS\""
{
    echo "set tag $LABEL"
    IFS=';' read -ra KV <<< "$PAIRS"
    for kv in "${KV[@]}"; do
        [ -z "$kv" ] && continue
        echo "set ${kv%%=*} ${kv#*=}"
        JSON="$JSON, \"${kv%%=*}\": \"${kv#*=}\""
    done
    sed 's/^window.*//; s/^\(\s*\)chart /\1#chart /' "$REPO/drivers/${DRV:-radIV}.tcl"
} > "$DRIVER"
echo "{ $JSON }" > "$TASK_DIR/params.json"

cd "$TASK_DIR"
"$FLXSHOME/release/flooxs" radIV_task.tcl
