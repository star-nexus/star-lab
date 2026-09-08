# E8: 10K render volume and 30 Hz completion

**Status:** CLOSED — sustained complete-trace gate PASS; short-window limitations retained.  
**STAR repository:** `star-nexus/star`  
**Problem:** `e7ba18b31870577110b591104ef8fa7b4713e43c`  
**Validated runtime:** `9581084835633e10d80aac849925939bc59b9138`  
**Local tag:** `scale-10k-100pct-30hz-sustained-e8`  
**Initial sustained tooling:** `94f8986280ca7c391fa45a854a62c7975cab1658`  
**E8-4 300s tooling:** `bed4e479859c65e23bf9ce403e381fa03e596d30`

| Complete trace | Seconds | Frames | Controlled avg ms | Controlled P99 ms |
| --- | ---: | ---: | ---: | ---: |
| Continuous | 305.447501 | 10240 | 28.220838 | 32.430227 |
| Repeat 1 | 65.285074 | 2389 | 25.784004 | 28.984507 |
| Repeat 2 | 65.301032 | 2342 | 26.310417 | 30.026299 |
| Repeat 3 | 65.271297 | 2336 | 26.370550 | 29.162605 |

All workload guards and all16 full30s blocks PASS. Regression505 PASS. The repeat
tooling is `4ccdc4972ded1bbc2d2125f214770d27865792d0`; neither runtime nor analyzer
changed between these gate runs. Short rolling5s and frame-body counterexamples
are described below. This case preserves all negative A/B and sustained runs.

## 1. Problem and significance

The retained E6-1 runtime does not reliably pass the controlled-work P99 <=33.33ms
gate at 10,000 resident units and 100% continuous movement. E7 identified correlated
UnitRender/Vision/Animation tails, but did not establish movement synchronization
as their cause. This case measures work volume, removes three concrete sources of
repeated work, and validates sustained Core runtime. It does not validate 10K
online Agent sessions or guarantee every frame meets its deadline.

## 2. Environment and fixed workload

Mac mini Mac16,10, Apple M4 (4P+6E), 16GB, macOS 26.5.2 (25F84), arm64.
CPython 3.13.12; pygame 2.6.1 / SDL 2.28.4; uv 0.12.5. Locked dependencies:
`uv.lock` SHA256 `e8a64dba4f65993ce7a1bd720f7c7b6d399422692e4202dfb25b9c1596ce5f95`.
Visible SDL window 2480x1261; default fixed scenario camera/zoom, no input.
Chrome remains open on the host; the user notes occasional CPU consumption. It
was not closed and no samples were removed due to presumed Chrome interference.
Scenario `chibi-144k-scale-10000` is actually a 120x120 board (14,400 hexes).
10,000 resident/moving, seeds 42 (scenario, route and phase), staggered, 12-step
routes prepared before timing; execution pathfinding OFF; real animation,
position commits and Vision/Fog ON. Uncapped, MiniMap dynamic units OFF,
`realtime_defer`, gameplay input blocked. Do not run benchmarks concurrently.

