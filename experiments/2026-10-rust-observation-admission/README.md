# E8：已接纳观测只读段复用

状态：P0 执行中。算法和停止条件见 [方案](../../records/rust-observation-admission-plan.md)。

## Reproduction

起点产品 `5b9658bc668b7d13f801351162f255f30622b32a`；先执行 `tools/rust_migration/test_observation_admission_probe.py`，再运行 `observation_admission_probe.py`。确切命令随本轮证据归档。冻结原 P3 工具，使用独立诊断适配器。

## Evidence and limits

[P0 预注册](results/p0-preregister.json) 固定身份、目标、原闭环及内存政策。诊断窗口不用于提速、容量或 Frontier 结论；E6/E7 研究默认关闭，已有 GAP 保留。
