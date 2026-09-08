# P0: 10K production closeout and archival migration

Date: 2026-09-08. User authorized integration, remote preservation and retirement
of exploratory branches/files before starting P1. Current execution status is in
[the recovery entry](../../records/10k-online-resume.md); historical notes below
are frozen as written and may mention old paths or unpublished/local states.

## Ownership and contents

STAR keeps production fast paths, the generic profiler/scale harness/driver,
functional and structural regression tests, and user-facing measurement docs.
STAR Lab owns phase-specific probes, A/B launchers, offline analyzers, their tests,
experimental scenario fixtures, raw results, decisions and work diaries.

- `workspace-migration.json`: SHA256, size and archive locator for 57 migrated
  files. The canonical 10K fixture is deduplicated against the E8 case ZIP.
- `results-migration.json`: every one of 1394 non-OS-metadata result files has an
  exact archive locator and SHA256. 681 match existing canonical case bytes;
  the other 713 are in `local-results-remainder.zip`. Remainders are historical
  working evidence, not newly endorsed formal experiments. Negative runs remain.
- `workspace/`: immutable source/document/fixture copies, including untracked
  helpers and a generated adapter bundle. Source imports and paths are historical;
  use the exact tooling checkout below rather than executing this directory.
- `branch-inventory.json`: captured branch tips and the explicit retirement scope.
  Only 10K/phase5 working and synchronization branches are retired. Unrelated
  feature, release, backup and tournament branches and milestone tags are retained.
- `phase5-retired-refs.bundle`: compact forensic capture of retired refs, excluding
  the captured production base. This is an archival artifact, not a maintained
  fork or a second production source tree. STAR remains the source authority.
- `e7-remote-final-note.md`: the final remote E7 note, including a remote-only
  documentation update that was not part of the retained runtime.
- `restore-verification.json`: independent empty-repository recovery test.
- `SHA256SUMS`: checksums for this package, excluding the checksum file itself.

## Restore a retired source state

The bundle requires the production base and its history. Start from a full STAR
clone, then import archival refs under a separate namespace (no branch overwrite):

```bash
git -C /path/to/star fetch origin main --tags
git -C /path/to/star bundle verify /path/to/star-lab/archives/2026-09-10k-p0/phase5-retired-refs.bundle
git -C /path/to/star fetch /path/to/star-lab/archives/2026-09-10k-p0/phase5-retired-refs.bundle 'refs/*:refs/archive/phase5/*'
git -C /path/to/star worktree add --detach /path/to/star-lab/runs/replay-e8 1e67bc04d97cb24056b09119df799a43929cd44b
unzip /path/to/star-lab/experiments/2026-09-10k-e8-volume/artifacts/scenario.zip -d /path/to/star-lab/runs/replay-e8/rotk_env/maps
cd /path/to/star-lab/runs/replay-e8
uv run --frozen python tools/run_phase5_e8.py --help
```

The source SHA above includes all final E8 tooling. For an exact historical rerun,
use that run's `tooling_sha` from its manifest. Follow the [E8 case](../../experiments/2026-09-10k-e8-volume/README.md)
for commands, dependencies, fixture hash and runtime SHA. The runner makes a
separate detached runtime checkout at `--sha` and stamps both source identities.
Run outputs land in the Lab-hosted worktree's `results/`; archive them with their
manifest and checksums before removing the worktree. Do not remove a worktree
containing unarchived outputs. `runs/` is ignored working space, not durable evidence.

Existing raw traces can be analyzed from this tooling checkout without launching
SDL or changing production. No P1 long run is part of this closeout.

## Acceptance boundary

The sustained E8 milestone identifies runtime `9581084835633e10d80aac849925939bc59b9138`.
Complete admitted traces and full 30-second blocks pass; rolling 5-second and
frame-body counterexamples are retained. No samples were removed for suspected
Chrome interference. P0 does not promote the result to every-frame or online-Agent
capacity, and does not perform a new machine timing acceptance run.

## Integrity check

From STAR Lab, run `python3 tools/verify_p0_archive.py`. This checks the package
index and all 1451 migrated file locators, including members deduplicated into
canonical experiment archives. The branch bundle also has a separate Git restore
test; byte checksums alone are not treated as proof of Git recoverability.

## Release gate definition

The E8 claim is pinned to the fixed workload and exact runtime above. Its gate
uses each complete admitted sustained trace independently: controlled-work P99
<=33.33ms, with no pooled runs, dropped slow samples or diagnostic-only substitutions.
Evidence consists of one >=300s run and three fresh-process >=60s repeats; each
passes all workload and non-truncation guards. Full 30s blocks and rolling5s /
frame-body metrics are reported separately, retaining failures. This is the
recorded milestone's scope; future soak tests must define admission, maintenance
windows, segmentation and recorder overhead before collecting release evidence.
