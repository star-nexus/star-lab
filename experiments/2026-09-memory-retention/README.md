# Scale Runtime Memory Retention — Visibility History

**Status:** CLOSED — pre-fix formal evidence complete; final post-fix PASS transcript backfill pending  
**STAR repository:** `star-nexus/star`  
**Problem/reproduction commit:** `c16aed62975f48a80b85db0f594789372cf2a782`  
**Fix commit:** `cc47acb661500787395b2b9b241256edadfed1d4`  
**Later milestone tag:** `scale-v1-cull-vision-closed`

## 1. Problem

After the Vision geometry cache had already been bounded, a repeated 600-second realtime soak still showed growing RSS and tracked Python objects even though safe-point full generation-2 collections repeatedly reported `collected=0`, the Vision cache stayed capped, and ECS entity/component counts stayed flat.

The useful question became:

> What reachable application state is intentionally retaining historical objects?

## 2. Canonical pre-fix evidence

Formal completed soak:

- [`results/realtime-gc-soak-v2-600s.json`](results/realtime-gc-soak-v2-600s.json)
- SHA256: `84e67049916b9fc49f0c20aa5b07c864ebd283a2780fdecda0b47b517e72a35d`

It completed **40/40 cycles (600 s)** and reported:

```text
baseline RSS                    328.359 MB
final post-collect RSS          380.312 MB
RSS growth                      +51.953 MB
baseline tracked objects        200,104
final tracked objects           350,054
tracked-object growth           +149,950
total safe-GC collected         0
entity growth                   0
component-instance growth       0
Vision geometry-cache size      4096 (bounded)
```

An earlier partial but diagnostically useful soak is retained separately:

- [`results/intermediate/realtime-gc-soak-600s-incomplete.json`](results/intermediate/realtime-gc-soak-600s-incomplete.json)

It executed eight valid cycles before terminating as `soak_incomplete`; it is investigation evidence, **not** formal validation evidence.

## 3. Root-cause investigation

Inspection found:

```text
VisibilityTracker.visibility_history
VISIBILITY_HISTORY_LIMIT = 100
```

At 5000 units this permits as many as:

```text
5000 × 100 = 500,000
```

reachable historical transition records.

Because those objects remained reachable by application state, additional GC was the wrong remedy. Current visibility semantics already lived in current-state structures; the full per-unit transition trajectory was telemetry.

## 4. Reproduce the pre-fix retention

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout c16aed62975f48a80b85db0f594789372cf2a782
uv sync
```

Run the 5K repeated realtime soak with `realtime_defer`, Fog ON, density 1.0, staggered movement, 15-second cycles, and a 600-second horizon.

Expected signature: post-safe-GC tracked objects and RSS keep climbing while safe Gen2 collections reclaim zero and ECS/major cache cardinalities stay bounded.

## 5. Fix

```bash
git checkout cc47acb661500787395b2b9b241256edadfed1d4
```

The scale/window visibility-history retention becomes:

```text
VISIBILITY_HISTORY_LIMIT = 1
```

Canonical/headless behavior is unchanged.

> Runtime state is not historical telemetry.

## 6. Final post-fix validation — backfill pending

The original final PASS was recorded as terminal output rather than a JSON artifact. Its historical validated summary indicates:

```text
visibility_history_records         5000
visibility_history_max_per_unit    1
Vision cache                        4096
ECS entities/components             stable
safe full GC collected              0
late tracked-object values          plateau near 209.7k
RSS                                 no monotonic growth
```

STAR Lab intentionally does **not** promote this summary to raw-evidence status. When the original terminal transcript is recovered, archive it as a text artifact (or faithful transcript), add its SHA256, and update the manifest from `pending_transcript_backfill` to verified post-fix evidence.

## 7. Integrity

```bash
shasum -a 256 -c artifacts/SHA256SUMS
```

The current checksum set covers the complete pre-fix formal soak and the retained intermediate partial soak.
