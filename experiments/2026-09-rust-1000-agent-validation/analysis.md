# Analysis

| 60s diagnostic | Mean observation service ms | Frame P99 ms | Observation response P99 ms |
|---|---:|---:|---:|
| python-normalized-60 | 7.575 | 28.717 | 935.146 |
| python-original-60 | 7.822 | 31.800 | 1594.992 |
| rust-60 | 2.741 | 26.453 | 46.631 |

All short controls use30s warmup, identical scenario/window/budget/workload parameters. Original Python and normalized Python both pass the frame gate but fail observation response, observation queue, action queue and bounded-queue guards. Rust passes all. Negative controls are retained.

Original Python → Rust observation service averages7.822→2.741ms:2.853× time ratio,64.95% less time. Whole-frame P9931.800→26.453ms:16.82% less time. Normalized Python → Rust:7.575→2.741ms,2.763× time ratio; frame28.717→26.453ms,7.88% less time. These are single independent live diagnostics per backend, not repeated fixed-input microbenchmarks. Actual acceptance times, action sequences and state trajectories differ; original-vs-normalized sorting is also versioned. Do not attribute all differences solely to language or R0 sorting.

Queue/response improvement1595→46.6ms is mainly the elimination of accumulated backlog, not34× faster computation. Service includes observation construction/encoding and client decoding, excludes admission wait. Long Rust service averages3.07–3.12ms as observed payload/state evolves; do not replace long-run values with short diagnostics.

In long run1 native_step averages0.295ms (P990.758), display systems8.679ms, display application2.768ms and presentation extraction0.709ms. Step excludes Agent observations. Parallelizing only world step cannot plausibly multiply overall frame throughput at this load. P99 component values must not be added or subtracted to predict whole-frame P99.

Python already shared facts within read batches; Rust also supports this and bounded Unit-panel worker pools. The current single-request Lab loop does not combine separate Agent reads into one shared context. Reusing that capability is an integration opportunity, not a newly discovered algorithm. Current Runtime::step remains ordered; see the dependency audit before System-level parallel work.

Three independent long runs all pass all guards, no retry selection. 5000 alive does not mean5000 simultaneously moving or high combat density. High-density negative controls,10000Unit expansion,platform wheels and real network integration remain separate work, not implied passes.
