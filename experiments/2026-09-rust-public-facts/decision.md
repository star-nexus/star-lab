# Decision — R4b 公共事实直接编码

**Status:** accepted，限本优化范围，非容量/默认切换验收  
**Decision date:** 2026-09-25  
**Validated STAR commit:** `90481f985bc66f30d8ed7627afe0ee37aec1aa75`  
**Validated STAR tag:** `rust-kernel-r4b-2026-09-25`

## 1. Decision

采用typed serde直接编码公共事实，保留按需诊断。Python与native单线程仍为默认；沿用同一只读段、写入边界和完整输出，不引入TTL或近似。Python SDK/UI/传输/策略继续保留Python。

## 2. Decision drivers

小子集查询的主要成本是公共事实构建和释放。优化数据表示能减少这些成本，同时保持博弈规则和Agent信息完全一致。

## 3. Measured alternatives

| 方案 | 证据 | 决策 |
| --- | --- | --- |
| JSON树缓存与首次深复制 | single5约19.2ms；公共14.1/释放4.9ms | 替换 |
| 同只读段typed编码事实 | single5约2.55ms；公共2.0/释放0.23ms；输出一致 | 采用 |
| 只增加worker | 公共构建仍串行，小子集收益有限/可能变慢 | 保留显式1/2/4，默认1 |
| 删除字段或使用旧快照 | 不必要地改变信息/规则 | 未引入 |

## 4. Headroom and scaling

满足完整30Hz门槛的最少线程数仍未知。没有新增线程池或经验阈值，查询微测不证明整体容量余量；完整负载必须再次测量。

## 5. Revisit

完整世界/展示/排队闭环验证之后再选择默认线程。如真实负载显示面板/路径仍是热点，再推进该部分。R5平台wheel矩阵与默认切换未完成。两个API17构建须用精确源码/扩展SHA区分。
