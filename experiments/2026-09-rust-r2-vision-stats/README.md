# R2b: Fog and statistics checkpoint

Source `062141d97fd6c8122c93e3dd1bc0b94736442e1e`, annotated tag `rust-kernel-r2b-2026-09-12`.
Tool `6650a423be711878e480d50a0b9fd69b6d0f9ad9`. R0 oracle remains `78cc8da3a03ffedaea58642abae8fcb710db997d`.

1046 production tests pass, including 127 native contracts. Three Rust tests and
Clippy pass. Six cases (284 operation nodes) compare the complete transferred
state, decoded low-level responses and ordered game events. All comparisons pass.
The trace includes reset during window sampling, pauses, Fog toggles, movement
and rule-mode attack/death. Geometry/LOS/LRU coverage is in the contract suite.

This is **partial R2**, not complete World.update or an Agent capacity test.
Permissions, full observations/actions, game lifecycle and window integration
remain pending. Python remains the default. Window/dummy cases test authoritative
state without rendering pixels; their combat display entities are not exercised.

## Reproduce

Use an intact checkout at the exact source SHA; formal measurement used Lab
`runs/star-rust-r2-vision-stats`. Unrelated active-checkout Agent/font deletions
were preserved and excluded from the production commit and formal checkout.

```sh
# Production checkout at 062141d97fd6c8122c93e3dd1bc0b94736442e1e; pinned Rust on PATH
uv sync --extra native
uvx --from maturin==1.15.0 maturin build --release --locked \
  --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/r2b-wheel
uv pip install --python .venv/bin/python --reinstall /tmp/r2b-wheel/*.whl
cargo test -p star-core -p star-rotk --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
.venv/bin/python -m pytest -q
# Lab checkout at tool SHA above:
/path/star/.venv/bin/python tools/rust_migration/r2_vision_stats_probe.py \
  --source /path/star --output /tmp/r2b.json.gz
```

The three-unit, 37-tile fixture has seed42, dt0.25, 40ticks/case, frozen external
wall metadata starting1720000000. Four paused ticks and three resets per case are
included. Mode=real_time/turn_based; display=none/dummy/window. No Agents, Hub or LLM.
No timing claims; Chrome was left open. Default GC, no camera/render workload.
The formal build used `CARGO_TARGET_DIR=/Users/liyang/Developer/star-main/target`
to reuse compiled dependencies; this does not change the source identity.

The compact JSON contains canonical gzip raw name/size/SHA256. This small
functional evidence uses gzip+JSON instead of duplicate ZIP bundles. Build,
installation, complete regression and Rust-check logs are included. No raw trace
is duplicated from R2a. The R2a kernel-only checks remain in the complete suite.

```sh
cd experiments/2026-09-rust-r2-vision-stats
shasum -a 256 -c artifacts/SHA256SUMS
```

The old R2a commit lacks native Fog/statistics computation; this archive validates
new functionality against the normalized Python implementation, not a performance
fix or a new Performance Frontier. No squash merge/default switch has occurred.
