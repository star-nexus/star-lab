# E6：展示数据与 ECS 缓存优化研究

状态：研究完整归档。优先候选reuse_typed通过固定输入收益门槛；普通路径仍关闭。
六次实际窗口对照整体未全通过（baseline第二轮超限），不声称容量提高。

进度：`基线/归因 █ | 契约/实现 █ | 完整等价 █ | 三轮收益 █ | 条件窗口 █ | 恢复/校验 █`。

## 先读

[结论与限制](decision.md) → [成本、缓存契约和完整对照](analysis.md) →
[机器可读分析](results/paired-analysis-complete.json) → [源码/环境/证据身份](manifest.yaml)。
恢复入口为[并行交接](../../records/rust-parallel-handoff.md)；下一项为显示链路准备成本。

## 源码与环境恢复

产品起点 `4657dd474c3b69eb849e11d30f32587ebb21bb70`；实现5f567d3、完整测量 `0a297a868f589dd49eb514f3c73402142df05e2c`；
验证源码 `068c1ecd17988ac6d884984e904aea924968e0ae` / `rust-parallel-e6-presentation-cache-2026-10-02`。最后节点仅增加文档，执行代码与测量节点相同。
原49项删除、冻结目录、E2/E3/E4/E5标签保留，未push/merge。

E6 source.bundle依赖E5验证3b167b1；先按
[E5 README](../2026-10-rust-movement-visuals-parallel/README.md)恢复此前bundle链，随后：

```bash
git bundle verify "$LAB_ROOT/experiments/2026-10-rust-presentation-cache/artifacts/presentation-cache-source.bundle"
git fetch "$LAB_ROOT/experiments/2026-10-rust-presentation-cache/artifacts/presentation-cache-source.bundle" refs/tags/rust-parallel-e6-presentation-cache-2026-10-02:refs/tags/rust-parallel-e6-presentation-cache-2026-10-02
git checkout --detach 0a297a868f589dd49eb514f3c73402142df05e2c
uv sync --frozen
```

使用macOS arm64、CPython3.13。准确版本见results/environment.json；AppleM4 10核/10线程16GB，
macOS26.5.2，Python3.13.12、Pygame2.6.1、NumPy2.3.2。未绑定CPU亲和性。
沿用完全相同的E5 wheel，API18/schema5。不要把重新构建但哈希不同的wheel冒充原测量扩展。

```bash
unzip "$LAB_ROOT/experiments/2026-10-rust-presentation-cache/artifacts/presentation-cache-raw.zip" -d "$E6_RAW_ROOT"
uv pip install --python .venv/bin/python --force-reinstall "$E6_RAW_ROOT/wheels/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl"
mkdir -p "$E6_INPUT_ROOT"
unzip -j "$LAB_ROOT/experiments/2026-09-rust-1000-agent-validation/artifacts/r4e-1000-agents-raw.zip" results/rust-300-r3.trace.json.gz results/rust-300-r3.initial.json.gz -d "$E6_INPUT_ROOT"
```

确认扩展SHA256=838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544。
原完整trace并非完整展示payload；本轮由ordinary Rust重生成9880份delta，全部载荷在
artifacts/presentation-cache-deltas.jsonl.gz（独立重新读取、事件校验见results/regenerated-delta-verification.json）。

## 执行与预期签名

变量LAB_ROOT/SOURCE_ROOT/E6_INPUT_ROOT/E6_RUN_ROOT为本机绝对路径，不复用系统HOME变量。
完整原始argv和环境由results/commands.json及各run元数据记录。使用新的空E6_RUN_ROOT，
否则runner可能复用已存在的结果。正式执行只改变consumer模式，无每帧World复制。

```bash
PYTHONHASHSEED=0 "$SOURCE_ROOT/.venv/bin/python" "$LAB_ROOT/tools/rust_migration/run_presentation_cache.py" --source "$SOURCE_ROOT" --source-sha 0a297a868f589dd49eb514f3c73402142df05e2c --inputs "$E6_INPUT_ROOT" --output "$E6_RUN_ROOT"
```

此入口依次执行native1/4完整正确性、6组Cocoa像素、12组三轮ABBA/BAAB、分析，
只在门槛通过时执行native4单实例ABBA和实时窗口。原测量Lab节点72445ab；精确tools源快照
在raw ZIP tooling/72445ab/tools，旧控制与补充分项版本亦保留。若需独立恢复tools，
将该tools树放入新的干净Git目录（git init/add/commit），其新Lab SHA必须如实记录；
逐文件哈希应与artifact-index一致，不能声称新Git SHA等于历史Lab SHA。

预期完整输入每实例40994请求/9880tick/9880presentation；输出流SHA e01f2147…，
最终权威状态SHA d069c717…，完整值见correctness元数据。两个线程配置的像素流一致；
普通apply与起点AST一致。边界回归：

```bash
cd "$SOURCE_ROOT"
PYTHONHASHSEED=0 .venv/bin/python -m pytest -q
.venv/bin/python "$LAB_ROOT/tools/rust_migration/check_presentation_retention.py" --source "$SOURCE_ROOT" --output "$E6_RUN_ROOT/retention.json"
```

实测2385回归通过；完整保留构造/替换的模式apply约慢2–3%，typed约改善44–46%。
不同机器或新的时段可能改变P99，必须重新满足同一门槛，不能只复算旧结论当新容量。

独立完整分项（验证节点只有文档变化）：

```bash
git checkout --detach 068c1ecd17988ac6d884984e904aea924968e0ae
PYTHONHASHSEED=0 .venv/bin/python "$LAB_ROOT/tools/rust_migration/presentation_cache_probe.py" --source "$SOURCE_ROOT" --source-sha 068c1ecd17988ac6d884984e904aea924968e0ae --trace "$E6_INPUT_ROOT/rust-300-r3.trace.json.gz" --output "$E6_RUN_ROOT/diagnose-complete-t1.json" --task diagnose --threads 1 --driver cocoa --archive-deltas
```

该诊断带探针，不参与速度门槛；旧完整成本和真实窗口诊断独立保留。正式性能仍保留
渲染器1.5ms构建预算。像素校验使用固定条目配额，仅用于相同渲染进度下的内容契约。

## 复算与完整性

解压raw后，复制两个原始R4e输入到解压的raw目录，使用当前analyzer复算：

```bash
.venv/bin/python "$LAB_ROOT/tools/rust_migration/analyze_presentation_cache.py" --runs "$E6_RAW_ROOT/raw" --output "$E6_RUN_ROOT/recomputed.json"
cd "$LAB_ROOT/experiments/2026-10-rust-presentation-cache"
shasum -a 256 -c artifacts/SHA256SUMS
cd "$E6_RAW_ROOT"
shasum -a 256 -c SHA256SUMS
```

复算结果应与results/paired-analysis-complete.json一致。raw ZIP保留全部样本、慢尾、Cocoa帧hash、
完整窗口负结果、控制失败与tests日志；compact为默认阅读入口，载荷与raw不相互替代。
输入/R4e和wheel/E5的canonical来源各自SHA验证。未对任何失败轮次补跑择优。
