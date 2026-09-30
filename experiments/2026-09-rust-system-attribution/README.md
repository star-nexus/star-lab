# P0 Rust System dependencies and fixed-input attribution

**Status: VALIDATED: scoped attribution/equivalence; no parallel speedup/capacity claim.**
Progress: `recovery █ | dependencies █ | attribution █ | parallel optimization ░ | capacity ░`.
Target remains 5000 Units + 1000 Agents; 5000 Agents paused.

Validated doc checkpoint `c058d75c0ad67a7c340c2a6ac74a9d5bc2888adf`, annotated
`rust-parallel-p0-attribution-2026-09-30`. Implementation remains2ac2b29.
All four probes passed; analyzer622c9e7441757c12d75cdf0d083cde4a7c6fd8dd.
2239Python regressions/22new,4Rust/fmt/Clippy/release passed. No new capacity.

## Problem and source

R4e world step is only 0.295ms mean, but its per-System costs are unknown. Putting
all Systems in a pool without read/write and business-order constraints would
risk changed Fog, occupancy, event/RNG and immediate action semantics. Production
[dependency table](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-system-dependencies.md)
separates between-System, within-System and cross-request sharing.

- Baseline R4e tag: rust-kernel-r4e-2026-09-29 / 7e145d169433695cd4957e186a6b2fda06813c26.
- Frozen measured implementation: 5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5.
- Attribution implementation/tests: 2ac2b29a7a3bf09d92370a0352dcf0fd47f741e5.
- Probe tool: 31c93a3fc294df55810f384b2e3e36b72c507cb3. Analyzer file SHA is in comparison.json.
- API18/schema5/oracle python-r0c-3cc4ffe; source and extension SHA distinguish private diagnostic capability.
- New release extension SHA a73c477263d792cd0c4f71e3ab6001a36223cf0afd7136f8e8975f16b584731f.
- Frozen release extension SHA 324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405.

## Environment and exact input

Mac mini M4/16GiB, CPython3.13.12, pinned Rust1.98.1 / Bevy0.19.1 / PyO3 0.29.2 /
maturin1.15.0, release wheel. This is headless replay with SDL dummy; it does not
rerender Cocoa pixels or admit real-time requests. The original R4e recording
used 30Hz fixed dt, 5000 live Units/1000 Agents, approximately 30s post-action
think time, staggered start, Fog/canonical/selected scope. All 9880 recorded ticks,
40994 requests and 9880 display extractions are replayed, INCLUDING original warmup.
No real LLM/Hub/network or new wallclock-response order is measured.

Canonical input is owned by ../2026-09-rust-1000-agent-validation/artifacts/r4e-1000-agents-raw.zip,
members results/rust-300-r3.trace.json.gz and results/rust-300-r3.initial.json.gz.
Extract just those two members into a private runs directory; do not duplicate
canonical input into this archive or modify a frozen checkout. Trace SHA:
1f9b155129de9e43780c8885b40aba805e4c4794755fd2af70747058a7824b77;
initial SHA: 8b594c465a63728222c57f257111d500c1c378e226b3496c63c0b11870629bc0.

## Reproduction

Check out exact source SHAs above in separate intact worktrees. `uv sync --locked`
creates each environment. Baseline install uses canonical R3d5 wheel referenced
by R4e manifest. Candidate build (or install the archived macOS ARM64 wheel):

```sh
PATH="$HOME/.cargo/bin:$PATH" uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/system-profile-wheel
uv pip install --python .venv/bin/python /tmp/system-profile-wheel/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
HEADLESS=1 SDL_VIDEODRIVER=dummy .venv/bin/python -m pytest -q
PATH="$HOME/.cargo/bin:$PATH" cargo test -p star-core -p star-rotk --locked
PATH="$HOME/.cargo/bin:$PATH" cargo fmt --all -- --check
PATH="$HOME/.cargo/bin:$PATH" cargo clippy --workspace --all-targets --locked -- -D warnings
```

All four exact probe argv, cwd, safe environment, source/extension/trace SHA and
exit codes are in results/commands.json. Substitute local source/Lab/input/output
paths; run SERIAL after tests/builds finish. A new build must record its actual
extension SHA; do not claim it is the archived binary. Probe checks source and
binary hashes before executing. `--mode plain` replays the frozen binary;
`--mode compare` advances two candidate worlds in identical input order, one
ordinary and one profiled. It compares full decoded responses, full deltas and
final full state. All request/events/final hashes also match canonical recording.
Cross-process frozen/candidate full-output-stream hashes must then match.

After extracting this package's raw archive into the experiment root, recompute:

```sh
python3 tools/rust_migration/analyze_system_attribution.py --root experiments/2026-09-rust-system-attribution --trace runs/rust-system-attribution-input/rust-300-r3.trace.json.gz
cd experiments/2026-09-rust-system-attribution
shasum -a 256 -c artifacts/SHA256SUMS
```

Expected: all four probes pass; identical request/tick/delta counts, full-output
stream/final hashes; compare runs validate complete objects, including list order.
No fields are normalized away. Phase summaries/absolute times may differ across
machines. Timings are diagnostic wall time, not a live-capacity result or a 1/2/4
speed comparison. Original step error/partial-write behavior is retained.

## Artifacts and limits

Compact evidence contains manifest/docs, commands/environment, all run summaries
and analyzer output. Raw forensic archive preserves every per-tick phase sample,
release wheel and regression log. results/packages.json provides both locators,
byte sizes and hashes; raw is never replaced by compact. Inputs reference R4e's
canonical archive. Stage does not update Performance Frontier, close an existing
GAP, switch defaults or enable System scheduling. See analysis.md and decision.md.
