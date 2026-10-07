# STAR Lab

> 下一项E8：已接纳观测只读段复用方案已制定，保留逐请求顺序与预算，复用已有ObservationBatch事实。仅方案，尚未实施/测量；先验证合法段与最小净收益。见[算法方案](records/rust-observation-admission-plan.md)与[阶段台账](records/rust-observation-admission-status.json)。

> E7 P3完成并独立复核：24次全部执行，23次计时有效、1次无效保留。候选empty_territory在7个完整分层未通过原收益门槛、1个分层证据不足，保持关闭；未进入窗口或默认接入。见[决策汇总](experiments/2026-10-rust-display-preparation/results/p3-decision-summary.json)和[恢复入口](records/rust-parallel-handoff.md)。

以下E7条目为历史阶段快照，当前状态以上述结果为准。

> E7 P3最新：用户授权资源干扰后继续原剩余13组；前10组有效，第11组干扰保留且不计收益，不重跑。见[接续修订](experiments/2026-10-rust-display-preparation/results/p3-continuation-20261007.json)。

> E7最新（2026-10-07）：P2完整4/4保持，用户授权开启P3。串行24组完整轨迹，原门槛、driver与分析不改，压力暂停的运行整体无效且保留。见[P3预注册](experiments/2026-10-rust-display-preparation/results/p3-preregister-20261007.json)。

> E7最新（2026-10-07）：**P2完整通过4/4并归档**，每组40994请求/9880tick，全权威/展示/命令/像素与原始证据内外SHA独立复核完成，临时跟进已暂停。仅为正确性验收，P3性能测量尚未开始，默认尚未启用。见[完整结果](experiments/2026-10-rust-display-preparation/results/p2-complete.json)与[复核记录](experiments/2026-10-rust-display-preparation/results/p2-integrity-review.json)。

> E7最新（2026-10-07）：用户授权第四组重新执行且取消自动退出。压力仅暂停现场、normal一分钟后继续，6GiB仅监测参考；前三组复用，P2仍3/4。见[恢复配置](experiments/2026-10-rust-display-preparation/results/p2-pause-only-resume.json)。

> E7最新（2026-10-07）：P2仍3/4。已验证warning时暂停并恢复同一活进程的新守护；不支持恢复已退出的8500tick现场，未重启完整重放，旧runner未接入。见[方法控制](experiments/2026-10-rust-display-preparation/results/p2-pause-guard-control.json)与[恢复入口](records/rust-parallel-handoff.md)。

> E7最新（2026-10-07）：P2完整通过3/4；第四组6GiB重试在8500里程碑后由系统warning策略停止，跟进暂停。[证据](experiments/2026-10-rust-display-preparation/results/p2-fourth-retry-interruption.json)，[恢复入口](records/rust-parallel-handoff.md)。

> E7最新（2026-10-06）：P2完整通过3/4；第四组于20:32再次由系统warning策略停止，跟进已暂停。[中断证据](experiments/2026-10-rust-display-preparation/results/p2-fourth-interruption.json)，[恢复入口](records/rust-parallel-handoff.md)。

> E7最新（2026-10-05）：P2仍为2/4；重启后第三组再次触发系统压力守护，自动跟进已暂停。[中断证据](experiments/2026-10-rust-display-preparation/results/p2-reboot-interruption.json)与[恢复入口](records/rust-parallel-handoff.md)。

**Engineering evidence, reproducibility, and scalability records for [STAR / StarBench](https://github.com/star-nexus/star).**

STAR Lab is intentionally separate from the production/runtime repository.

- `star-nexus/star` is the product and benchmark repository. Users should normally use `main` there.
- `star-nexus/star-lab` is the engineering research archive: reproducible problem reports, controlled experiments, raw evidence, root-cause analyses, engineering decisions, and the historical STAR Performance Frontier.

The core rule is simple:

> Every important engineering conclusion must be traceable from the claim, to raw evidence, to a reproducible experiment, to an exact `star` commit or immutable tag.

## Start here

For the active 10K work, read [the recovery entry](records/10k-online-resume.md).
[P0 archive and exact-source recovery](archives/2026-09-10k-p0/README.md) preserve retired experiments.

1. Read [`PROTOCOL.md`](PROTOCOL.md) before adding a formal experiment.
2. Create new experiment packages from [`templates/`](templates/).
3. Preserve only evidence that supports a durable engineering conclusion.
4. Bind every formal experiment to exact `star-nexus/star` commit SHA(s); never rely on a moving branch name alone.
5. Update [`records/performance-frontier.md`](records/performance-frontier.md) only for validated frontier results.

## Repository layout

```text
star-lab/
├── README.md
├── PROTOCOL.md
├── templates/
│   ├── experiment-readme.md
│   ├── manifest.yaml
│   ├── analysis.md
│   └── decision.md
├── experiments/
├── investigations/
├── decisions/
└── records/
    └── performance-frontier.md
```

## Version roles

```text
star branch       = active work line
star checkpoint   = temporary comparison / debugging baseline
star annotated tag= validated immutable engineering milestone
star-lab          = reproducible evidence and decision history
```

STAR Lab does not maintain a production source fork. The P0 archival bundle preserves retired experiment refs for recovery. It has its own Git history and references STAR source states through exact commit SHAs and tags.
