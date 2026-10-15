#!/bin/bash
# HPG batch job: environment (first time), the two builds of flooxs-pyplot, selftest, and ctest of both builds.
# Submit with submit.sh build (from the HEMTRAD repo root on HPG). Writes $RUN/logs/build-*.log and $RUN/ctest/*.
#SBATCH --job-name=fangs-build
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24gb
#SBATCH --time=04:00:00
set -uo pipefail
source "$SLURM_SUBMIT_DIR/fangs-hpg-tests/env.sh" || { echo "environment failed (see the conda output above)"; exit 1; }
L=$RUN/logs; C=$RUN/ctest; mkdir -p "$L" "$C"
NJ=${SLURM_CPUS_PER_TASK:-8}
cd "$FLX" || exit 1
step() { echo "== $* $(date -Is)"; }

step "versions"
{ git log --oneline -1; hostname; lscpu | grep 'Model name'; which python cmake c++; c++ --version | head -1
  python --version; conda list --explicit; } > "$L/versions.txt" 2>&1
[ "$(git rev-parse --short=8 HEAD)" = "${COMMIT:0:8}" ] || { echo "checkout is not $COMMIT"; exit 1; }

common=(-DCMAKE_PREFIX_PATH="$CONDA_PREFIX" -DPython_EXECUTABLE="$(which python)" -Dnanobind_DIR="$(python -m nanobind --cmake_dir)")
for b in build build-tcl; do
  extra=(); [ "$b" = build-tcl ] && extra=(-DFANGS_WITH_TCL=ON)
  step "configure $b"
  cmake -S . -B "$b" "${common[@]}" "${extra[@]}" > "$L/cmake-$b.log" 2>&1; echo "cmake rc=$?"
  step "build $b"
  cmake --build "$b" -j "$NJ" > "$L/make-$b.log" 2>&1; echo "make rc=$?"
  grep -E "error:|Error [0-9]" "$L/make-$b.log" | head -20
done
grep -iE "FANGS_WITH_TCL|FFTW3|HDF5|UMFPACK|Eigen|OpenMP|BLAS|nanobind|Tcl" "$L/cmake-build.log" "$L/cmake-build-tcl.log" > "$L/cmake-summary.txt"

export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
step "selftest"
tools/fangs --selftest > "$L/selftest.log" 2>&1; echo "selftest rc=$?"; tail -3 "$L/selftest.log"
tools/fangs --version >> "$L/selftest.log" 2>&1

for b in build build-tcl; do
  step "ctest $b"
  ctest --test-dir "$b" -N | tail -1 > "$C/count-$b.txt"
  ctest --test-dir "$b" -j $((NJ / 4)) --timeout 3600 --output-on-failure > "$C/ctest-$b.log" 2>&1; echo "ctest $b rc=$?"
  grep -E "tests passed|tests failed|\(Failed\)|Timeout|Not Run" "$C/ctest-$b.log"
done
step "done"
