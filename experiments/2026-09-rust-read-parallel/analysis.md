# Analysis — R4a scoped read-panel parallelism

## 1. Observation

R3k4 already shared encoded facts within each write-free batch, but all Unit panel computation was serial even with threads2/4. R4a uses actual bounded workers for independent missing panels. Unit count5000 is a query fixture, not5000Agents or a world-frame test.

## 2. Competing hypotheses

H1: independent panel computation can benefit from workers when work per panel is sufficient. H2: public data/encoding and scheduling overhead can limit or reverse this gain. These are not competing correctness models: both preserve exact rules and inputs.

## 3. Instrumentation

Three scheduling diagnostics (parallel_panel_batches, panel_tasks, panel_worker_threads) plus existing census/panel/candidate/encoding counts. Rust Barrier test proves distinct simultaneous workers and excludes caller participation. Full response/state comparisons exclude only the three new diagnostic fields, never Agent content. Import time reported separately; no subphase timings collected, so public projection vs final encoding remaining shares are not quantified here.

## 4. Evidence

All120 rows pass guards;30 cases each compare oldserial/new1/new2/new4. MP0 preserves archived inputs/results; MP6 sets movement budget and spaces5000Units overexisting5677tiles, retaining alive count and exact occupancy rules. Selected100Units return966reachable cells. MP6 failed original dense fixture is retained separately and excluded.

All numbers below are milliseconds, median of5 calls after1warmup. Experiments run serially, not randomized; local noise and thermal/background drift remain. These are not P99 or frame times.

| workload | scenario | mode/requests | API15 t1 | API16 t1 | API16 t2 | API16 t4 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| mp0 | terrain-local | handler/1 | 0.104 | 0.101 | 0.122 | 0.136 |
| mp0 | terrain-local | public/1 | 0.128 | 0.116 | 0.120 | 0.139 |
| mp0 | terrain-local | single/1 | 0.104 | 0.123 | 0.120 | 0.125 |
| mp0 | terrain-local | handler/8 | 0.132 | 0.137 | 0.139 | 0.144 |
| mp0 | terrain-local | public/8 | 0.167 | 0.142 | 0.169 | 0.173 |
| mp0 | terrain-disabled | handler/1 | 14.457 | 14.986 | 15.210 | 14.091 |
| mp0 | terrain-disabled | public/1 | 14.229 | 14.271 | 30.031 | 14.650 |
| mp0 | terrain-disabled | single/1 | 14.866 | 15.013 | 14.729 | 14.609 |
| mp0 | terrain-disabled | handler/8 | 15.079 | 15.266 | 14.281 | 14.632 |
| mp0 | terrain-disabled | public/8 | 15.065 | 15.222 | 15.942 | 15.456 |
| mp0 | units-5000 | handler/1 | 24.012 | 23.867 | 22.557 | 24.548 |
| mp0 | units-5000 | public/1 | 23.668 | 23.215 | 24.678 | 22.715 |
| mp0 | units-5000 | single/1 | 22.839 | 23.481 | 23.849 | 23.648 |
| mp0 | units-5000 | handler/8 | 26.624 | 25.934 | 25.324 | 25.016 |
| mp0 | units-5000 | public/8 | 24.518 | 25.756 | 25.617 | 26.307 |
| mp6-spaced | terrain-local | handler/1 | 0.143 | 0.156 | 0.136 | 0.149 |
| mp6-spaced | terrain-local | public/1 | 0.157 | 0.166 | 0.150 | 0.154 |
| mp6-spaced | terrain-local | single/1 | 0.154 | 0.152 | 0.147 | 0.141 |
| mp6-spaced | terrain-local | handler/8 | 0.169 | 0.172 | 0.150 | 0.203 |
| mp6-spaced | terrain-local | public/8 | 0.180 | 0.185 | 0.187 | 0.234 |
| mp6-spaced | terrain-disabled | handler/1 | 15.235 | 11.629 | 12.941 | 12.059 |
| mp6-spaced | terrain-disabled | public/1 | 12.391 | 12.111 | 12.186 | 11.936 |
| mp6-spaced | terrain-disabled | single/1 | 11.603 | 12.024 | 12.110 | 11.623 |
| mp6-spaced | terrain-disabled | handler/8 | 12.423 | 13.888 | 13.589 | 12.785 |
| mp6-spaced | terrain-disabled | public/8 | 13.710 | 13.376 | 13.628 | 12.989 |
| mp6-spaced | units-5000 | handler/1 | 22.772 | 23.157 | 21.399 | 20.222 |
| mp6-spaced | units-5000 | public/1 | 22.751 | 24.992 | 20.885 | 21.307 |
| mp6-spaced | units-5000 | single/1 | 22.594 | 22.569 | 20.777 | 22.689 |
| mp6-spaced | units-5000 | handler/8 | 24.624 | 25.775 | 24.692 | 24.170 |
| mp6-spaced | units-5000 | public/8 | 25.429 | 24.467 | 23.791 | 23.017 |

## 5. Root cause and limits

Static call structure and counters establish the removed serial dependency: workers read immutable native data and produce separate panel results. End-to-end gains are modest and not universal. MP6 5000Units public single25.0→20.9/21.3ms; eight-query batch24.5→23.8/23.0ms. Small terrain-local queries can regress. Per-phase attribution remains futurework; do not present H2 as a measured exact percentage or choose a global winner from these samples.

## 6. Regression and compatibility

2165Python tests,83targeted,4Rust tests,fmt/Clippy and6oldscenes/510nodes passed. FullPython oracle comparisons cover display none/dummy/window andFog on/off; mixed writes/lifecycle compare serial/parallel. No new confirmed game-rule GAP. R002 remains bounded, not closed: Combat/UnitSkills currently static at ingress; statistics/Player have real writes; Python display is derived, not complete authority.

## 7. Unresolved

World systems still serial. New pool does not admit Agents concurrently or cross writes. Public faction construction, final output, Python presentation, queue and whole30Hzcapacity still require profiling/acceptance.5000Agents is a separate expansion target.
