# Decision — 保留显式批次共享，容量目标继续开放

**Status:** accepted implementation / OPEN capacity  
**Decision date:** 2026-09-09  
**Validated STAR commit:** `626d3a8db900fc18599bc96206bc76b960826999`  
**Validated STAR tag:** `p3-read-batch-pre-squash-2026-09-09`

## 1. Decision

保留 owner-thread 同步短批次API，缓存只活在调用内。普通逐条入口保持可用，不自动接入Protocol/Hub；不修改视野、碰撞、移动预算或攻击规则。

## 2. Decision drivers

保持原有博弈信息与权限；保序而不重排动作；独立1Hz基线；全部成本和积压可见。

## 3. Measured alternatives

single与batch-off在3000/1000均约11.8%完成；batch-on约21.1%。首版预取过量被修正；5K改善而10K无稳定收益。

## 4. Why this option

冻结世界跨源oracle逐字节相同；899生产回归和10Lab测试通过。公共构建/命中计数及计时证明重复计算减少。

## 5. Why not the alternatives

不采用跨帧TTL、延迟情报、删减观察字段或叠格改变：这些改变会影响benchmark规则或需要新的授权范围。
未将decode省略，未把30s决策当成低频观测。

## 6. Headroom and scaling rationale

32条/12ms只是有限批次起点，不是容量保证。当前目标规模全部未过线，不发布Frontier，不启动无望通过的容量认证长测。

## 7. Risks / trade-offs

首张快照代价大时缓存可能变慢；完整公共载荷仍重复编码和发送。下一项应依据每批首次构建与响应输出成本选择，不能直接开启跨帧缓存。

## 8. Revisit when

需要接入路由/Hub并发、允许世界写入穿插、改变观测字段、提高规模/观测频率时重新验证；不得将本API作为线程安全锁。

## 9. Provenance

见README、manifest、analysis、results与Lab恢复入口。开发分支保留用于追溯；集成须先annotated tag，再squash。


## 10. Integration

Pre-main `08c857e5df39f671c5a13bf04b9af9aac0800e78`; annotated tag object `2f6f124132e20ccf515684ad36bf39f4c561ac3f` pins developer `626d3a8db900fc18599bc96206bc76b960826999`.
`git merge --squash` produced main `906386312d70d77af25e4b4da883f6dd5b0fe5ef`. Main has exactly one parent and its tree matches the tagged development tree. Post-integration production regression:899 passed.
