# Raw results — canonical formal evidence

This directory contains the canonical raw JSON artifacts for the MiniMap unit-layer tail investigation and 5K Core 60Hz stress boundary.

The formal set is defined in [`../manifest.yaml`](../manifest.yaml) and includes:

```text
25% crossing-cost correlation diagnostic
25% MiniMap dynamic-unit-layer ON/OFF A/B
50% Core 60Hz three fresh-process runs
```

Do not duplicate these artifacts into another case directory. Other STAR Lab investigations should cross-reference these canonical paths if they need the same evidence.

Every formal JSON in this directory is covered by [`../artifacts/SHA256SUMS`](../artifacts/SHA256SUMS).

Verify from the experiment root:

```bash
shasum -a 256 -c artifacts/SHA256SUMS
```

All 12 formal artifacts were verified `OK` before the case was marked CLOSED.
