# <Experiment / Investigation Title>

**Status:** DRAFT | REPRODUCED | VALIDATED | CLOSED  
**STAR repository:** `star-nexus/star`  
**Problem commit:** `<EXACT_SHA>`  
**Fix commit:** `<EXACT_SHA or N/A>`  
**Validated commit:** `<EXACT_SHA>`  
**Validated tag:** `<TAG or N/A>`

## 1. Problem

Describe the externally observable problem in one concise paragraph.

## 2. Why it matters

State the user/runtime/scalability consequence. Avoid implementation speculation here.

## 3. Source checkout

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout <PROBLEM_COMMIT_SHA>
uv sync
```

## 4. Environment

Record required OS/runtime/tooling constraints and relevant environment variables.

```text
Machine:
OS:
Python:
Display mode:
Scenario:
```

## 5. Reproduce the problem

### Terminal A — start STAR

```bash
<complete command>
```

### Terminal B — run workload

```bash
<complete command>
```

## 6. Expected problem signature

A successful reproduction should show:

```text
<metric/event 1>
<metric/event 2>
<metric/event 3>
```

Do not use vague phrases such as "it gets slower." Give enough evidence to decide whether reproduction succeeded.

## 7. Validate the fix

```bash
git checkout <FIX_OR_VALIDATED_SHA>
```

Repeat the comparable workload above.

Expected fixed signature:

```text
<metric/event 1>
<metric/event 2>
<metric/event 3>
```

## 8. Formal artifacts

```text
results/<artifact>
results/<artifact>
```

## 9. Result summary

| Metric | Before | After | Change |
|---|---:|---:|---:|
| <metric> | | | |

## 10. Related records

- [`manifest.yaml`](manifest.yaml)
- [`analysis.md`](analysis.md)
- [`decision.md`](decision.md)
- Related STAR tag / checkpoint / issue / PR if applicable
