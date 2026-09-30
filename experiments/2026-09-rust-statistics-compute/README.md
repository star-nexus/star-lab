# E2 — Statistics 批次计算并行研究与验收

**Status:** VALIDATED

**STAR repository:** `star-nexus/star`

**Problem commit:** `c058d75c0ad67a7c340c2a6ac74a9d5bc2888adf`

**Serial extraction:** `44c3696814b82d7c9d92a83ef7d160ef462168af`

**Experimental dispatch:** `7ab0ac1d97f5d68b8d81c505fa505a1cb234a56c`

**Fix / measured selected commit:** `2bc57d5f2241a578f61d71bb5774e7063a03ec25`

**Validated commit/tag:** `0aa28ac2ae0267048fcdb3998f9d76175ed4d699` / `rust-parallel-e2-statistics-2026-10-01`.


## 1. Problem

E1选择Statistics当前批次内部计算作为首个System并行点，但其健康算术、JSON记录、顺序提交及历史裁剪尚未分项。把整个System交给线程池会碰到旧Position/MP/Fog采样、组件插入、错误前缀和周期状态边界；小批次也可能被调度开销拖慢。

## 2. Why it matters

目标保持5000Units＋1000Agents，5000Agents暂缓。需要在不改变游戏规则、观测内容、动作接纳顺序或确定性的前提下证明完整step净收益，随后维持真实30Hz窗口与Agent队列门槛。Python保留接口、策略、显示及生态；Rust执行世界。默认线程数仍1。

## 3. Source checkout

```bash
git clone https://github.com/star-nexus/star.git
cd star
git fetch --all --tags
# 当前里程碑尚未push；从本实验artifact恢复到已克隆的生产历史。
git fetch /absolute/path/to/statistics-source.bundle refs/tags/rust-parallel-e2-statistics-2026-10-01:refs/tags/rust-parallel-e2-statistics-2026-10-01
git checkout 2bc57d5f2241a578f61d71bb5774e7063a03ec25
uv sync
env PATH="$HOME/.cargo/bin:$PATH" uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out dist
uv pip install --python .venv/bin/python dist/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
```

原测Apple M4/10逻辑核/16GiB，macOS26.5.2(25F84)、Python3.13.12、Rust/Cargo1.98.1、Bevy0.19.1、PyO3.29.2。精确源码、wheel/扩展、输入及工具哈希见manifest/各compact结果。异机重建可能有不同二进制哈希；记录实际身份，不强行复用原hash。

## 4. Environment

headless固定输入：`HEADLESS=1 SDL_VIDEODRIVER=dummy PYTHONHASHSEED=0`。窗口：`HEADLESS=0 SDL_VIDEODRIVER=cocoa PYTHONHASHSEED=0 PYTHONUNBUFFERED=1`，Chrome保持打开，不删除慢帧。

原窗口2480×1239，canonical固定场景、Fog开启、seed保留在initial/trace、30Hz固定模拟dt、1000独立闭环Agent、30秒思考＋±5秒jitter、post-action、selected权限、stochastic完整动作、8ms预算、realtime_defer GC、原公共信息／客户端完整解码／native-wire。现有p3_runtime启动实际生产入口，不额外运行并行负载。

## 5. Reproduce the problem

先解开本包raw及原R4e canonical输入。完整启动argv/cwd/env/UTC/exit见`results/serial-commands.json`、`parallel-commands.json`、`net-commands.json`、`selected-commands.json`。它们可直接复放；替换路径时保留全部参数。当前工具在Lab `69969a1713bb83d7e18fd4b05137276bc412cb72`，selected runner在 `87c1b99`，旧profile工具变体也通过git历史恢复。

旧P0 binary来自`2026-09-rust-system-attribution/artifacts/rust-system-attribution-raw.zip`内的wheel，extension SHA a73c477263d792cd0c4f71e3ab6001a36223cf0afd7136f8e8975f16b584731f。`--native-package`指向解包的star_native父目录，`--kernel-source-sha c058d75c0ad67a7c340c2a6ac74a9d5bc2888adf`明确区别包装层源码。旧P0、串行拆分、原型及正式策略均保留，不能用新实现自比替代独立基线。

```bash
# 在star-lab根；此A/B先checkout7ab0ac1并安装prototype wheel。
# 设置STAR为独立源码checkout、ROOT为本实验目录。
STAR=/absolute/path/to/star
ROOT=experiments/2026-09-rust-statistics-compute
# INPUT是解开的原R4e results/rust-300-r3.trace.json.gz所在目录。
INPUT=/absolute/path/to/r4e-input
HEADLESS=1 SDL_VIDEODRIVER=dummy PYTHONHASHSEED=0 "$STAR/.venv/bin/python" tools/rust_migration/profile_statistics_trace.py --source "$STAR" --source-sha 7ab0ac1d97f5d68b8d81c505fa505a1cb234a56c --extension-sha256 f84c9e8be6ebb616892e0625de4feb28647774065f0b25637720fbae0dd760df --trace "$INPUT/rust-300-r3.trace.json.gz" --trace-sha256 1f9b155129de9e43780c8885b40aba805e4c4794755fd2af70747058a7824b77 --mode plain --threads 4 --min-rows 1152921504606846976 --output "$ROOT/results/reproduce-inline.json"
# 同一原型binary、线程数及输入，仅将--min-rows改为128，另用输出名；交替3轮。
```

