# Analysis — bounded text presentation caches

## Observation and hypotheses

此前确认坐标每格每帧新Font+5次文字render；飘字虽有字体预热，每帧仍重建文字surface且不剔除屏幕外文字。
假设：缓存不变的文字、缓存静止视图的坐标overlay，可降低Python工作和栅格化频率，同时不改变显示内容/位置/淡出和博弈状态。

## Instrumentation

同一工具SHA、相同seed和随机条件顺序、相同5000U/1000已注册Agent/窗口/Fog/GC策略，旧版和修复版串行运行。
与上轮不同：120帧坐标关闭的地图稳定期，逐条件确认overscan job完成、surface存在且zoom匹配。两源均通过全部replay guard：source/tool clean、世界位置兵力不变、模拟时间冻结、5000驻留、Fog ON、1600测量帧完整和地图稳定。
之后10帧文字预热+100帧测量；不删除慢帧。另标记每次首次开启文字的cold_activation帧，只有每条件2个冷样本，因此用max表达冷启动结果。

## Evidence — full update P99

| 条件 | 旧版ms | 修复ms |
| --- | ---: | ---: |
| zoom1，坐标OFF | 13.442 | 13.693 |
| zoom1，坐标ON | 182.294 | 13.578 |
| zoom0.5，坐标OFF | 13.648 | 13.578 |
| zoom0.5，坐标ON | 736.375 | 15.521 |
| zoom0.5，坐标ON，每帧平移1px | 779.096 | 23.530 |
| 1000可见飘字 | 21.387 | 20.390 |
| 1000屏幕外飘字 | 19.359 | 16.995 |
| 1000组件，文字绘制关闭 | 17.626 | 21.004 |

这里的full update为GameEngine._update，包含ENV系统、绘制队列和display.flip；replay没有Agent pump，不包括帧率等待及Lab census。不能把这些数字直接当作自然Agent全闭环P99。
hidden1000的修复侧P99反而更高，说明系统噪声/其他工作仍影响整帧尾部；没有因该负对照不利而丢弃结果，不能从总P99的细小差异精确分摊文字成本。

## Evidence — causal local paths

| 路径P99 | 旧版ms | 修复ms |
| --- | ---: | ---: |
| zoom1坐标 | 174.119 | 0.006 |
| zoom0.5坐标 | 720.155 | 0.008 |
| zoom0.5连续平移坐标 | 755.431 | 2.833 |
| 1000可见飘字准备 | 2.542 | 0.967 |
| 1000屏幕外飘字准备 | 2.927 | 0.357 |

坐标稳态路径只计一次排队，真正overlay像素混合仍在flush里，不能把0.008ms误称为整个坐标显示的CPU总成本。
自然闭环与最慢帧归因单独保存在results/live.json，使用runtime的预热边界；两层wrapper按完整帧序号对齐，保留epoch offset稳定检查。

修复版自然闭环30秒预热+60秒：平均24Hz、1440帧=60模拟秒，整帧P99=41.331ms、max45.202ms；全部5000Units存活，接受4930次move/111次attack，同时移动平均120、最大167。
飘字同时平均4.269、最大11；文字准备P99=0.032709ms。旧诊断43.08ms与本次41.33ms来自不同自然动作轨迹，不宣称这1.75ms全部由文字缓存产生。
本次frameP99 guard通过，但观测响应/动作排队P99的100ms guard仍失败，原始失败值保留；该wrapper属于诊断，runtime自身not_diagnostic字段不构成新容量认证。

## Cold activation

修复版zoom1坐标首次开启整帧21.816/23.056ms；zoom0.5静止35.265/36.871ms；zoom0.5平移34.078/37.081ms。
这6个冷样本全部低于24Hz的41.667ms预算；4个zoom0.5冷样本超过30Hz的33.333ms预算，不宣称每次冷打开都保证30Hz。没有用延迟生成标签或逐帧少画部分标签掩盖冷启动。

## Root cause and implementation

坐标：只在视图变化时遍历可见格并重建overlay。只有新标签/字号变化才生成文字；前景和描边各渲染一次，合成4方向描边。固定视图使用不可变cull集合的身份和几何key进行O(1)检查，提交一个overlay。缓存仅一个视图/一个字号/该视图标签，离开视图的标签在重建时释放。
飘字：每个活动组件首次可见才生成文字surface，text/color/font/组件身份变化才失效。各组件独立surface以保持不同alpha。新效果在右/下屏幕外可在字体工作前跳过；左/上边缘用缓存的文字尺寸作完整矩形裁剪。每帧缓存只保留本次仍存活组件，不累计历史记录，不扫所有resident Units。

## Correctness and rejected alternatives

完整pytest912与结构契约94通过。新增13个用例验证稳态无逐格工作、视图/字号/resize/方向/世界切换、cache有界、低缩放/关闭、坐标描边像素、独立CRIT透明度、组件替换/删除、部分可见边缘和伤害像素等价。
坐标多级透明合成使用预乘alpha，像素oracle允许最多4级RGB整数舍入差；伤害像素与原路径逐字节相同。
首次尝试直接RGBA多级合成会使边缘变暗，已在测试中拒绝；对SDL_ttf padding行直接premul在本机pygame2.6.1产生错误像素，使用一次compact copy解决。不是改字体/去掉描边来换性能。[API语义](https://www.pygame.org/docs/ref/surface.html#pygame.Surface.premul_alpha)。
没有共享可变CRIT alpha surface，没有世界TTL或新ECS系统，没有关掉视觉反馈，没有更改ENV伤害/CD/移动/Agent观测规则。

## Limits

固定坐标视图O(1)指Python检查/提交；像素混合仍随窗口面积变化。变更视图O(Vvisible)，飘字更新/呈现O(Aactive)，首次文本栅格化还依赖字符串长度；不能称为整个渲染O(1)。
replay为两组100帧诊断，不是长时容量认证。自然live只有canonical一组60秒，不能泛化成高密度全图混战或保证所有UI/观测导致的慢帧消失。
无新Frontier；旧历史负结果和本轮hidden1000波动均保留。所有重要数字可从raw ZIP重新算出。
