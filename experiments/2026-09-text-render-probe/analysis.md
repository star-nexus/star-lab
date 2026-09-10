# Analysis — 坐标与伤害/CRIT飘字

## 1. Observation

用户在攻击后观察到数字/CRIT浮动卡顿，按0打开坐标也掉帧。
对照运行2600测量帧，源代码/工具clean、5000Units、Fog ON、Unit位置/兵力fingerprint不变、模拟时钟冻结等guard全部通过。

| 视角 | 格子数 | 坐标OFF frame P99 ms | 坐标ON frame P99 ms | 坐标路径P99 ms |
| --- | ---: | ---: | ---: | ---: |
| zoom1 | 577 | 18.143 | 181.022 | 171.487 |
| zoom0.5 | 2379 | 21.429 | 743.937 | 726.779 |

以上frame为GameEngine._update，包括ENV systems、render flush与display.flip；不包含Agent pump、帧上限sleep、Lab外部census。
每组200帧，两轮单独数据均保留：zoom1坐标ON的两轮P99为184.694/177.986ms；zoom0.5为746.136/739.615ms。

## 2. Competing hypotheses

- H1：坐标文字的重复构建导致大开销。被直接路径计时、开关对照、格子数变化支持。
- H2：伤害/CRIT文字本身导致当前千Agent闭环的约43ms尾部。自然战斗数据不支持其为主要来源。
- H3：只画了屏幕内飘字。代码和屏幕外1000条对照均反驳；屏幕外仍准备文字。
- H4：Font对象完全未缓存，第一次CRIT才加载字库。标准窗口已经缓存并预热20/24/28号字体，不能这样归因。

## 3. Instrumentation / diagnostic changes

只有Lab猴子补丁，STAR不变。计时BaseAnimation.render_damage_numbers、WindowAnimation._update_damage_numbers、MapRender._render_coordinates_optimized、RenderEngine.update及display.flip。
“伤害文字准备”包含query、font.render、set_alpha及入队；不包含随后统一flush。flush时间包含全窗口绘制，不能全部算给飘字。
replay合成文字75%数字/25%CRIT，elapsed0.5、velocity0；每项保留相同数量组件，hidden1000只屏蔽绘制，仍更新生命周期；offscreen1000只改变位置。
屏幕内计数是锚点落在窗口矩形，非像素遮挡面积统计。

live probe初始化时间早于runtime注册完成时间约0.594s，因此分析工具按一一对应帧序号连接原始记录，并统一使用runtime的30秒预热边界；1440帧，offset跨度小于0.5ms，完整保留对齐证据。probe自身summary使用其自身epoch，不混充runtime窗口数据。

## 4. Evidence

默认zoom0.15时，10/100/500/1000条飘字的文字准备P99分别为0.073/0.432/1.283/2.612ms；1000条屏幕外为2.981ms。
1000条关闭绘制时仍有动画更新P99=0.631ms；1000条正常绘制更新P99=0.415ms。不能将不同P99简单相减。

自然闭环30秒预热+60秒测量：5000Units始终存活，1000Agent，接受4906次move、115次attack；同时移动平均120、最大162。
平均世界24Hz，1440帧推进60模拟秒，整帧P99=43.077ms；观测响应P99=169.278ms，动作排队P99=166.012ms。既有严格frame/100ms请求guard为false，保留原状。

- 同时飘字平均4.442、P99=10、最大11；1440帧中1410帧有飘字，非无战斗负对照。
- 文字准备P99=0.053958ms、最大0.081583ms；动画更新P99=0.016917ms。
- 整帧最慢1%共有15帧：文字准备平均0.039375ms，最大0.079417ms，占这15帧总work的0.08618%。这不是文字最终blit占比。
- 同15帧Agent pump平均24.657ms、ENV update平均19.359ms（含所有渲染）；其中present平均1.643ms。文字准备并不足以解释整帧尾部。
- 完整窗口flush P99=3.907ms，包含地图/单位/UI/文字；不将其按飘字数量假分摊。

## 5. Root cause

坐标路径每帧、逐可见格重新`pygame.font.Font(None, font_size)`，白字render一次、黑描边render四次，5个surface入队；没有字体/标签surface缓存。可见格增多时，大量重复文字构建直接耗尽帧预算。
`map_render_system.py:676`入口在zoom<0.3提前退出。因此之前默认zoom0.15大规模实验没有这项标签绘制成本；不能把它作为历史44.54ms的原因。

飘字在`animation_system.py:191`逐个活动DamageNumber重新font.render，字体缓存/预热并未缓存整段文字surface；也没有屏幕外提前裁剪。因此大量同时飘字有额外负载，但本次canonical自然闭环中数量较小，准备成本不足以成为主要P99瓶颈。

## 6. Causal chain

坐标ON → 可见格数×每格新Font及5次文字渲染 → 坐标路径171/727ms → 整帧181/744ms。
自然战斗 → 平均4.4/最多11条活动飘字 → 文字准备P99 0.054ms → 对43ms整帧尾部贡献很小。

## 7. Rejected explanations / measurement correction

不能把攻击时动画停顿直接当成文字慢：整个主循环耗时增加，同样会让浮动动画断续。
不能把replay的所有整帧波动都归因于display.flip。原始记录中，empty第二轮慢帧集中在condition的第12–18帧，flush约10.5ms而present约1.3ms；首20帧平均25.29ms、末20帧12.69ms。切换缩放后的地图绘制缓存过渡是合理解释，但本工具未直接记录cache job状态，不宣称已完成该项根因证明。

## 8. Limits of the evidence

每条件只预热10帧，没有证明地图缓存完全稳定；全部早期慢帧仍纳入P99，没有事后删帧。replay整帧包含视角切换后的尾部，所以不能从damage1000与hidden1000的整帧P99差值推算关闭飘字净收益。独立文字路径计时、重复的坐标量级，以及自然live的慢帧归因仍可直接使用。
0.15坐标ON/OFF本来就都跳过；这两项是阈值负对照，不是标签优化。
自然live只有canonical布局和一组60秒诊断，不能代表密集混战、其他缩放/界面、用户实际手动攻击现场，更不能逐帧重建旧300秒实验的44.54ms。
runtime原not_diagnostic guard只识别其--attribute选项，本wrapper实际是diagnostic；该字段不构成本轮容量认证。
没有实现任何修复；Font/缓存策略的改善幅度需要后续受控修复A/B。本次不新增Frontier。

## 9. Raw evidence

[manifest](manifest.yaml)、[replay](results/replay.json)、[live](results/live.json)。两份raw ZIP保留原始frame记录、汇总与日志；两份compact ZIP保留全部决策相关指标和raw SHA/size。
