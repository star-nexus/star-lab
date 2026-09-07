# Preregistered Decision

E5-4 will compare exact production behavior against an exact-production runtime with a startup-only monkeypatch that reuses long-lived per-hex `(world_x, world_y, bucket)` payload objects while still constructing fresh `UnitSpatialRecord` objects.

Positive attribution requires:

```text
50% Cull saving >= 0.08 ms/frame
100% Cull saving >= 0.15 ms/frame
UnitRenderSystem avg improves at 100%
workload rates remain within ±2%
controlled avg does not regress >2%
```

If satisfied:

```text
DERIVED_GEOMETRY_REUSE_CANDIDATE_JUSTIFIED
```

Otherwise:

```text
DERIVED_GEOMETRY_REUSE_NOT_MATERIAL
```

A positive result is not a KEEP; it only authorizes a production-source candidate and separate closeout A/B.
