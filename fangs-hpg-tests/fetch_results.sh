#!/bin/bash
# Workstation: copy $RUN from HPG into flooxs-pyplot's Test/Regression/hpg_results/<TAG>-fangs/ (gitignored there),
# check every file against HPG's MANIFEST.sha256, and write a short REPORT.md next to it.
# Run from the HEMTRAD repo root after compare.slurm has finished: fangs-hpg-tests/fetch_results.sh
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
source "$here/config.env"

ssh -o BatchMode=yes hpg "test -s $RUN/MANIFEST.sha256" || { echo "no $RUN/MANIFEST.sha256 on HPG: has compare.slurm run?" >&2; exit 1; }
mkdir -p "$WS_RESULTS"
rsync -a --exclude 'core*' --exclude '*.bundle' "hpg:$RUN/" "$WS_RESULTS/"
( cd "$WS_RESULTS" && grep -vE '  \./(MANIFEST\.sha256|logs/compare-[0-9]+\.(out|err))$' MANIFEST.sha256 | sha256sum --quiet -c - ) && echo "all $(wc -l < "$WS_RESULTS/MANIFEST.sha256") files match the HPG manifest"

{
  echo "# FANGS on HiPerGator, $TAG"
  echo
  echo "flooxs-pyplot commit \`$COMMIT\`, built on HPG with the conda route of docs/runbooks/hipergator-setup.md."
  echo "Fetched $(date -Is) from \`$RUN\` (manifest checked)."
  echo
  echo "## Build and ctest"
  echo '```'
  cat "$WS_RESULTS"/logs/build-*.out 2>/dev/null | grep -E "^== |rc=|tests passed|tests failed|\(Failed\)|Timeout|Not Run"
  echo '```'
  echo
  echo "## Comparisons (regress.py compare --tier hpg)"
  for f in "$WS_RESULTS"/compare/*.txt; do
    echo; echo "### $(basename "$f" .txt)"; echo '```'; cat "$f"; echo '```'
  done
  echo
  echo "## Array tasks"
  echo '```'
  grep -h -E "^set=|^RC=" "$WS_RESULTS"/logs/tier-*.out 2>/dev/null
  echo '```'
} > "$WS_RESULTS/REPORT.md"
echo "report: $WS_RESULTS/REPORT.md"
