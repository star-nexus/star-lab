# 决策：R3b 功能检查点

**状态：接受检查点，完整迁移未完成。** 日期 2026-09-13。源码 `d5abc70e9cda8a6820546112e6172dd9e43c1515`，tag `rust-kernel-r3b-2026-09-13`。

## 1. 选择

五种非图像观测由 Rust 读取权威世界并构造结果；共用逐 Unit 基础事实。保留每种投影各自字段、权限、动作选项与错误语义。先规范化 Python 两处坐标列表，再以 R0c 对照，不让跨语言实现猜测 Python 集合布局。

## 2. 缓存与导入边界

具名观测只复用同世界 revision 的结果。公开 from_cache 和快照墙钟时间导致有效缓存也是重放状态的一部分，故 bootstrap/export 携带有效条目，reset 使用新 scene 的条目。返回值拥有独立生命周期；Python 只在确定的 visible_area 字段还原 set，不对用户任意 metadata 做通用标记解释。

不采用 TTL/上一帧投影，不借迁移修复旧 godview 战报属性，也不统一历史 display 模式差异。API/schema=4、oracle=python-r0c-3cc4ffe；旧 tag/wheel 留在原实验可重放。

## 3. 依据与权衡

1443 回归和 4203 节点差分/重放支持本阶段兼容性。缓存完整输出仍有内存、JSON 装配和复制成本；本轮没有速度优胜参数，不作 headroom 或最少线程结论。实际线程池与 O(active) 优化留 R4。

## 4. 下一节点

优先真实窗口所需的战斗展示事件、派生展示数据、输入命令与 VLM 截帧，然后 BOT/结算。全部 R3 功能可用后再进入 R4 和 R5。Python 默认/main 不变；最终按 annotated tag + squash 规则集成。

## 5. 重新评估条件

观测接口/缓存键/世界写边界改变时重跑本归档；引入并行必须保持动作 M→查询 Q→动作 N 顺序和列表一致。窗口接入后增加真实行为/图形检查；容量及 CPython3.14/Linux wheel 需独立完成。

[复现](README.md)、[身份](manifest.yaml)、[证据分析](analysis.md)。
