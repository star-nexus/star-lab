# R1: owned Rust world, lifecycle, clock and RNG

Source `92a6812beeaee71f4dd3650f5e7cc30f808c7895`, annotated tag
`rust-runtime-r1-2026-09-11`; tool `b2d0bf5` (full SHA in raw evidence).
R0 oracle is `78cc8da3a03ffedaea58642abae8fcb710db997d`.

The complete Python suite passes 952 tests (33 new native contracts), plus two
Rust core tests and warning-free Clippy. A release macOS ARM64 CPython3.13 wheel
was built, installed into a clean virtualenv and exercised without STAR/Pygame
installed. This is **R1 only: no playable Rust game, parallel systems or capacity
claim**. Linux and CPython3.14 wheel acceptance remains R5.

```sh
# Production checkout at the source SHA:
# Install pinned Rust 1.98.1 with cargo on PATH, then:
uv sync --extra native
cargo test -p star-core -p star-rotk --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
uv run --extra native pytest -q
# Lab checkout at the exact tool SHA recorded in probe:
/path/star/.venv/bin/python tools/rust_migration/r1_probe.py \
  --source /path/star --output /tmp/native-r1.json
```

The probe executes real_time/turn_based initialization, reset and RNG sequences
for thread settings1/2/4. Those settings are reserved configuration, **not active
parallel computation**. Raw input, imported/reset state, Python/native draw lists
and complete random states are in `results/probe.json.gz`. The summary's raw
checksum refers to its decompressed bytes. All archived bytes, including the
wheel, are covered by `artifacts/SHA256SUMS`.

```sh
cd experiments/2026-09-rust-r1
shasum -a 256 -c artifacts/SHA256SUMS
```

Formal measurement used a clean detached checkout in `runs/star-rust-r1`.
The active development checkout had an unrelated deletion of `assets/fonts/sh.otf`
under investigation; it was excluded from the source commit and formal checkout.
No user asset change was overwritten.
