## E7 P2第四组仅暂停监督器（2026-10-07，最新）

用户明确授权继续最后一组且不设置自动退出。本轮只重新执行reuse_typed/native4/static；前三组40994请求/9880tick及完整raw/守护再次核验复用。旧8500进程已退出，无法恢复，历史尝试全部保留。
新入口tools/rust_migration/resume_final_display_p2_pause.py，目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261007-pause-only/runs；工具与控制已冻结，见E7 results/p2-pause-only-resume.json。warning连续两次或critical/未知信号只暂停同一进程组，normal连续60秒恢复；6144MiB仅监测参考值，不作为终止条件。监测查询失败保留进程暂停重试；监督器外部中断也保留暂停子进程，不自动杀死。没有自动运行超时或重复重启。暂停不会释放已有内存，退出/重启后仍无持久检查点。
合成控制通过同PID暂停/恢复、进度恰好一次、critical不退出及超出参考预算仍完成；首次过短合成子进程控制未观察到第二个warning样本，其完整raw保留。控制不计作P2通过。专用finalize_display_correctness_pause.py保持全部正确性与raw阈值，并显式区分前三组强制守护和第四组仅暂停监测，不宣称统一预算验收。
当前P2仍3/4，最后一组已启动（parent PID65461/test PID65533），e7-p2跟进ACTIVE；只完成P2，不进入P3、不启用默认。产品HEAD5b9658b、probe/native、历史guard与冻结runner保持；Lab阶段GAP更新，既有GAP/容量/Frontier不改，5000Agents暂缓、不push/merge。
进度：`P2完整通过 3/4 ███████░░░ | 无自动退出控制/归档 █ | 第四组运行 ▒ | P2最终归档 ░ | P3/窗口/默认接入 ░`。

## E7 P2压力策略与保留现场控制（2026-10-07，最新）

用户要求解释warning并不要从头运行。macOS压力由可用内存、交换速率、wired和文件缓存等综合反映，warning不是OOM；内核公开说明也将其定义为开始出现压力。旧guard的“连续两次warning终止”是Lab主动采用的保守策略。此次运行停止未触达6GiB限额；旧日志未保存当时完整vm_stat或交换速率，不能确定具体系统触发原因，也不能用现在的3GiB空闲/1.4GiB交换反推停止时状态。
第四组旧进程已经SIGINT退出并关闭native世界/显示实例，probe只在完整结束时写校验raw；8500tick仅进度日志，不是可恢复检查点。本轮未启动完整轨迹、不重跑前三组。P2仍3/4，e7-p2保持PAUSED。
新增独立guard_display_preparation_resumable.py：两次warning暂停同一进程组，normal持续60秒后原PID恢复，critical/未知信号或6GiB预算仍终止。暂停事件原子落盘，记录最后日志进度及vm_stat/swap/query快照。暂停保留内存，不释放世界；不支持退出/重启后恢复，仅限正确性运行，不用于性能计时。旧guard、冻结runner、probe和产品HEAD5b9658b未改，新guard尚未接入P2 runner。
独立合成控制验证同PID恢复、暂停期间进度不变、40条进度恰好一次、暂停中critical清理、预算/未知信号终止及默认60秒策略。控制源码与完整raw已归档并核验ZIP内外SHA；它不计作E7正确性通过。见E7 results/p2-pause-guard-control.json。复现：python3 tools/rust_migration/test_resumable_display_guard.py --output <不存在的新目录>。
进度：`P2完整通过 3/4 ███████░░░ | 活进程暂停控制 █ | 旧8500现场恢复不可用 × | 新完整重放未启动 ░ | P3/窗口/默认接入 ░`。Lab阶段GAP更新，产品GAP暂缓；既有GAP不关闭、容量/Frontier不更新、5000Agents继续暂缓、不push/merge。


## E7 P2第四组6GiB重试中断（2026-10-07，最新）

