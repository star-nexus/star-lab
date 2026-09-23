# R3d3b — 保留输入对象顺序与Python Unicode文字表示

**Status: VALIDATED checkpoint; 完整迁移仍OPEN。**
生产修复/测量 `11aefce1fb498cd6b388b1dcf498dbd8529eafb0`；最终 `24215823c74a79774d38cc0b354b6e3d091a3b86`，annotated tag `rust-kernel-r3d3b-2026-09-23`。最终只改GAP台账，代码/测试相同，见source-equivalence。工具 `5f75250bf98a76e1f3dc85c994ddf009348db425`；问题节点 `a11c2b125cae451bcac6e3c3332bcbd65af24409`。

迁移进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（█完成、▒进行中、░待实施/验收；非工时百分比）。

## 1. 问题与意义

G006：被接受的字典在Rust解析时按键排序，策略依据、嵌套对象、第二次统计上报的provider/model标签转成不同文本。G013：非打印Unicode字符在列表/字典repr中没有Python转义。它们是持久化文本差异，不能因为JSON对象通常忽略键序而忽略；例子数值策略分相同，未证明真实LLM排名变化。详见[主GAP台账](../../../star-main/docs/native-benchmark-gaps.md)。

## 2. 环境与身份

M4/16GiB/macOS26.5.2、CPython3.13.12/Unicode15.1、Rust1.98.1，API10/schema5，oracle=python-r0c-3cc4ffe。release扩展SHA `214b864f854a6fda64b0c56226bac15f9e8babc2ded28cea9195184311001d77`。环境、锁文件SHA和全部验证命令见environment.json与commands.json。Chrome保持开启；编译/正式验证串行。默认Python；main仍6a970dea，无merge/push；活动目录原49处删除未触碰。

## 3. 精确复现

路径按生产/Lab同级组织。以下均创建新checkout，不覆盖现有实验。API9 before wheel使用上一阶段唯一归档，API10使用本目录归档。

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3d3b-before a11c2b125cae451bcac6e3c3332bcbd65af24409
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3d3b-after 11aefce1fb498cd6b388b1dcf498dbd8529eafb0
cd /Users/liyang/Developer/star-lab
git worktree add --detach runs/repro-r3d3b-tools 5f75250bf98a76e1f3dc85c994ddf009348db425
cd /Users/liyang/Developer/star-lab/runs/repro-r3d3b-before
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-player-gaps/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3b-tools/tools/rust_migration/r3_gap_audit_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3b-before --output /Users/liyang/Developer/star-lab/runs/repro-r3d3b-before-results --expect-numeric-equivalence --extended-text-audit
cd /Users/liyang/Developer/star-lab/runs/repro-r3d3b-after
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-text-order/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3b-tools/tools/rust_migration/r3_gap_audit_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3b-after --output /Users/liyang/Developer/star-lab/runs/repro-r3d3b-after-results --expect-numeric-equivalence --extended-text-audit --expect-text-order --expect-unicode-repr
.venv/bin/python -m pytest -q
export PATH="$HOME/.cargo/bin:$PATH"
cargo test -p star-core -p star-rotk --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3b-tools/tools/rust_migration/generate_unicode_repr.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3b-after --check
```

从源码构建：在after checkout执行 `CARGO_TARGET_DIR=/Users/liyang/Developer/star-main/target uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /Users/liyang/Developer/star-lab/runs/repro-r3d3b-wheel`。安装新wheel后必须新建Python进程。完整窗体验证/Player/新旧重放命令位于results/commands.json，可替换输出目录后逐条运行；历史trace使用原归档，不重复复制。

## 4. 预期反例与修复签名

before：7组均响应相等；三组映射文字及一组Unicode文字权威状态不同，3组数值/float对照相同。after：7组响应与完整状态全部相同。工具的migration_gate_passed始终false，表示完整迁移还未验收，不能解释为这7组失败。

| 检查 | 结果 |
| --- | --- |
| G006普通/嵌套依据/累计标签 | 0/3→3/3状态相同 |
| G013不可打印Unicode依据 | 不同→相同 |
| Unicode数值2例、float文字1例 | 3/3→3/3 |
| 完整回归 / Native / 新增文字契约 | 1897 / 975 / 45 |
| Rust单测 / fmt / Clippy / Unicode表核验 | 3 / 通过 / 通过 / 通过 |
| Player投影，权威与展示 | 36/36，36/36 |
| 旧场景重放 / 新场景及独立重放 | 各510节点、6场景 |

45个新契约覆盖排序、截断、first raw→second text、导出/reset、1/2/4设置、浮点文字对照，以及Unicode可打印性边界的公开动作转换。线程设置仍串行，不能当作并行验收。

## 5. 证据与范围

before/after各一份完整压缩raw及compact，窗口trace一份，4PNG、6JSON/6CSV报告。新六场景237次更新：158窗口配置，79在同Cocoa引擎中的headless场景，不冒充独立dummy验收；合成SDL事件/直接回调，不冒充物理输入。看过turn_based-menu.png，旧HUD重叠保留。无吞吐/容量结论，无VLM/BOT/网络兼容结论。

```sh
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-text-order
shasum -a 256 -c artifacts/SHA256SUMS
```

## 6. 当前使用与下一步

完整试玩目录 `runs/star-rust-r3-text-order` 已固定最终节点并安装API10；活动生产venv也安装匹配release扩展。旧API9目录和旧tag仍保留。离线启动：

```sh
cd /Users/liyang/Developer/star-lab/runs/star-rust-r3-text-order
.venv/bin/python -m rotk_env.main --backend rust --no-hub --skip-start --mode real_time --scenario chibi-small --seed 42
```

无BOT时AI槽不会自主行动。接下来继续VLM、动态冷组件覆盖、网络host/回合ACK/结束投递及BOT；R001宽松输入风险保持开放。完成完整R3后才进入R4真并行及R5容量/平台安装。没有提前切默认后端或合并main。

[manifest](manifest.yaml) · [analysis](analysis.md) · [decision](decision.md)
