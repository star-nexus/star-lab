# Analysis

Observation: API13 scans all ECS entities for census/enemies and all map cells for terrain even when only seven cells are visible. Exact before/after timings and work counts are in results/comparison.json.

Hypothesis: unrelated terrain/visual entities and hidden map scans cause query cost to grow with map size, even at fixed Unit count and response size.

Instrumentation: API14 counts census/enemy member visits and terrain candidates; API13 counts are derived from actual initial entity/tile counts and its traversal code. Initial state and decoded Agent response hashes are equal in every case. All samples and payloads are archived.

Evidence: at 60919 tiles and 100 Units, two full entity walks become 100-member walks; seven visible tiles require seven candidate visits. Local query median falls 1.224→0.125ms, empty vision 0.842→0.084ms. Disabled Fog still visits and emits all tiles, with 294.697→296.953ms, so scan pruning does not remove assembly/encoding cost.

Root cause: iteration domains included unrelated ECS residents and hidden terrain. A stable Unit membership index and exact smaller-set intersection remove that work without changing information or authority.

Rejected explanation: fewer observed facts, changed game rules, or a stale snapshot do not explain this result: complete outputs and state guards match. General throughput/parallel/frame claims are unsupported; five samples do not establish significance, and large full-map outputs remain expensive.
