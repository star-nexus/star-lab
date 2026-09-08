# P3 — local synthetic Agent / ENV interaction

Updated: 2026-09-08. Status: P3.0 contract recorded; P3.1 building. No new capacity claim.

## Scope and identity

STAR baseline: `02d0fc1b598c54a172e1122ac9ea4c1e2f46ec15`.
Lab baseline: `85d142e897194264810ab94ddeab0c6f63fd9e9a`.
User explicitly skips P1/P2; network/Hub/session-transport validation and P4 soak are deferred.
Keep the Framework / Protocol / ENV / Agent four-layer architecture.
Agents are local deterministic session state machines, not LLM calls or OS processes.
Register and claim through the normal ENV validation/execution entry. No direct state mutations to stand in for Agent actions.

## Workload contract

- World target 30 Hz. Think/response delays: 1, 5, 15, 60 seconds; a mixed cohort covers slow agents.
- Independent session timelines; observation -> think -> action -> next observation.
- Finite in-flight work per session. Record scheduled/offered/completed counts and busy/late sessions; never claim nominal throughput from registered counts.
- Staggered normal load; synchronized arrivals are a separate stress scenario. No synthetic wire noop verb: waiting is local session behavior.
- Sizes (Agent / resident Unit): 100/100, 1000/1000, 1000/3000, 1000/5000, 1000/10000, 5000/10000, 10000/10000.
- Current faction-wide observation remains the compatibility reference. Explicit selected/controlled-unit observation may reduce own-unit panels/affordances only with documented semantics; shared faction Fog/visible enemies/terrain must remain faithful.
- Per-agent commandability must not leak through shared caches. Preserve same-state affordance/executor parity and freshness after in-place changes.
- Moving-only E8 comparison and normal legal-action closed loop are distinct workloads. All-moving empty reachable lists cannot prove actionable-observation performance.
- Include real execution pathfinding/action costs in closed-loop measurements. Never reset AP/MP invisibly to sustain load. Record alive/moving counts, actual accepted move/attack counts and world progress.

## Preregistered measurement and gates

P3 discovery starts with short diagnostics; they are not capacity acceptance.
Formal candidate evidence: one >=300s and three fresh-process >=60s traces, with fixed warmup and all admitted frames preserved. At 60s thinking, report the small per-session cycle count explicitly.
Full frame work includes render, ENV interaction and maintenance, excluding only deliberate FPS waiting. P99 <= 33.33ms; report throughput, complete 30s blocks, rolling5s, misses and longest miss streak separately.
Proposed service SLO: ENV queue+observation response P99 <=100ms; action queue->execution start P99 <=100ms. Thinking time is separate; rejected stale actions and retry effects are counted, never hidden.
No growing backlog or silent dropped requests; validate completed vs offered load and per-session fairness. World simulation-time/wall-time progress must be reported.
Pure response construction and actual JSON encode/byte counts are separately attributed; JSON-inclusive results cannot be inferred from zero-copy results.
Recorder is bounded, overflow checked, with measured overhead. P1 long-run recorder/30-60 minute soak is not in this scope.
Chrome remains open. One performance process at a time. No slow-frame deletion.

## Stages

| Stage | State | Deliverable |
|---|---|---|
| P3.0 | complete | This contract; resume/priorities updated; baseline/dev isolated worktrees |
| P3.1 | in progress | Local deterministic registration/claim/observe/think/act driver + meaningful tests |
| P3.2 | pending | Source-pinned baseline, causal counts/timing, negative evidence |
| P3.3 | pending | Evidence-led production optimization, A/B, correctness regression |
| P3.4 | pending | Size/delay frontier and formal candidate repeats |
| P3.5 | pending | Protocol-standard archive, source tags, squash integration and final receipt |

## Source and archive policy

Production development: `codex/p3-agent-observation`, Lab-hosted `runs/star-p3-dev`.
Baseline: detached `runs/star-p3-base`. Formal runs require exact clean source/tooling SHAs.
Use standard `templates/` layout in `experiments/2026-09-p3-local-agents/`.
Keep decision-grade compact + raw forensic artifacts with SHA256/size/locator.
Before main integration, annotated tag pins developer tip. Integrate exclusively with `git merge --squash`; record pre-main/development/tag/post-main identities. Immutable published tags are never moved.

## Next action

Build the local driver and deterministic smoke workload, then establish observation cost on baseline before production changes.
