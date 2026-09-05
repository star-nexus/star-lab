# Artifact integrity — pending raw upload

Do not create an empty `SHA256SUMS` file.

After the canonical raw JSON artifacts are uploaded under `../results/`, generate experiment-relative checksums from the experiment root:

```bash
shasum -a 256 results/*.json > artifacts/SHA256SUMS
shasum -a 256 -c artifacts/SHA256SUMS
```

Promote the case from `DRAFT` only after all listed artifacts verify `OK` and the manifest is updated with the final raw paths/checksums.
