# E5：Movement 与 Visuals 的 System 之间并行

状态：主收益研究已完成，native2/4均未通过稳定门槛；正在补齐诊断、敏感性及正式归档。无默认接入或容量结论。

目标为 5000 Units＋1000 Agents，5000 Agents 暂缓。E4 保守负筛选只适用于
Vision∥Recovery/Lifecycle，不能否定本轮另一种实际重叠。

代码起点：72bf05a2f6ec6d1d15ffad7914226c0c3e16b9cf；测量代码：
94913a4f836a3c106e08a1334cb81971cfd728c3。

实现次序：Clock→Statistics 成功→窄准备→worker Visuals∥caller Movement→join
→原序结构提交→Recovery→Lifecycle→Vision→Capture。worker 不借用可变 ECS。
Visuals maps 转移所有权，泛型访问适配器复用原阶段算法，主线程原序执行
Spawn/Remove；expected error 提交同样的成功前缀，panic 两侧 join 后返还 maps。

主门槛固定8条浮字，native2/4各三轮逐 tick ABBA/BAAB；同一parallel模式与
usize::MAX禁用门槛比较。100-tick 分块、10000 bootstrap、seed42；每轮完整
step均值改善、P99不回退且配对改善95%区间为正。P99使用两侧各19760个
原始step样本，CI使用9880个tick的配对均值。全部预热tick和慢尾保留。

四模式分别为 baseline / empty_fork / split_serial / parallel，均为按次私有
推进。普通step、默认native1、API18/schema5、Python生态和动作顺序保持。

原始输入沿用E3恢复链；正确性边界输入在本轮raw中冻结，不依赖再次生成时
的墙钟。所有full response、presentation/event流及final state检查完整；
逐步完整state/error/delta在13个边界场景×29step中核对。
