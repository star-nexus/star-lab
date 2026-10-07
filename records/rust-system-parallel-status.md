# Rust System并行：当前状态与边界（2026-09-29）

## E7 P3正式收益矩阵接续（2026-10-07，最新）

用户授权开启P3。P2四组完整结果/raw/身份已再次核验，不重跑。固定源码5b9658b、原性能driver/analyzer/native扩展/依赖不改；新增P3-only监督器tools/rust_migration/run_display_preparation_p3.py，持久目录/Users/liyang/Developer/star-lab-runs/e7-p3-20261007/runs。原24组矩阵（三轮×static/exercise×baseline/reuse_typed×native1/4）逐组串行，每组四个持续实例、完整9880tick、逐tick ABBA/BAAB；全部预热和慢尾保留。
正式计时关闭完整权威/像素哈希、细诊断及vmmap，保留原dummy2480×1239/1.5ms overscan wall预算和同侧GC策略。收益门槛仍是每轮render D+Q均值≥5%、chain/total均值正改善、100tick/10000bootstrap/seed42的95%下界>0及各自P99不回退；ordinary为主结论，typed独立交互，不跨层归因。
沿用用户不自动退出授权：压力仅暂停现场，6GiB仅监测参考，normal一分钟恢复。计时正式有效必须整次压力样本全部normal且无暂停/监测事件；发生干扰仍保留完整raw，该次不能用于收益，结束当前运行后停止剩余矩阵，不自动重跑或筛慢样本。只在无干扰的完整结果上复算；新的方法控制覆盖24组/三轮及无效资源事件和5%门槛，不计为速度结论。
预注册与冻结工具/控制内外SHA见E7 results/p3-preregister-20261007.json。各组完整后自动归档，全部24组后收尾结果到p3-complete.json；异常到p3-interruption-20261007.json。仅本轮P3，不自动启动单实例确认/窗口/默认接入，不关闭既有GAP或更新容量/Frontier，不改产品GAP或push/merge，5000Agents暂缓。
进度：`P2 ██████████ 4/4 | P3预注册/控制 █ | P3完整计时 0/24 ░░░░░░░░░░ | 确认/窗口/默认接入 ░`。

## E7 P2独立复核完成（2026-10-07，最新）

P2四组完整正确性全部通过并归档；自动收尾于06:46:36（Asia/Shanghai）结束。每组40994请求/9880tick，完整权威/展示投影/绘制命令/像素各19760次及冷World99次，流、最终权威和所有raw/四组ZIP内外SHA与持久目录逐字节复核通过。见E7 results/p2-complete.json、p2-integrity-review.json。
最后一组完整校验耗时14515.76秒（约4小时2分钟）；峰值RSS1855635456 bytes（约1.73GiB），采样footprint1610612736 bytes（1.50GiB）。压力采样均normal，实际暂停0秒；不把合成暂停控制当成本次真实暂停证据。第四组仅暂停监测、6GiB参考值非强制预算，前三组2500/2500/5120MiB原守护分别保留。结论是规范轨迹正确性通过，不是性能收益、统一资源预算或一般无泄漏证明。
测试/收尾均已退出；e7-p2已PAUSED。Lab README/manifest/analysis/decision/handoff/status/GAP阶段更新，历史失败attempt状态保持并链接后续完成结果。产品HEAD5b9658b/扩展/probe/锁文件与冻结工具核验，原49删除及两个冻结树保留；不改产品GAP、不关闭既有GAP、不更新容量/Frontier、不push/merge。
进度：`P2完整正确性 4/4 ██████████ | 独立证据校验/归档 █ | P3性能/窗口/默认接入 ░`。后续进入P3性能测量；本次仅完成P2，未启动P3、未启用默认，5000Agents继续暂缓。

## E7 P2完整通过（恢复运行，2026-10-07）

