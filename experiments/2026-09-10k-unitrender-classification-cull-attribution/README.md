# Phase 5 10K UnitRender E — Cull + Animation Classification Attribution

**Status:** CLOSED — attribution complete  
**Formal decision:** `SPECIALIZED_ANIMATION_DISPLACEMENT_API_CANDIDATE_JUSTIFIED`  
**Cull:** `NOT_CLOSED` — separate follow-up required  
**STAR production:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a` unchanged

## Result

Formal run:

```text
run_id      20260907-032059
ZIP SHA256  05e431a613f5237efa6a6da61541f82636ea28e0cc67aaeee20f2355c1a2863b
regression  14 passed in 0.42s
guards      PASS
```

### Animation classification

```text
                         0% moving     50% moving    100% moving
classification ms/frame   3.004          4.242          4.953
helper est ms/frame       3.039          4.321          5.206
generic est ms/frame      1.650          2.655          3.325
direct redundant est      1.375          1.037          0.379
```

0%→100% classification growth is `+1.949 ms/frame`.

The source-level semantic round trip is confirmed as a material candidate:

```text
get_unit_render_position(entity)
  -> HexPosition
  -> AttackAnimation
  -> MovementAnimation
  -> static hex_to_pixel or movement interpolation
renderer
  -> HexPosition again
  -> committed hex_to_pixel again
  -> displacement compare
```

The preregistered specialized-API gates all pass.

### Cull

```text
candidates/frame        8920.0 -> 8930.4   (+0.12%)
cull ms/frame           1.715  -> 2.513    (+0.798 ms)
us/candidate            0.192  -> 0.281    (+46.3%)
volume closure                            0.25%
```

Therefore candidate volume does **not** explain cull growth. Cull remains a separate open attribution problem and is explicitly excluded from the animation candidate.

## Selected candidate boundary

The next candidate is one **window-only active-animation render-position API**:

```text
attack active   -> attack world-pixel position
movement active -> interpolated movement world-pixel position
no active animation -> None
```

The renderer retains its current epsilon comparison against committed HexPosition. This preserves attack precedence, movement interpolation, zero-displacement boundaries, and static grouping.

No animation algorithm, movement state, cull/Fog behavior, draw deduplication, or RenderEngine submission change is authorized by this result.

## Diagnostic note

This instrumented run's analyzer printed `controlled avg/p99 = 0` because it did not resolve the current controlled-work field shape. Aggregate frame timing was preregistered diagnostic-only, so the local attribution decision remains valid. Production A/B tooling must correct that extraction before closeout.

## Next

```text
E1: implement active-animation-only API
    -> targeted semantic regression
    -> uninstrumented same-session A/B

E2: preserve cull per-candidate growth as a separate NOT_CLOSED signal
```

See `analysis.md`, `decision.md`, and `result.yaml` for the full evidence trail.
