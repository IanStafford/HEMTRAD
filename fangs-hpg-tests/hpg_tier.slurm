#!/bin/bash
# HPG array job: the seven gan_hpg cases of flooxs-pyplot in four sets, one case per task (23 tasks).
#   0-6   tcl        the Tcl deck, expression tape on (the default since D1)
#   7-13  py         the Python port (Tcl-free build), tape on
#   14-20 tcl-dag    the Tcl deck with FLOOXS_TAPE=0 (the old DAG walk): tells a tape difference from a compiler one
#   21-22 tcl-thr4v  gan_quickIV and gan_trapF with threaded assembly (FLOOXS_ASSEMBLY_THREADS=4) and
#                    FLOOXS_ASSEMBLY_VERIFY=1 (every load also assembled serially and compared bit for bit)
# Submit with submit.sh tier (from the HEMTRAD repo root on HPG). Each task writes $RUN/<set>/<case>/.
#SBATCH --job-name=fangs-hpg
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=32gb
#SBATCH --time=05:00:00
set -uo pipefail
source "$SLURM_SUBMIT_DIR/fangs-hpg-tests/env.sh" || { echo "environment failed"; exit 1; }
CASES=(gan_quickIV gan_calibIdVg gan_trapF gan_vg0 gan_vgm1 gan_sin gan_rescue)
i=$SLURM_ARRAY_TASK_ID
if   [ "$i" -le 6 ];  then SET=tcl;       CASE=${CASES[$i]}
elif [ "$i" -le 13 ]; then SET=py;        CASE=${CASES[$((i - 7))]}
elif [ "$i" -le 20 ]; then SET=tcl-dag;   CASE=${CASES[$((i - 14))]}
else                       SET=tcl-thr4v; THR=(gan_quickIV gan_trapF); CASE=${THR[$((i - 21))]}
fi
FRONT=tcl; [ "$SET" = py ] && FRONT=py
unset FLOOXS_TAPE FLOOXS_ASSEMBLY_THREADS FLOOXS_ASSEMBLY_VERIFY FLOOXS_ASSEMBLY_REPORT
case $SET in
  tcl-dag)   export FLOOXS_TAPE=0 ;;
  tcl-thr4v) export FLOOXS_ASSEMBLY_THREADS=4 FLOOXS_ASSEMBLY_VERIFY=1 FLOOXS_ASSEMBLY_REPORT=1 ;;
esac
export FANGS_CORE_DIR=$FLX/build/python                  # the Python port uses the Tcl-free fangs._core
echo "set=$SET case=$CASE node=$(hostname) partition=$SLURM_JOB_PARTITION cpus=$SLURM_CPUS_PER_TASK cpu=$(lscpu | grep 'Model name' | sed 's/.*: *//') tape=${FLOOXS_TAPE:-default} start=$(date -Is)"
cd "$FLX" || exit 1
# --threads caps OpenMP/BLAS at the allocation (16 cores, as on 2026-10-08); --force because the node is shared
python tools/regress.py run --case "$CASE" --frontend "$FRONT" --flooxs "$FLX/build-tcl/flooxs" \
       --run-dir "$RUN/$SET" --run-id "${SLURM_ARRAY_JOB_ID}-$SET" --threads "$SLURM_CPUS_PER_TASK" --force
rc=$?
[ "$SET" = tcl-thr4v ] && grep -h "VERIFY" "$RUN/$SET/$CASE/flooxs.log" | tail -5
echo "RC=$rc end=$(date -Is)"
exit $rc
