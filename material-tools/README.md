# Trial fork-migration tools

Prototype of the sync routine, used for the trial branches. Paths assume a scratch directory.

- `hunks.py`, `split.py`, `manifests.py`, `stack-fast.sh`, `stack-kit.py`: split `vendor/` (against crates.io archives or Kit `bb85882`) into one commit per patch in the source layout.
- `replant.sh`: cherry-pick a stack onto a commit one patch at a time and print conflicted files and hunks per patch.
- `make-dist.sh`: patches branch to a generated published-shape commit (`prepare-release.ts` plus wgpu 30.0.1 with `present_checked`), which is what Cargo `[patch]` points at.
- `sim_sync.py`: textual simulation of the next Zed sync; its result is not pushed.
