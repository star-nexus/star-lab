# Analysis — Dynamic World Scaling Methodology

## 1. Observation

The recovered archive contains three generations of controlled 5000-unit Dynamic World results rather than one isolated benchmark run.

The raw artifacts preserve density curves, synchronized bursts, fixed-camera/Fog guards, measurement epochs, and subsystem timing breakdowns. Provenance recovery now binds each archive cohort to the exact STAR HEAD recorded at its contemporaneous run handoff.

## 2. Provenance recovery

The recovered source anchors are:

```text
V1    0f0d0a2a173457de099af714b2ee5b86600f91b2
V2    571ea207db52478a56f0710c6cad7e45de3bf0e3
V2.1  916d88dcd3d796fe49a0cadd64be40b68c331b5c
```

The provenance chain is stronger than a timestamp/file-name inference:

```text
contemporaneous run-handoff explicitly states current pushed HEAD
        +
Git commit content matches the cohort's implementation/diagnostic generation
        +
raw artifact schema and guards match that generation
```

The raw JSON files themselves do not contain Git SHAs, so this distinction remains explicit in the archive.

### V1 source fingerprint

`0f0d0a2...` documents the first formal Density Curve protocol with:

- warmup before measurement;
- common 5000-plan pool;
- deterministic nested density prefixes;
- fixed seed/Fog/camera/zoom guards;
- deferred execution measurement epoch;
- explicit `results/dynamic-world-v1/...` output examples.

### V2 source fingerprint

`571ea207...` contains the explicit tail/Fog diagnostic contract after incremental Fog presentation work, including:

```text
fog_render_mode = incremental_patch
fog_delta_tiles
fog_patch_tiles
fog_surface_patch
epoch_worst_slow_frame_ms
```

These fields mark the V2 generation that reduced MapRender's dominant full-surface rebuild cost.

### V2.1 source fingerprint

`916d88dc...` is `profile: attribute rare UnitRender tails`. It keeps the verified renderer implementation as a base and adds low-overhead attribution for:

```text
Python GC pauses
render-queue command growth
UnitRender stage boundaries
```

while also removing the unnecessary Fog visible-set copy. This matches the V2.1 generation used to pursue the remaining ~50 ms tail.

## 3. Representative progression

Representative valid 100%-moving runs preserve the broad progression:

```text
V1 density100
  avg frame      ~32 ms
  MapRender      ~11 ms class
  unit cull      ~3.4 ms class

V2 density100
  avg frame      ~23 ms
  MapRender      ~2 ms class
  unit cull      ~3.5 ms class

V2.1 density100
  avg frame      ~23 ms
  MapRender      ~2 ms class
  unit cull      ~3.5 ms class
  rare ~50 ms tail still visible
```

Now that source states are bound, these rows can be located in code history. They still must **not** be interpreted as a clean one-variable A/B because several engineering changes separate the cohorts.

The supported historical conclusion is:

> As dominant MapRender work was reduced, residual UnitRender/cull work and rare tail behavior became visible enough to isolate with dedicated experiments.

## 4. Methodology evolution

The series establishes the dimensions needed for trustworthy realtime scaling work:

```text
resident population
moving density
common planning workload
nested execution subset
staggered vs synchronized phase
Fog requirement
camera/zoom stability
warmup
planning/kickoff/execution epoch separation
rolling-window completeness
subsystem timing
worst-frame diagnostics
```

Without these controls, aggregate FPS would confound workload changes with implementation changes.

V1 is especially important because it formalizes the rule that density changes **execution density only**, while the full 5000-plan planning workload remains fixed and excluded from steady execution timing.

## 5. Relationship to later dedicated investigations

The controlled workload context later enabled stronger causal experiments for:

```text
GC policy
  -> AUTO vs realtime_defer

memory retention
  -> repeated safe-GC soak

unit culling
  -> pre/post hot-loop implementation

Vision cache
  -> 4096/8192/16384/32768 capacity ablation
```

Those dedicated cases, rather than this methodology series, remain the canonical source for their final causal conclusions.

## 6. Provenance boundary

Directory labels `v1`, `v2`, and `v2.1` are archive cohort names, while the SHAs above are the source-control identities recovered from contemporaneous run handoffs.

The archive does **not** claim that the JSON files internally encode those SHAs. Instead it records the external provenance evidence that binds the cohort to its source state.

This distinction is intentional:

```text
artifact integrity   -> SHA256
measurement content  -> raw JSON
source identity      -> contemporaneous run-handoff + Git commit inspection
```

## 7. Result

Dynamic World is now a provenance-complete methodology archive:

```text
14 original raw JSON artifacts     recovered
SHA256 integrity                   verified
V1 source HEAD                     recovered
V2 source HEAD                     recovered
V2.1 source HEAD                   recovered
source-generation fingerprints     verified in Git
```

No additional Dynamic World source-provenance backfill is currently required.
