
## E7 P2重启尝试再次资源中断（2026-10-05，最新）

完整通过仍为2/4，本轮重新核验前两组完整40994请求/9880tick及全部raw SHA、权威/展示/命令/像素检查与守护。重启后的第三组reuse_typed/native1/exercise在运行180.95秒后，被175.160/180.166秒连续两个system warning样本停止（SIGINT，child_exit=-2）；第四组未启动，无运行中的测试或收尾进程。没有tick里程碑输出，不能推算已完成tick数；日志未报告等价错误，中断也不能计作通过。
测试进程峰值RSS为1371127808 bytes（约1307.6MiB），最新采样footprint为1001494937 bytes（约955.1MiB），均未达到2500MiB限额。实际触发的是系统整体压力；中断堆栈位于完整权威JSON导出，不证明该位置是根因，也不证明E7缓存泄漏或Chrome是原因。
证据：[E7本轮中断](results/p2-reboot-interruption.json)，原日志、守护、父进程状态、输入恢复身份全部归档并核验内外SHA256。e7-p2已PAUSED，不反复自动重启、不放宽守护。下一步先审查持续系统压力与正确性harness资源成本，再决定新的受控恢复；本轮未修改测量源码/probe/守护。
进度：`P2完整通过 2/4 ▓ | 本次中断归档 █ | 剩余两组受资源阻碍 ▒ | P3/窗口/默认接入 ░`。产品HEAD固定5b9658b，既有GAP不关闭、容量/Frontier不更新、不push/merge。

# E7 analysis — P0 completed, P1 in progress

Full 9880-tick diagnostic replay at source 57b6520, same native extension, ordinary consumer: apply 2.6499ms, display including clear 8.5771ms, RMS 1.9456ms; D+Q 10.5227ms. Inclusive territory traversal 2.3707ms versus batch packing 0.1118ms. Typed layer separately: territory traversal 2.7087ms. These contain diagnostic overhead and do not predict speedup.

Initial snapshot and all 9880 canonical full deltas contain zero TerritoryControl components. Real Cocoa short diagnostics corroborate territory traversal cost; diagnostic scope aggregation includes warmup. Both short runs fail frame P99 and not_diagnostic guards: no capacity conclusion. A 600-tick baseline/probed-baseline/unprobed-baseline control passes fields, commands and pixels (development control only).

Select C, empty territory ECS lookup avoidance, rather than A command packing. Cache only validated coordinate sequence, capped at32768. Tile IDs remain live; any component membership or nonstandard input falls back. Complexity remains O(visible), no computed ownership, style, Fog, Surface or entity reference retained. Ordinary update untouched. No default enablement or native changes.

P1/P2/P3 preregistration fixes modes and the original plan gates before formal performance. Baseline diagnostics are not formal performance. Correctness and net speed remain pending.
