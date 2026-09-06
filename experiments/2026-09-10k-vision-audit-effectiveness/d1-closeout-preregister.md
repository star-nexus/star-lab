# Vision D1 closeout preregistration

**Candidate:** indexed window periodic-audit boundary  
**Control:** `6896cdc0f3103a1de5fc6f3c5cb04913d146bf5b`  
**Treatment:** `17ced8d2ba1725b4d0c1a5458e6c61c06c1e206a`

Same-session ABBA:

```text
A50 -> B50 -> B100 -> A100
```

D1 changes only the indexed window periodic audit boundary. Bootstrap force-all reconciliation and non-indexed-world safety-audit semantics remain unchanged.

## Primary causal gates

Control must demonstrate the expected periodic full scan:

```text
vision_audit_scanned.max >= 9000
vision_audit_scan.max_inclusive_ms >= 3.0 ms
```

Treatment must eliminate that pulse:

```text
vision_audit_scanned.max == 0
vision_audit_scan.max_inclusive_ms <= 0.25 ms
```

## Workload / semantic preservation

```text
position commits/s              +/-2%
Vision dirty/s                  +/-2%
Vision scanned/s                +/-2%
geometry calls/s                +/-2%
faction visible add/remove/s    +/-5%
fog delta/s                     +/-5%
geometry hit-rate drop          <=0.5 pp
geometry evictions              0
controlled avg regression       <=2%
Vision avg regression           <=2%
```

`controlled_work_frame_ms.p99` is recorded as an important diagnostic but is not the sole KEEP/REVERT gate. A later dedicated three-run 100%-moving frontier confirmation remains responsible for the formal 30Hz capacity claim.

Decision values:

```text
CAUSALLY_CONFIRMED_KEEP
REVERT_OR_INVESTIGATE
```
