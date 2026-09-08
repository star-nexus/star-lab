# P3 local synthetic Agents — active investigation

**Status:** REPRODUCED, optimization and runtime validation in progress. No accepted capacity point yet.
**STAR:** star-nexus/star. Baseline `02d0fc1b598c54a172e1122ac9ea4c1e2f46ec15`.

## Problem

Faction-wide pulls repeat own-unit legality work for every Agent. A local 100-session / 100-unit / 1-second think loop produced multi-second queueing despite small frame work times. Static 1000-unit observations expose repeated global occupancy scans and all-visible-enemy attack checks.

## Reproduction

Use exact STAR and Lab SHAs in each result (tooling is separate from runtime). Run from a Lab checkout; prepare a detached STAR worktree at the result source SHA. The Python interpreter must have STAR uv.lock dependencies.

```bash
/path/to/star/.venv/bin/python tools/p3_local_agents.py --source /absolute/star-worktree --units 1000 --agents 1000 --queries 3 --layout interleaved --index --attribute --output /absolute/probe.json
/path/to/star/.venv/bin/python tools/p3_runtime.py --source /absolute/star-worktree --units 100 --agents 100 --delay 1 --seconds 10 --warmup 3 --output /absolute/runtime.json
```

For selected panels add `--scope selected` (requires source `0c1ec5b454a703ed3d90d19db98a6683758996a8` or later). Static indexed probes build the same index as a window world, but do not demonstrate runtime capacity. Fixtures derive from canonical E8 `scenario.zip` and, for interleaved cases, the authoritative board parser; every generated fixture is hashed.

## Measurement boundary

Production window/Animation/Vision/Fog remain active in runtime runs. Lab controller invokes the ENV business gate with `send_response=False`; it includes actual JSON encoding unless `--no-encode`. Socket transport/Hub and LLM inference are absent. One lightweight session owns multiple units. There is no synthetic wire noop; waiting is a scheduler state.

Read `records/10k-online-p3-progress.md` for preregistration and current work. Early runtime-base100 used tool `2e410b8` and measures `_update` work only; it is negative queueing evidence, never a full-frame capacity point. Tool `e05cf06` corrected pacing overshoot drift; `0616503` extended timing to include engine/profiler frame bookkeeping. Do not pool these methodologies.

## Artifacts

Small diagnostic JSON is raw causal evidence. Runtime `.raw.json` preserves all recorded frames/events/censuses. Final compact/raw packaging and integrity receipt are maintained as stages close.
