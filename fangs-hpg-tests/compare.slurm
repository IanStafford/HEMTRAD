#!/bin/bash
# HPG batch job (small, after the array): every comparison of this campaign, written to $RUN/compare/.
# Submit with submit.sh compare <array job id> (it waits for the array with --dependency=afterany).
#SBATCH --job-name=fangs-cmp
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=00:30:00
set -uo pipefail
source "$SLURM_SUBMIT_DIR/fangs-hpg-tests/env.sh" || { echo "environment failed"; exit 1; }
O=$RUN/compare; mkdir -p "$O"
cd "$FLX" || exit 1
cmp() { local name=$1; shift; echo "== $name: regress.py compare $*"; python tools/regress.py compare --tier hpg "$@" > "$O/$name.txt" 2>&1; echo "rc=$?"; cat "$O/$name.txt"; }
cmp tcl-vs-baseline     --run-dir "$RUN/tcl"                                # Tcl deck, tape on, against the stored 2026-10-08 baselines
cmp py-vs-tcl           --run-dir "$RUN/py"  --reference "$RUN/tcl"         # Python port against the Tcl deck of this session
cmp py-vs-baseline      --run-dir "$RUN/py"                                 # Python port against the stored baselines
cmp tcl-vs-dag          --run-dir "$RUN/tcl" --reference "$RUN/tcl-dag"     # tape against the DAG walk, same binary (should be 0)
cmp dag-vs-baseline     --run-dir "$RUN/tcl-dag"                            # DAG walk against the stored baselines (compiler only)
cmp thr4v-vs-tcl        --run-dir "$RUN/tcl-thr4v" --reference "$RUN/tcl" --case gan_quickIV gan_trapF
grep -h "VERIFY" "$RUN"/tcl-thr4v/*/flooxs.log > "$O/thr4v-verify-lines.txt" 2>/dev/null
echo "== threaded-assembly VERIFY lines (every diffs= must be 0):"; cat "$O/thr4v-verify-lines.txt"
( cd "$RUN" && find . -type f ! -name 'core*' ! -name '*.bundle' -print0 | sort -z | xargs -0 sha256sum ) > "$RUN/MANIFEST.sha256"
echo "manifest: $(wc -l < "$RUN/MANIFEST.sha256") files"
