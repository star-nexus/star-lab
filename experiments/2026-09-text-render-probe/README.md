# 坐标与伤害/CRIT飘字的渲染归因

2026-09-10；诊断已完成，未实施生产修复。

**坐标标签是已复现的严重渲染瓶颈；当前5000U/1000A自然闭环负载中的少量飘字不是整帧P99的主要来源。**

- [分析与限制](analysis.md)、[决策](decision.md)、[精确身份](manifest.yaml)。
- [渲染对照compact数据](results/replay.json)、[自然闭环与慢帧归因](results/live.json)。
- 原始逐帧数据、全部慢帧和日志保存在各自raw ZIP；compact ZIP含默认阅读数据和raw SHA/size。
- 不更新Performance Frontier，不宣称新的容量认证；生产source未改，默认FPS未改。

## 源码与环境

STAR `906386312d70d77af25e4b4da883f6dd5b0fe5ef`；测量工具SHA见manifest。
Macmini M4/16GB，macOS26.5.2，Python3.13.12，实际窗口2480×1261，Chrome保持开启。
实验使用Lab中的detached生产worktree，不把生成地图放入生产工作目录。

在新机器取回生产仓库后：

```bash
git -C /path/to/star fetch --all --tags
git -C /path/to/star worktree add --detach /path/to/star-lab/runs/star-p3-clock24 906386312d70d77af25e4b4da883f6dd5b0fe5ef
cd /path/to/star-lab/runs/star-p3-clock24
uv sync
```

Lab工具依赖已归档的E8地图，由`fixture()`生成canonical5000地图。此地图和上一轮24Hz案例完全同SHA，manifest指向已有canonical fixture ZIP，不重复归档。

## 完整测量命令

在测量工具SHA对应的Lab checkout根目录执行；按本机路径替换Python/source。
两条命令必须串行，测量期间不运行压缩/重型测试。工具自身设置`STAR_SCALE_MINIMAP_UNITS=off`。

```bash
/Users/liyang/Developer/star-main/.venv/bin/python tools/p3_text_probe.py --source /Users/liyang/Developer/star-lab/runs/star-p3-clock24 --mode replay --samples 100 --repeats 2 --output runs/p3-text-probe/replay.json > runs/p3-text-probe/replay.log 2>&1
/Users/liyang/Developer/star-main/.venv/bin/python tools/p3_text_probe.py --source /Users/liyang/Developer/star-lab/runs/star-p3-clock24 --mode live --seconds 60 --warmup 30 --output runs/p3-text-probe/live.json > runs/p3-text-probe/live.log 2>&1
```

先创建`runs/p3-text-probe`目录以供shell重定向。replay有13种条件×2轮×100测量帧；60初始预热帧，每条件10预热帧，条件顺序seed42随机。
5000单位/1000已注册认领Agent保持驻留；replay不pump Agent且delta=0，只用于隔离渲染成本，不能当作持续Move/Attack运行。
live复用上一轮24Hz固定模拟时钟、30±5秒墙钟思考、move/attack/wait=50/25/25、18ms Agent预算、Fog ON、canonical、single/selected、GC realtime_defer。

## 打包与重新核验

分析/归档工具保存在本案例收尾提交（不是历史测量SHA）：

```bash
python tools/p3_text_archive.py --input runs/p3-text-probe --case experiments/2026-09-text-render-probe
python tools/p3_text_archive.py --input runs/p3-text-probe --case experiments/2026-09-text-render-probe --verify
cd experiments/2026-09-text-render-probe
shasum -a 256 -c artifacts/SHA256SUMS
```

`--verify`只读取已归档ZIP，不依赖input目录里的原始文件；逐个解包、重算全部probe汇总、独立重算runtime指标和raw SHA，再与compact数据精确比较。

## 预期问题特征

zoom1约577格：坐标路径P99约171ms；zoom0.5约2379格：约727ms。zoom0.15直接跳过标签。
自然闭环同时飘字最大11，文字准备P99约0.054ms，整帧P99约43ms。
具体帧耗时会受平台和系统活动影响；未定义修复后签名，因为尚未实施修复。
