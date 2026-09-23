# Analysis — G004/G005修复与G006开放证据

## Observation

R3d2b在致死动作后权威状态和Python相等，但展示Player.units不相等；36配置均复现。边界输入审计还发现全角数字策略分、累计计数和对象转文字三种差异，完整状态比对可以发现“响应相同但统计不同”的情况。

## Hypotheses and instrumentation

H1是战斗删除规则不同；H2是展示增量漏了Player；H3是数值随机性；H4是Python/Rust字符串解析接受集不同。探针对同一初始状态、可信动作、注入墙钟/注册时间调用两个后端，保存全量状态和输出；同时消费独立Python展示副本。输入审计独立创建三场景，避免限流或先前累加污染。

## Evidence / root cause

- 权威36/36相同排除H1；Runtime.presentation此前没有Player投影，新增初始基线及死亡成员补丁后展示36/36相同，支持H2。重复Faction Player的历史first-match行为由37个契约覆盖，未改为删除所有匹配Player。
- `float("０.５")`在CPython接受；Rust字符串parse未转换Unicode十进制数字而失败。`int("１２")`同理；首次report保留原值，第二次累加才暴露14→2差异。不存在战斗RNG参与。转换680个Unicode15.1 Nd字符后，77数值契约及两个原始反例精确相等，支持H4、排除H3。
- 对象evidence原插入顺序在serde_json对象中被排序，随后py_display把键顺序写进字符串；不是JSON对象键排列的豁免项。修复数字后这条仍不同，G006明确OPEN，未使用容差或删字段。

## Limits

1852回归、36配置、6场景510节点重放验证这里的范围，不证明所有宽松Python输入、所有冷组件、完整网络/BOT等价。Unicode表以CPython3.13/15.1为基线；3.14及未来Unicode需另核验。Player投影开销变为初次全量/随后成员ID补丁，但权威成员集合扫描仍存在；没有时延/容量测量。输入频率、VLM视角/编码、真实LLM排行未在本阶段验证。

原始来源与校验：[manifest](manifest.yaml)、[README](README.md)、`results/`。
