# STAR Engineering Experiment & Reproducibility Protocol

**Version:** 1.1  
**Status:** Normative  
**Applies to:** STAR / StarBench performance work, scalability experiments, runtime debugging, architecture optimization, and engineering investigations.

## 1. Purpose

STAR engineering work must remain understandable and reproducible after the original engineer, machine, branch, and local files are gone.

A formal engineering conclusion is complete only when a future engineer can:

1. locate the exact source state;
2. reproduce the original problem;
3. reproduce the measurement;
4. inspect the evidence used to identify the root cause;
5. run the corrected version under comparable conditions;
6. understand why the final design was selected;
7. trace any reported number back to raw evidence;
8. verify that archived evidence is byte-identical to the recorded artifact.

> A conclusion without reproduction is a memory, not engineering evidence.

---

## 2. Repository boundary

### `star-nexus/star`

Product/runtime repository. It owns source code, benchmark behavior, public APIs, production tests, user-facing documentation, releases, working branches, checkpoints, and validated source tags.

Ordinary StarBench users should be able to use `star/main` without reading STAR Lab.

### `star-nexus/star-lab`

Engineering evidence repository. It owns reproducible problem records, raw experiment results, controlled ablations, investigations, engineering decisions, training material, and the Performance Frontier.

STAR Lab is **not** a source-code fork. Every formal experiment references `star` through exact commit SHAs and, where applicable, annotated tags.

---

## 3. Version semantics

```text
branch            = active work line
checkpoint branch = temporary debugging / A-B comparison point
annotated tag     = validated, immutable engineering milestone
star-lab          = durable evidence and decision history
```

Branches may move. Never use a branch name alone as the identity of a formal experiment.

Use checkpoints for regression comparison, `git diff`, `git bisect`, or returning to a known development baseline. They are useful working references but are not permanent historical identities.

Use annotated tags for important validated milestones. Tags are treated as immutable once published.

Example:

```bash
git tag -a scale-v1-cull-vision-closed <EXACT_SHA> \
  -m "Validated scale baseline: realtime GC, bounded memory, spatial cull and Vision cache closed"
git push origin scale-v1-cull-vision-closed
```

Do not move or silently recreate a published milestone tag.

---

## 4. Required evidence chain

Important engineering work SHOULD form this chain and MUST not skip directly from symptom to rewrite:

```text
Observation
  -> Problem reproduction
  -> Hypothesis
  -> Instrumentation
  -> Evidence
  -> Root cause
  -> Candidate fix
  -> Controlled A/B
  -> Regression check
  -> Engineering decision
  -> Validated source commit
  -> Annotated milestone tag when appropriate
  -> Archive / Performance Frontier
```

Intermediate causal metrics are required whenever they materially distinguish competing explanations.

---

## 5. What must be archived

### MUST archive

- a confirmed major performance bottleneck;
- memory leak or live-retention investigation;
- GC / allocator / scheduler latency investigation;
- architectural complexity reduction such as `O(Nresident) -> O(Ndirty)` or spatial/event-driven conversion;
- controlled ablation used to choose an engineering parameter;
- important cache-capacity decision;
- major scalability point such as 5K / 10K / 20K / 50K;
- runtime policy that changes latency behavior;
- significant negative result that changes engineering direction;
- a new Performance Frontier record;
- any important issue formally marked CLOSED.

### SHOULD archive

- representative rejected designs;
- platform-specific findings likely to recur;
- instrumentation methodology that future engineers should reuse;
- partial experiments that executed a valid workload and materially changed the investigation.

### Do not promote to formal evidence

- configuration mistakes;
- failed guards before the intended workload starts;
- uncontrolled camera/Fog/workload runs;
- disposable smoke tests;
- results whose exact source state is unknown;
- random profiler dumps that support no durable conclusion.

---

## 6. Standard experiment package

Every formal experiment uses this structure:

```text
experiments/YYYY-MM-<name>/
├── README.md
├── manifest.yaml
├── analysis.md
├── decision.md
├── results/
└── artifacts/
```

Use the files in `templates/` rather than inventing a new layout.

| File | Question it answers |
|---|---|
| `README.md` | How do I reproduce the problem and the fixed behavior? |
| `manifest.yaml` | Exactly what source, machine, scenario, workload, and artifacts define this experiment? |
| `analysis.md` | How did the evidence establish the root cause? |
| `decision.md` | What was finally chosen, what alternatives were rejected, and when should the decision be revisited? |

---

## 7. Reproduction requirements

A formal experiment MUST record:

