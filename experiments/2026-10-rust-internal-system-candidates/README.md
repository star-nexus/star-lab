# E3：其他 System 内部并行候选

**Status:** VALIDATED research；未新增并行执行策略。

**STAR:** star-nexus/star；问题起点0aa28ac2ae0267048fcdb3998f9d76175ed4d699。

**测量/validated:** 6d4018cc0c607a51a3783428867ba9259bb43f43；执行fix N/A。

**最终文档:** ad02b75f2b83f97fe0bef4c1c9eee5742b1610fb；代码/测试与测量相同。

**Annotated tag:** rust-parallel-e3-internal-attribution-2026-10-01。

进度：`边界审计 █ | 分项归因 █ | 完整等价 █ | 条件排序 █ | raw/compact/复算 █`。

## 1. Problem

E2只并行Statistics的当前批次记录构建。需要识别其余System内部哪些纯计算值得继续分离，避免将整个System阶段成本错误地视作可并行预算。

## 2. Why it matters

目标5000Units＋1000Agents，保持规则/观测/动作/RNG/ID/提交确定性；5000Agents暂停。Rust执行世界，Python保留接口与生态。减少不必要派发、世界复制和提交重排，比扩大线程覆盖更重要。

## 3. Source checkout

源码节点与tag尚未push，使用bundle恢复，不假定远程已有节点。在含原main6a970dea的STAR clone执行（路径按实际Lab checkout设置）：

```bash
git fetch /Users/liyang/Developer/star-lab/experiments/2026-09-rust-statistics-compute/artifacts/statistics-source.bundle refs/tags/rust-parallel-e2-statistics-2026-10-01:refs/tags/rust-parallel-e2-statistics-2026-10-01
git fetch /Users/liyang/Developer/star-lab/experiments/2026-10-rust-internal-system-candidates/artifacts/system-candidates-source.bundle refs/tags/rust-parallel-e3-internal-attribution-2026-10-01:refs/tags/rust-parallel-e3-internal-attribution-2026-10-01
git checkout 6d4018cc0c607a51a3783428867ba9259bb43f43
uv sync
```

采用独立checkout；原用户49删除和冻结测量目录不作为恢复工作区。E3增量bundle要求E2的0aa28ac2已存在。原始E2 wheel和canonical inputs复用原案例单一位置；manifest提供archive/member/hash。

## 4. Environment

Mac mini M4/10逻辑核/16GiB，macOS26.5.2/25F84，Python3.13.12、Rust/Cargo1.98.1、maturin1.15.0、Bevy0.19.1、PyO3 0.29.2，Release。原5000Units/1000Agents、seed42、120×120、Fog、30Hz、post-action30±5秒截断15–45等输入原样保存；在headless重放，包括录制预热。没有启动Cocoa/新live agent host，也没有CPU affinity。

## 5. Reproduce the problem

完整原始构建/回归命令见`results/validation.json`，完整4重放＋4契约argv/env见`results/commands.json`；工具测量checkpoint和每文件SHA见manifest。如下恢复输入与Apple arm64 wheel中的原包，不改变venv安装：

```bash
cd /Users/liyang/Developer/star-lab
/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/.venv/bin/python tools/rust_migration/prepare_system_candidates.py --experiment experiments/2026-10-rust-internal-system-candidates --work-dir runs/ecs-e3-reproduction
```

另一个STAR checkout可用其Python替换上述解释器。先检出6d4018c，再在Lab运行以下完整重放（STAR变量必须指向上述checkout；OUT用新scratch，避免覆盖归档）：

```bash
LAB=/Users/liyang/Developer/star-lab
STAR=/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main
OUT="$LAB/runs/ecs-e3-reproduction"
for THREADS in 1 2 4; do
  HEADLESS=1 SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 "$STAR/.venv/bin/python" "$LAB/tools/rust_migration/profile_system_candidates.py" --source "$STAR" --source-sha 6d4018cc0c607a51a3783428867ba9259bb43f43 --trace "$OUT/inputs/rust-300-r3.trace.json.gz" --trace-sha256 1f9b155129de9e43780c8885b40aba805e4c4794755fd2af70747058a7824b77 --extension-sha256 e0f46cfbffd8542c08cd2b2e6b4a26c000da05ecb9bffd3466d77fa859a9834d --native-package "$OUT/candidate" --kernel-source-sha 6d4018cc0c607a51a3783428867ba9259bb43f43 --output "$OUT/candidate-t$THREADS.json" --threads "$THREADS" --mode compare
done
HEADLESS=1 SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 "$STAR/.venv/bin/python" "$LAB/tools/rust_migration/profile_system_candidates.py" --source "$STAR" --source-sha 6d4018cc0c607a51a3783428867ba9259bb43f43 --trace "$OUT/inputs/rust-300-r3.trace.json.gz" --trace-sha256 1f9b155129de9e43780c8885b40aba805e4c4794755fd2af70747058a7824b77 --extension-sha256 23dc7e4f5425e855a780a802d889f13bd28f300577688e66378ab574b7712d55 --native-package "$OUT/baseline" --kernel-source-sha 2bc57d5f2241a578f61d71bb5774e7063a03ec25 --output "$OUT/baseline-e2-t1.json" --threads 1 --mode plain
```