四组完整40994请求/9880tick校验全部通过：ordinary native1/static、ordinary native4/exercise、reuse_typed native1/exercise与native4/static。每组完整权威、展示/事件、绘制命令、像素、查询顺序及最终权威指纹通过，原始样本/指纹和内存守护全部保留。结论只覆盖P2正确性；第四组仅监测与保留现场，不代表强制资源上限验收；不代表性能收益、容量提升或一般无泄漏证明。
证据入口E7 results/p2-complete.json。已完成组的完整证据复用，缺失组新完整运行；历史不完整资源中断继续保留，未计作通过。测量源码5b9658b、原probe/扩展保持；前三组保留旧守护，第四组用户授权压力仅暂停、无自动终止；各组限额依次为2500/2500/5120/6144MiB（第四组仅监测参考值，不是强制上限），不能据此宣称统一内存预算验收。
进度：`P2完整正确性 4/4 █ | 证据与校验 █ | P3/窗口/默认接入 ░`。未启动P3、未启用默认路径、未push/merge；既有GAP、容量和Frontier保持。

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
证据：[E7本轮中断](../experiments/2026-10-rust-display-preparation/results/p2-reboot-interruption.json)，原日志、守护、父进程状态、输入恢复身份全部归档并核验内外SHA256。e7-p2已PAUSED，不反复自动重启、不放宽守护。下一步先审查持续系统压力与正确性harness资源成本，再决定新的受控恢复；本轮未修改测量源码/probe/守护。
进度：`P2完整通过 2/4 ▓ | 本次中断归档 █ | 剩余两组受资源阻碍 ▒ | P3/窗口/默认接入 ░`。产品HEAD固定5b9658b，既有GAP不关闭、容量/Frontier不更新、不push/merge。

## E7 P2重启恢复（2026-10-05，最新）

用户已重启机器并授权全力完成P2。系统压力normal、可回收余量60%，固定源码5b9658b及native扩展/原probe保持。原临时目录已被重启清除；从R4e canonical归档恢复输入，从E7 canonical ZIP恢复两组完整结果，内外SHA均验证。历史49删除、冻结工作树保持。
本轮持久目录/Users/liyang/Developer/star-lab-runs/e7-p2-20261005，inputs、inherited与runs分开。入口tools/rust_migration/run_remaining_display_p2.py，串行只重跑剩余两组并保留原2.5GiB/system pressure守护；全部通过后调用finalize_display_correctness.py自动核验/归档/更新Lab阶段记录。
恢复记录E7 results/p2-reboot-resume.json。实时状态runs/resume-progress.json，收尾状态runs/p2-finalization.json。自动跟进e7-p2需恢复并使用新持久路径；未变化保持安静，失败需处理或四组全部完成时报告、停用，不自动反复重启。
进度：`输入/完成证据恢复 █ | P2完整通过 2/4 ▓ | 剩余两组 ▒ | P2最终归档 ░ | P3/默认接入 ░`。不启动P3，不修改产品源码，不push/merge，不更新容量或Frontier、关闭既有GAP。

## E7 P2最新核对：未完成，重复资源中断

完整通过仍为2/4。第三组reuse_typed/native1/exercise的恢复尝试在最后记录3500tick后，被两次system warning压力样本停止（SIGINT，非已报告的等价错误）；第四组未启动，当前无测试进程。最新证据E7 results/p2-recovery-interruption.json。当前压力normal只证明检查时状态，不能外推整组数小时安全。
临时automation e7-p2已PAUSED，按既定规则不反复自动重启或放宽保护。下一步先解决持续运行的资源条件或审查正确性harness资源成本，保留两组完整结果与两次不完整尝试，再重跑剩余两组；不进入P3或默认接入。
进度：`P2完整通过 2/4 ▓ | 剩余两组受资源阻碍 ▒ | P3/窗口/默认接入 ░`。既有GAP不关闭，容量/Frontier不更新，产品测量HEAD5b9658b不变。

## E7 P2资源中断与剩余恢复（最新）

