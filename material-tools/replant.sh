#!/bin/bash
# replant.sh <repo> <range-base> <range-tip> <onto>: cherry-pick one commit at a time,
# printing conflicted files and marker counts per patch; a conflict keeps the patch side
# (-X theirs) so later patches stay measurable.
cd "$1"; base=$2; tip=$3; onto=$4
git checkout -q -f --detach "$onto"; git clean -fdq -e target
tf=0;th=0
for c in $(git rev-list --reverse "$base..$tip"); do
  s=$(git log -1 --format=%s "$c" | sed 's/material: //')
  if git cherry-pick "$c" >/dev/null 2>&1; then echo "$s|0|0|"; continue; fi
  if [ -z "$(git diff --name-only --diff-filter=U)" ]; then git cherry-pick --skip >/dev/null 2>&1; echo "$s|empty|0|"; continue; fi
  files=$(git diff --name-only --diff-filter=U)
  n=0; for f in $files; do k=$(grep -c '^<<<<<<< ' "$f" 2>/dev/null); n=$((n+k)); done
  nf=$(echo "$files" | wc -l | tr -d ' ')
  echo "$s|$nf|$n|$(echo $files | sed 's#crates/##g')"
  git cherry-pick --abort
  git cherry-pick -X theirs "$c" >/dev/null 2>&1 || { git add -A; git -c core.editor=true cherry-pick --continue >/dev/null 2>&1 || git cherry-pick --skip >/dev/null 2>&1; }
done