## 3. Source checkout and fixture

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
git checkout bed4e479859c65e23bf9ce403e381fa03e596d30
export UV_PYTHON=3.13.12
uv sync --frozen
unzip /path/to/star-lab/experiments/2026-09-10k-e8-volume/artifacts/scenario.zip -d rotk_env/maps
shasum -a 256 rotk_env/maps/chibi-144k-scale-10000.json
```

Expected fixture SHA256:
`e5bacb41c499fdfb9e91a917a1427515f2be1dae5ca4961692e921c05b816d25`.
These source commits and the Lab case are local until explicitly published; a
fresh clone requires access to those commits. No push is implied by this record.

## 4. Reproduce the problem and attribution

The runner creates an isolated detached runtime worktree at `--sha`, copies only
the fixture and exact tooling launcher, starts a fresh visible process per repeat,
runs the harness, validates guards, and removes its own temporary worktree.

```bash
uv run --frozen python tools/run_phase5_e8.py --sha e7ba18b31870577110b591104ef8fa7b4713e43c --mode off --window 30 --repeats 3 --label baseline
uv run --frozen python tools/run_phase5_e8.py --sha e7ba18b31870577110b591104ef8fa7b4713e43c --mode volume --window 30 --repeats 3 --label volume
uv run --frozen python tools/phase5_e8_analyze.py results/phase5-e8/<volume-run>
```

Expected baseline signature on the original interleaved run: controlled avg
33.514..34.082ms, P99 36.932..37.419ms. Absolute timings vary with machine state.
Volume signature: animated units equal visible units, one unit command per visible
unit, static groups zero; ~20,000 commits/simulation-second. Diagnostics are not
release gate evidence. Individual A/B/B/A commands, runtime and tooling SHAs are
preserved in each compact manifest, including the historical tooling used then.

## 5. Validate the candidate

```bash
uv run --frozen pytest framework/tests rotk_env/tests tools/test_phase5_e8_snapshot.py tools/test_phase5_e8_trace.py tools/test_phase5_e8_gate_analyze.py -q
uv run --frozen python tools/run_phase5_e8.py --sha 9581084835633e10d80aac849925939bc59b9138 --mode off --window 5 --sample-after 70 --trace --repeats 3 --label gate60
uv run --frozen python tools/phase5_e8_gate_analyze.py results/phase5-e8/<gate60-run> --seconds 60
uv run --frozen python tools/run_phase5_e8.py --sha 9581084835633e10d80aac849925939bc59b9138 --mode off --window 5 --sample-after 310 --trace --repeats 1 --label gate300
uv run --frozen python tools/phase5_e8_gate_analyze.py results/phase5-e8/<gate300-run> --seconds 300
```

The bounded experiment recorder copies completed profiler samples outside the
controlled sections. No diagnostic timers/system patches are enabled. Production
profiler remains 5s/4096 samples; extending its percentile window would itself add
cost. The analyzer excludes a fixed first 10s and uses **all** remaining trace
frames (including any extra coverage), not just the last rolling snapshot. It
checks minimum coverage, no overflow, contiguous IDs and per-frame workload/input
invariants, then reports P99, all full 30s blocks, missed-frame fractions, longest
miss streak and a descriptive block-bootstrap interval. Individual deadline misses
are permitted by the specified P99 gate. Frame-body timing is separate. This
sustained evidence does not imply that every 5s rolling estimate passes: E8-4's
300s run ended with rolling-5s P99 34.745ms, while its complete-trace P99 was
32.430ms and all full 30s blocks passed. Both values remain archived. Neither
window definition nor frame-body timing should be silently substituted for the
other when interpreting a claim.

Expanded commands for the continuous run (the runner records exact paths/env):

```bash
STAR_SCALE_MINIMAP_UNITS=off STAR_E8_MODE=off STAR_E8_RUNTIME_SHA=9581084835633e10d80aac849925939bc59b9138 STAR_E8_WINDOW=5 STAR_E8_TRACE=1 uv run --frozen python tools/phase5_e8_snapshot.py --skip-start --mode real_time --scenario chibi-144k-scale-10000 --players human_vs_two_ai --no-hub --seed 42 --uncapped --scale-harness-socket /tmp/star-e8-repro.sock
uv run --frozen python tools/scale_driver.py --socket /tmp/star-e8-repro.sock --command-timeout 120 density-point --density 1 --phase staggered --seed 42 --phase-seed 42 --route-steps 12 --duration 315 --warmup 5 --sample-after 310 --ready-timeout 120 --gc-policy realtime_defer --profile /tmp/e8-profile.json --output /tmp/e8-point.json
```

Run the expanded commands in the prepared runtime worktree with the two tooling
files copied as the runner does; use separate terminals. The wrapper above is the
canonical entrypoint and avoids missing this setup.

## 6. Evidence and recovery

Read compact JSON in `results/` first. Each contains original run manifest,
guards, causal metrics/analyses, raw profile hashes and raw ZIP SHA256/size/path.
Complete raw output remains in `artifacts/*-raw.zip`; `scenario.zip` owns the
fixture. Re-analyze by extracting a raw ZIP and invoking the frozen analyzer.
Check integrity from this case root:

```bash
shasum -a 256 -c artifacts/SHA256SUMS
```

See [analysis](analysis.md), [decision](decision.md), [manifest](manifest.yaml),
and STAR `docs/dev/10k-online-resume.md` for the current recovery state.
