# P3 — 同步只读批次共享观测

**Status:** VALIDATED implementation / OPEN capacity  
**STAR repository:** `star-nexus/star`  
**Problem commit:** `08c857e5df39f671c5a13bf04b9af9aac0800e78`  
**Fix / measured commit:** `72e36414de7129a1046ce36861de18eb25b2d180`  
**Validated development tip:** `626d3a8db900fc18599bc96206bc76b960826999`  
**Validated tag:** `p3-read-batch-pre-squash-2026-09-09` → `626d3a8db900fc18599bc96206bc76b960826999`  
**Integrated main (squash):** `906386312d70d77af25e4b4da883f6dd5b0fe5ef`

## 1. Problem

每个 Agent 重建阵营公共观测，千 Agent 独立 1Hz 时大量请求积压。世界 30Hz 本身不能说明观测实时。

## 2. Why it matters

需要保留原有视野、合法动作、单位控制权限和事件次序，同时消除只读区间内的重复构建。

## 3. Source checkout

```bash
git -C /Users/liyang/Developer/star-main fetch --all --tags
git -C /Users/liyang/Developer/star-main worktree add --detach /Users/liyang/Developer/star-lab/runs/reproduce-read-batch 72e36414de7129a1046ce36861de18eb25b2d180
```

原始首版 `3017547a87360a667b6b6cb13def21d63b528399` 保留作负对照；开发 tip 仅在测量提交之后补充契约测试和文档。
完整工具 SHA 位于各 compact 的 tooling.sha；首版 `64cc1697f1c90bbfa5baa0f06b2e44eecc38191d`，修正版主矩阵 `edbe917`，补充归因 `eabf8e3b7e3c23848a27a95eb758c8294d80bc6d`。manifest 列出完整 SHA。

## 4. Environment

Python 3.13.12；真实窗口和 ENV 系统，世界目标30Hz；Chrome保持开启；seed42、canonical/interleaved、Fog ON、selected面板；GC realtime_defer。
精确平台、窗口、依赖锁、fixture SHA 见各结果。CPU任务串行，保留全部慢帧。

## 5. Reproduce the problem

在对应工具提交的 Lab checkout 中运行；先创建输出目录：

```bash
mkdir -p runs/reproduce-read-batch-results
/Users/liyang/Developer/star-main/.venv/bin/python tools/p3_runtime.py --source /Users/liyang/Developer/star-lab/runs/reproduce-read-batch --units 3000 --agents 1000 --delay 1 --observation-hz 1 --observation-mode batch-off --scope selected --policy move --seconds 15 --warmup 5 --budget-ms 12 --gc-policy realtime_defer --output runs/reproduce-read-batch-results/off.json > runs/reproduce-read-batch-results/off.log 2>&1
```

fixture工具从既有E8 canonical ZIP裁剪；归档内也保存每个精确fixture的单份ZIP。

## 6. Expected problem signature

3000/1000/1Hz batch-off 仅完成约11.9%的预定观测量，观测P99约17.6秒。短测仅重现过载，不是容量验证。

## 7. Validate the fix

保持上述命令参数，将 `batch-off` 改为 `batch-on`，输出名改为 `on`。另测 `single` 分离批次入口影响。
三路均进行stdlib JSON编码和客户端解码；历史第一轮没有解码成本，不能直接当作本轮公平基线。
独立进程冻结快照 oracle：

```bash
python tools/p3_batch_equivalence.py --source /path/to/checkout --output /tmp/oracle.json
```

生产起点和修正版得到逐字节相同的标准化JSON；修正版另验证逐条、关闭复用、开启复用逐字段一致。

## 8. Formal artifacts

本包保存完整工程诊断证据，**没有已通过的正式容量点**。
30个运行各有compact ZIP、raw ZIP（summary/raw/log）；首个 `3000-single` stdout 未保存为log，标为非受控试跑，受控基线使用 `3000-single-log`。
fixture按内容hash单份保存；冻结oracle单份保存。所有文件见manifest和SHA256SUMS。
所有raw ZIP已解包重算，compact中 reanalysis 与raw重算一致；原始散文件在验证后由canonical ZIP替代。

## 9. Result summary

| Point | World Hz | Frame P99 ms | Completed / offered | Observation P99 ms |
|---|---:|---:|---:|---:|
| [lazy-3000-single](results/lazy-3000-single.json) | 30.00 | 26.45 | 11.77% | 17613.64 |
| [lazy-3000-batch-off](results/lazy-3000-batch-off.json) | 30.00 | 26.42 | 11.89% | 17592.14 |
| [lazy-3000-batch-on](results/lazy-3000-batch-on.json) | 30.00 | 29.04 | 21.06% | 15245.78 |
| [lazy-3000-batch-on-d30](results/lazy-3000-batch-on-d30.json) | 30.00 | 28.94 | 34.25% | 13368.46 |
| [lazy-5000-batch-off](results/lazy-5000-batch-off.json) | 30.00 | 32.72 | 8.81% | 18151.92 |
| [lazy-5000-batch-on](results/lazy-5000-batch-on.json) | 30.00 | 31.21 | 14.03% | 17157.35 |
| [lazy-5000-batch-on-hz5](results/lazy-5000-batch-on-hz5.json) | 30.00 | 29.48 | 3.00% | 19298.01 |
| [lazy-5000-batch-on-hz10](results/lazy-5000-batch-on-hz10.json) | 30.00 | 30.25 | 1.50% | 19580.83 |
| [lazy-5000-batch-on-hz30](results/lazy-5000-batch-on-hz30.json) | 30.00 | 29.97 | 0.50% | 19765.06 |
| [lazy-10000-batch-off-a1000](results/lazy-10000-batch-off-a1000.json) | 28.60 | 43.16 | 3.48% | 19233.07 |
| [lazy-10000-batch-on-a1000](results/lazy-10000-batch-on-a1000.json) | 29.53 | 38.48 | 2.95% | 19294.42 |
| [lazy-10000-batch-on-a5000](results/lazy-10000-batch-on-a5000.json) | 30.00 | 35.95 | 0.60% | 19751.50 |
| [lazy-10000-batch-on-a10000](results/lazy-10000-batch-on-a10000.json) | 30.00 | 36.03 | 0.30% | 19823.10 |
| [lazy-combat-batch-on](results/lazy-combat-batch-on.json) | 30.00 | 36.77 | 51.27% | 10028.94 |

所有点15s测量+5s预热，均未达容量门槛。300s+三次60s认证没有启动，因为目标规模的短测已经严重过载。

## 10. Related records

- [manifest](manifest.yaml)、[analysis](analysis.md)、[decision](decision.md)
- [恢复入口](../../records/10k-online-resume.md)
- [预先批准方案](../../records/10k-online-p3-read-batch-plan.md)