上例要求先checkout7ab0ac1并安装raw归档中的prototype wheel；不能把2bc57d5冒充实验原型。固定canonical contract输入在本raw包`inputs/contracts.json.gz`，不要重新生成后混作同输入。

## 6. Expected problem signature

串行分项中非空观测tick：平均125行，健康算术0.151µs而JSON构建154.005µs；trim107.958µs保留串行。合成1–32行强制并行平均更慢；64行开始平均正收益，但余量较小。整体step计时包含全部System；有计时孪生世界的compare模式只做等价/归因，不参与独立净收益对照。

## 7. Validate the fix

```bash
# 还原正式策略2bc57d5及selected wheel；安装后的extension SHA见manifest。
(cd "$STAR" && HEADLESS=1 SDL_VIDEODRIVER=dummy .venv/bin/python -m pytest -q --capture=sys)
# 在本Lab根；fresh输出目录避免覆盖已归档原始证据。
"$STAR/.venv/bin/python" tools/rust_migration/run_statistics_selected.py --source "$STAR" --source-sha 2bc57d5f2241a578f61d71bb5774e7063a03ec25 --extension-sha256 23dc7e4f5425e855a780a802d889f13bd28f300577688e66378ab574b7712d55 --trace "$INPUT/rust-300-r3.trace.json.gz" --contracts "$ROOT/inputs/contracts.json.gz" --root /absolute/path/to/fresh-e2-run
```

正式runner要求源码/Lab干净、已安装哈希正确的wheel、不覆盖既有结果；先1/2/4完整契约及普通step重放，再逐轮真实窗口。共享配置原始argv全部保留。3×(30预热＋300秒)不能用headless缩短替代。固定输入含原录制预热，所有9880step样本保留。

预期：36场景/174step的8种旧/新策略完整JSON字节相同；20次R4e重放输出流e01f2147b0fba41b27d15634c552bfb96ee84480a7628926890e57027a65b76b，最终状态d069c7173464d787c28f86120f1f173105f9f2c3f5cf959a758ab84290780dbf；三组同线程完整step均值/P99改善；2291Python、4Rust、fmt/Clippy通过。真实容量guard结果见comparison，不推断整帧因果收益。

## 8. Formal artifacts

`results/compute-comparison.json`汇总全契约、归因、净收益及门槛重算；`capacity-comparison.json`记录真实窗口；每点compact JSON保留hash/size/path。`results/packages.json`是canonical raw zip的成员/别名索引。8份字节相同完整契约只保留一份raw，原路径全部映射，旧报告/负对照均不覆盖。`SHA256SUMS`校验compact与原包。`artifacts/statistics-source.bundle`保存到validated tag的生产Git历史，基于可克隆的原Python6a970dea；无需依赖尚未push的分支恢复源码：在原生产仓库含该base时 `git bundle verify /path/to/statistics-source.bundle`，再 `git fetch /path/to/statistics-source.bundle refs/tags/rust-parallel-e2-statistics-2026-10-01:refs/tags/rust-parallel-e2-statistics-2026-10-01`。Python/编译日志、wheel、逐tick时延、完整contract输出、live原始帧/事件/输入/初始快照/截图均归档。

解包后可运行：
```bash
"$STAR/.venv/bin/python" tools/rust_migration/analyze_statistics_capacity.py --root "$ROOT"
"$STAR/.venv/bin/python" tools/rust_migration/analyze_statistics_compute.py --root "$ROOT"
```

## 9. Result summary

同7ab binary/同线程/同输入完整step，2线程三轮均值减少4.18–16.76%，4线程减少7.58–10.36%；每组P99也下降，max慢样本保留。完整当前批次才分块，不扫描全世界补任务。测得mean-positive64行，运行门槛128，默认1线程不变。三轮实际窗口均通过：帧P99 28.283/28.643/28.631ms，Hz 29.997/29.993/30.000；max帧91.923/102.449/32.239ms、worst5s P99 39.837/76.037/31.794ms均保留；peak movers180/173/173。不把局部收益写成整帧提升或5000Agents容量。

## 10. Related records

[manifest](manifest.yaml)、[analysis](analysis.md)、[decision](decision.md)、[恢复入口](../../records/rust-ecs-parallel.md)、生产`docs/native-statistics-parallel.md`/GAP台账、E1依赖/方案包、P0归因、R4e容量包。无新已确认规则GAP，G008/G009 OPEN、R001/R002 RISK均保留。原49项删除与两处冻结实验checkout保留。未push/merge。