第三组reuse_typed/native1/exercise在最后记录8500tick后被系统warning压力保护停止，不能计作通过；并非已检测到等价错误。完整事件归档E7 results/p2-warning-interruption.json。两组完整通过仍有效，旧P3/确认/窗口监督器均已随上游停止。
新恢复入口E7 results/p2-recovery.json及tools/rust_migration/resume_remaining_display_correctness.py，输出/private/tmp/star-e7-20261004-p2-recovery。复用两组经哈希验证的完成结果，只重跑剩余两组；压力normal连续一分钟才开始，原probe源码和2.5GiB守护不变。失败仍停止，保留全部尝试；本恢复工具只完成P2。
压力已恢复normal，第三组正在从头重放。临时线程跟进automation e7-p2每小时检查同一个任务，不重复启动；第三组完成时归档，四组完成时核验/归档/报告并停用。资源或校验失败需处理时报告并停用，不自动反复重启。
进度：`P2完整通过 2/4 ▓ | normal恢复 █ | 剩余完整校验 ▒ | P3/窗口 ░`。默认接入尚未获门槛通过，产品HEAD5b9658b固定，既有GAP/容量/Frontier边界保持。

## E7继续与条件默认接入授权（2026-10-04）

native1/static与native4/exercise两组完整40994请求/9880tick正确性通过，结果归档E7 results/p2-t1-static-completed.json及p2-t4-exercise-completed.json。其余两组仍顺序执行，之后24组性能对照及有条件的8次单实例确认。continue_display_preparation_live.py等待确认通过后串行六次Cocoa窗口（AB/BA/AB；30+300秒），无诊断，保留全部失败和慢尾；live-progress.json为下一阶段入口。
用户最新授权收益验证通过后默认接入，替代此前“本轮仅保留研究开关”的限制；测量期间旧默认保持，先满足完整P2/P3/确认/六窗口门槛，默认native1也必须获稳定正收益，再验证默认接入并归档。默认接入补丁及独立dispatch合同见E7 results/default-patch-preparation.json：只准备、未应用，完整回归和默认路径验证留待收益门槛通过后。授权详见E7 results/default-adoption-authorization.json，不包含push/merge或容量/Frontier更新。
进度：`P0 █ | P1 █ | P2 2/4 ▓ | P3 ░ | 确认 ░ | 窗口 ░ | 条件默认接入 ░`。

## E7恢复执行（2026-10-04）

用户已清理系统内存并明确授权继续，归因于Chrome/编辑器占用；历史事件保留，不据此断言产品存在或不存在泄漏。系统压力正常、可回收余量72%。带完整权威导出的100tick冒烟通过，footprint约0.75–0.78GB，压力始终normal。
活动执行源码5b9658bc668b7d13f801351162f255f30622b32a（相对原型6730832仅GAP文档差异）。四组完整正确性在/private/tmp/star-e7-20261004顺序从头重放，每组由独立2.5GiB RSS/footprint及系统压力保护；之后24组无细探针性能对照顺序执行，性能阶段不用vmmap。
恢复预注册与完整工具快照见E7 results/preregister-resume.json及artifacts/display-preparation-resume-tools.zip。恢复工具tools/rust_migration/resume_display_preparation.py；实时进度resume-progress.json、各组guard.json/supervisor.log。失败立即停止，保留全部记录；通过P3后仍需条件单实例/窗口决策，尚无正式收益结论。普通路径和研究默认关闭、所有GAP/容量/Frontier边界保持。
进度：`P0 █ | 原型/小型契约 █ | 恢复冒烟 █ | 全轨迹 ▒ | 正式收益 ░ | 条件窗口/最终归档 ░`。

## E7：内存不足事件，重型校验与自动性能任务已停止

2026-10-02 14:49用户报告macOS应用内存不足，ChatGPT/Codex组约8GB；四个完整权威校验进程并发、GC延迟。全部测试进程与等待性能矩阵已停止，没有完整正确性或正式收益通过结论。
事件证据见[E7内存事件](../experiments/2026-10-rust-display-preparation/results/memory-exhaustion-incident.json)。停止前swap已用约10GB；停止后空闲内存约49MB→3GB。不能由RSS或此截图直接证明优化缓存泄漏，也不能用1200小型坐标缓存循环代表完整链路内存安全。
下一步先串行、限额、带进程footprint/压缩/交换与GC保留诊断，隔离baseline/candidate、完整导出及测试实例数量；在原因与安全边界确认前不重启全轨迹或性能矩阵。自动性能入口已有事件阻断。
原型源码6730832、GAP文档节点5d31d35；原型默认关闭，2389回归及补充边界对照仅证明各自范围。四个未完成全轨迹运行均不可用作完整验收。
进度：`归因 █ | 原型 █ | 小型契约 █ | 完整正确性/内存失败 ▒ | 收益 ░ | 窗口 ░`。
原49删除、冻结目录、既有GAP、5000Agents暂缓、容量/Frontier/no push/merge约束保持。

