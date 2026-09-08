# Decision — sustained complete-trace gate CLOSED / KEEP E8-1 through E8-4

Validated runtime `9581084835633e10d80aac849925939bc59b9138`, local annotated tag
`scale-10k-100pct-30hz-sustained-e8`. The fixed-workload 305.447501s trace has
controlled avg28.220838/P99 **32.430227ms**. Three subsequent independent-process
65s traces have P99 **28.984507/30.026299/29.162605ms**. All workload/trace guards
and all16 complete30s blocks pass (worst block P99 33.248388ms). Regression505 PASS.
23 raw archives, fixture and50 checksummed evidence files verified; all8 gate
analyses replay exactly, including negative results. See results/integrity.json.

This accepts the measured complete sustained traces against33.33ms. It does not
claim every short window or frame passes: final rolling5s P99 of the long run is
34.745ms, and repeat2 is37.231ms (max53.484ms); these are preserved in compact
evidence. The long-run frame-body P99 is34.033ms, a separate timing quantity.
Chrome remains open; no presumed Chrome/OS interference is filtered. The long
trace has64 breaches (.625%), maximum41.817ms and longest streak3. This is a P99
capacity result for the specified desktop workload, not a hard realtime guarantee.
60Hz, MiniMap-enabled full interactive operation and10K Agent sessions remain
outside this validation. No architecture rewrite is required by this Core result.

Local retained improvements: E8-1 frame-scoped texture preparation, E8-2 exact
all-Unit faction roster references, E8-3 coalesced component-row reads. Each has
interleaved A/B/B/A local evidence and semantic regression coverage. Combined
runtime `88b19fe92957ee660f50cc366c5a737cb2dc8ca8` passes three >=60s admitted
traces, but FAILS the continuous 305.466s trace: P99 34.520437ms, 4.017% breaches.
Do not promote it as a sustained 10K/100%-moving frontier.

The late slowdown also appears with history recording disabled: final 5s avg
32.406ms/P99 35.724ms after 310s execution. This rules out history retention as
the only condition under which the symptom appears; it is not a randomized
estimate of recorder overhead. Its exact underlying cause remains unresolved.

Accepted E8-4 runtime `9581084835633e10d80aac849925939bc59b9138` reuses movement
references while their component versions remain valid and invalidates immediately
after synchronous callbacks change references. 505 regression tests PASS. Live
interleaved A/B/B/A shows Animation7.446/7.676ms in A versus5.111/5.348ms in B;
controlled avg29.172/29.810ms versus26.800/27.253ms. B2's P99 35.789ms is retained
as a short-window counterexample, not discarded. Later controlled sustained
validation uses the preregistered complete-trace windows and includes every
admitted sample. E8-4 is retained for its causal local work reduction plus that
bounded sustained capability, not a claim that all observed windows pass.

Rejected explanations/designs preserved:

- E7 command count aliases are not independent confirmations.
- All visible units take the animated path, one unit command each. Grouping,
  static/animated mixture and command amplification do not explain this workload.
- Commit rate is ~20,000/simulation-second; rising per-frame commits partly follow
  rising dt. A movement synchronization root cause has not been established.
- Do not count the environment-wide speed difference between sessions as a code
  saving. Use the local interleaved bracket and subsystem metrics.
- UI spatial living counts are not equivalent to all-Unit faction counts.
- The earlier query-result identity draft was rejected before measurement.
- Slots composition remains NOT MATERIAL based on the inherited E6-2 case.
- No animation/Fog deferral, frame dropping, native rewrite or parallelism used.

Revisit on failure of sustained gates, a new scenario/camera/display size, dense
component membership churn, different runtime/hardware, MiniMap enabled, or the
separate online-Agent data plane. A requirement that every5s rolling estimate or
every frame meet33.33ms would reopen latency work; it is not validated here.
All changes are local on codex/10k-30hz-volume; no merge or push was performed.
