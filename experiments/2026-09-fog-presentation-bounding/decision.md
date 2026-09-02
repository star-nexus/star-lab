# Decision — <Experiment Title>

**Status:** proposed | accepted | superseded  
**Decision date:** YYYY-MM-DD  
**Validated STAR commit:** `<EXACT_SHA>`  
**Validated STAR tag:** `<TAG or N/A>`

## 1. Decision

State the final engineering decision in one paragraph.

## 2. Decision drivers

- <measured requirement>
- <operational constraint>
- <scalability / maintainability requirement>

## 3. Measured alternatives

| Option | Relevant causal metrics | System metrics | Decision |
|---|---|---|---|
| <A> | | | |
| <B> | | | |

## 4. Why this option

Explain why the chosen option is justified by the controlled evidence rather than by intuition or one noisy aggregate metric.

## 5. Why not the alternatives

### <Alternative>

Rejected because:

### <Alternative>

Rejected because:

## 6. Headroom and scaling rationale

If the decision intentionally includes resource headroom, distinguish:

```text
measured minimum sufficient
operational/default value
future scaling trigger
```

Do not confuse an experimentally sufficient minimum with the default chosen for future workloads.

## 7. Risks / trade-offs

- <trade-off>
- <trade-off>

## 8. Revisit when

This decision MUST be revisited when any of the following occurs:

- <measurable condition>
- <architecture change>
- <new scale regime>

## 9. Provenance

- Reproduction: [`README.md`](README.md)
- Experiment identity: [`manifest.yaml`](manifest.yaml)
- Root-cause analysis: [`analysis.md`](analysis.md)
- Raw evidence: [`results/`](results/)
