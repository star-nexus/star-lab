# E1 — ECS System 间与 System 内并行方案探索

**Status:** VALIDATED — dependency design and synthetic mechanisms only

**STAR repository:** `star-nexus/star`

**Problem / measurement commit:** `c058d75c0ad67a7c340c2a6ac74a9d5bc2888adf`

**Fix commit:** N/A; production execution unchanged

**Validated design commit:** `be3867b3ad65749e0e34efd245359c4123189031`

**Validated design tag:** `rust-parallel-e1-design-2026-09-30`

进度：`访问审计 █ | 锁定API探针 █ | 方案选择 █ | 生产原型 ░ | 容量 ░`。
目标仍5000 Units＋1000 Agents；5000 Agents暂缓。按用户最新指示，本阶段探索
ECS内部并行。P0跨请求只读批次候选保留在原实验，不再作为当前首个原型。

## 1. Problem

Runtime::step仍按顺序调用取得整体可变Runtime的方法。仅将这些方法包成
System或将Runtime放入单一可变Resource，无法让调度器识别窄读写集，也无法保留
原错误后的部分写入与阶段中止。需要同时识别真实规则依赖、接口造成的互斥和
当前成本，才能选择实现点。

## 2. Why it matters

并行计算不得改变旧Position/MP/Fog采样、活动索引、空间跨格、结构修改、事件、
缓存LRU、动作即时生效或RNG顺序。5000常驻实体并不意味着每tick处理5000个实体。
[完整读写/成本表](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-system-dependencies.md)
和[设计矩阵](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-ecs-parallel-design.md)
在生产设计commit中；本包保存选择路线的机制与成本证据。

## 3. Source checkout

在一个新的复现目录执行；不改原开发/冻结工作树：

```bash
git clone https://github.com/star-nexus/star.git star
git -C star fetch --all --tags
git -C star checkout c058d75c0ad67a7c340c2a6ac74a9d5bc2888adf
git clone https://github.com/star-nexus/star-lab.git star-lab
git -C star-lab checkout adf399f96db5beef6427caba4ec83c491424755e
uv sync --project star
cargo fetch --locked --manifest-path star/Cargo.toml
```

上述SHA为本地精确检查点，本阶段未push。异机使用前须取得这些Git对象和Lab
归档，可从本机Git bundle/仓库副本获取；若远端尚无对象，不能用移动分支替代。
源工作树必须干净。工具会校验source SHA、锁定所有直接依赖，并确认探针解析的
每个包名/版本/source都出现在源Cargo.lock中。

## 4. Environment

Mac mini M4/16 GiB，macOS26.5.2 arm64，Rust/Cargo1.98.1，Python3.13.12，
Bevy ECS/tasks0.19.1，release＋thin LTO＋codegen-units1。
`results/environment.json`记录版本和相关环境变量；无覆盖。
Python仅编排编译/分析，未启动游戏或Python世界。探针无随机seed、Fog、地图、
相机或Agent。P0成本来源是原R4e seed42、5000/1000固定输入，包括录制预热。
runner把本机cargo路径加到PATH前；异机需让cargo在PATH中。

## 5. Reproduce the problem / mechanism

此处没有窗口或网络服务；runner编译一个隔离二进制，随后依次启动五个独立进程。
从上述复现目录执行：

```bash
star/.venv/bin/python star-lab/tools/rust_migration/run_ecs_parallel_probe.py \
  --source "$PWD/star" \
  --source-sha c058d75c0ad67a7c340c2a6ac74a9d5bc2888adf \
  --output "$PWD/ecs-e1-reproduction"
star/.venv/bin/python star-lab/tools/rust_migration/analyze_ecs_parallel_probe.py \
  --probe-results "$PWD/ecs-e1-reproduction" \
  --p0-raw "$PWD/star-lab/experiments/2026-09-rust-system-attribution/artifacts/rust-system-attribution-raw.zip" \
  --output "$PWD/ecs-e1-analysis"
```

