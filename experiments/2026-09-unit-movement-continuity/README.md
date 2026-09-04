# Unit movement continuity misattributed to Fog reveal

**Status:** CLOSED — investigation complete; production integration pending  
**Scope:** interactive window unit movement on the 15×15 `river_split` scenario

## Conclusion

A visible micro-stutter was initially reported while a moving unit crossed the Fog boundary. Controlled observation showed the same boundary stutter with Fog enabled and disabled, rejecting Fog/Vision work as the cause of the regular movement discontinuity.

Two independent STAR-side temporal/presentation defects were identified and fixed on `perf/unit-fog-reveal-tail`:

1. movement segment progress discarded overshoot and could miss an exact 60 Hz boundary because `0.9999999999999999 < 1.0`;
2. the window unit renderer ignored small animation displacements around the committed hex centre (legacy 5 px rich-path and 1 px batch-path dead zones).

The fixes materially improved visible continuity. Final human validation judged the remaining small, non-uniform judder acceptable. The remaining occasional large hitches were separately attributed to the already-closed macOS SDL event-pump platform-tail case, not to Fog, Vision, movement integration, or UnitRender cost.

## Exact source states

```text
problem / production baseline
57bd8eac0fa8352cc39876092c9068c9e944e8ac

fix stage 1 — preserve movement time across segment boundaries
acc77f8928933dd68f4dc57690d8ae686b06afe1
fix: preserve movement animation continuity

fix stage 2 / accepted experiment HEAD — remove animation render dead zones
cf779e642c9620ed71bbb0ed713f0f2aa7c6c33d
fix: remove unit animation render dead zones
```

Historical working branch:

```text
perf/unit-fog-reveal-tail
```

The branch name is context only; the SHAs above are the source identities.

## Reproduction of the original symptom

Checkout the problem baseline:

```bash
git checkout 57bd8eac0fa8352cc39876092c9068c9e944e8ac
uv run rotk_env/main.py \
  --skip-start \
  --no-hub \
  --mode real_time \
  --players human_vs_two_ai \
  --scenario default \
  --seed 42 \
  --profile
```

Use a human-controlled unit and issue paths of several adjacent hexes. Observe the token at each committed hex boundary.

Controlled visual A/B:

1. Fog ON: repeatedly move through/along the Fog boundary.
2. Fog OFF: toggle Fog off, allow the input-toggle frame to settle, then repeat comparable multi-hex movement.

Expected problem signature:

```text
Fog ON  -> small boundary stutter visible
Fog OFF -> same small boundary stutter visible
```

That A/B rejects Fog reveal as the cause of the regular movement discontinuity.

## Fixed behavior

Checkout the accepted experiment HEAD:

```bash
git checkout cf779e642c9620ed71bbb0ed713f0f2aa7c6c33d
```

Run the same capped 60 Hz workload. Expected behavior:

- no systematic lost-time pause at each segment boundary;
- no renderer freeze/jump caused by the old 5 px / 1 px animation dead zones;
- movement is materially more continuous in both Fog ON and Fog OFF;
- small residual visual judder may remain from 60 Hz / integer-pixel presentation and was accepted as non-blocking;
- isolated large hitches may still occur when `input_event_pump` stalls on macOS; classify those under `2026-09-macos-sdl-event-pump-stall` rather than reopening this case.

## Final validation snapshot

Final capped 60 Hz validation remained healthy outside isolated platform tails. Representative steady windows were approximately:

```text
FOG OFF
frame p99            ~17.65–17.84 ms
AnimationSystem      ~0.01–0.02 ms
UnitRenderSystem     ~0.16–0.22 ms

FOG ON
frame p99            ~17.60–17.81 ms
AnimationSystem      ~0.01–0.02 ms
UnitRenderSystem     ~0.08–0.13 ms
fog_surface_patch    ~0.00–0.02 ms
```

The final Fog-ON run also captured platform-tail frames unrelated to movement/Fog work, including:

```text
frame 2739: frame_ms=76.53, input_event_pump=68.98 ms,
            vision_fog_delta_tiles=0, vision_units_changed=0
frame 2828: frame_ms=35.18, input_event_pump=28.50 ms,
            input_events=0, vision_fog_delta_tiles=0
```

The first was followed by a macOS `IMKCFRunLoopWakeUpReliable` message. These reinforce the existing macOS/SDL case and do not invalidate the movement fix.

## Regression coverage added in STAR

Stage 1 added `rotk_env/tests/test_movement_animation_continuity.py` covering:

- exact 60 Hz × 2 tiles/s segment completion on tick 30;
- overshoot preservation across a segment boundary;
- consuming a large delta across multiple segments without losing movement time.

Stage 2 extended `rotk_env/tests/test_unit_render_batch_animation.py` so a real sub-pixel animation displacement is not collapsed back to the committed static position.

No CI status or local pytest transcript for `cf779e6` is archived with this case. The test source exists at the exact SHA, but production integration must rerun the normal regression gate rather than treating this archive as a release-test record.

## Evidence state

The final validation logs were supplied during the investigation but could not be transferred byte-for-byte into STAR Lab through the available repository connector. Their locally computed identities were:

```text
FOG_ON_2.TXT
size: 69 KiB (filesystem display)
SHA256: 3ae3401029f4f5a176dc085d5ebd9385e0f7593ef30f255926cc101cc7b40b35

FOG_OFF_2.TXT
size: 67 KiB (filesystem display)
SHA256: eb3ba65564d2c1c5894b50bdf0685269ec808a55a63b19961a5eff75d869977f
```

This package therefore archives exact source provenance, controlled observations, validated profiler excerpts, fix reasoning, and artifact identities, but does **not** claim local raw-evidence completeness. No empty `SHA256SUMS` is created.

See `manifest.yaml`, `analysis.md`, and `decision.md` for the causal chain and closure policy.
