# Analysis — R3k4 encoded read-segment facts

## 1. Observation
R3k3 still cloned faction public trees and Unit panel trees into every query response, then traversed them again during final JSON encoding. The identical eight-query workload remained materially more expensive than one query despite a shared gameplay fact build.

## 2. Competing hypotheses
H1: repeated common tree cloning/encoding is a large batch cost. H2: gameplay fact computation alone dominates, so shared encoded responses offer little benefit. Full payload byte emission is a separate unavoidable cost under the current interface.

## 3. Instrumentation
API15 adds public_encodes/panel_encodes and shared_public_results/shared_panel_results. Counts refer to complete public objects/panels, not individual keys; response reference counts include the first. Existing gameplay/scan metrics, Agent outputs and complete state hashes are compared. No allocator/timing-phase instrumentation was added.

## 4. Evidence
For5000Units, eight public queries build/encode one faction object and100 distinct panels, referenced8/800 times. Original work counters and full Agent responses match. Public median88.366→23.552ms; single action27.639→21.531ms. A public batch with6211 visible tiles falls51.357→14.373ms. Small local vision improves in absolute microseconds, a limited effect. See all15 rows and every sample in results.

## 5. Root cause
Fact sharing stopped before response construction/encoding. Immutable encoded field ownership lets responses share those computed values without deep clones or repeated field-value encoding. Per-request permissions are captured separately and final output remains complete.

## 6. Causal chain
Same world/facts -> once-per-segment field encoding -> immutable shared references -> same ordered Agent payload -> lower batch processing/encoding time. Writes end the shared context and old results own their earlier facts.

## 7. Rejected explanations
Fewer fields, weaker Fog/permissions, fewer gameplay checks and reduced load are contradicted by full outputs, states, original counters and differential tests. No parallel workers were added. Five samples do not rule out noise quantitatively or establish statistical significance.

## 8. Limits
One machine, stationary synthetic scenes, MP0, 1/8 immediate requests, five samples. No world tick/render/decode/network/queue/LLM. Raw diagnostic wrapper changes by four fields while Agent response stays equal. No memory peak or allocation count measured. Final6MB byte copying and Python decoding remain. 23.552ms is not whole-frame P99 or capacity acceptance.

## 9. Evidence
README.md, manifest.yaml, before/after raw.json.xz and compact.json, comparison.json, full regression and replay logs. Canonical input worlds/trace remain in their original archives with checksums.
