# R0: normalized Python oracle

Validated source `78cc8da3a03ffedaea58642abae8fcb710db997d`, annotated tag
`rust-python-oracle-r0-2026-09-11`. Origin `6a970deaee7d9b8d3939edd102973f2377edd6ac`.
Tool source `85c7dc8d9406e22761390eadbf80f3edbec0b873` (STAR Lab).

The full regression has 919 passing tests. Six real_time/turn_based × none/dummy/window
traces replay with exact state, event and decoded-response equality across
PYTHONHASHSEED=123 and 981. Each trace has 150 ticks plus ordered local actions.
All modes use SDL's dummy driver: window here means the window system configuration,
**not a visual window acceptance test or a performance result**.

Reproduce with the exact checkouts and the production virtualenv after `uv sync`:

```sh
# In the production checkout at the source SHA above:
uv run pytest -q
# In Lab at the tool SHA above (replace absolute checkout paths):
PYTHONHASHSEED=123 /path/star/.venv/bin/python tools/rust_migration/replay.py \
  --source /path/star --mode real_time --display dummy --ticks 150 \
  --output /tmp/oracle.json.gz
PYTHONHASHSEED=981 /path/star/.venv/bin/python tools/rust_migration/replay.py \
  --source /path/star --replay /tmp/oracle.json.gz --output /tmp/replayed.json.gz
```

Repeat for both modes and all three display values. Replaying the archived
`real_time-dummy.json.gz` against origin reproduces the documented visibility-history
list difference and exits 1, while the normalized source exits 0. Inputs, scenario,
seed, simulation dt and injected wall times are inside each gzip JSON trace.
The tool creates/removes its uniquely named temporary map in the chosen source;
it refuses to overwrite an existing map. Hub/BOT/real LLM are disabled.

```sh
cd experiments/2026-09-rust-r0
shasum -a 256 -c artifacts/SHA256SUMS
```

`results/*.summary.json` are compact indexes, not substitutes for the raw gzip
state records. Diagnostic serialization fails on unspecified objects; it does not
silently omit new game state. Presentation exclusions are explicit in the tool.
Rust-specific lifecycle/authority/parallel tests belong to subsequent phases.
