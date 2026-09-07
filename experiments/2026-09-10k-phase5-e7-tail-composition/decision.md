# Decision — Phase 5 E7 Tail Composition Attribution

**Status:** PENDING FORMAL THREE-REPEAT ATTRIBUTION

Retained production remains:

```text
e7ba18b31870577110b591104ef8fa7b4713e43c
```

Choose `STABLE_TAIL_CONTRIBUTORS_FOUND` only if all source/workload guards pass and at least one controlled section:

```text
appears in the positive top-3 tail uplift list in >= 2 of 3 repeats
median self-time tail uplift >= 0.15 ms
```

The highest such stable median uplift becomes `next_causal_target`.

Otherwise choose:

```text
NO_ACTIONABLE_STABLE_TAIL_CONTRIBUTOR
```

If source/workload/sample guards fail, choose:

```text
INVALID_GUARDS
```

This experiment changes no retained production code. It cannot authorize a production KEEP or Performance Frontier update. The 33.33 ms p99 result is diagnostic only; any later optimization must receive its own controlled validation.
