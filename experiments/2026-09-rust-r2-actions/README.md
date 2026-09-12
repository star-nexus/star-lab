# R2d trusted local request checkpoint

Source `02ac380d631b7391bdf0f583084aee8d13d5de0a`, annotated tag
`rust-kernel-r2d-2026-09-12`; tool `d762bd1f06298a59776a554c93d3b49e3fe9a2f2`.
Normalized Python oracle remains R0b `17b17766923ce4db05efb17aaf023818cf69cdf6`.

1115 complete regression tests pass (195 native), plus 3 Rust tests and Clippy.
18 display/Fog/thread configurations record 678 sequential request nodes,
294 faction queries and 114 read segments in the batch replay. The batch runs
those same 678 requests again; do not double this count as distinct workload nodes.
All decoded responses and complete imported states match Python, and batch results
and final state match sequential native execution. Reset invalidates registration.

This connects trusted identity, registration/re-registration, team ownership/FIFO,
move/attack validation, errors and action counters to the public local Rust API.
Consecutive faction queries share facts; any intervening non-query ends the borrow.
This includes a release request that writes a prefix and then fails on an invalid
list element: the next query reflects the actual partial mutation.

**Partial R2 only.** No Hub authentication/transport or real LLM is exercised. The
caller supplies identity at local ingress. Fixtures are three units and 37 tiles,
not a large-scale Agent benchmark. There are no world ticks, rendering or wall-time
performance measurements here. Attack runs only with display=none; dummy/window
cases exercise initialization, move commands, team state and queries. The 1/2/4
settings are still serialized by the native mutex; worker parallelism is R4.
Full lifecycle, remaining actions, window handoff and capacity remain incomplete.

## Reproduce

Use an intact clean checkout at the source SHA. Formal worktree:
`runs/star-rust-r2-actions`; the active production checkout's 49 unrelated Agent/font
deletions were preserved and excluded from commits and complete regression runs.

```sh
uv sync
cargo test -p star-core -p star-rotk --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
uvx --from maturin==1.15.0 maturin build --release --locked \
  --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/r2d-wheel
uv pip install --python .venv/bin/python --reinstall /tmp/r2d-wheel/*.whl
.venv/bin/python -m pytest -q
# From Lab at the tool SHA:
/path/star/.venv/bin/python tools/rust_migration/r2_actions_probe.py \
  --source /path/star --output /tmp/r2d.json.gz
```

Pinned Rust1.98.1/BevyECS0.19.1/PyO3 0.29.2/maturin1.15.0; macOS26.5.2 ARM64,
CPython3.13.12, Mac mini M4 16GiB. Formal builds reuse
`CARGO_TARGET_DIR=/Users/liyang/Developer/star-main/target`; Rust bin is on PATH.
Chrome remains open; no performance gate or timing window applies to this fixture.
Seed42, real_time, displays none/dummy/window, Fog off/on, threads1/2/4. Per-request
wall timestamp is 1720000000+index; registration date is 2026-09-12T12:00:00.
No simulation elapsed time is derived from this metadata.

Raw gzip retains request envelopes, complete expected/actual states and responses,
batch results, cache counters, reset state and console diagnostics. Compact JSON
retains all guards and measured read-segment counters, plus raw name/size/SHA256.
These small functional artifacts use gzip+JSON instead of redundant ZIP bundles.
The first valid driver output remains intermediate in `runs/r2-actions-initial-evidence`;
its compact lacked measured segment counters, so the canonical final tool reran
exactly the same workload with those counters added. It is not a performance repeat.

```sh
cd experiments/2026-09-rust-r2-actions
shasum -a 256 -c artifacts/SHA256SUMS
```
