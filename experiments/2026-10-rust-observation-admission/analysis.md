# Analysis — E8

## Hypothesis

已接纳连续只读请求可以共享 census、公共事实编码与重复 panel，且逐请求执行/返回/计数顺序保持。

## Instrumentation

仅包装冻结单请求 pump 的原 heappop，读取最多四个堆前缀；不批量弹出、不执行额外查询。诊断探针和 300 组前缀及插入事件契约检查已通过。正式性能须关闭诊断。

## Evidence / limits

P0 待测。历史相邻查询不是当前接纳证据。

## P0 measured diagnosis

1943 measured observations; 1106 (56.92%) belonged to legal 2–4 query candidate segments. No batching was executed. Full 12148 requests, 2617 ticks and 2617 presentation events replayed identically, including final authority. 19 pressure samples were normal; peak RSS 695.9 MiB.

| Kind | Samples | Individual fact build ms | Shared fact build ms | Individual/shared panel builds |
|---|---:|---:|---:|---:|
| 1-same | 10 | 1.181 | 0.986 | 5/5 |
| 2-mixed | 10 | 2.377 | 1.659 | 10/10 |
| 2-same | 10 | 2.499 | 0.968 | 10/10 |
| 3-mixed | 10 | 3.645 | 1.752 | 15/15 |
| 3-same | 10 | 3.814 | 1.082 | 15/15 |
| 4-mixed | 10 | 4.228 | 1.790 | 20/20 |
| 4-same | 1 | 4.734 | 0.955 | 20/20 |

Faction timings include census and public encoding; never add nested times. Singles-before-shared is warm-biased: singleton difference demonstrates noise. These are removable-build screening data, not authenticated service improvement. No repeated panels were found in sampled segments. P0 window Hz/queue guards failed; diagnostic overhead/slow samples all retained, no capacity validation. Actual cache residency remains to be measured in P1. The failed normalization probe and resource-interrupted smoke remain archived; neither counts as workload pass.
