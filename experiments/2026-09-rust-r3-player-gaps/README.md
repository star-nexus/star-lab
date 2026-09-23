# R3d3a：Benchmark GAP台账、Player投影与数值兼容修复

**VALIDATED CHECKPOINT；完整R3/R4/R5仍OPEN。** 2026-09-23。

进度：`R0 █ | R1 █ | R2/R3 ▒ 功能迁移中 | R4 ░ | R5 ░`（不是工时百分比）。

主台账位于生产仓库 [docs/native-benchmark-gaps.md](../../../star-main/docs/native-benchmark-gaps.md)。记录已发生的差异、首次/实测版本、Benchmark影响、修复、仍开放项和证据；修复后不删除历史。VLM/BOT/网络host尚未迁移，不能作为可比性通过项。

## 问题与结果

| 问题 | 修复前Python/Rust | 修复后 | 影响 |
| --- | --- | --- | --- |
| G004死亡成员投影 | Rust权威已删死者，Python展示Player.units仍保留 | 36配置展示相等0/36→36/36；权威始终36/36 | 派生数据过期；本复现未改变权威战斗值 |
| G005 Unicode策略分 | Python接受`０.５`并累加0.5，Rust拒绝 | 完整响应/状态相等 | 确认改变策略评分 |
| G005 Unicode累计计数 | 字符串`１２`再加2；Python总14/成功率14.29%，Rust总2/100% | 完整响应/状态相等 | 确认改变评测统计 |
| G006对象转文字 | evidence对象`z,a`键顺序被Rust变成`a,z` | 仍不同，保留OPEN | 数值示例相同，文字记录不同，潜在评价器影响 |

Player初次给完整基线，之后只发被移除成员ID；没有每次死亡跨语言复制全部成员。保留Python第一个同阵营Player的规则。旧权威死亡路径仍有集合扫描，不声称全死亡处理O(active)。数字修复保持CPython3.13/Unicode15.1的Nd接受范围，68组680数字；不扩大为上标/圈号数字。无新依赖、无规则平衡变更。

1852完整回归（930 Native契约），新增114项：Player37、数值77；3Rust、fmt、Clippy通过。36配置为两模式×none/dummy/window×1/2/4设置×首次提取前/后死亡，3Unit小fixture、不绘制；raw保留全部初始状态、动作结果、权威/派生状态。Python/Rust权威差分直接断言，不是只比较最终计数。含重复Faction Player、reset/epoch、展示独立生命周期、空闲增量契约。

另跑原R3d2b场景探针：chibi-small/10Units/0Agents、两模式×三入口，237次场景更新（158窗口配置、79同Cocoa引擎里的headless配置），510操作节点及6初始快照独立精确重放，新进程重放通过。6JSON/6CSV与4PNG保存，回合menu截图检查沿用旧布局；不是物理输入或全GUI验收。模拟dt1/30，实时超时临时1秒、回合上限1，结算注入+61墙钟秒。初始菜单种子由现有菜单生成并完整记入trace；其他入口seed42。没有容量测量；Chrome保持开启，实验串行，1/2/4仍是串行Mutex。

## 精确版本

- before：`a6bf5f381b0393b0ab93973502d9744d6b9e3713` / API8 / tag `rust-kernel-r3d2b-2026-09-23`。
- 修复、构建、完整回归和全部after探针：`5e086be1160d49d148d09cfa6f3ee1743a3b8a1c`。
- 最终检查点：`a11c2b125cae451bcac6e3c3332bcbd65af24409` / annotated tag `rust-kernel-r3d3a-2026-09-23`。与测量节点仅GAP台账状态/证据文字不同，运行代码、测试完全相同，见`results/source-equivalence.json`。不为纯文档提交重复性能或功能测量。
- Player工具before `4c7f057f32633f0353286b2ac961474712a9499a`；数字/文字before工具 `b76302acf93f1c54de2c40fb0ecccdaf956ee5a1`；统一after工具 `39e2c374cce0c0e0b8e46fee2ce3142a5a1d9196`（Player工具未变；数值审计新增expect开关）。Cocoa/replay工具文件沿用Lab `2efdb7d6c4a2c7627f8ad033358e183b3fb23ac3`，本次运行的Lab HEAD为39e2c37。
- API9/schema5，oracle `python-r0c-3cc4ffe`。release扩展SHA `60a6a30e7e267e08140173e821a53b52fcde02222124ce3382a94d2fba153070`。
- Apple M4/16GiB/macOS26.5.2/CPython3.13.12；环境/锁SHA见`results/environment.json`。Linux/3.14尚未验收，Unicode版本变化需复核。

