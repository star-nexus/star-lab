# E3 decision

**Research complete; no new execution-policy fix or capacity claim.**

保留E2 Statistics内部并行和默认native1。当前规范负载下不新增其他System线程派发。E3已否定将整个Vision阶段作为LOS并行预算的假设；未来先量合法大批叶子，不先将全部System入池。

| 优先级 | 条件路线 | 进入下一实施阶段前需要的证据 |
|---|---|---|
| 条件1 | Vision冷缓存几何 | 原dirty批次有足够独立miss/合法较大range；串行拆分后纯计算显著覆盖gather/dispatch/output/commit成本；LRU元数据顺序模拟和A→B→A契约先通过 |
| 条件2 | Movement路径/插值算术 | 更多同时移动单位的固定合法输入，仍O(active)；逐段跨格/空间占用/dirty原序，完整错误及多段跳跃等价；实际纯计算/提交成本分开 |
| 条件3 | Visuals同阶段行更新 | 大量浮字/效果或另建合法ranged负载；单阶段达足够批量；attack→spawn→projectile→effect→damage栅栏、ID流和错误前缀完整保持 |
| 暂缓 | Recovery/Lifecycle/Clock | 大到期桶若成为热点再归因；本次skill无样本。Lifecycle索引判定/Clock标量不改成resident扫描 |
| 先补样本 | Capture | 本轨迹无活动；先测大量合法捕获及同tile冲突，不能以空闲样本判定全面不适合 |

这些优先级是架构可分离性与重访条件，不是当前负载的已证收益排序。当前没有足够证据选定另一个上线kernel，也没有新数字门槛。E2的128只用于Statistics，不挪用到LOS/Movement/Visuals。未来最小实验是Vision串行冷几何拆分与条件成本试验；当前目标若继续优化，更值得先考察Vision串行集合/提交的表示成本。

Rejected：完整Vision/Movement方法入池、按worker完成顺序分配ID/RNG/提交、复制整个世界、跨请求等待凑批、跨Visuals栅栏、合并缓存键改变命中/淘汰计数、因平均小就删除尾峰。既有线程池只在证明净收益后复用。

No closure：没有新live/Frontier验收、没有新增确认玩法GAP，G001–G003基线变化、G008/G009 OPEN和R001/R002 RISK保留；5000Agents暂缓。E2真实容量证据仍指其原2bc57d5/23dc7e4 binary，不自动给E3诊断binary扩展容量保证。未push/merge。所有原删除与冻结目录核验保留。

Revisit：场景视距/terrain、缓存容量或命中率、同时移动数、同阶段视觉行数、到期桶密度发生变化；或线程池/CPU/构建配置变化。每项需要同输入完整等价、同binary单变量A/B、mean/P99/尾样本全保留、净收益及新实际闭环验证。
