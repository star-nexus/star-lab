# R2c team and faction projection checkpoint

Source `582dbdab6e7b060c2589096cd41bc45ee96a474f`, annotated tag `rust-kernel-r2c-2026-09-12`.
Tool `f02fef40c5eb2b361ab2908f5b7eac8fca5c87af`. Python oracle is now R0b
`17b17766923ce4db05efb17aaf023818cf69cdf6` (skill-list ordering addendum).

1075 complete production tests pass (155 native contracts), plus3 Rust tests and
Clippy. Six display/Fog cases record60operation nodes, including252 decoded
faction queries. All state/response comparisons and per-batch reuse guards pass.

Native TeamCoordination retains exclusive atomic conflicts, forced transfer,
request duplicates/order, sorted release-all, registration-order membership and
bounded FIFO. A reverse owner index avoids scanning all claims for release-all.
Deque maxlen survives independently from subsequently changed cap defaults.

Native faction projections preserve own panels, visible enemy/terrain facts,
reachable/attackable, unit_ids selection and per-request commandable fields.
The immutable runtime borrow bounds cache lifetime; census/faction/panel/enemy/tile
facts are lazy and shared only within that batch. Response trees still clone and
some scans remain; R4 optimization/performance has not happened.

**Partial R2 only.** No authenticated dispatcher or registration action has been
connected. Internal probes must not receive Agent requests. The fixtures initialize
registration mappings directly, and do not test transport identity authentication.
Full World.update/game lifecycle, real window presentation and capacity remain open.
Python stays default. Thread count1 here is not a selected parallel default.

## Reproduce

Use a clean intact source checkout at the exact SHA. Formal checkout:
`runs/star-rust-r2-projection`; unrelated active Agent/font deletions were preserved.

```sh
uv sync
cargo test -p star-core -p star-rotk --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
uvx --from maturin==1.15.0 maturin build --release --locked \
  --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/r2c-wheel
uv pip install --python .venv/bin/python --reinstall /tmp/r2c-wheel/*.whl
.venv/bin/python -m pytest -q
# Lab checkout at the tool SHA:
/path/star/.venv/bin/python tools/rust_migration/r2_projection_probe.py \
  --source /path/star --output /tmp/r2c.json.gz
```

Pinned Rust1.98.1, BevyECS0.19.1, PyO3 0.29.2, Maturin1.15.0; Mac miniM4/16GiB,
macOS26.5.2/ARM64, CPython3.13.12. Formal builds set
`CARGO_TARGET_DIR=/Users/liyang/Developer/star-main/target` to reuse dependencies.
Chrome remains open. This is a three-unit,37-tile deterministic fixture,seed42,
real_time mode, no clock steps, renderer, Agents, Hub or LLM. Each case executes
six query batches of seven requests, three claim/release operations, one move,
and a reset before its final query. Both successful and invalid selections are
retained. Three displays×Fog on/off; no timing window/GC/camera selection.

The complete gzip trace is canonical raw; summary indexes name/size/SHA256.
These small functional artifacts use gzip+JSON instead of duplicate ZIP bundles.
All local artifacts, wheel and verification logs have checksums.

```sh
cd experiments/2026-09-rust-r2-projection
shasum -a 256 -c artifacts/SHA256SUMS
```