## E6 展示数据与 ECS 缓存研究完成（2026-10-02）

验证节点 `068c1ecd17988ac6d884984e904aea924968e0ae` / `rust-parallel-e6-presentation-cache-2026-10-02`；测量0a297a8，执行代码相同，native扩展838c693保持。
2385回归、native1/4完整40994请求/9880tick的响应、权威、展示、查询和像素契约通过。
reuse_typed六轮apply改善44.26–45.62%、完整链14.66–15.53%、总工作10.78–11.61%，
均值/P99/区间门槛通过；native4单实例确认通过。reuse_constructed apply慢2.11–2.71%，不选择。
候选三轮窗口guards通过，但baseline第二轮帧/队列超限，六次整体window gate未全通过。
研究默认关闭，不声称容量或Frontier提升，既有GAP不关闭，5000Agents暂缓。

先读[E6 README](../experiments/2026-10-rust-presentation-cache/README.md)、
[成本/完整结果](../experiments/2026-10-rust-presentation-cache/analysis.md)、
[决策](../experiments/2026-10-rust-presentation-cache/decision.md)。原始样本/失败控制、完整重生成delta、
wheel、source bundle和校验链均保留。像素契约固定游戏墙钟及地形构建条目配额；
正式性能/实时窗口仍采用原时间预算，产品未因此修改。
下一项：显示链路准备成本，先拆真实窗口约3.184ms未归因update和3.349ms RMS分项，并追踪baseline尾延迟。
进度：`归因 █ | 契约/实现 █ | 等价 █ | 三轮收益/确认 █ | 窗口结论 █ | 证据/恢复 █`。
原49删除/冻结目录/E2–E5标签保留，不push/merge。

## 整体性能评估完成：建议优先展示与观测（2026-10-02，未实施）

进度：`运行链路 █ | canonical复算 █ | 源码/已有机制 █ | 投入排序 █ | 恢复/边界 █`。
先读[整体评估与候选排序](rust-performance-optimization-assessment.md)、[精确结果/校验](rust-performance-optimization-assessment.json)，再按其引用下钻E2/R4e/E3/E5。此处是新的投入建议，E5的执行/验收结论仍保留；没有启动优化实施或重新测量当前binary live。

审查源码3b167b1；最新完整窗口仍为E2 native4/source2bc57d5三轮，平均world step0.260–0.264ms（约整帧1.25%）、显示Systems8.491–8.748ms、展示应用2.693–2.748ms。约5.114–5.164ms update尚未分项，不归因为render/GC。不同分母、P99和跨输入结果不可相加或当因果收益。

建议首项：展示路径细分归因＋Python消费已有组件字段更新，减少deepcopy/组件重建/缓存失效；随后接已有合法read-batch。纯ENV优先观测公共工作、Statistics历史结构、Vision集合/Fog提交表示。已有裁剪/批量blit/缓存/typed编码/JSON直传/E2并行应继承；不重做whole-World快照进程池。Statistics kernel∥Movement的2/4诊断零开销上限约5%，不是净收益。

[复算工具](../tools/rust_migration/assess_optimization_priorities.py)校验E2/E3 canonical整体及6个所用member、14个源码SHA，结果可字节复算。此阶段是规划记录，无新加速比/live/容量/Frontier、生产执行变更或GAP关闭。默认1/API18/schema5、规则/观测/动作/确定性/Python生态、原49删除/冻结目录/历史标签保留，5000Agents暂缓，未push/merge。


## E5 研究完成：Movement∥Visuals真实重叠，默认不接入（2026-10-02）

进度：`依赖/窄接口 █ | 四模式/等价 █ | 主门槛/敏感性 █ | 条件停止/决策 █ | canonical归档/恢复 █`。
恢复先读[E5正式包](../experiments/2026-10-rust-movement-visuals-parallel/README.md)，再读analysis/decision/manifest、源码native-movement-visuals-parallel与GAP；E4/E3/E2/E1历史保留。

