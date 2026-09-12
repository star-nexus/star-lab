# R2e world lifecycle and native rule-mode loop

Source `2c83c001780ddf103b94905df81e8a1bc469af6e`, annotated tag
`rust-kernel-r2e-2026-09-12`. Probe and loop tools:
`db3400a09b1681559ac8aaf05652595d681d9d9c`; replay verifier:
`d208e3ebffa2c38514cf1b683df66b0beec6cf65`. Python oracle remains R0b.

1152 complete regression tests pass (232 native), plus 3 Rust tests and Clippy.
The small-scene probe records 394 operation nodes, including 360 calls through
core World.update. Imported authoritative state, complete responses and ordered
events match Python. Tests additionally cover real-time/turn-mode timeout rules,
annihilation precedence, enabled flags, pause and positionless units.

A 60-second, 5000-Unit/1000-Agent **rule-mode integration diagnostic** completes
2007 closed loops. Every Agent finishes at least one; 4017 moves and 64 attacks
are accepted, 63 moves rejected, and all 5000 Units survive. Replaying the recorded
8151 requests and 1779 ticks reproduces every response digest, per-tick game events
and the exact final-state digest. Initial world and request/tick trace are preserved.

This is not rendered capacity acceptance: no window/drawing, and display=none moves
instantaneously. The loop includes client JSON work, per-response SHA256 tracing,
native steps and presentation extraction. Its P99 work is 41.93ms, actual world
frequency29.635Hz; observation response P99=119.21ms and action queue P99=120.65ms.
These already exceed the corresponding numerical main targets, even before adding
rendering; different semantics/diagnostic overhead also prohibit a direct window
comparison. `all_passed` in loop.json means its documented functional guards only.
No Performance Frontier update, default switch, merge or capacity certification.

## Reproduce

Use a clean, intact worktree at the source SHA. Formal checkout is
`runs/star-rust-r2-lifecycle`; active production's 49 unrelated deletions are untouched.

```sh
uv sync
cargo test -p star-core -p star-rotk --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
uvx --from maturin==1.15.0 maturin build --release --locked \
  --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/r2e-wheel
uv pip install --python .venv/bin/python --reinstall /tmp/r2e-wheel/*.whl
.venv/bin/python -m pytest -q
# From Lab at db3400a (substitute the intact source/interpreter):
/path/star/.venv/bin/python tools/rust_migration/r2_lifecycle_probe.py \
  --source /path/star --output /tmp/probe.json.gz
/path/star/.venv/bin/python tools/rust_migration/r2_native_loop.py \
  --source /path/star --output /tmp/loop.json.gz --units 5000 --agents 1000 \
  --seconds 60 --fps 30 --threads 1 --budget-ms 18
# Replay the archived trace with the archived wheel and exact source, using verifier d208e3e:
/path/star/.venv/bin/python tools/rust_migration/replay_native_loop.py \
  --source /path/star --trace experiments/2026-09-rust-r2-lifecycle/results/loop.json.gz \
  --output /tmp/loop-replay.json
```

Pinned Rust1.98.1/BevyECS0.19.1/PyO3 0.29.2/maturin1.15.0, CPython3.13.12,
macOS26.5.2 ARM64, Mac mini M4/16GiB. Formal builds reuse
`CARGO_TARGET_DIR=/Users/liyang/Developer/star-main/target`; Rust bin is on PATH.
Chrome remains open. Diagnostic and replay were serial; no performance run overlapped
builds/tests. All startup/slow loop frames are retained, no warmup exclusion.

Small probe: seed42, 3 Units/37 tiles, real_time, three display profiles with no
actual rendering; only none attacks. 120 ticks of1/30 per case, injected wall
metadata increments0.25 per tick, reset at tick61. Statistics, movement, recovery,
lifecycle and Vision run in World.update order. Offline LLMSystem is mounted, but
no SettlementReportSystem or UI rendering is part of this core fixture.

Large loop: canonical120x120 fixture, seed42, all three factions, selected owned
Unit panels, real register/claim actions, move/attack/wait50/25/25, invalid waits
without resampling. First request uniform0–30 wall seconds; after actions, rejection-
sampled normal(30,5) constrained15–45 seconds, no polling during thought. LocalAgents
is reused with only the request gate overridden; the initialization Python world
is reset/released before timing, so all subsequent authority is native. Simulation
advances1/30 per actual tick, without wall catch-up. Setup2.185s is outside timing.

Canonical fixture bytes match the earlier P3 archive hash
`1eeff5d72863206587e852c85fb5b594dc5489488bf40556e848fe13a9fc1a52`; use its existing
single canonical archive rather than duplicating it. Native initial world is a new
artifact containing imported components and exact wall metadata for this run.
Gzip raw plus compact JSON follow the existing small-functional-artifact convention.
All artifacts, release wheel, logs and summaries are covered by SHA256SUMS.

```sh
cd experiments/2026-09-rust-r2-lifecycle
shasum -a 256 -c artifacts/SHA256SUMS
```
