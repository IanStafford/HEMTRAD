#!/bin/bash
# HPG: submit one stage of the campaign with the account, QOS, partition and log paths of config.env.
# Run from the HEMTRAD repo root on HPG. Ask Ian before each submission (HEMTRAD CLAUDE.md section 2).
#   fangs-hpg-tests/submit.sh build                 # environment, two builds, selftest, ctest (about 1-2 h)
#   fangs-hpg-tests/submit.sh tier [MAXPAR]         # the 23-task array, at most MAXPAR tasks at once (default 6 = 96 CPUs)
#   fangs-hpg-tests/submit.sh compare JOBID         # the comparisons, after array JOBID has finished
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
source "$here/config.env"
[ "$(basename "$PWD")" = HEMTRAD ] || { echo "run from the HEMTRAD repo root" >&2; exit 2; }
mkdir -p "$RUN/logs"
common=(--account="$ACCOUNT" --qos="$QOS" --parsable)
case "${1:-}" in
  build)   sbatch "${common[@]}" --output="$RUN/logs/build-%j.out" --error="$RUN/logs/build-%j.err" "$here/build.slurm" ;;
  tier)    sbatch "${common[@]}" --partition="$PARTITION" --cpus-per-task="$CPUS" --array="0-22%${2:-6}" \
                  --output="$RUN/logs/tier-%A_%a.out" --error="$RUN/logs/tier-%A_%a.err" "$here/hpg_tier.slurm" ;;
  compare) [ -n "${2:-}" ] || { echo "usage: submit.sh compare <array job id>" >&2; exit 2; }
           sbatch "${common[@]}" --dependency="afterany:$2" \
                  --output="$RUN/logs/compare-%j.out" --error="$RUN/logs/compare-%j.err" "$here/compare.slurm" ;;
  *) sed -n '2,7p' "$0"; exit 2 ;;
esac
