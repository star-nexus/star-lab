# Decision — E8 观测服务专项

**Status:** ordinary-host confirmation complete; service gain supported, frame gate not met; default off
**Decision date:** 2026-10-09
**Research STAR commit:** `8c2afd7153ebc8ec6c80dd9f3a1406be440405e0`
**Validated production commit/tag:** N/A

## 1. Decision

完成本轮有界专项。EntityRef 候选未证实稳定服务收益；census 借用键得到正的服务收益，但没有通过预注册组合门槛。两者都保持默认关闭。保留借用键候选和源码证据供后续成本/宿主研究，不继续补跑、择优或扩充矩阵，不叠加失败候选。

## 2. Decision drivers

预注册：服务均值至少减少2%，服务及所测总工作改善区间下界均正，pooled/最差侧 P99 不回退。最终 census 的总工作改善区间跨零，不能以“均值变快”代替通过。

## 3. Measured alternatives

| 方案 | 服务因果证据 | 系统证据 | 决策 |
|---|---|---|---|
| baseline | 既有完全拥有缓存和组件访问 | 原默认 | 保持 |
| entity_ref | +2.773%，区间跨零 | 总工作 −3.138% | 未采用，保留负对照 |
| borrowed_census | +9.157%，区间正、P99改善；census 诊断下降 | 总工作 +1.696%，区间跨零 | 保留研究候选，默认不采用 |

## 4. Why this option

借用键保留缓存独立所有权，且不需要扩大缓存、改变接纳边界或引入线程。131个相关契约与短完整输入一致性通过，足以支撑该研究修改的适用范围；完整宿主/稳定多轮还没有验证。冻结分析器给出的 `stop this census ownership factor` 指当前组合门槛停止，不否定已测到的服务层改善。

## 5. Why not the alternatives

不因第一项接近零的区间补跑；不通过过滤慢尾或重设门槛挽救第二项。没有证据支持先调整缓存容量、放宽写入边界，或把相关工作放入更多线程。

## 6. Headroom and scaling rationale

本轮只覆盖5000 Units＋1000 Agents、native1服务输入。native4仅契约检查，不代表实时收益。容量、Frontier、G009生产网络及其他既有GAP保持，5000 Agents暂缓。产品原49项删除、两个冻结目录/历史标签和安装扩展保持；不 push/merge。

## 7. Revisit conditions

进一步投入应先有界定位总工作和实际宿主中的剩余成本/慢尾，或做明确预注册的短宿主净收益确认。不得将此次服务改善当作默认上线条件，也不得自动重复这两轮筛选。当前进程均已结束。


## 8. Ordinary-host follow-up decision (2026-10-09)

按用户授权执行一个有界ABBA，四次运行/资源guards通过。普通single观测service改善9.225759%、CI全正、P99未回退；完整帧改善1.325623%，CI −0.173029–0.685167ms跨零，因此预注册组合门槛未通过。默认baseline保持，保留borrowed_census研究候选，不自动进入正式代码采用、不加轮择优。此次不否定局部收益，也不证明整帧没有收益；“完整净收益未确认”是准确结论。

先前encoded服务筛选与这次ordinary宿主是不同条件，结果分别保留。无需靠新增长矩阵来追求显著性；进一步工程投入应有明确新目标，例如观测吞吐或更大的已测成本来源，再制定有界单因子验证。当前不继续自动测试，不更改缓存策略或叠加EntityRef失败因子。源8c2/安装3e0ebb/原49删除/冻结HEAD保持，只提交Lab。G009和既有GAP不关闭，容量/Frontier不变、5000 Agents暂缓，无push/merge或validated生产tag。
