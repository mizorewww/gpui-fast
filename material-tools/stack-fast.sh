#!/bin/bash
# Build one commit per patch on $1 in the Fast source layout.
set -e
W=~/Developer/.figma-shots/work/forks
cd $W/gpui-fast
git checkout -q -f --detach "$1"; git clean -fdq -e target
for p in $W/patches/*.diff; do
  n=$(basename "$p" .diff)
  patch -s -p1 -F3 --no-backup-if-mismatch < "$p" || { echo "FAILED $n"; find . -name '*.rej' -not -path './target/*'; exit 1; }
  find . -name '*.orig' -not -path './target/*' -delete
  python3 -I $W/scripts/manifests.py "$n"
  git add -A crates
  git commit -q -m "material: ${n#*-}" -m "Patch ${n%%-*} of the Material stack, carried from gpui-kit-material vendor/ at 79b4d0f." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
done
git log --oneline "$1"..HEAD | wc -l