P2完整通过仍3/4；三组完整40994请求/9880tick和全部raw、权威/展示/命令/像素及对应2500/2500/5120MiB守护再次核验。第四组重试于01:46:47（Asia/Shanghai）运行12749.64秒后，被12742.667/12747.683秒连续两个system warning样本停止（SIGINT，child_exit=-2），最后正式进度8500/9880tick。当前测试和收尾均已退出。
本轮峰值RSS1693810688 bytes（约1.58GiB），采样footprint1503238553 bytes（约1.40GiB），没有达到6144MiB限额。退出Chrome后本次运行更久，但没有控制证据把差异归因于Chrome；5→6GiB进程预算并未改变独立warning停止条件。日志未报告状态/命令/像素不一致，KeyboardInterrupt不是AssertionError，中断不算通过，不证明实际内存耗尽或产品泄漏。
证据E7 results/p2-fourth-retry-interruption.json；守护、完整父/子日志、状态和启动身份已归档并验证内外SHA，原源码/probe/native/guard及本次冻结执行工具未修改。e7-p2已PAUSED，不反复自动重启。下一步应核查内核压力信号与活动监视器的口径以及guard warning策略有效性，再考虑新的第四组单独重放；不能继续只加进程预算并原样重试。
进度：`P2完整通过 3/4 ███████░░░ | 第四组8500后中断归档 █ | P2最终完成 ░ | P3/窗口/默认接入 ░`。产品HEAD5b9658b、既有GAP/容量/Frontier、5000Agents暂缓保持，不进入P3、不启用默认、不push/merge。


## E7 P2仅第四组恢复，6GiB预算（2026-10-06，最新）

用户退出Chrome并授权重启、进一步增加单进程预算。预检内核压力normal，查询可回收余量72%；实时swap查询仍有既有交换占用，因此不记录“交换为零”结论。前三组完整证据及全部raw已验证复用，不重跑；本次只执行reuse_typed/native4/static，进程限额6144MiB（6GiB）。系统warning/critical策略、原guard代码、probe、产品HEAD5b9658b/native扩展不变。
专用入口tools/rust_migration/resume_final_display_p2.py；目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261006-fourth-retry/runs。预注册E7 results/p2-fourth-retry.json，冻结工具display-preparation-p2-fourth-retry-tools.zip。已验证三组原始证据、第四组单独派发及预算传递的控制；不把mock方法控制视为正确性通过。完成后finalize_display_correctness.py显式核验各组2500/2500/5120/6144MiB，不冒充统一资源预算或性能结果。
历史第四组中断3500里程碑和全部失败证据保留；新完整重放从头开始，成功才计入4/4。若再资源/校验失败，保留并停止，不自动反复重启。自动收尾只到P2，不启动P3或普通默认，不push/merge；既有GAP、容量/Frontier和5000Agents暂缓边界不变。
进度：`P2完整通过 3/4 ███████░░░ | 第四组专用恢复/预算核验 █ | 第四组重放 ▒ | P2最终归档 ░ | P3/窗口/默认接入 ░`。


## E7 P2第四组系统压力中断（2026-10-06，最新）

完整通过保持3/4；三组完整40994请求/9880tick及权威/展示/命令/像素/raw SHA再次核验。第四组reuse_typed/native4/static于20:32（Asia/Shanghai）运行4940.27秒后，由4932.417/4937.432秒两次system warning样本停止（SIGINT，child_exit=-2），最后正式进度3500tick；之后frames3600仅为render debug，不能据此补计完整tick。
峰值RSS1706868736 bytes（约1.59GiB）、采样footprint1288490188 bytes（约1.20GiB），均低于本轮5120MiB；停止原因仍是独立系统压力策略。堆栈在显示后权威JSON导出比较，错误为KeyboardInterrupt而不是AssertionError，日志未报告等价失败；中断不能计作通过，也不能据此证明内存耗尽或缓存泄漏。
证据E7 results/p2-fourth-interruption.json；守护、完整子/父日志、执行状态与启动身份已归档并核验内外SHA。当前测试/收尾均已退出，e7-p2已PAUSED，不自动反复重启、不修改冻结工具或进一步放宽守护。下一步保留三组成功，仅在明确新的运行条件或系统压力策略后受控重跑第四组；不能用现有恢复工具原样重复第三组。
进度：`P2完整通过 3/4 ███████░░░ | 第四组中断归档 █ | P2最终完成 ░ | P3/窗口/默认接入 ░`。产品HEAD5b9658b及probe/native/guard保持、既有GAP不关闭、容量/Frontier不更新、不push/merge。


## E7 P2第三组完整通过，第四组运行（2026-10-06，最新）

reuse_typed/native1/exercise已完整通过40994请求/9880tick：完整权威19760、展示投影19760、命令19760、像素19760及完整冷World99检查。流与最终权威指纹、全部raw SHA、固定源码/probe/扩展/输入身份与前两组一致；5120MiB守护passed，系统压力采样均normal。原始样本、权威/像素指纹、guard与日志已归档，内外SHA核验。证据E7 results/p2-typed-t1-exercise-completed.json。
第四组reuse_typed/native4/static已由原父任务自动启动，初次核对到500/9880tick；继续等待，不重复启动、不修改冻结执行工具。完整通过现在3/4，尚未完成P2，不代表性能收益或一般无泄漏结论；预算前两组2500MiB、本组5120MiB分别记录。
进度：`P2完整通过 3/4 ███████░░░ | 第三组证据/校验 █ | 第四组 ▒ | P2最终归档 ░ | P3/窗口/默认接入 ░`。产品HEAD5b9658b、49删除、冻结目录与GAP/容量/Frontier保持，不进入P3、不启用默认、不push/merge。


