# Artifact integrity — verified

Canonical formal JSON artifacts are stored under `../results/` and covered by [`SHA256SUMS`](SHA256SUMS).

Verify from the experiment root:

```bash
shasum -a 256 -c artifacts/SHA256SUMS
```

All 12 listed artifacts were verified `OK` before this case was promoted to CLOSED.

Checksum paths are experiment-relative, as required by [`../../../PROTOCOL.md`](../../../PROTOCOL.md).
