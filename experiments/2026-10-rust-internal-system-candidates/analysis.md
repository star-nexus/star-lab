# E3 analysis

## Observation

对当前5000 Units＋1000 Agents输入，整个Vision耗时不能代表可并行LOS成本；Movement/Visuals/Recovery的合法活动批次也远小于resident数量。全量录制含预热，每配置9880tick。诊断路径均值µs如下；不是普通step耗时，也不是线程加速比。

| 配置 | Vision | Movement | Visuals | Recovery | Lifecycle | Capture |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 43.504 | 31.049 | 9.315 | 3.887 | 0.340 | 0.066 |
| 2 | 43.685 | 32.968 | 9.458 | 4.066 | 0.429 | 0.074 |
| 4 | 42.542 | 31.637 | 9.264 | 4.068 | 0.377 | 0.079 |

## Hypotheses

H1：Vision大阶段成本可能来自未缓存几何，适合第一并行leaf。H2：Movement活跃单位多，插值/路径算术可能值得派发。H3：Visuals阶段独立实体JSON更新可能形成较大批次。H4：Recovery尾峰可能对应大量同桶到期项。这些是待分项归因的假设，不预先选择线程池方案。

## Instrumentation

`system_profile.rs`提供按次自有计数/纳秒字段。PROFILE=true推进与普通路径共用算法、保留原序；false不读Instant。Vision分audit/gather/cache/geometry/commit/presentation；Movement分活动行/跨格及row/spatial/pixel/dirty/cleanup；Visuals记录每阶段行数/循环和spawn/remove结构提交；Recovery记录new-ID审计上下文、MP pending、AP/MP/skill到期组及stale项。原API18/schema5/oracle、RNG/ID和错误前缀不改。失败step不输出timing，仍保留原部分写入。

这些区域有嵌套关系。row_ns已经包含spatial/pixel/dirty，不能把它们再次相加。Movement上界=row−spatial−dirty，仍含ECS写入/计时；Visuals循环与Recovery到期组仍包含JSON/dirty或调度/提交。它们不是已拆出的纯kernel。小任务计时会增加开销、出现时钟量化零值；仅用作成本定位及保守筛选。

## Evidence

- Vision：80603重算，78391hits/2212misses、0evictions，命中97.26%。8011/9880tick无miss，最多5miss、effective range最多2；几何0.553/0.599/0.583µs/tick，仅1.27–1.37%，提交27.10–28.17µs/tick，占63.69–64.75%。1线程有miss的tick平均几何2.924µs，P99 7.332µs；将整个43µs阶段当纯计算被否定。
- Movement：平均122.47、峰186活动行、0invalid，每tick平均8.16跨格。1线程row12.140、spatial3.570、dirty3.211、pixel0.091µs；乐观行上界5.359µs，P99 9.259µs。其他配置上界均值5.384/5.445µs。即使只计算候选，还需未来gather/owned输出/原序commit。
- Visuals：1线程四行循环合计8.135µs/tick；attack0.316、projectile0.036、effect0.940、damage6.843，结构提交0.909。attack/effect/damage平均行数0.30/1.58/6.66，峰5/11/28；本轨迹projectile与spawn均0，不能据此推断大量ranged负载。四阶段有栅栏，不能合并8µs预算为一个任意并行任务。damage非空tick均值7.111µs、P99 22.416µs，含JSON与dirty写入；尾样本完整保留。
- Recovery：AP974、MP26753、skill0到期项，0stale；平均2.81、峰24条/tick。1线程到期组三者合计2.370µs，P99 10.625µs。最大整阶段431.375µs对应seq2000、new_ids5007、到期项0，是首次新ID审计，不能解释成宽到期批次。2/4对应样本也保持。
- Capture整轨迹capturing_before=0；Lifecycle仅索引计数/标量判定。其小阶段时间不构成所有配置的性能定论。

完整三配置distribution/histogram、各System最慢5tick上下文见`results/analysis.json`。没有删除离群/慢样本。Vision 1线程最大commit3.555ms仍保留；不能从单个计时区间推断调度/分配等未测成因。

## Root cause supported by evidence

只针对这个规范轨迹：Vision阶段的大部分成本在串行可见集合/Fog提交，几何已被缓存有效消除；其他候选的当前活动批次小，或有效计算预算包括必须有序的写入。现有证据不支持立即新增并行，不代表这些System在任意合法大批负载都不值得并行。

## Rejected explanations and limitations

否定“Vision43µs都是LOS”、“5000resident就有5000移动/动画任务”、“Recovery最大431µs可以并行均分到期项”、“四个Visuals循环可无栅栏合并”。E1空派发median约7–9µs是其他检查点的机制成本，只作开销量级，不能充当当前严格break-even或因果A/B。没有新生产并行，因此不做新的live容量/Frontier/加速比结论。真正的优化仍需单变量控制试验。

## Correctness and forensic audit

E2独立普通二进制与E3普通/诊断1/2/4共4轮完整重放，每轮40994请求/9880tick/9880展示。完整解码twin响应/delta/final直接相等，记录wire/events/final hash也匹配；stream e01f2147…、final d069c717…全部一致。4个独立契约变体各36场景/174step，错误/reset/close完整输出SHA9db82664…一致，复用已有E2 canonical成员。2315Python/4Rust/fmt/Clippy/Release通过，24新增测试含A→B→A、缓存容量1/4、跨格、同tick新箭和恢复。

`analyze_system_candidates.py`只从canonical raw读取，核对raw整体SHA、内部每成员SHA、每条phase父子计时关系及9880样本，再重算所有candidate_summary和派生指标。`packages.json`提供每原始文件SHA/bytes，关联E2相同契约及R4e原始输入；loose scratch不是复算依据。
