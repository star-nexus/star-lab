> 2026-10-08 精简修订：普通完整参考两次已通过，不再重跑。旧no_reuse完整组按用户要求取消，7543节点前缀只归档不计通过。当前仅执行规范encoded候选并复用已核验的旧扩展完整指纹；targeted/实际接纳仍待完成。见[预注册](results/p2-streamlined-preregister-20261008.json)。早期矩阵描述为历史计划，已被本修订覆盖。

# Decision — E8

**Status:** proposed; P0 complete, P1 authorized

## Decision

Proceed to a minimal owned-cache prototype because about 57% of measured queries have eligible continuous segments and repeated census/public builds are demonstrated. Do not claim speedup from profiled handler batching. First prove no_reuse equivalent to single, then encoded equivalence and a short non-diagnostic service screen.

## Resource policy

Latest user explicitly authorizes continuing under memory warning. E8 now uses telemetry only: no automatic pause, kill or runtime timeout. Pressure evidence still governs formal timing validity; no silently accepting interfered performance samples.

## Limits and revisit

Original window operational guards failed; P0 is diagnosis. Existing GAPs/capacity/Frontier unchanged; 5000 Agents deferred; default research off. Later implementation/benefit gates govern P2–P4 and adoption.

## Provenance

[Results](results/p0-complete.json), [Integrity](results/p0-integrity.json), [Raw](artifacts/e8-p0-20261007-raw.zip).

## P1 decision

小型契约及独立旧扩展短宿主对照通过；公共build下降且代表service未明显恶化，允许进入P2。单次screen不是正式收益，candidate普通路径对旧扩展的未配对回退保留，不隐藏。P2以固定6ec8e05、同wheel和独立旧扩展比较。只正确性校验，不进入P3或默认；targeted全部通过后才宣布P2完成。

## Accounting correction decision

发现null==null断言后不把旧计数检查称通过；原始证据完整保留并单独勘误。允许当前普通全状态轨迹自然结束，身份门槛阻止旧诊断进一步进入cached模式。隔离修正wheel、修正oracle新预注册后按序继续，不因本缺陷杀掉正在执行的有效ordinary轨迹，不启动P3。
