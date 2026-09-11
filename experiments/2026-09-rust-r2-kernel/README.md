# R2 intermediate kernel checkpoint

Source `d1f5838496b38b97907d31cd0439d3dae53b0eb4`, annotated tag
`rust-kernel-r2a-2026-09-11`. Tool `7af8e4cecb463d294c73fd05f1b7898c840bdd5b`.
R0 oracle remains `78cc8da3a03ffedaea58642abae8fcb710db997d`.

1032 production tests pass, including 113 native contracts. Three Rust core tests
and Clippy pass. Six recorded cases (360 operation nodes) compare complete imported
state, decoded low-level results and ordered events. All comparisons pass.

This is **not complete R2** and makes no capacity claim. It covers dynamic occupancy,
stable A*, rule-mode instant movement and dummy/window authoritative animation,
AP/MP/skill deadlines, and rule-mode damage/crit/death with fallback statistics.
Normal statistics subscribers, Fog, ownership/registration and observations are
not connected yet. Private probes must not be used as Agent APIs. Window movement
tests do not render pixels or allocate combat display effects. Python stays default.

## Reproduce

Use an intact production checkout at the exact source SHA. Formal testing used
`runs/star-rust-r2-kernel`, a clean detached checkout. Unrelated deletions of
`rotk_agent/*` and the font in the active checkout were preserved and excluded.

```sh
uv sync --extra native
cargo test -p star-core -p star-rotk --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
uv run --extra native pytest -q
# From Lab at the tool SHA, with the release extension installed:
/path/star/.venv/bin/python tools/rust_migration/r2_kernel_probe.py \
  --source /path/star --output /tmp/r2-kernel.json.gz
```

The formal release wheel was built with pinned maturin1.15.0 and Rust1.98.1 using
`maturin build --release --locked --manifest-path native/python/Cargo.toml`.
The precise extension and Cargo.lock hashes are in `results/probe.summary.json`.
The compact JSON indexes the complete gzip raw trace (name/size/SHA256). This small
functional archive uses a gzip trace and JSON summary rather than duplicate zip
copies. `results/pytest.log`, `results/rust-checks.log` and `results/build.log`
preserve verification output. No timing conclusion is drawn from their durations.

```sh
cd experiments/2026-09-rust-r2-kernel
shasum -a 256 -c artifacts/SHA256SUMS
```

`cargo test --workspace` without Maturin's extension link flags is not the documented
macOS test command: it attempts to link Python extension artifacts as standalone
targets and fails unresolved Python symbols. Core/rules use Cargo tests, bindings
use the installed wheel's Python contract suite. This build-invocation failure is
distinct from a kernel parity failure.
