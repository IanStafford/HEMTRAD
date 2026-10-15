#!/bin/bash
# Workstation: bundle flooxs-pyplot at $COMMIT and copy it to HPG (HPG has no GitHub credentials; the repo is private).
# Run from the HEMTRAD repo root: fangs-hpg-tests/make_bundle.sh
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
source "$here/config.env"

git -C "$WS_REPO" cat-file -e "$COMMIT^{commit}" || { echo "commit $COMMIT not in $WS_REPO" >&2; exit 1; }
git -C "$WS_REPO" merge-base --is-ancestor "$COMMIT" main || { echo "$COMMIT is not on main" >&2; exit 1; }
git -C "$WS_REPO" bundle create "$WS_BUNDLE" main
git bundle verify "$WS_BUNDLE" >/dev/null
echo "bundle $WS_BUNDLE ($(du -h "$WS_BUNDLE" | cut -f1)) holds $COMMIT"

ssh -o BatchMode=yes hpg "mkdir -p $BASE"
rsync -a --info=progress2 "$WS_BUNDLE" "hpg:$BASE/flooxs-pyplot.bundle"
ssh -o BatchMode=yes hpg bash -l <<REMOTE
set -euo pipefail
cd $BASE
if [ -d flooxs-pyplot/.git ]; then
  git -C flooxs-pyplot fetch -q flooxs-pyplot.bundle main
else
  git clone -q flooxs-pyplot.bundle flooxs-pyplot
fi
git -C flooxs-pyplot checkout -q --detach $COMMIT
echo "HPG checkout: \$(git -C flooxs-pyplot log --oneline -1)"
REMOTE
