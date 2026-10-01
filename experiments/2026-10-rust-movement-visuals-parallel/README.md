# E5：Movement 与 Visuals 的 System 之间并行

状态：E5研究完成。安全重叠机制及四模式验证通过；native2/4均未通过稳定净收益门槛，普通step不启用E5，无新live/容量结论。

目标为 5000 Units＋1000 Agents，5000 Agents 暂缓。E4 保守负筛选只适用于
Vision∥Recovery/Lifecycle，不能否定本轮另一种实际重叠。

代码起点：72bf05a2f6ec6d1d15ffad7914226c0c3e16b9cf；测量代码：
94913a4f836a3c106e08a1334cb81971cfd728c3；validated：
3b167b151c3bc32e1d54f6015d0f15d2c3dd6a74（native代码相同，仅补测试和文档）。Annotated tag：
`rust-parallel-e5-movement-visuals-2026-10-02`。

实现次序：Clock→Statistics 成功→窄准备→worker Visuals∥caller Movement→join
→原序结构提交→Recovery→Lifecycle→Vision→Capture。worker 不借用可变 ECS。
Visuals maps 转移所有权，泛型访问适配器复用原阶段算法，主线程原序执行
Spawn/Remove；expected error 提交同样的成功前缀，panic 两侧 join 后返还 maps。

主门槛固定8条浮字，native2/4各三轮逐 tick ABBA/BAAB；同一parallel模式与
usize::MAX禁用门槛比较。100-tick 分块、10000 bootstrap、seed42；每轮完整
step均值改善、P99不回退且配对改善95%区间为正。P99使用两侧各19760个
原始step样本，CI使用9880个tick的配对均值。全部预热tick和慢尾保留。

四模式分别为 baseline / empty_fork / split_serial / parallel，均为按次私有
推进。普通step、默认native1、API18/schema5、Python生态和动作顺序保持。

原始输入沿用E3恢复链；正确性边界输入在本轮raw中冻结，不依赖再次生成时
的墙钟。所有full response、presentation/event流及final state检查完整；
逐步完整state/error/delta在13个边界场景×29step中核对。

## 通俗结论

让Visuals在后台计算、同时让主线程推进Movement，确实能同时做事，而且没有改变游戏状态、展示或错误顺序；但每tick可重叠的工作较小，完整step收益在不同轮次不够稳定。2/4线程都只有一轮达到预设门槛，其他门槛的单轮信号也未被置信区间确认，所以保留研究接口、默认继续原序执行。此结论限定本机、当前5000Units/1000Agents轨迹和本轮方案，不代表所有System并行方案都无价值。

进度：`依赖/窄接口 █ | 四模式/等价 █ | 净收益/敏感性 █ | 条件停止/决策 █ | 归档/校验 █`。

## 恢复与复算

使用独立checkout。首先按[E3恢复链](../2026-10-rust-internal-system-candidates/README.md)
获取E2/E3源码，再fetch E4 bundle获取72bf05a；本轮bundle的前置commit为72bf05a。
源码节点均未push，不能假定远程已有tag。取得前置节点后：

```bash
git fetch /Users/liyang/Developer/star-lab/experiments/2026-10-rust-movement-visuals-parallel/artifacts/movement-visuals-source.bundle refs/tags/rust-parallel-e5-movement-visuals-2026-10-02:refs/tags/rust-parallel-e5-movement-visuals-2026-10-02
git switch --detach 94913a4f836a3c106e08a1334cb81971cfd728c3
uv sync --python 3.13.12
```

下面以源码checkout为`/tmp/e5-star`、Lab为原路径、空恢复目录为`/tmp/e5-evidence`：

```bash
/tmp/e5-star/.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/prepare_movement_visuals.py --experiment /Users/liyang/Developer/star-lab/experiments/2026-10-rust-movement-visuals-parallel --work-dir /tmp/e5-evidence
uv pip install --python /tmp/e5-star/.venv/bin/python --force-reinstall /tmp/e5-evidence/wheels/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
/tmp/e5-star/.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/analyze_movement_visuals.py --runs /Users/liyang/Developer/star-lab/experiments/2026-10-rust-movement-visuals-parallel/artifacts/movement-visuals-raw.zip --output /tmp/e5-evidence/recomputed-analysis.json
```

prepare校验整包和全部成员，恢复E4/E3/R4e输入链及本轮准确边界输入、两种binary。
它只写指定恢复目录，不安装、不修改任何冻结目录。复算analyzer只读raw；输出应与
`results/analysis.json`字节一致。canonical输入不重新生成：测试夹具包含墙钟字段，
重生成工具用于新增研究，不替代已归档输入。复算无需重新跑耗时轨迹。

重测完整序列（先完成正确性检查，不同时运行测试、其他benchmark或打包）：

```bash
HEADLESS=1 SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 /tmp/e5-star/.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/run_movement_visuals.py --source /tmp/e5-star --inputs /tmp/e5-evidence/e4/e3/inputs --output /tmp/e5-new-run --source-sha 94913a4f836a3c106e08a1334cb81971cfd728c3 --extension-sha256 838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544
```

该入口串行跑27个完整报告：1拆分正确性、12主/拆分配对、8四模式诊断、6门槛敏感性。
每报告40994request/9880step/9880presentation；配对报告包含4个独立世界。
任何assert失败都不算正式性能结果。成功的全部慢样本保留，无预热或尾部裁剪。