一worker计算owned Visuals、caller执行Movement，join后原序提交实体操作/状态；只读Position存在性与next-ID，不复制World，复用实例pool，区域最多两个执行参与者。四模式按次私有，新接口_movement_visuals_step_json；E4的Vision未实施模式仍明确拒绝。普通step/default1/API18/schema5/E2 Statistics128、观测/动作/RNG/规则和Python生态不变。

native2三轮mean改善0.593/0.688/−0.023%，native4 −0.747/−0.273/0.742%，各仅1/3轮通过完整mean/P99/CI95门槛。0/4/16六组单轮敏感性全部CI跨零。诊断3772候选tick的计时区间交叠下界均值16.917/15.769µs，支持机制但不是无诊断收益。保留私有原型、普通step不启用；4线程未过前置门槛，未进入单实例确认或live窗口，不新增容量/Frontier。5000Units/1000Agents目标保持，5000Agents暂缓，既有GAP OPEN/RISK不关闭。

测量94913a4f836a3c106e08a1334cb81971cfd728c3；validated 3b167b151c3bc32e1d54f6015d0f15d2c3dd6a74（仅补文档/测试，native代码相同）；annotated rust-parallel-e5-movement-visuals-2026-10-02；扩展838c693398d9f8cbfd62e4ed898d3c287b657aadce91e9ccf5c20e5a9bd48544。source.bundle需要E4 72bf05a；新空repo由原main及E2→E3→E4→E5 bundle完整恢复已验证。

2345Python/6Rust/fmt/Clippy/release通过，含多段移动/GameOver后Vision、ID耗尽、effect/Capture/Statistics错误前缀、混合实体、reset/close/多实例和两侧fault join。27完整报告、90 world重放各40994request/9880tick/展示完整校验；13合同变体各13case/377step完整state/error/delta/reset字节一致，canonical载荷单存＋13别名。所有预热和慢尾保留。

raw SHA a3593da48438e7c96c9e9c003b8374d4d8b393d45a806d1a2582a2d12e3c4f07（15916081 bytes），compact SHA 2b53b12dadc326ef04a4e43cd115b1e7c71c9dab473f71efdf9ccae4fe3bef65（21057 bytes）。原始全部step/timing/wheel/准确工具版本/检验链保存；canonical analysis与诊断成本复算字节一致，E4/E3/R4e输入和wheel恢复只写新目录。原49删除、两冻结HEAD/扩展、E2/E3/E4标签均保留；活动工作树clean，未push/merge，迁移发布未完成。


## E4 System 之间并行研究完成：派发筛选负结果（2026-10-02）

进度：`边界/理想预算 █ | scoped负对照 █ | 完整ABBA █ | 等价/决策 █ | canonical归档/复算 █`。
先读[E4正式包](../experiments/2026-10-rust-between-system-parallel/README.md)、analysis/decision/manifest，再读E3/E2/E1历史。当前结论优先于旧下一步。

只完成私有baseline/empty_fork。当前同二进制相邻配对诊断8020/9880候选tick，2/4成本均值9.512/9.048µs，当前理想预算7.098/7.769µs；成本减预算95%区间[0.456,5.385]/[0.256,2.421]µs。含计时/bookkeeping和固定先后效应，按收益优先保守停止；不是无诊断严格负收益或所有System并行无价值的证明。无诊断三轮ABBA有矛盾结果，全部保存，没有实际Vision并行净收益。

split_serial/parallel未进入且明确拒绝，真实窗口未进入，普通step未接入。实例池最多一worker＋caller；默认1/E2 Statistics128门槛/API18/schema5/oracle及Python生态不变。目标5000Units/1000Agents，5000Agents暂缓。

测量 **dede5ca0ca3472abdb1d24589878e6a72d812f88**；validated **a7508bce4b900ccf8465e761291adb7e7e2ce98d**；最终文档 **72bf05a2f6ec6d1d15ffad7914226c0c3e16b9cf**（native代码相同）；annotated **rust-parallel-e4-dispatch-screen-2026-10-02**。扩展 **9c7eebe03257d1d6941e67b5e31a947e4c6cedf32db6979e624629fd5cf5dd91**。source.bundle需要E3 ad02b75。

