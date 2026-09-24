# Analysis — R3k3 owned JSON assembly

## 1. Observation
R3k2 retained expensive large-payload queries after scan pruning. This archive measures API14 before/after on identical archived input worlds via both handler and authenticated batch paths. See comparison.json for all 12 cases and all raw samples.

## 2. Competing hypotheses
H1: repeated serialize-to-Value of already owned JSON arrays is material. H2: only gameplay predicates or scan costs dominate, so changing assembly would show no useful effect. Neither hypothesis implies a whole-frame capacity result.

## 3. Instrumentation / diagnostic changes
No new production counters. Existing census/faction/panel/enemy/tile/scan/attack counts are equal across versions. Exact initial/final states and full responses/lengths are checked. Source comparison identifies five ownership-transfer boundaries: public enemy/terrain fields, reachable, request units, batch results/segments and diagnostic report results. The locked serde_json macro expands a general expression to to_value(&$other); its Value serializer recursively visits objects/arrays/strings. This is source-level evidence of eliminated copies, not an allocator measurement.

## 4. Evidence
All work counters, decoded responses and final states remain equal. At 5000Units, public single query median 52.232→30.815ms and eight-query batch 173.365→95.241ms; full visible terrain eight-query batch 100.544→54.464ms. Local small responses also improve but absolute savings are small. Public and diagnostic paths both improve; there is no diagnostic-only fast path.

## 5. Root cause
Owned response values were recursively rebuilt during envelope assembly. Moving the already owned arrays removes that redundant work; gameplay and scan work remain the same. No payload truncation or changed visibility explains the measured difference.

## 6. Causal chain
Identical gameplay facts -> fewer recursive JSON tree rebuilds -> unchanged response contents/length -> lower measured native query and batch duration.

## 7. Rejected explanations
Different world state, fewer reported facts, weaker permission checks and changed scan counts are contradicted by exact guards and regression coverage. There is no new parallel code. OS/cache noise is not ruled out quantitatively by five samples; the report does not assert significance or universal speedup.

## 8. Limits of the evidence
One M4 machine; synthetic stationary scenes; MP0; 1/8 immediately supplied requests; five samples after one warmup; import/reset outside timing. No world loop, Python decode, render, Hub or request queue. Per-Agent shared-fact copying, final encoding and complete multi-MB output remain; eight large requests still take about95ms. No CPU/memory allocation volume was measured and no capacity/default-backend gate is closed.

## 9. Raw evidence
See results/before/raw.json.xz, results/after/raw.json.xz, results/comparison.json and manifest.yaml. Canonical initial worlds and replay trace are referenced once by SHA256.
