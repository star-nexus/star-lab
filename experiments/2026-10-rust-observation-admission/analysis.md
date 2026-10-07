# Analysis — E8

## Hypothesis

已接纳连续只读请求可以共享 census、公共事实编码与重复 panel，且逐请求执行/返回/计数顺序保持。

## Instrumentation

仅包装冻结单请求 pump 的原 heappop，读取最多四个堆前缀；不批量弹出、不执行额外查询。诊断探针和 300 组前缀及插入事件契约检查已通过。正式性能须关闭诊断。

## Evidence / limits

P0 待测。历史相邻查询不是当前接纳证据。
