# R4e: 5000 Units + 1000 Agents capacity validation (2026-09-29)

**PASS: API18, one native thread, three independent 30s warmups + 300s measurements.** 5000-Agent expansion is paused by user request. This validates the current canonical workload, not migration release or arbitrary combat density.

Progress: `World core █ migrated | 1000-Agent capacity █ passed | System parallel ▒ partial/internal only | integration/platform/release ▒ pending` (stage status, not elapsed-work percentage).

| Run | Frame P99 ms | Observation response P99 ms | Action queue P99 ms | Hz | Alive / peak moving |
|---|---:|---:|---:|---:|---:|
| rust-300-r1 | 29.800 | 45.872 | 35.293 | 30.0 | 5000 / 171 |
| rust-300-r2 | 29.275 | 47.783 | 35.601 | 30.0 | 5000 / 177 |
| rust-300-r3 | 29.470 | 44.798 | 34.744 | 30.0 | 5000 / 173 |

Every long run passes frame P99 ≤33.33ms, world Hz ≥29.7, observation response/observation queue/action queue P99 ≤100ms, backlog, completed-loop and survival guards. All 9000 admitted frames per run, including slow frames, are retained. Individual maximum frames reach 37.361/35.370/39.215ms; passing the whole-window P99 is not an every-frame guarantee.

Mac mini M4 / 16GiB / 10 CPU cores, macOS26.5.2, CPython3.13.12, release API18, Cocoa2480×1239, canonical120×120/Fog ON, minimap Unit layer OFF, finite-run GC deferred, Chrome open. One thread and 8ms Lab Agent budget are sufficient for this gate. World fixed dt=1/30; Agents use wall-clock post-action thinking30±5s truncated15–45s, initial requests uniform0–30s. Each observation covers controlled Units; perUnit move/attack/wait50/25/25, illegal choice waits. No polling while thinking. All 5000 Units survive; only171–177 move simultaneously at peak. Protocol/Hub and realLLM excluded.

Final documentation source `7e145d169433695cd4957e186a6b2fda06813c26`, annotated `rust-kernel-r4e-2026-09-29`; measurement implementation remains5147e4d. No runtime change between measured source and this documentation checkpoint.

## Source and reproduction

- Original production Python: `6a970deaee7d9b8d3939edd102973f2377edd6ac`.
- Current normalized Python and Rust measurement: `5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5`, oracle `python-r0c-3cc4ffe`, API18/schema5. Source checkouts were clean.
- Measurement tooling: `103f2ebf633b4934c3007228db3f62740e51d231`; analysis/replay/packaging tooling: `38c4322e5bfadf66d96d05098bf9c09b6ff11ef9`.
- Extension SHA256 `324454a00ab8bd3559c9229e6c6c9644242d65c488585eba7d29a63b39d29405`; binary build source `07bdb2e89c69959c2b8cb8e61329536c032f187e`.
- Canonical wheel: `../2026-09-rust-integer-limit/artifacts/r3d5-integer-limit-raw.zip`, member `artifacts/after/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl`. Unchanged binary; no rebuild this stage.

Use intact checkouts at the exact source SHAs, `uv sync --locked`, then install that wheel for Rust. Exact six measurement commands, environment and exit status are in [commands.json](results/commands.json); substitute local source/Lab/output paths. Run serially with Chrome open and the stated window profile. Original Python uses `--legacy-python-cli` because its entrypoint predates backend flags; this adapter only omits unsupported CLI arguments.

Extract `artifacts/r4e-1000-agents-raw.zip` into this experiment directory before recomputing/replaying. From Lab run:

```sh
PYTHONPATH="$SOURCE:$LAB/tools:$LAB/tools/rust_migration" "$SOURCE/.venv/bin/python" tools/rust_migration/analyze_1000_gate.py --root experiments/2026-09-rust-1000-agent-validation
HEADLESS=1 SDL_VIDEODRIVER=dummy PYTHONPATH="$SOURCE:$LAB/tools:$LAB/tools/rust_migration" "$SOURCE/.venv/bin/python" tools/rust_migration/replay_rendered_loop.py --source "$SOURCE" --trace "$LAB/experiments/2026-09-rust-1000-agent-validation/results/rust-300-r3.trace.json.gz" --threads 4 --output /tmp/r4e-replay.json
python3 tools/rust_migration/package_agent_capacity.py --root experiments/2026-09-rust-1000-agent-validation --prefix r4e-1000-agents
```

`SOURCE` is the clean5147e4d checkout and `LAB` the Lab root; replay enforces source/binary checksums. Verify `shasum -a 256 -c artifacts/SHA256SUMS` from the experiment directory. Compact archive contains summaries and its own checksums; raw archive/index retain all six runs and negative controls.

## Correctness and limitations

4-thread replay matches all40994 requests,9880ticks,9880presentation extractions, and final state from the third1-thread long run. This verifies thread equivalence on that trace, not4-thread performance or System-level parallelism. 18 Lab tests passed. An initial pytest invocation omitted PYTHONPATH and failed collection; corrected invocation passed. Production code is unchanged this stage;2217 prior production regressions are R4d evidence, not rerun here.

No new rule change is introduced. Original-vs-normalized ordering changes G001–G003 still apply; G008/G009/R001/R002 remain open. Python stays the default, native threads=1. No merge/push. See [analysis](analysis.md), [decision](decision.md), [System parallel audit](../../records/rust-system-parallel-status.md) and production GAP ledger.