28次完整run报告（24无诊断＋4诊断twins）全部录制响应/事件/最终hash核对，四组twins完整对象一致；7合同变体各36case/174step字节等于canonical；2330Python/5Rust/fmt/Clippy/release通过。raw **c15f4476ce9a7582fd0a33313cf5f8a21670c709d033f75746df2d1011131f4a**；脚本版本/全部tick/慢尾/wheel/日志/校验链保存，canonical复算、只读恢复、bundle验证通过。原49删除、两冻结HEAD/扩展保留；G001–G003历史、G008/G009 OPEN、R001/R002 RISK保留，无新确认玩法GAP、live容量/Frontier、push/merge或发布结论。



## E3 其他 System 内部候选研究完成（2026-10-01）

进度：`边界审计 █ | 分项归因 █ | 完整等价 █ | 条件排序 █ | canonical归档/复算 █`。
先读[E3正式报告](../experiments/2026-10-rust-internal-system-candidates/README.md)、analysis/decision/manifest与[生产成本/依赖表](/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main/docs/native-internal-system-candidates.md)，再读E2/E1/P0历史。此状态优先于下面旧“下一候选”。

活动工作树仍`/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`、`codex/rust-ecs-parallel`。测量/validated **6d4018cc0c607a51a3783428867ba9259bb43f43**；最终文档 **ad02b75f2b83f97fe0bef4c1c9eee5742b1610fb**（执行代码/测试相同）；annotated **rust-parallel-e3-internal-attribution-2026-10-01**指测量节点。Release扩展SHA **e0f46cfbffd8542c08cd2b2e6b4a26c000da05ecb9bffd3466d77fa859a9834d**。仅增加按次私有归因，**没有启用其他System新并行**；E2 Statistics策略/128门槛、API18/schema5/oracle、默认1、Python接口生态不变。

当前规范轨迹Vision诊断均值约43µs，但几何仅0.553–0.599µs/tick，占1.27–1.37%，提交约27–28µs。Movement行处理乐观上界5.36–5.45µs/tick（含写入/计时），活动平均122.47/峰186。Visuals四阶段循环合计约8µs，上界不能跨栅栏合并；damage平均6.66/峰28行。Recovery平均2.81/峰24到期项，最大阶段是首次5007新ID审计，到期0；Capture无活动样本。

**当前目标没有足够证据启动另一项并行执行。**条件roadmap：先测Vision大批冷几何/合法更大视距，再测更多同时移动单位的Movement、Visuals大批同阶段更新。先串行拆分和分项成本，再决定scoped计算；保持LRU A→B→A、逐段空间写入、新箭同tick推进、ID/错误前缀/事件原序。不得复制世界或全部System入池。当前目标进一步优化可先研究Vision串行提交/表示；其收益仍待单独验证。

旧E2与新1/2/4共4轮每轮40994请求/9880tick/展示完全核对；4个36场景/174step契约输出字节相同；2315Python/4Rust/fmt/Clippy/release通过。原始包SHA **c3e347b145fcc5edfda304bb35030d3d3d9320861f116a5507d2b92cbd9b6abd**，全部逐tick/慢样本/wheel/日志保存；相同输入/合同引用R4e/E2 canonical。恢复bundle需要E2 0aa28ac2；复算只读canonical ZIP，索引/校验/完整argv见正式包。E2的原live容量仍指2bc57d5/23dc7e4，**E3没有新live/Frontier/加速比**。

无新确认玩法GAP；G001–G003历史、G008/G009 OPEN和R001/R002 RISK保留，5000Agents暂缓。原49删除、两冻结HEAD/扩展hash核验一致；未push/merge，发布未完成。


## E2 Statistics 内部并行研究完成（2026-10-01）