```text
source repository
problem commit SHA
measurement commit SHA when different
fix commit SHA
validated commit SHA
validated tag when available
hardware
OS/runtime versions
scenario
seed
workload parameters
all relevant environment variables
full startup command
full experiment command
expected problem signature
expected fixed signature
raw result paths
validation guards
```

A future engineer should be able to execute:

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout <EXACT_PROBLEM_SHA>
uv sync
```

Then run the documented commands without guessing omitted arguments.

Expected signatures must be specific enough to determine whether reproduction succeeded.

---

## 8. Manifest requirements

`manifest.yaml` is the machine-readable identity of the experiment. It must use exact source SHAs and stable artifact paths.

A branch name may be recorded as historical context but never substitutes for a SHA.

If historical evidence has been recovered but the exact source SHA has not yet been proven, mark the archive explicitly as `provenance_backfill_pending`. Do not guess a commit merely to make the manifest look complete.

---

## 9. Analysis discipline

`analysis.md` MUST distinguish:

- **Observation** — measured facts only.
- **Hypothesis** — possible explanations, explicitly labeled.
- **Instrumentation** — what distinguished the hypotheses.
- **Evidence** — measurements supporting or contradicting each explanation.
- **Root cause** — state only after evidence supports it.
- **Rejected explanations** — preserve important rejected hypotheses when they prevent repeated investigation.

---

## 10. Decision discipline

`decision.md` must record more than the winning number. For a parameter decision it should state:

```text
measured minimum sufficient value
operational/default value
headroom rationale
rejected alternatives
why aggregate benchmark noise was or was not causal
conditions that require revisiting the decision
```

A source constant should never become an unexplained magic number when a controlled experiment determined it.

---

## 11. Controlled A/B and ablation standard

When several reasonable engineering choices exist, change one primary independent variable at a time whenever practical.

Keep other formal conditions fixed: source state, machine, scenario, seed, camera, Fog, movement phase, density, measurement window, and GC policy unless one of those is itself the variable under test.

Do not select the winner from aggregate FPS alone. Trace the intended causal chain, for example:

```text
cache capacity
 -> hit/miss/eviction
 -> subsystem latency
 -> frame latency
```

If aggregate metrics disagree with causal intermediate metrics, investigate confounders rather than declaring causation.

---

## 12. Raw data policy

Keep controlled evidence that supports a durable conclusion. Do not keep every local debugging run.

Before committing raw data, classify each artifact as:

```text
formal
intermediate / invalid-but-informative
disposable
```

### `ok:false` is not an automatic deletion rule

Classify the run by what actually executed:

```text
ok:false
  |
  +-- guard/config failed before valid workload
  |      -> discard
  |
  +-- accidental/debug run
  |      -> discard
  |
  +-- valid workload partially completed
         + produced useful diagnostic evidence
         -> keep under results/intermediate/ (or results/invalid/)
         -> never use as a formal conclusion
```

A partial run may be valuable investigation evidence even though it cannot validate a final result.

### One canonical location per raw artifact

Do not duplicate the same raw JSON into multiple case directories merely because it supports more than one investigation.

Use:

```text
one canonical raw artifact
       -> canonical checksum
       -> cross-case references from other manifests / analyses
```

This prevents two copies of the same evidence from silently diverging.

---

## 13. Artifact integrity (SHA256)

Every small formal raw artifact committed to Git **MUST** be covered by SHA256 integrity metadata.

Standard location:

```text
experiment/
├── results/
└── artifacts/
    └── SHA256SUMS
