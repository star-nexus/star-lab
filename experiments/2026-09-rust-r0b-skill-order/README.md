# R0b skill-list ordering follow-up

The first R0 pass omitted `available_skills`: its source is a Python set and the
handler emitted it in hash order. A four-skill fixture reproduces different lists
under PYTHONHASHSEED1 and99 at `062141d97fd6c8122c93e3dd1bc0b94736442e1e`.
Source `17b17766923ce4db05efb17aaf023818cf69cdf6` fixes only this list order, with
1047 full tests passing. Tag `rust-python-oracle-r0b-2026-09-12` is annotated.
The original `rust-python-oracle-r0-2026-09-11` and its evidence remain immutable.

This corrects the earlier broad claim of fully normalized R0 observation lists:
the old six scenarios did not exercise a populated multi-skill set. R0b is the
new Python comparison baseline for subsequent native observation work; R2a/b
archives retain their original comparison scope and version.

## Reproduce

Create intact before/after checkouts at the SHAs above. Tool source:
`b45d8bb281f32cbdd76b2e9d83a55f96c144bc81` in Lab.

```sh
/path/star/.venv/bin/python tools/rust_migration/oracle_skill_order_probe.py \
  --before /path/before --after /path/after --output /tmp/skill-order.json
# In after checkout, with the recorded R2b release wheel installed:
/path/star/.venv/bin/python -m pytest -q
```

Formal tests used the R2b isolated interpreter and installed wheel, with cwd at
`runs/star-rust-r0b`. Rust code is identical to R2b in this commit. See the canonical
wheel/build/installation logs in `../2026-09-rust-r2-vision-stats/`; no duplicate
wheel is stored here. Mac miniM4 16GB, macOS26.5.2 ARM64, CPython3.13.12. No gameplay
timing or capacity measurement; no renderer, Agent or Hub; Chrome left open.

The small raw JSON is also the complete compact evidence: it contains all four
lists and three guards. Full regression log and all evidence have checksums.

```sh
cd experiments/2026-09-rust-r0b-skill-order
shasum -a 256 -c artifacts/SHA256SUMS
```