正式包：[E2报告](../experiments/2026-09-rust-statistics-compute/README.md)，含analysis/decision/manifest、完整raw、逐步samples、错误/reset契约、wheel及源码恢复bundle。
活动工作树 `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`，分支 `codex/rust-ecs-parallel`。
实测/策略 **2bc57d5f2241a578f61d71bb5774e7063a03ec25**；最终文档 **0aa28ac2ae0267048fcdb3998f9d76175ed4d699**（执行代码相同）；
annotated **rust-parallel-e2-statistics-2026-10-01**。正式扩展SHA **23dc7e4f5425e855a780a802d889f13bd28f300577688e66378ab574b7712d55**。
串行44c3696、实验调度7ab0ac1及独立旧P0 binary均保留。
进度：`串行拆分 █ | 分项归因 █ | scoped计算 █ | 全量等价 █ | 净收益/门槛 █ | 真实容量 █ | canonical归档/复算 █`。

仅当前Statistics批次的JSON记录构建在已有实例池内部并行，主线程原序提交；实际候选行至少128且显式native2/4才调度。小/尾批inline、默认1不变，没有between-System调度器。健康算术极小，trim/visibility/factions及写入保留串行。
旧/新8种契约完整输出字节相同（36场景/174step）；20次R4e40994请求/9880tick/展示的完整流/最终状态一致，含正式普通step1/2/4。2291Python/4Rust/fmt/Clippy/release通过，多实例/reset/close覆盖。
同binary同线程只改门槛的3组完整step对照：2线程均值减少4.18–16.76%，4线程7.58–10.36%，各组P99改善。合成1–32行并行负收益；64为测得mean-positive点，64行native4 P99反而更差，128保守操作门槛。此因果对照不是旧P0到全部新实现或整帧加速。

真实5000Units/1000Agents/native4三轮30预热＋300s Cocoa全部guard通过：帧P99 28.283/28.643/28.631ms，Hz29.997/29.993/30.000。
max帧91.923/102.449/32.239ms、worst5s P99 39.837/76.037/31.794ms原样保留，不保证每帧/短窗口。alive_min5000，peak movers180/173/173；不外推全5000移动、高密度、Hub/真实LLM或5000Agents。R4e native1验收及全部历史证据不覆盖。
canonical raw SHA **62c5e73a2356334fc0fa85e3b5f4054a46f5f759ad7cb6c9fcef41dcd7b190ba**；8个完全相同contract raw只存1成员+别名；analyzer由canonical包复算而非依赖ignored loose scratch。工具checkpoint **69969a1713bb83d7e18fd4b05137276bc412cb72**，各测量工具hash/旧变体commit及完整argv/env见manifest/results。

API18/schema5/oracle/Python生态边界不变。无新确认玩法GAP；G008/G009 OPEN、R001/R002 RISK、G001–3基线变化保留，5000Agents暂缓。原49项删除和两处冻结HEAD/扩展hash均核验保留。没有push/merge，迁移/发布未完成。
下一候选E3先归因Vision uncached几何与有序缓存/Fog提交；between-System Recovery/Lifecycle/Vision保留低优先级窄接口研究（现有理想重叠小于派发成本），不直接全System入池。先读本E2包/生产native-statistics-parallel/GAP，再读E1依赖与机制、P0归因和R4e历史容量。
此状态优先于下方历史E1/P0下一步。

## 独立Rust并行任务：E1 ECS方案探索完成（2026-09-30）

按用户最新指示，活动任务转向**System之间及System内部并行**，详见
[恢复入口](rust-ecs-parallel.md)及[E1正式方案/机制包](../experiments/2026-09-rust-ecs-parallel-design/README.md)。
工作树 `/Users/liyang/.codex/worktrees/rust-ecs-parallel/star-main`，分支
`codex/rust-ecs-parallel`，从R4e tag隔离；最新设计commit **be3867b3ad65749e0e34efd245359c4123189031**，
annotated **rust-parallel-e1-design-2026-09-30**。P0完整依赖表/成本/等价性保留。
进度：`恢复 █ | 归因 █ | ECS方案/机制 █ | 生产并行原型 ░ | 新容量 ░`。

