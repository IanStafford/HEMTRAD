#!/bin/bash
# Delete everything this campaign made, after the results are on the workstation and Ian has confirmed.
#   fangs-hpg-tests/cleanup.sh           # dry run: shows what would go
#   fangs-hpg-tests/cleanup.sh --yes     # deletes
# Removes on HPG: $BASE (checkout, both builds, conda environment and package cache, results, logs).
# Removes on the workstation: the bundle $WS_BUNDLE. Keeps the fetched results in flooxs-pyplot (gitignored there) and
# this folder (move it to archive/ per HEMTRAD's rule, or delete it, as Ian says).
# Not touched: the older HPG checkout $HPG_USER_BLUE/flooxs-pyplot (da619c4c, 2026-10-08); ask Ian about that separately.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
source "$here/config.env"
go=0; [ "${1:-}" = --yes ] && go=1

[ -s "$WS_RESULTS/MANIFEST.sha256" ] || { echo "no fetched results at $WS_RESULTS: run fetch_results.sh first" >&2; exit 1; }
# every manifest file must match in the fetched copy, or (when a later recompute rewrote it there, e.g. the regress.py
# reports) its original saved under hpg-original/
bad=$( cd "$WS_RESULTS" && grep -vE '  \./(MANIFEST\.sha256|logs/compare-[0-9]+\.(out|err))$' MANIFEST.sha256 \
       | sha256sum -c - 2>/dev/null | sed -n 's/: FAILED.*$//p' || true )
for f in $bad; do
  ( cd "$WS_RESULTS/hpg-original" 2>/dev/null && grep -F "  $f" ../MANIFEST.sha256 | grep -E "  ${f//./\\.}$" | sha256sum --quiet -c - ) \
    || { echo "fetched results do not match the manifest ($f): not deleting" >&2; exit 1; }
  echo "$f: changed after the fetch; original kept in hpg-original/"
done
case "$BASE" in "$HPG_USER_BLUE"/fangs-hpg-*) ;; *) echo "refusing: BASE=$BASE is not a fangs-hpg-* folder" >&2; exit 1 ;; esac

ssh -o BatchMode=yes hpg "squeue -h -u \$USER -n fangs-build,fangs-hpg,fangs-cmp" | grep -q . && { echo "campaign jobs still queued or running" >&2; exit 1; }
echo "HPG: $BASE ($(ssh -o BatchMode=yes hpg "du -sh $BASE 2>/dev/null | cut -f1"))"
echo "workstation: $WS_BUNDLE ($(du -h "$WS_BUNDLE" 2>/dev/null | cut -f1))"
if [ "$go" = 1 ]; then
  ssh -o BatchMode=yes hpg "rm -rf '$BASE'" && echo "deleted $BASE on HPG"
  rm -f "$WS_BUNDLE" && echo "deleted $WS_BUNDLE"
else
  echo "dry run: nothing deleted (add --yes)"
fi