```

`SHA256SUMS` paths MUST be relative to the experiment root, for example:

```text
<sha256>  results/capacity-4096.json
<sha256>  results/capacity-8192.json
```

Verification MUST work from the experiment root:

```bash
cd experiments/<experiment>
shasum -a 256 -c artifacts/SHA256SUMS
```

All listed artifacts must report `OK` before the archive is considered integrity-verified.

If a case owns no local raw artifacts and only cross-references canonical evidence in another case, **do not create an empty `SHA256SUMS`**. Reference the canonical artifact path and checksum instead.

For GB-scale traces, heap dumps, video, or other external artifacts, keep the artifact outside ordinary Git and record at least:

```text
artifact name
size
storage locator
SHA256
creation/source context
```

An external artifact without a checksum is not durable evidence.

---

## 14. Large artifact policy

Ordinary Git stores small structured evidence: Markdown, YAML, JSON, CSV, compact profiler summaries, and checksums.

Do not put GB-scale traces, heap dumps, videos, trajectories, or frame captures directly into normal Git history.

Use:

```text
Git                 -> manifest + metadata + checksum
Release/LFS/storage -> large immutable artifact
```

---

## 15. Fix validation

A closed problem must demonstrate both sides:

```text
problem commit + documented workload -> problem reproduced
fix commit     + comparable workload  -> problem removed / bounded
```

Prefer direct before/after metrics and preserve all experiment guards.

A code change without controlled validation is not a closed engineering investigation.

---

## 16. Performance Frontier

`records/performance-frontier.md` records how STAR's validated scalability boundary moves over time.

A Frontier entry requires:

- valid experiment guards;
- exact source SHA;
- raw result preserved;
- artifact integrity verified;
- workload and machine documented;
- no known measurement contamination;
- experiment marked validated;
- result reproducible from STAR Lab instructions.

A frontier is not a casual benchmark leaderboard. It is a historical record of validated capability.

---

## 17. Definition of CLOSED

An important issue is CLOSED only when all applicable items are complete:

```text
problem reproduced
root cause demonstrated
fix implemented
controlled validation passed
regression tests passed
raw evidence archived or canonical evidence referenced
artifact integrity verified
reproduction documented
exact commits recorded
decision documented
milestone/tag preserved when appropriate
```

"The code has been changed" is not Definition of Done.

---

## 18. Engineering principles

### Profile first. Native second.
Do not migrate work to Rust/native code simply because Python appears slow. Establish a stable hot boundary first.

### Tight budgets expose wrong complexity.
Prefer constrained resources during diagnosis. Excess capacity can hide full scans, unbounded state, repeated work, random maintenance, and poor data structures. Remove wrong complexity before scaling hardware.

### Runtime state is not historical telemetry.
Do not retain complete historical trajectories in latency-critical runtime state merely because they may be useful for later analysis. Historical evidence belongs in logging/evaluation/archive planes.

### Expensive work may move rather than disappear.
Maintenance that is necessary but unpredictable should execute at safe points or state-change boundaries rather than randomly inside latency-critical loops.

### Do not optimize a black box.
If a section is 5.3 ms, first split and instrument the 5.3 ms. Attribute cost before redesigning it.

### Every important number must have provenance.
Every reported result should trace to:

```text
raw artifact -> SHA256 -> manifest -> exact source commit -> machine/workload
```

---

## 19. New-engineer training procedure

Before independently owning STAR runtime/performance work, a new engineer SHOULD reproduce one historical closed investigation.

Training sequence:

1. Read this protocol and one closed experiment package.
2. Check out the documented problem SHA.
3. Reproduce the expected failure signature.
4. Explain the hypotheses and causal evidence without using the final decision as a shortcut.
5. Check out the fix/validated SHA.
6. Re-run the comparable workload and reproduce the fixed signature.
7. Create a temporary training experiment package using the standard templates.
8. Verify artifact checksums.
9. Have an existing engineer review provenance, measurement controls, interpretation, and archive quality.

Training is complete when the engineer can independently perform:

```text
checkout -> reproduce -> measure -> interpret -> validate -> archive -> verify
```

---

## 20. Formal archive review checklist

### Source
- [ ] exact problem SHA recorded
- [ ] exact fix/validated SHA recorded
- [ ] source repository recorded
- [ ] milestone tag recorded or absence explained

### Reproduction
- [ ] environment can be rebuilt
- [ ] startup command complete
- [ ] workload command complete
- [ ] seed fixed or explicitly variable
- [ ] expected failure signature explicit
- [ ] expected fixed signature explicit

### Measurement
- [ ] profiler window valid
- [ ] experiment guards pass for formal results
- [ ] no uncontrolled camera/Fog/workload change
- [ ] primary metrics recorded
- [ ] causal intermediate metrics recorded when needed

### Evidence
- [ ] formal raw results preserved or canonical evidence referenced
- [ ] intermediate/invalid runs separated
- [ ] disposable invalid runs removed
- [ ] observations and hypotheses separated
- [ ] root cause supported by evidence
- [ ] useful rejected hypotheses preserved

### Integrity
- [ ] every local formal raw artifact is listed in `artifacts/SHA256SUMS`
- [ ] checksum paths are experiment-relative
- [ ] `shasum -a 256 -c artifacts/SHA256SUMS` reports `OK`
- [ ] external large artifacts include checksum + size + locator
- [ ] no empty checksum file exists for a cross-reference-only case

### Fix
- [ ] before/after comparable
- [ ] regression tests pass
- [ ] fix SHA recorded

### Archive
- [ ] `decision.md` complete
- [ ] large artifacts kept out of normal Git history
- [ ] Performance Frontier updated when applicable
- [ ] annotated milestone tag created when appropriate
