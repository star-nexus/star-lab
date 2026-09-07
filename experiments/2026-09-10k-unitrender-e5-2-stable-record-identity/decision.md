# Decision — UnitRender E5-2

## Decision

```text
FRESH_RECORD_REPLACEMENT_NOT_MATERIAL
```

The stable-record-identity treatment did not meet the preregistered additional Cull-saving floors at either movement density:

```text
50%  required >= 0.08 ms   observed 0.007 ms
100% required >= 0.15 ms   observed 0.044 ms
```

All workload/semantic guards passed, so this is a valid negative result rather than an invalid measurement.

## Consequences

- Do not implement stable identity / in-place mutation as a production candidate.
- Do not combine E5-1 slots with stable identity and rerun production A/B; the incremental mechanism is too small.
- Keep production at `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`.
- Close the fresh-record-container identity hypothesis.
- Continue with field-payload first-touch attribution before considering SoA or broader spatial-index redesign.

## Methodology lesson

A strong locality attribution does not justify every cache-locality-flavored treatment. E5-2 directly tested object identity and found it insufficient; the remaining investigation must move one layer deeper rather than widening the implementation.
