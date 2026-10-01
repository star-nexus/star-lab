# E4：System 之间并行派发预算

状态：已完成并验证派发筛选负结果（2026-10-02）。起点 E3 ad02b75，阶段一测量源码 dede5ca，固定已有 R4e 完整输入，不改规则、观测、动作顺序或确定性。默认1，普通 step 不启用此机制。最终选择保守停止，不进入Vision拆分；诊断数据不是实际并行净收益。

进度：`边界/理想预算 █ | scoped负对照 █ | 完整ABBA █ | 等价/决策 █ | canonical归档 █`。

先测 baseline/empty_fork。匹配 tick 的派发开销耗尽理想预算则保守停止，后续 split_serial/parallel/window 标记未进入，不伪造四模式结果。未耗尽才继续串行拆分和真实并行验证。派发区诊断 residual 为 fork_region−Recovery−Lifecycle，包含额外计时开销，仅用于阶段筛选；诊断关闭的完整 step ABBA 是独立外部对照，所有轮次和矛盾结果保留。

候选只覆盖 native2/4、realtime/window/indexed、bootstrap/Fog 存在、Vision dirty 和 Recovery 活动。后台任务为空，调用线程保持 Recovery→Lifecycle→Vision→Capture。最多一个 worker＋caller，复用实例 ReadPool，scope 内捕获两侧 panic、join 后重新抛出。

## 复现入口

1. 按 E3 的 `prepare_system_candidates.py` 恢复 canonical R4e trace/initial 与 E2 contracts、E3 preserved wheel；校验链见 E3 manifest。
2. checkout 本轮 manifest 的 exact measurement SHA；按 results/validation.json 命令构建 release 并安装到该活动 checkout 的 venv，不修改冻结目录。
3. 按 results/commands.json 的每条 argv 顺序执行，在新 checkout 中替换绝对本机根路径；每条运行检查源码、扩展及 trace/initial hash。baseline/empty_fork 两个模式都走同一私有 FFI，性能关闭诊断。
4. 用 `analyze_between_systems.py --replays <raw.zip> --e3-archive <E3 canonical raw.zip> --output <analysis.json>` 仅从 checksum-verified canonical ZIP 复算。

精确输入轨迹为40994请求、9880tick、9880展示，包含录制预热；旧 live 负载5000Units/1000Agents/30Hz，峰 movers186。当前是 headless 固定输入研究，不是新容量或整帧验收。

## 固定结果与恢复链

源码测量 `dede5ca0ca3472abdb1d24589878e6a72d812f88`；validated `a7508bce4b900ccf8465e761291adb7e7e2ce98d`（只补测试，native代码相同）；最终文档 `72bf05a2f6ec6d1d15ffad7914226c0c3e16b9cf`。Annotated tag `rust-parallel-e4-dispatch-screen-2026-10-02` 固定validated节点。source.bundle需要E3文档ad02b75；先按E3的恢复链取得该commit，再 `git bundle verify/fetch` 本包。无push/merge。

`prepare_between_systems.py --experiment <本目录> --work-dir <新目录>` 校验完整raw和wheel并恢复R4e/E2/E3输入及当前包，不安装或修改venv。实际测量source checkout必须为dede5ca，代码/测试最终节点只用于恢复/审计。

raw含两版runner源代码：前26个commands使用 `tools/profile_between_systems-stage1.py`（28d5bf1），最后两个matched对照使用 `tools/profile_between_systems.py`（ed4a9ee）。复现时把所需版本放在Lab的tools/rust_migration下另名文件，替换argv脚本路径，按其记录SHA校验；脚本需保持距Lab根两层的路径，以记录正确tooling_commit。合同runner/analyzer/归档和恢复脚本也在raw中，全部成员有SHA256。未来只恢复数据/复算无需重新运行长测。

当前配对筛选2/4成本9.512/9.048µs，对应理想预算7.098/7.769µs。95%差值区间均正，但含诊断开销与固定顺序效应。三轮无诊断全step结果存在矛盾，见analysis全部表格。结论是收益优先保守停止；没有实施Vision拆分、没有System之间净收益或新窗口容量。

2330Python/5Rust/fmt/Clippy/release通过，原49项删除及两冻结目录保留，全部既有GAP状态不变。raw、source bundle与完整结果路径由manifest/checksums固定。
