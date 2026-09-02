# Analysis — <Experiment Title>

## 1. Observation

Record measured facts only. Do not state the suspected cause here.

```text
<fact>
<fact>
```

## 2. Competing hypotheses

### H1 — <hypothesis>

Why it is plausible:

### H2 — <hypothesis>

Why it is plausible:

## 3. Instrumentation / diagnostic changes

Record what was measured or added specifically to distinguish the hypotheses.

```text
<metric / trace / counter>
```

When diagnostic code changes the source state, record the exact instrumentation commit in `manifest.yaml`.

## 4. Evidence

### Evidence for / against H1

```text
<measurement>
```

Interpretation:

### Evidence for / against H2

```text
<measurement>
```

Interpretation:

## 5. Root cause

State the root cause only after the evidence above establishes it.

> <root cause>

## 6. Causal chain

```text
<input / condition>
  -> intermediate mechanism
  -> subsystem cost / state
  -> observed system symptom
```

## 7. Rejected explanations

Preserve important explanations that were tested and rejected, especially when future engineers are likely to revisit them.

- <rejected explanation> — rejected because <evidence>.

## 8. Limits of the evidence

State what this experiment does **not** prove.

Examples:

- tested only one machine;
- tested only one map scale;
- aggregate FPS difference is confounded;
- capacity is sufficient for 5K but not yet validated at 20K.

## 9. Raw evidence

- [`results/<file>`](results/<file>)
- [`manifest.yaml`](manifest.yaml)
