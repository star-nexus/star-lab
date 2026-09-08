# P0 closeout — complete

Completed 2026-09-08. P1 has not started.

## Published source and evidence

- STAR production `main`: `02d0fc1b598c54a172e1122ac9ea4c1e2f46ec15`.
- Validated runtime remains `9581084835633e10d80aac849925939bc59b9138`.
- Published annotated tag `scale-10k-100pct-30hz-sustained-e8` still resolves to that runtime.
- Lab canonical E8 evidence: `2dfbb09b4c2fc556bcbe05dadaa1b1fe46c6de89`.
- Lab archival checkpoint, pushed before removal: `d4a6ad697ecd80a40e1e598586e8be38fbcf1279`.
- This final receipt is maintained on Lab main; use `git log -1 -- archives/2026-09-10k-p0/closeout.md` to identify its commit.

STAR main includes the latest map-editor upstream and all retained runtime
changes; no forced production history rewrite was used. The closeout itself
changes no measured system hot path. Its only runtime-side cleanup removes the
experiment-specific crossing-cost correlation module and snapshot fields.
General scale harness, profiler, driver, production tests and user docs remain.

## Preservation and cleanup

57 exploratory/generated files and 1394 result files were byte-verified in Lab;
681 results reuse canonical case bytes and 713 are in the supplement ZIP. The
approximately 387 MiB local results directory is removed. Rejected experiments,
negative gates, untracked helpers/maps and the generated adapter ZIP are preserved.
31 generated Python/OS cache paths were removed; local environment and tool
configuration were retained. STAR checkout has no experimental results or diaries.

29 local and 34 remote 10K/phase5 working branches were deleted. All unrelated
remote branches were checked unchanged. Remote deletion used one atomic push with
expected-SHA leases. 63 archived ref entries represent 40 distinct commits; an
independent empty repository restored all of them from the captured production
base and bundle. Historical tooling was checked out, its fixture restored, and
its CLI plus 9 E8 tests ran successfully. See machine-readable migration,
restoration and retirement manifests beside this file.

## Validation

- `uv run --frozen pytest -q`: **869 passed**, 4.97s.
- `uv run --frozen python tools/run_performance_contracts.py`: **81 passed**, 1.11s.
- `uv run --frozen python -m compileall -q framework protocol rotk_env rotk_agent tools`: PASS.
- Frozen tooling CLI, fixture hash and E8 test replay: **9 passed**, 12.63s.
- `python3 tools/verify_p0_archive.py`: package and **1451 migrated file locators** pass.
- STAR `git diff --check`, clean main, remote main/tag identities and sole remaining local branch verified.

The above suites overlap and must not be added into a unique-test count. These
are integration/recovery checks, not a new machine performance acceptance run.
No P1 long test or architecture change was performed. Sustained gate and known
short-window/frame-body limitations remain exactly as recorded in the E8 case.

## Resume

Read [records/10k-online-resume.md](../../records/10k-online-resume.md), then the
[next-step priorities](../../records/10k-online-next-steps.md). P1 starts with a
bounded long-run recorder and measured overhead, before 30–60 minute soak runs.
New experiment workspaces and results belong under Lab; keep STAR main user facing.
