# Cached coordinate overlay and active combat text

2026-09-10。已实现坐标/伤害数字/CRIT缓存修复，生产规则和按键不变。

- [分析](analysis.md)、[决策](decision.md)、[版本/环境/归档身份](manifest.yaml)。
- [旧版对照](results/baseline.json)、[修复版](results/fixed.json)、[自然闭环](results/live.json)。
- 问题来源：[上一轮诊断](../2026-09-text-render-probe/README.md)；本轮重新测量旧版，并确认地图缓存已稳定，未混用此前预热不足的P99。

## 版本

问题源码`906386312d70d77af25e4b4da883f6dd5b0fe5ef`。
修复/测量源码`5f13218ea1b6cf563e94b61e30a1609f01c2a138`，分支`codex/cached-combat-coordinate-text`。
测量工具`b93139777ef65d3abf5f7aae41a99e180930b81c`。
合并采用annotated tag钉死开发节点后squash；操作节点见manifest和恢复入口。
已集成main `6a970deaee7d9b8d3939edd102973f2377edd6ac`，唯一parent为问题源码9063863，树与测量源码相同；tag `p3-text-cache-pre-squash-2026-09-10`指向5f13218。
Chrome保留开启，实验串行，未剔除任何准入窗口慢帧。没有新增Frontier或千Agent容量认证。

## 复现

取回STAR和Lab仓库，给STAR源码建立两个Lab内的worktree，然后在源码worktree运行`uv sync`。

```bash
git -C /path/to/star fetch --all --tags
git -C /path/to/star worktree add --detach /path/to/star-lab/runs/star-text-base 906386312d70d77af25e4b4da883f6dd5b0fe5ef
git -C /path/to/star worktree add --detach /path/to/star-lab/runs/star-text-fixed 5f13218ea1b6cf563e94b61e30a1609f01c2a138
```

测量使用对应工具SHA。以下是原始完整命令，位于Lab根目录执行；请按机器替换Python/source路径，三个运行串行。

```bash
mkdir -p runs/p3-text-cache/baseline runs/p3-text-cache/fixed runs/p3-text-cache/live
/Users/liyang/Developer/star-main/.venv/bin/python tools/p3_text_probe.py --source /Users/liyang/Developer/star-lab/runs/star-p3-clock24 --mode replay --settle-frames 120 --samples 100 --repeats 2 --cases zoom1_empty,zoom1_coordinates,zoom05_empty,zoom05_coordinates,zoom05_pan,damage1000,offscreen1000,hidden1000 --output runs/p3-text-cache/baseline/replay.json > runs/p3-text-cache/baseline/replay.log 2>&1
/Users/liyang/Developer/star-main/.venv/bin/python tools/p3_text_probe.py --source /Users/liyang/Developer/star-lab/runs/star-text-cache-dev --mode replay --settle-frames 120 --samples 100 --repeats 2 --cases zoom1_empty,zoom1_coordinates,zoom05_empty,zoom05_coordinates,zoom05_pan,damage1000,offscreen1000,hidden1000 --output runs/p3-text-cache/fixed/replay.json > runs/p3-text-cache/fixed/replay.log 2>&1
/Users/liyang/Developer/star-main/.venv/bin/python tools/p3_text_probe.py --source /Users/liyang/Developer/star-lab/runs/star-text-cache-dev --mode live --seconds 60 --warmup 30 --output runs/p3-text-cache/live/live.json > runs/p3-text-cache/live/live.log 2>&1
```

8条件×2轮×100测量帧；每条件先120帧坐标OFF让地图缓存稳定并检查overscan job完成且zoom匹配，随后10帧文字预热，再测100帧。初次开启cold_activation单独保留（每条件2个冷样本，报告max，不称冷启动P99）。开始另有60帧预热。
连续平移为zoom0.5时每帧向右1px，属于动态视图诊断。replay的世界delta0且不pump Agent；实际5000Units和1000已注册认领Agent仍驻留，不能把它称为持续5000Move。
live是24Hz固定模拟时钟、30±5秒墙钟思考（15–45秒截断）、canonical、move/attack/wait50/25/25、single/selected、18ms Agent预算、GC realtime_defer。工具设置`STAR_SCALE_MINIMAP_UNITS=off`。

## 回归与归档复核

```bash
python -m pytest -q
python tools/run_performance_contracts.py
```

生产全量912通过，结构契约94通过；包括13个新增文字缓存用例。
Lab收尾版本提供以下归档/复算工具（测量完成后再运行）：

```bash
python tools/p3_text_cache_archive.py --input runs/p3-text-cache --case experiments/2026-09-text-render-cache
python tools/p3_text_cache_archive.py --input runs/p3-text-cache --case experiments/2026-09-text-render-cache --verify
cd experiments/2026-09-text-render-cache
shasum -a 256 -c artifacts/SHA256SUMS
```

`--verify`只从归档ZIP解包，复算全部统计和冷样本，对齐live帧序号并重新核验runtime raw SHA及汇总；也检查compact内容等于results。fixture沿用上一轮canonical5000的相同SHA ZIP，manifest引用该唯一副本。

## 预期签名

旧版zoom0.5坐标路径约720ms；修复后静止视图仅一次overlay提交，路径P99约0.008ms，连续平移约2.83ms。修复冷首次开启整帧最大约37.08ms（本机/本配置的少量冷样本）。
1000条可见飘字的文字准备P99约2.54→0.97ms，屏幕外约2.93→0.36ms。完整帧含其他系统和像素提交，不等于局部路径用时。