## 复现与使用

按下面路径操作，避免覆盖活动生产目录的49处无关Agent/font删除。工具也按精确SHA检出；输出目录使用新目录，不混写原数据。

```sh
cd /Users/liyang/Developer/star-main
git worktree add --detach /Users/liyang/Developer/star-lab/runs/repro-r3d3a 5e086be1160d49d148d09cfa6f3ee1743a3b8a1c
cd /Users/liyang/Developer/star-lab/runs/repro-r3d3a
uv sync --locked
uv pip install --python .venv/bin/python /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-player-gaps/artifacts/star_native-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
.venv/bin/python -m pytest -q
export PATH="$HOME/.cargo/bin:$PATH"
cargo test -p star-core -p star-rotk --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cd /Users/liyang/Developer/star-lab
git worktree add --detach runs/repro-r3d3a-tools 39e2c374cce0c0e0b8e46fee2ce3142a5a1d9196
cd /Users/liyang/Developer/star-lab/runs/repro-r3d3a
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3a-tools/tools/rust_migration/r3_player_projection_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3a --output /Users/liyang/Developer/star-lab/runs/repro-r3d3a-players
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3a-tools/tools/rust_migration/r3_gap_audit_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3a --output /Users/liyang/Developer/star-lab/runs/repro-r3d3a-gaps --expect-numeric-equivalence
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3a-tools/tools/rust_migration/r3_scene_host_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3a --output /Users/liyang/Developer/star-lab/runs/repro-r3d3a-window
.venv/bin/python /Users/liyang/Developer/star-lab/runs/repro-r3d3a-tools/tools/rust_migration/r3_scene_host_probe.py --source /Users/liyang/Developer/star-lab/runs/repro-r3d3a --output /Users/liyang/Developer/star-lab/runs/repro-r3d3a-replay --replay /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-player-gaps/results/window/trace.json.xz
```

before复现：另外检出a6bf5f3完整SHA，安装前一R3d2b目录的API8 wheel，运行同一Player工具及数字审计工具，后者去掉`--expect-numeric-equivalence`。预期Player36例全部派生不一致、权威全相等；三种边界输入均存在状态差异。`all_guards_passed`只表示成功复现预期现象；数字/文字审计明确 `migration_gate_passed:false`，after也保持false，因为G006仍未解决。

源码构建：在精确修复checkout执行 `uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /Users/liyang/Developer/star-lab/runs/repro-r3d3a-wheel`。本次设置 `CARGO_TARGET_DIR=/Users/liyang/Developer/star-main/target` 复用编译缓存；锁文件不变，maturin日志注明实际源码目录。

当前完整试玩checkout：`/Users/liyang/Developer/star-lab/runs/star-rust-r3-player-gaps`，已更新到最终文档节点并装API9。原R3d2b checkout/API8仍保留。离线试玩：

```sh
cd /Users/liyang/Developer/star-lab/runs/star-rust-r3-player-gaps
.venv/bin/python -m rotk_env.main --backend rust --no-hub --skip-start --mode real_time --scenario chibi-small --seed 42
```

默认Python、main仍6a970dea，未merge/push；所有合并继续要求tag后squash。Rust暂不支持Hub/BOT，空AI槽不会自主行动。

## 证据与下一步

`results/summary.json`为覆盖范围摘要；Player及输入审计各保留before/after compact+完整压缩raw；窗口原始trace及新进程重放独立归档。各raw的压缩和解压SHA/大小在compact和manifest中，所有小型证据在SHA256SUMS内。数值/文字审计是有意构造的有效负结果，不丢弃或伪装为普通通过样本。

下一步先修复G006并扩大宽松类型转换审计，再继续VLM、动态冷组件、网络host和BOT；随后R4真正并行/R5容量与安装验收。本文不声称既往真实LLM Benchmark分数已受影响：需要从对应版本输入日志审计；原main未合并Rust。

```sh
cd /Users/liyang/Developer/star-lab/experiments/2026-09-rust-r3-player-gaps
shasum -a 256 -c artifacts/SHA256SUMS
```
