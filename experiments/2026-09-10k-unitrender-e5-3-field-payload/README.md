# Phase 5 10K UnitRender E5-3 — Cull Field-Payload Attribution

**Status:** RUNNING — preregistered attribution  
**Experimental base:** `682fdb3a4c64002b402eb74bdda2331ca7123ab4` (E5-1 slotted record; not production-retained)  
**Production remains:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

## Trigger

The sequence so far is:

```text
E5   record-field first-touch dominant (~0.498 ms @100%)
E5-1 slots=True causally beneficial but insufficient (0.113 ms @100%)
E5-2 stable record identity not material (0.044 ms additional @100%)
```

This weakens both per-instance attribute-dictionary layout and record-container replacement as explanations for the majority of the remaining first-touch signal.

Pure movement still refreshes the field payload consumed by Cull. In particular, `_record_for_hex()` creates new `world_x/world_y` Python float values on every movement commit. Cull reads fields in this order:

```text
world_x/world_y  -> exact bounds
faction          -> Fog faction branch
col/row          -> Fog membership tile
```

E5-3 decomposes these payload groups before considering a wider spatial-index representation change.

## Measurement design

No runtime source is modified. The runner creates a detached worktree at the exact slotted experimental base and copies in only the measurement probe.

Most frames are baseline. Every sixth Cull call rotates through four cumulative read-only prewarm modes:

```text
lookup   = bucket traversal + by_entity.get only
world    = lookup + world_x/world_y
faction  = world + faction
hex      = faction + col/row
```

Prewarm time is excluded. The exact runtime `_get_visible_units()` is the timed core after prewarm.

Profiler horizon remains 8 seconds and `sample_after=10s`, preserving the 2-second aging margin discovered during E5 measurement correction. Sampling cadence remains 1/6 frames.

## Derived stage contributions

At each density:

```text
world-coordinate payload = lookup_core - world_core
faction payload          = world_core - faction_core
hex col/row payload      = faction_core - hex_core
full field payload       = lookup_core - hex_core
```

## Frozen decisions

Measurement guards:

```text
all driver guards PASS
runtime/source guard PASS
>= 8 samples for baseline and every mode
>= 7.5s profile target/coverage
candidate count 0%->100% within ±2%
```

The slotted baseline Cull growth must reproduce:

```text
baseline 100% - baseline 0% >= 0.40 ms
```

The cumulative field-payload effect at 100% must be material:

```text
lookup_core - hex_core >= 0.20 ms
and >= 10% of lookup_core
```

A field group is dominant only if at 100% it contributes:

```text
>= 0.10 ms
and >= 35% of the full field-payload effect
```

Possible positive decisions:

```text
WORLD_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT
FACTION_PAYLOAD_FIRST_TOUCH_DOMINANT
HEX_COORD_PAYLOAD_FIRST_TOUCH_DOMINANT
MIXED_CULL_FIELD_PAYLOAD
```

Negative/inconclusive decisions are also preregistered. None of these is a production KEEP decision.

## Candidate boundary after attribution

If `world_x/world_y` dominates, the next candidate should first explore reuse/compact storage of derived per-hex render geometry rather than immediately introducing SoA. The key question would be whether movement can reference long-lived derived geometry instead of allocating fresh Python float payloads every commit.

If no payload group dominates, only then should a broader compact Cull read representation be considered.

## Methodology

> **先把“record fields”拆成真正被 Cull 消费的 payload，再决定是否值得重构 spatial representation。**
