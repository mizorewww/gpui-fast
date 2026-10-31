#!/bin/bash
# make-dist.sh <patches-branch> <dist-branch> <version-tag>: generated published-shape tree as a child commit.
set -e
W=~/Developer/.figma-shots/work/forks; cd $W/gpui-fast
git checkout -q -f "$1"; git clean -fdq -e target
bun script/prepare-release.ts --tag "$3" 2>&1 | tail -1
D=$(mktemp -d "$W/dist.XXXX"); cp -R target/release-workspace/. "$D"/
# Published-include trimming: tests/examples/benches are not part of the packages.
for c in "$D"/gpui*; do [ -d "$c" ] || continue; rm -rf "$c"/benches "$c"/examples "$c"/tests "$c"/docs; done
# Dev overlay wgpu 30.0.1 + present_checked (crates.io archive + patch, not a member).
cp -R $W/archives/wgpu-30.0.1 "$D"/wgpu; rm -f "$D"/wgpu/.cargo-ok "$D"/wgpu/Cargo.lock; (cd "$D"/wgpu && patch -s -p2 -F3 < <(sed -E 's#^(---|\+\+\+) [^ \t]*/(archives/wgpu-30.0.1|vendor/wgpu)/#\1 x/y/#' $W/diffs/wgpu.diff))
cat >> "$D"/Cargo.toml <<'T'
exclude = ["wgpu"]
T
rm -f "$D/rust-toolchain.toml"; I=$(mktemp -u "$W/idx.XXXX"); export GIT_INDEX_FILE="$I"; GIT_WORK_TREE="$D" git add -A . ; T=$(GIT_WORK_TREE="$D" git write-tree); unset GIT_INDEX_FILE; rm -f "$I"
C=$(git commit-tree "$T" -p "$(git rev-parse "$1")" -m "material: generated published-shape tree of $1" -m "bun script/prepare-release.ts --tag $3, plus wgpu 30.0.1 with present_checked for the dev overlay. Do not edit: regenerate." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
git branch -f "$2" "$C"; rm -rf "$D"; git log -1 --format='%H %s' "$2"; git ls-tree --name-only "$2" | tr '\n' ' '