源版本6d4018c构建命令为`env PATH="/Users/liyang/.cargo/bin:$PATH" uvx --from maturin==1.15.0 maturin build --release --locked --manifest-path native/python/Cargo.toml --interpreter .venv/bin/python --out /Users/liyang/Developer/star-lab/runs/ecs-e3-build/wheel`，工作目录STAR。wheel/extension hashes用于区分二进制；不同平台或编译器重建需要记录新的binary身份，不能冒称原正式测量。

## 6. Expected problem signature

旧E2 binary能通过相同完整流，但profile只有既有phase/statistics，无法判断LOS或行循环/提交分项。新E3提供candidates分项；4轮均all_passed，stream e01f2147b0fba41b27d15634c552bfb96ee84480a7628926890e57027a65b76b、final d069c7173464d787c28f86120f1f173105f9f2c3f5cf959a758ab84290780dbf，9880step、40994request、9880presentation。成本无需逐纳秒相同，计数/流/最终状态必须相同。

## 7. Validate the research

执行旧E2=1与新E3=1/2/4契约的原命令见commands，输入SHA11b33c95…；每变体36case/174step、完整raw SHA9db82664…与E2 canonical相同。回归见validation。无需重复所有重放即可复算已归档证据：

```bash
cd /Users/liyang/Developer/star-lab
/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/.venv/bin/python tools/rust_migration/analyze_system_candidates.py --experiment experiments/2026-10-rust-internal-system-candidates --output runs/ecs-e3-reanalysis.json
cd experiments/2026-10-rust-internal-system-candidates
shasum -a 256 -c artifacts/SHA256SUMS
```

analyzer从canonical raw读取/验每成员SHA、重新计算candidate_summary/所有派生值，及跨E2完整流/合同身份。2315Python/4Rust/fmt/Clippy/Release通过；没有新执行fix，所以没有before/after净收益或live容量门槛。

## 8. Formal artifacts

默认阅读本目录README/manifest/analysis/decision和results/analysis.json、validation、isolation、commands、packages。compact ZIP为这些决策级内容的便携快照；raw ZIP保存全部逐tick计时/step、4重放和契约metadata、wheel与测试日志，所有慢样本保留。两个包的SHA/bytes由packages.json索引。相同合同raw只引用E2 canonical，输入只引用R4e/E2，避免重复。源码bundle也有SHA和base prerequisite。

## 9. Result summary

| System | 首轮阶段均值µs | 有效候选证据 | 决策 |
|---|---:|---|---|
| Vision | 43.504 | geometry0.553；commit28.169；三配置几何占比1.27–1.37% | 当前保持串行；条件优先大批冷几何，当前先关注串行提交/表示 |
| Movement | 31.049 | 行处理乐观上界5.359；活动平均122.47/峰186 | 条件候选更多同时移动单位 |
| Visuals | 9.315 | 四阶段循环上界8.135；damage6.843、平均6.66/峰28行 | 条件候选大批同阶段更新，保留栅栏 |
| Recovery | 3.887 | 到期组2.370、峰24条；最大阶段是新ID审计 | 暂缓；大量同桶到期再研究 |
| Lifecycle/Capture/Clock | 小标量/无捕获活动 | 增量索引、缺捕获样本 | 不扩大覆盖；捕获先补合法负载 |

以上为诊断成本，loop上界不是纯kernel；三个配置不是新增内部并行A/B。当前没有足够证据启用另一项System并行。System之间与跨请求共享仍分别沿原E1/P0路线，未在本阶段实施。E2 Statistics继续有效；E2 live三轮容量仅指原binary，不扩展E3容量/Frontier。G008/G009/R001/R002不关闭，5000Agents暂停；原删除/冻结目录完整保留；未push/merge。

## 10. Related records

[analysis](analysis.md)、[decision](decision.md)、[manifest](manifest.yaml)、[恢复入口](../../records/rust-ecs-parallel.md)、[生产边界/成本表](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-internal-system-candidates.md)、[GAP](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-benchmark-gaps.md)。E1/P0/E2/R4e历史证据保持不可覆盖；最新E3恢复状态优先于其旧“下一候选”。
