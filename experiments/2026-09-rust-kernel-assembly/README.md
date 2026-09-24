# R3k3 — Rust观测JSON装配：转交已拥有的数据

**Status: VALIDATED 内核检查点，完整迁移/容量仍未完成。** 生产 `star-nexus/star`；problem `67e35deaacef22ed1754f39245d771c3af887888`，fix/measurement `450bf97db4c52ead5d5ab36eda5a035a33ee4158`，validated `a3ff47b796537e2a543d42da6094aa13d64f6e63`，annotated tag `rust-kernel-r3k3-2026-09-24`。最终仅两份文档变化，代码/测试与测量节点一致。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 内核补齐中 | R4 ░ | R5 ░`（非工时百分比）。仍只推进Rust世界执行/观测计算；Python保留SDK、策略、网络/ACK、UI与报告。

## 1. 问题与影响

地形、敌军、reachable、Unit面板数组和批次结果已构造成JSON值，原代码装入外层对象时又通过`json!`的serialize-to-Value路径递归重建同样的树。除必要共享副本外，多做数组/对象/字符串分配和复制，载荷和请求数放大这部分成本。

新实现仅把已拥有的`Vec<Value>`转交给最终容器；保持所有字段、对象插入顺序、列表次序、独立返回生命周期和读写边界。仍需要独立响应的公共事实/Unit面板复制继续保留；不是零复制接口，也不是跨帧缓存。不新增依赖/API字段/线程调度。

## 2. 环境与工作负载

Mac mini M4/16GiB/macOS26.5.2、CPython3.13.12、Rust1.98.1 release，Chrome开启、实验串行；dummy环境、无渲染。复用R3k1/R3k2唯一raw中的3个场景：100静止Units/6211地块/7格视野或关闭Fog、5000静止Units/射程3/关闭Fog。seed42，MP0；前两者查询5个己方Units，后者查询100个己方Units。

每场景1或8请求，每请求独立注册一个合成身份；分别走handler probe和真实可信动作批次入口。注册/reset导入不计时。每项预热1次、测5次，固定墙钟元数据；包含native查询/鉴权/批次统计与JSON编码（handler没有鉴权/统计），排除Python解码、世界tick、渲染、网络、排队和LLM。每次样本reset到同一已注册状态，保留全部样本。

## 3. 前后结果

| 场景 | 入口 | 请求数 | 旧中位ms | 新中位ms | 旧/新 |
| --- | --- | --- | --- | --- | --- |
| terrain-local | handler | 1 | 0.188 | 0.125 | 1.50× |
| terrain-local | public | 1 | 0.206 | 0.137 | 1.51× |
| terrain-local | handler | 8 | 0.744 | 0.290 | 2.56× |
| terrain-local | public | 8 | 0.760 | 0.343 | 2.21× |
| terrain-disabled | handler | 1 | 29.105 | 17.838 | 1.63× |
| terrain-disabled | public | 1 | 32.413 | 17.525 | 1.85× |
| terrain-disabled | handler | 8 | 99.552 | 55.400 | 1.80× |
| terrain-disabled | public | 8 | 100.544 | 54.464 | 1.85× |
| units-5000 | handler | 1 | 50.414 | 30.086 | 1.68× |
| units-5000 | public | 1 | 52.232 | 30.815 | 1.70× |
| units-5000 | handler | 8 | 175.864 | 101.202 | 1.74× |
| units-5000 | public | 8 | 173.365 | 95.241 | 1.82× |

可信接口5000Unit单请求52.232→30.815ms，8请求173.365→95.241ms。后者仍须完整返回约6.04MB，超过单帧预算；这些数字**不是5000Units+1000Agents的30Hz容量验收**，也不说明1000请求可同时处理。5样本仅为受控局部诊断，不宣称统计显著性；跨阶段旧数字不能替代本次同条件before。

## 4. 验证与GAP

2144完整回归、62针对性、3Rust/fmt/Clippy通过；旧6场景510节点重放通过。复用现有差分和独立结果生命周期契约，没有另写镜像实现的测试。12组新旧初始/最终状态hash、完整响应（含diagnostic metrics）、输出字节长度一致，实际解压后的完整结果逐项比较一致。public批次另与同内核逐条执行结果和最终状态比对；所有观测与原归档handler响应一致。回归包含Python差分、1/2/4线程参数、none/dummy/window、跨阵营/越权、混合写入和reset/close。

未发现新增机制差异，[生产GAP台账](../../../star-main/docs/native-benchmark-gaps.md)已记录边界。G008/G009应用接入和R001/R002风险仍开放。API14/schema5、oracle不变；源码与扩展SHA区分旧/新API14，不把兼容版本号当作性能版本标识。

## 5. 复现

工具固定到Lab `864f01ad2764aa387b3b472a096e3572cd070911`；两个仓库平级。下面为源码和归档wheel复现，工具路径应指向该Lab节点的checkout。

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-kernel-assembly 450bf97db4c52ead5d5ab36eda5a035a33ee4158
cd /Users/liyang/Developer/star-lab/runs/repro-kernel-assembly
uv sync --locked --python 3.13
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-kernel-assembly/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/kernel_observation_assembly_probe.py --source . --output /Users/liyang/Developer/star-lab/runs/repro-kernel-assembly-results
```

旧版用生产 `67e35deaacef22ed1754f39245d771c3af887888` 和R3k2归档wheel，运行相同工具。精确构建/安装/测试/原始A/B命令及环境覆盖在`results/commands.json`，固定源身份在manifest；环境与已安装扩展SHA在`results/environment.json`。两份canonical输入/旧轨迹不重复复制，manifest记录路径与checksum。raw保存实际请求、完整结果、每次样本；初始/最终状态以hash守卫，初始世界由引用raw与工具中的固定注册流程完整重建。

```sh
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-kernel-assembly
shasum -a 256 -c artifacts/SHA256SUMS
```

## 6. 当前可用版本与接续

生产venv和完整目录`runs/star-rust-kernel-assembly`已安装匹配release，扩展SHA `a36e0684f4e76b7b4036e6ca20b217d1f5a78dda11929f7a9a714afd090a7c74`。旧R3k2目录/wheel保留；生产原49处删除保留，main仍6a970dea，未merge/push，默认Python。

下一步继续针对剩余共享事实复制与完整JSON编码做成本拆分，核验能够借用稳定只读上下文的响应表示和批次生命周期，再实施真正的观测并行。权威状态写入审计仍需继续；Python网络/ACK/BOT策略集成单列。5000Units+1000Agents/30Hz/约30秒闭环与5000Agents扩展均未完成验收。
