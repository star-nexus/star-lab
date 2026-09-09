# P3 — local synthetic Agent / ENV interaction

Updated: 2026-09-09. Status: P3.0/P3.1 complete; P3.2 reproduced; P3.3 first-round fixes integrated; corrected P3.4 discovery archived. Capacity goal OPEN.

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
| P3.1 | complete | Local deterministic registration/claim/observe/think/act driver + meaningful tests |
| P3.2 | reproduced | Source-pinned baseline, causal counts/timing, negative evidence |
| P3.3 | first round integrated | Evidence-led production optimization, A/B, correctness regression |
| P3.4 | discovery complete; capacity unmet | Size/delay frontier and formal candidate repeats |
| P3.5 | first-round archive/integration complete | Protocol-standard archive, source tags, squash integration and final receipt |

## Source and archive policy

Production development: `codex/p3-agent-observation`, Lab-hosted `runs/star-p3-dev`.
Baseline: detached `runs/star-p3-base`. Formal runs require exact clean source/tooling SHAs.
Use standard `templates/` layout in `experiments/2026-09-p3-local-agents/`.
Keep decision-grade compact + raw forensic artifacts with SHA256/size/locator.
Before main integration, annotated tag pins developer tip. Integrate exclusively with `git merge --squash`; record pre-main/development/tag/post-main identities. Immutable published tags are never moved.

## Next action

First-round integration and corrected discovery are complete. Next: explicit read-batch shared faction observation construction; see the checkpoint below.

## Checkpoint — driver and attribution

Lab driver `1a68ed8` and subsequent source-pinned runner revisions are saved in Git. Real registration/claim/think/action scheduling has three passing Lab tests; source contracts have 54 passing focused tests (including 10 new selected-observation tests).
Source checkpoints: selection `0c1ec5b454a703ed3d90d19db98a6683758996a8`, local occupancy `7f72703`, attack candidates `39f937f`, tested spatial candidate `32a0eb9`. All remain development checkpoints, not accepted milestones.
Evidence and causal interpretation: [active experiment](../experiments/2026-09-p3-local-agents/README.md). Interleaved layout setup bounds mistakes were corrected using the authoritative parser; no invalid pre-workload run is capacity evidence.
Current next action: runtime candidate smoke, then controlled scale/delay points; complete helper A/B and preserve equivalent-payload results. Formal world throughput gate allows 1% pacing tolerance (>=29.7Hz) in addition to P99 frame work <=33.33ms; no formal results preceded this definition.

## Measurement correction before acceptance (2026-09-09)

Runtime clock pacing carries oversleep forward rather than slowing each frame. Full-frame timing includes profiler bookkeeping. Actual queue wait is measured from request eligibility; nominal cycle lag is retained separately. A sequential LLM session cannot offer the next observation until its prior think/action completes. Require >=95% of ideal phase-scheduled observation load to prevent closed-loop throttling from hiding overload. This threshold was fixed before formal capacity validation.
The first 5000-unit / 1000-Agent / 60-second-think 65s trial met frame/service/load gates, but its end-queue measurement was taken after shutdown/analysis. That result remains failed as recorded; tool `1e08a17` freezes queue health at the actual end boundary. Fresh repeats are required. No retrospective deletion/relabeling of samples.
Current full production regression: 879 passed, 4.75s. Runtime candidate hot path `32a0eb9`; client array schema/docs finalization `46dbc77`.

## Adaptive delay bracket (before collection)

5000/1000 at 15s still misses the 100ms service SLO after selected panels, spatial queries and one live census (source `e8b48c0`). 60s discovery met timing/load but needs fresh end-boundary validation. Add a 30s midpoint with unchanged gates, GC policy `realtime_defer`, 12ms per-frame local pump budget, move policy, canonical fixture, selected panels, JSON encoding. Warmup 30s; one 60s fresh process first, then >=300s + remaining independent repeats if it passes. Report the adaptive choice and all failed 15s points. This is capacity bracketing, not changing a threshold.

## Frequency correction and failed long candidate (2026-09-09)

The user explicitly requested observation 1/5/10/30 Hz per Agent, independently of slow LLM decisions. The initial plan incorrectly coupled these. Preserve all previous evidence as sequential-loop diagnostics. New `--observation-hz` schedules every periodic pull at its original deadline, retains overdue work without drops, and does not replace an in-flight decision snapshot. One pending periodic pull and one pending action per Agent bound heap storage; nominal offered counts and oldest queue age expose logical backlog. Test the requested frequency matrix with decision delay 1s first, then slow/mixed decision checks. No capacity threshold changes.

`gate5000-d30-r1` passed a 60s trace, but `gate5000-d30-300` FAILED full-frame P99 (34.591ms), despite world 30Hz, observation 35.670ms, action queue 28.431ms, 99.9% offered load. No formal capacity claim and no selective short-repeat continuation. Ten 30s block P99s rise from 29.017 to 35.308ms; preserve complete raw data. Current production regression 881 passed; performance contracts 81 passed.

## Corrected observation discovery matrix (preregistered)

Run fresh serial processes at 1Hz for (Units,Agents)=(100,100),(1000,1000),(3000,1000),(5000,1000),(10000,1000),(10000,5000),(10000,10000), then 5/10/30Hz at 5000/1000. Each is 5s warmup +15s measurement, 1s decision latency, selected panels, JSON, canonical map, move, realtime_defer, 12ms pump. These short overload diagnostics cannot validate capacity. Run a separate 3000/1000/1Hz attribution trace and no-encode counterpart to distinguish construction and serialization. The attributable trace completed first (12.31% offered observation load; 17.503s service P99), and is explicitly not a formal point.


## First-round integration and reproducibility checkpoint

Main `08c857e5df39f671c5a13bf04b9af9aac0800e78` via squash; pre-merge tag
`p3-observation-pre-squash-2026-09-09` pins `c9737451de97f1b1903123377a1514227c3ffdf5`.
Timed source remains `e8b48c0568fb8830055bf053a724acc2b4e5c04c`; final developer change is docs/comments only.
881 production /81 structural /7 Lab tests passed. All24 runtime raw ZIPs checksum-verified and reanalyzed.
Corrected matrix is archived in the case; 3000/1000/1Hz completes12.06%, 5000/1000/1Hz8.99%, 10000/10000/1Hz0.58%.
No accepted four-trace point; no Frontier addition. No 100%-moving plus observation capacity claim.
Next: read-batch sharing of faction public observations with explicit freshness boundaries and per-Agent private panel construction.
P3 overall remains OPEN; do not repeat P0 or the completed first-round implementation.


## Second-round read-batch closeout (2026-09-09)

Branch codex/p3-shared-observation; eager measured3017547, lazy measured72e3641; exact SHAs in case manifest.
Before main `08c857e5df39f671c5a13bf04b9af9aac0800e78`; pre-squash tag `p3-read-batch-pre-squash-2026-09-09` pins `626d3a8db900fc18599bc96206bc76b960826999`; integrated main `906386312d70d77af25e4b4da883f6dd5b0fe5ef`.
899 production and10Lab tests pass. Frozen-world oracle from pre-main and lazy source is byte-identical across30queries; each new-source state also verifies batch-on/off against standalone.
30diagnostics archived with raw reanalysis and SHA256,65archive artifacts including deduplicated fixtures/oracle.
3K/1K/1Hz batch-off11.89%→on21.06%;5K/1K8.81%→14.03%;10K/1K3.48%→2.95%. No target capacity accepted; no formal long certification begun.
All experimental tools/evidence remain Lab; source/rule-compatible API/contracts/docs in STAR. Next: review cold-snapshot and full-output cost before another optimization.