完整错误前缀/state/delta合同复现，用归档的`/tmp/e5-evidence/inputs/contracts.json.gz`
调用`movement_visuals_contracts.py`；mode选择ordinary（加`--native-package
/tmp/e5-evidence/e4/candidate`及旧扩展9c7eebe…）或本轮四模式，threads1/2/4，指定
`--source /tmp/e5-star --input <上述input> --output <新文件> --extension-sha256
<manifest对应完整hash>`。原始所有13条完整argv见`results/contract-commands.json`，
不用猜参数；每组输出gzip应为相同checksum，各13case/377step。

如需重新构建而非使用准确wheel，在94913a4 checkout执行：

```bash
PATH=/Users/liyang/.cargo/bin:$PATH uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /tmp/e5-rebuilt-wheels
PATH=/Users/liyang/.cargo/bin:$PATH cargo test --locked -p star-core -p star-rotk
PATH=/Users/liyang/.cargo/bin:$PATH cargo clippy --locked -p star-core -p star-rotk -p star-python --all-targets -- -D warnings
HEADLESS=1 SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 .venv/bin/python -m pytest -q
```

私有调用不是dry run，会推进世界。PROFILE=false返回`null`。metadata中的历史字段
`ordinary_step_summary`在本工具中指private推进调用；配对报告该字段P99为配对均值，
**正式P99门槛始终取`paired_raw`两侧各19760个未平均原始样本**。完整mean/CI/P99决策
以`results/analysis.json`为准，不能用该历史摘要替换门槛。

合同完整示例（相同input，每种mode和threads按results中的argv展开）：

```bash
HEADLESS=1 SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 /tmp/e5-star/.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/movement_visuals_contracts.py --source /tmp/e5-star --input /tmp/e5-evidence/inputs/contracts.json.gz --output /tmp/e5-evidence/new-parallel-t4.json --mode parallel --threads 4 --extension-sha256 838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544
HEADLESS=1 SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 /tmp/e5-star/.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/movement_visuals_contracts.py --source /tmp/e5-star --input /tmp/e5-evidence/inputs/contracts.json.gz --output /tmp/e5-evidence/new-e4.json --mode ordinary --threads 1 --native-package /tmp/e5-evidence/e4/candidate --extension-sha256 9c7eebe03257d1d6941e67b5e31a947e4c6cedf32db6979e624629fd5cf5dd91
```

测量checkout94913a4的测试签名为2342Python/6Rust；validated checkout3b167b1
增加3项多段移动/GameOver/Vision专项，完整签名2345Python/6Rust。二者native源码相同。

## System读写与成本边界

| System | 读 | 写 | 顺序/并行边界 |
|---|---|---|---|
| Clock | dt/config | clock/revision/singleton | 先于Statistics |
| Statistics | 旧Position/MP/Fog/current batch | observation/history/visibility/counts | 成功后才能准备并行区 |
| Movement | Movement/Position/map | Position值/animation/spatial/dirty/moving | 不改变Position存在性或external ID计数 |
| Visuals compute | Position存在性/next ID/owned maps/raw dt | owned maps/有序Spawn-Remove journal | 与Movement计算重叠，不访问World |
| Visuals publish | journal成功前缀 | World结构/InitialComponents/unit membership/Visuals | join后，Recovery前，原序提交 |
| Recovery | clock/components/deadlines/new IDs | AP/MP/SP/index/dirty | 在Visuals完整发布后 |
| Lifecycle | clock/mode/rules/living | GameState/GameOver event | 在Recovery后、Vision前 |
| Vision | 新Position/Vision/terrain/rules | cache/Fog/Vision/presentation | 原序，GameOver仍执行 |
| Capture | 新Position/capture/ownership | capture/ownership/events | 原序；错误保留前序提交 |

成本表（诊断全tick均值µs；不能直接当净收益）：

| System | native2 | native4 |
|---|---:|---:|
| clock | 1.071 | 0.898 |
| statistics | 147.732 | 128.982 |
| movement | 39.866 | 33.672 |
| visuals | 11.061 | 10.049 |
| recovery | 4.715 | 4.241 |
| lifecycle | 0.613 | 0.462 |
| vision | 50.671 | 46.206 |
| captures | 0.088 | 0.069 |

本轮仅新增System之间的计算重叠；System内部并行继续E2 Statistics，跨请求只读共享继续已有观测segment机制，E5未改它们。更细的四模式成本和同tick掩码见analysis及results/matched-diagnostic-costs.json。

13份逐步合同raw逐字节一致，raw包只存contracts/contracts-canonical.raw.json.gz，contract-aliases.json保存所有原输出名和checksum映射；不丢任何变体证据。

诊断成本canonical复算：

```bash
/tmp/e5-star/.venv/bin/python /Users/liyang/Developer/star-lab/tools/rust_migration/movement_visuals_diagnostic_costs.py --raw /Users/liyang/Developer/star-lab/experiments/2026-10-rust-movement-visuals-parallel/artifacts/movement-visuals-raw.zip --output /tmp/e5-evidence/recomputed-diagnostic-costs.json
```

输出应与results/matched-diagnostic-costs.json字节一致。收益上限用movement_visuals_cost_bounds.py
的--e3-raw指向E3 canonical ZIP、--output指定新文件，输出与results/ideal-bounds.json一致。

E4完整源码恢复命令（在E2/E3 bundle已经fetch后）：

```bash
git fetch /Users/liyang/Developer/star-lab/experiments/2026-10-rust-between-system-parallel/artifacts/between-systems-source.bundle refs/tags/rust-parallel-e4-dispatch-screen-2026-10-02:refs/tags/rust-parallel-e4-dispatch-screen-2026-10-02
```

本轮raw约15.9MB、compact约21KB，exact bytes/SHA见manifest和results/artifact-index.json。
normal review从README/analysis/decision及compact机器数据开始；raw保留全部低层样本，
compact不替代raw。源码bundle也由SHA固定，恢复前置为72bf05a。