拆窄访问后Recovery/Lifecycle/Vision是System间候选；P0理想零开销重叠节省mean3.883µs。
锁定Bevy0.19.1机制探针1/2/4验证窄组件重叠、冲突串行、100/5000活动子集；
已有池2/4验证5000有序结果，空dispatch median9.125/7.084µs。这些不是实际游戏并行/净收益。
**下一阶段E2：Statistics当前批次纯计算＋有序提交，先1线程拆分/分项归因，再决定2/4。**
P0跨请求批次候选暂缓、原证据不改；不直接把全部System入池。

目标仍5000Units/1000Agents，5000Agents暂缓；生产执行/API/schema/oracle/默认1线程未改。
G008/G009/R001/R002原状态保留，无新已确认玩法GAP。原49删除、两个冻结测量目录和负结果保留。
此状态优先于下方历史下一步；无新的容量/Frontier/发布或push/merge结论。


当前验收目标收回到5000 Units＋1000 Agents；5000-Agent扩展暂缓。用户Python接口、策略、窗口和网络编排继续保留Python。

## 已有能力与缺口

- Python时期已实现同步只读批次共享，测量节点72e36414、集成9063863。原生产main6a970dea已包含它。
- Rust的ObservationBatch也已实现只读段公共事实和Unit面板复用；R4a另加入2/4线程Unit面板计算。
- 当前Lab post-action闭环逐请求调用single入口，因此没有利用跨请求只读批次。这是已有能力的接入缺口，不是一个新的共享算法。
- R4d的get_faction_state_json省去服务端重复JSON往返，仍是逐请求入口。
- 当前Runtime::step显式顺序调用各推进阶段；不是由Bevy Schedule分配所有System到多个核心。主要世界计算已在Rust，不等于System并行、容量或发布全部完成。

代码锚点：生产 `native/rotk/src/runtime.rs:341`、`native/rotk/src/movement.rs:259`、`native/rotk/src/vision.rs:395`、`native/rotk/src/observation.rs:412`。核验源码5147e4d8e0c33c997bd86960d87fa4b5b3ca90c5（R4d实现；72ea765仅追加文档）。

## ECS为什么适合并行，又为什么不是自动并行

ECS把状态与逻辑分开，使System可以显式声明读写组件和资源。这正适合依赖调度。System之间不直接调用仍可能共同访问同一数据，或通过事件形成生产/消费关系。

当前真实例子：advance_movement写Position、Movement、spatial，跨格时写vision_dirty；advance_vision随后消费新位置及dirty事实。若把二者直接并行，可能读到本tick移动前状态，改变Fog及Agent可见信息。事件替代函数调用后仍需要明确哪些事件本tick生效、消费顺序是什么。

Bevy支持让没有冲突的System并行，但冲突的组件/整个World访问会阻止并行：[官方schedule文档](https://docs.rs/bevy_ecs/0.19.1/bevy_ecs/schedule/index.html)。当前多个advance_*方法取得整体&mut Runtime，接口没有把最小读写集交给调度器。需要分解借用与共享资源访问，而不是只打开multi_threaded开关。

## 合理的后续实现方式

1. 列出每个阶段读取/写入的组件、空间索引、活动集合、事件和随机数；标记依赖及原执行顺序。
2. 让只读或读写互不冲突的System通过明确参数接入Schedule；独立实体计算可以在System内部并行。
3. 空间占用、死亡/生命周期、统计、共享集合及随机数消费的提交保持规定顺序；必要时每个任务生成独立结果，再有序合并。
4. 同一录制输入的1/2/4线程完整状态、响应和事件必须一致；随后再测真实窗口整帧与排队收益。

这里没有宣称任何尚未审计的System对已经可安全并行；不能先把全部System放上线程池，再靠锁随机决定次序。

## 优先级依据

R4e第一轮长测世界step平均0.295ms/P990.758ms，整帧P9929.800ms。这个step不包含全部Agent观测、Python展示和呈现；其耗时不能代表整个ENV处理量。System并行值得保留为R4工程项，但针对当前负载，不能仅靠加速这段亚毫秒step得到数倍整帧提升。

R4e已完成当前1000-Agent三轮长测及原生产/规范化Python同条件短测，见[报告](../experiments/2026-09-rust-1000-agent-validation/README.md)。将世界计算已迁移、并行覆盖程度、容量验收、Python上层接入和发布分别报告，不再笼统称“性能迁移全部完成”。
