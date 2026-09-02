# Scale Runtime Memory Retention — Visibility History

**Status:** CLOSED (historical archive; original soak JSON backfill pending)  
**STAR repository:** `star-nexus/star`  
**Problem/reproduction commit:** `c16aed62975f48a80b85db0f594789372cf2a782`  
**Fix commit:** `cc47acb661500787395b2b9b241256edadfed1d4`  
**Later validated scale milestone:** `a24482d438157aa23b371b6e34d49b1c04fec7f7`

## 1. Problem

After the Vision geometry cache had already been bounded, long repeated realtime soak runs still showed growing RSS and tracked Python objects even though full safe-point generation-2 collections repeatedly reported `collected=0`, the Vision cache stayed capped, and ECS entity/component counts stayed flat.

The important diagnostic question was therefore not "why is GC failing?" but:

> What live application state is still intentionally retaining historical objects?

## 2. Historical pre-fix signature

A long soak before the visibility-history fix showed approximately:

```text
baseline RSS              328.359 MB
later RSS                 380.312 MB
post-baseline growth      +51.953 MB
tracked-object growth     +149,950
safe full GC collected    0 repeatedly
Vision geometry cache     fixed at 4096
ECS entities/components   stable
```

Inspection then identified scale statistics visibility history as a bounded-but-large live retention structure:

```text
VisibilityTracker.visibility_history
VISIBILITY_HISTORY_LIMIT = 100
5000 units × up to 100 records = up to 500,000 retained transition dicts
```

## 3. Reproduce the old retention policy

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout c16aed62975f48a80b85db0f594789372cf2a782
uv sync
```

Start the formal 5000-unit realtime ENV with the scale harness and `realtime_defer`, then run the repeated GC soak driver. The historical command family was:

```bash
uv run tools/scale_gc_soak.py \
  --socket /tmp/star-scale.sock \
  --realtime-seconds 120 \
  --cycle-realtime-seconds 15 \
  --priming-realtime-seconds 15 \
  --sustained-duration 20 \
  --density 1.0 \
  --seed 42 \
  --target-radius 12 \
  --phase staggered \
  --require-fog on \
  --output results/gc-soak/realtime-gc-soak.json
```

For stronger reproduction, extend `--realtime-seconds` toward the historical long-soak horizon.

Expected pre-fix signature: safe full collections reclaim little or nothing while retained visibility-history records and tracked objects continue to rise with historical activity.

## 4. Validate the fix

```bash
git checkout cc47acb661500787395b2b9b241256edadfed1d4
```

The scale/window `VISIBILITY_HISTORY_LIMIT` becomes `1`; canonical/headless behavior is unchanged.

The later 120-second v3 validation produced:

```text
primed RSS                         368.812 MB
final RSS                          337.438 MB
visibility_history_records         exactly 5000
visibility_history_max_per_unit    exactly 1
unit_observation_history_records   10000
Vision cache                        4096
ECS entities/components             stable
safe full GC collected              0
```

Tracked objects warmed to roughly 209.7k and then plateaued; late-window slope was effectively zero rather than leak-shaped.

## 5. Resolution

The runtime keeps only the latest scale-mode visibility transition per unit. Full visibility trajectories are historical telemetry and belong in logging/evaluation/archive planes, not live realtime ECS state.

> Runtime state is not historical telemetry.

## 6. Archive note

This investigation predates `star-lab`. The exact source commits and validated numeric summaries are preserved here, but the original long-soak raw JSON files were not available in the current archive workspace. They should be added later if recovered; this omission is explicit rather than silently reconstructing fake raw evidence.