## E7 P2提高单进程预算并恢复（2026-10-06，最新）

用户重启并授权再次运行、显著放宽2500MiB单进程限额。预检内核压力normal；查询可回收余量78%。剩余两组串行采用5120MiB（5GiB），系统warning/critical保护保持；原probe、产品源码5b9658b和native扩展未改。提高进程限额不解决此前warning触发，若再触发仍停止并保留证据，不自动循环重启。
前两组完整证据与全部raw已核验复用，不重复运行；历史49删除及两个冻结工作树保持。新持久目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261006/runs，输入及继承证据仍引用Oct5持久目录。预注册E7 results/p2-budget-resume.json，冻结工具display-preparation-p2-budget-tools.zip；原守护代码只通过既有--limit-mib参数改变预算，包装与收尾接口新增显式预算/日期，核验错误预算和中断不会算通过。
完成后需四组完整40994请求/9880tick、全部权威/展示/事件/命令/像素检查与SHA；报告明确前两组2500MiB、后两组5120MiB，不冒充统一内存预算、一般无泄漏或性能收益结论。自动收尾只完成P2；不启动P3、默认路径、不push/merge，容量/Frontier和既有GAP不变。
进度：`P2完整通过 2/4 ▓ | 提高预算/身份核验 █ | 剩余两组恢复 ▒ | P2收尾 ░ | P3/窗口/默认接入 ░`。


## E7 P2重启尝试再次资源中断（2026-10-05，最新）

完整通过仍为2/4，本轮重新核验前两组完整40994请求/9880tick及全部raw SHA、权威/展示/命令/像素检查与守护。重启后的第三组reuse_typed/native1/exercise在运行180.95秒后，被175.160/180.166秒连续两个system warning样本停止（SIGINT，child_exit=-2）；第四组未启动，无运行中的测试或收尾进程。没有tick里程碑输出，不能推算已完成tick数；日志未报告等价错误，中断也不能计作通过。
测试进程峰值RSS为1371127808 bytes（约1307.6MiB），最新采样footprint为1001494937 bytes（约955.1MiB），均未达到2500MiB限额。实际触发的是系统整体压力；中断堆栈位于完整权威JSON导出，不证明该位置是根因，也不证明E7缓存泄漏或Chrome是原因。
证据：[E7本轮中断](results/p2-reboot-interruption.json)，原日志、守护、父进程状态、输入恢复身份全部归档并核验内外SHA256。e7-p2已PAUSED，不反复自动重启、不放宽守护。下一步先审查持续系统压力与正确性harness资源成本，再决定新的受控恢复；本轮未修改测量源码/probe/守护。
进度：`P2完整通过 2/4 ▓ | 本次中断归档 █ | 剩余两组受资源阻碍 ▒ | P3/窗口/默认接入 ░`。产品HEAD固定5b9658b，既有GAP不关闭、容量/Frontier不更新、不push/merge。

> 最新：P2恢复尝试再次因系统内存warning被守护停止，仍2/4通过。暂停自动跟进，不反复重跑，不进入P3或默认接入；这不是正确性不一致或性能负收益结论。

> 2026-10-04最新：第一组完整正确性通过，剩余三组继续；用户授权所有门槛通过后默认接入（详见results/default-adoption-authorization.json）。目前没有正式收益，尚未启用。下文停止决策为历史记录。

> 2026-10-04更新：用户授权恢复，守护冒烟通过；旧停止决策作为历史事件保留。完整正确性/收益/窗口仍待验证，原型继续默认关闭。

# E7 决策：停止重型校验，原型继续关闭

四个全状态/像素校验并发触发系统应用内存不足，完整轨迹正确性与资源验收未完成；不进入正式性能或窗口阶段。所有未完成运行保留为失败控制，不报告速度结论。

目前不能确认产品缓存泄漏。坐标缓存有界的小型测试只覆盖该缓存；全native导出、native临时分配/allocator保留、GC延迟、双实例及四进程并发的组合仍未隔离。测试安排超出本机安全范围，必须先补串行限额内存诊断和主动压力停止条件。

自动性能入口被未解决事件阻断。原型默认关闭，不更新容量/Frontier或关闭既有GAP。