原执行命令和cwd保存在`results/commands.json`。编译日志、原JSON和解析锁在raw包。
每个进程分别初始化池，避免全局池首初始化影响线程变量；这不证明生产实例的
线程预算/生命周期正确。不能同时运行多个计时进程。

## 6. Expected signature

| Probe | threads=1 | threads=2 | threads=4 |
|---|---:|---:|---:|
| 窄MovePoints/Vision两个System最大同时执行数 | 1 | 2 | 2 |
| 同MovePoints写入 | 1 | 1 | 1 |
| 同Resource不同字段写入 | 1 | 1 | 1 |
| 独占World与组件System | 1 | 1 | 1 |
| 唯一活动子集，常驻5000/选中100/实际变化100 | pass | pass | pass |
| 已有ReadPool返回5000有序输出，与串行整数结果相等 | N/A | pass | pass |

所有命令退出0、all_passed=true，分析器也必须all_passed=true。
2ms人为等待只为观察System重叠，不计作性能证据。活动子集只证明合法访问与结果，
不证明线程参与或实际游戏System等价性。100预热＋1000次空作业dispatch保留所有
采样；median/P99可因机器变化，不作为跨机器通过阈值。

## 7. Validate the design / re-audit archived output

设计commit相对measurement只修改三份生产文档。未重跑生产回归或构建wheel；
没有宣称真实System并行通过。P0已有2239Python/4Rust回归只属于P0。

从Lab根目录用归档raw重算到临时目录：

```bash
python3 tools/rust_migration/analyze_ecs_parallel_probe.py \
  --probe-results experiments/2026-09-rust-ecs-parallel-design/artifacts/ecs-parallel-design-raw.zip \
  --p0-raw experiments/2026-09-rust-system-attribution/artifacts/rust-system-attribution-raw.zip \
  --output /tmp/ecs-e1-reanalysis
cmp /tmp/ecs-e1-reanalysis/comparison.json experiments/2026-09-rust-ecs-parallel-design/results/comparison.json
cmp /tmp/ecs-e1-reanalysis/overlap-ceiling.json experiments/2026-09-rust-ecs-parallel-design/results/overlap-ceiling.json
cd experiments/2026-09-rust-ecs-parallel-design
shasum -a 256 -c artifacts/SHA256SUMS
```

源设计阅读可另checkout validated design tag，不能拿它冒充measurement SHA。
真实原型须先串行拆分等价性、再同输入1/2/4完整响应/展示/权威状态及首错部分写入
对照，最后真实5000/1000窗口验收。详见decision和生产设计第6节。

## 8. Formal artifacts

默认阅读`results/comparison.json`、manifest、analysis、decision；
`results/packages.json`含compact/raw名称、字节数与SHA256。
raw保留全部调度输出、dispatch1000样本、构建日志、解析锁、环境和命令；
compact保留所有决策数值与raw逐文件hash。P0原始timings只引用其规范raw，不复制。
最初旧版API路径的编译失败发生在工作负载前，按PROTOCOL不列为正式负结果/GAP。

## 9. Result summary

Recovery/Lifecycle/Vision拆窄访问后是System间候选；Statistics/Motion/Vision等
可拆出内部纯计算。当前P0时间下，三者理想零开销重叠节省mean3.883µs/P9913.292µs；
另外空作业调度median2线程9.125µs/4线程7.084µs。两者是不同工作负载的诊断，
不能相减成实际净收益。Statistics当前批次平均0.167297ms，为首个串行拆分与
分项测量对象；不是已经证明可加速的0.167297ms。

## 10. Related records

- [Manifest](manifest.yaml)、[Analysis](analysis.md)、[Decision](decision.md)
- [恢复入口](../../records/rust-ecs-parallel.md)
- [P0规范归因](../2026-09-rust-system-attribution/README.md)
- [R4e规范容量](../2026-09-rust-1000-agent-validation/README.md)
