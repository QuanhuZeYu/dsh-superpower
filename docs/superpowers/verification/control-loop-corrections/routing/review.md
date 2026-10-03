# 路由与反馈闭环只读审查

最终结论：无未关闭的 Critical / Important 问题。首次审查发现的 2 项 Important 已由父代理修正，受影响段局部复核通过。未发现本次改动把不可逆动作的授权门槛放宽。以下结论是静态文本审查，不声称已完成实际会话行为测试。

## 修正后局部复核

- [using-superpowers:16](<D:/Code/dsh-plugins/dsh-superpower/skills/using-superpowers/SKILL.md#L16>) 已改为仅当任务需要创建或改变行为且设计尚未明确时加载 brainstorming；明确纯阅读、审查和已有方案不因切换模式新增设计流程。复读第 10–19 行，Important 1 关闭。
- [brainstorming:160](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L160>) 的前进边已明确“约定审阅已通过，或无需额外审阅且授权齐备”；第 164–170 行统一了终态与探针段，保留诊断重评；第 253–261 行仍要求修正后复核、用户约定审阅以及新增授权范围的必要决定。复读第 135–176、252–261 行，Important 2 关闭。
- 最终 brainstorming 的 totalLines 为 261；其余首次完整读取范围见下表。下面保留首次发现作为关闭记录，其中原始行号对应首次审查版本，后续段落可能因父代理编辑移动一行。源文件修正均由父代理实施，本审查者仅更新报告。

## 范围与证据

审查当前工作树中的五份技能；以 [before.json](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/routing/before.json>) 为旧版。使用 read 读取文本，长文件继续分段读取到 totalLines；旧版 JSON 的长行被工具截断后，使用 Node 解析完整文件。没有修改技能、使用 PowerShell 或派发子代理；不评执行技能及 writing-skills 的并行修改。

| 文件 | 完整读取行范围 |
| --- | --- |
| [using-superpowers:1](<D:/Code/dsh-plugins/dsh-superpower/skills/using-superpowers/SKILL.md#L1>) | 1–55 |
| [brainstorming:1](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L1>) | 1–262 |
| [receiving-code-review:1](<D:/Code/dsh-plugins/dsh-superpower/skills/receiving-code-review/SKILL.md#L1>) | 1–206 |
| [systematic-debugging:1](<D:/Code/dsh-plugins/dsh-superpower/skills/systematic-debugging/SKILL.md#L1>) | 1–282 |
| [writing-plans:1](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-plans/SKILL.md#L1>) | 1–196 |

## 已关闭 Important 1：plan mode 仍会无依据地加载 brainstorming

证据：[using-superpowers:16](<D:/Code/dsh-plugins/dsh-superpower/skills/using-superpowers/SKILL.md#L16>) 保留“进入 plan mode 之前：如果你还没有做过 brainstorming，先加载 brainstorming 技能”。这条无条件入口不检查任务是否涉及设计，与同文件第 10、14 行的“任务明确匹配”“不匹配就停止套用”，以及第 28 行纯阅读不触发 brainstorming 的边界不一致。旧版也有这条规则，本轮删掉 1% 规则后仍留下另一条无依据加载通道。

触发场景：用户要求在 plan mode 中进行只读调查或审查，需求不涉及产品设计；仅因为进入该模式，仍必须加载 brainstorming。即使随后停止套用，也已经发生了本次目标要求消除的无依据加载，并可能引出分类、设计及规格流程。

最小修正：把入口限定为“进入 plan mode 前先核对是否需要设计探索；仅当任务明确匹配 brainstorming 且尚未加载时才加载”。保留用户明确点名技能的优先规则。不要把 plan mode 本身当作技能适用证据。

## 已关闭 Important 2：brainstorming 流程图仍缺少沿用自主授权的出口

证据：[brainstorming:138](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L138>)、[brainstorming:158](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L158>) 至第 160 行把规格自审后的唯一前进路径写成“规格通过约定审阅？”→“已认可”→writing-plans，另一个出口只有“要求修改”。没有“用户未要求该节点审阅，且已有授权覆盖当前步骤”的出口。附近的 [brainstorming:166](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L166>) 仍写“有界：认可之后”，[brainstorming:171](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L171>) 仍用“呈现探针、得到点头”描述阶段。

冲突依据：同文件 [brainstorming:35](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L35>) 明确允许已授权自主实施后直接推进；第 117 行仅在约定节点要求评审；[brainstorming:257](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L257>) 更明确写“用户要求该节点审阅时等待回复；已授权自主推进时继续编写计划”。图中的“已认可”不能被理解为“用户看过尚不存在的规格”，正文也禁止把未经审阅的产物称为已认可。

触发场景：用户已经授权完成架构工作且未要求逐阶段审阅，规格写完并自审通过。按正文可以继续，按图却没有无须用户再次认可的路径，代理容易停下来重复索取审阅。这直接影响本轮取消重复授权的目标。

最小修正：在自审后显式判断“此节点是否约定用户审阅”；需要时等待并按反馈修订，不需要且授权与必要决定齐备时直接进入 writing-plans。也可把现有前进边改成“约定审阅已通过，或无需该节点审阅且已有授权覆盖”，并将附近“认可之后”“得到点头”统一为“授权与必要输入齐备”。保留用户明确要求的审阅，不把无需新审阅表述成产物已获审阅。

## 未发现此级别问题的其余目标

- 降级：[brainstorming:70](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L70>) 至第 73 行明确由证据升级或降级，要求保留验收、禁止用路径变化跳过用户审阅；旧版单向棘轮已删除。
- 局部暂停：[receiving-code-review:43](<D:/Code/dsh-plugins/dsh-superpower/skills/receiving-code-review/SKILL.md#L43>) 至第 48 行，以及第 56–57、104–111、199–201 行，规则、顺序与两个示例一致地先核对依赖，再推进独立已授权事项；未保留旧版“任一不清便全部停工”的规则。
- 次数与架构：[systematic-debugging:199](<D:/Code/dsh-plugins/dsh-superpower/skills/systematic-debugging/SKILL.md#L199>) 至第 211 行把失败转为反馈通道检查、假设重评和最小实验；明确失败次数不能单独证明架构错误。快速参考与修复策略未继续用次数推出架构结论。
- 修正后反馈：[brainstorming:254](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L254>) 与第 257 行，以及 [writing-plans:171](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-plans/SKILL.md#L171>)，都要求就地修正后复核受影响范围，未要求无差别重跑全部评审。
- 真实验收：[using-superpowers:38](<D:/Code/dsh-plugins/dsh-superpower/skills/using-superpowers/SKILL.md#L38>) 保留运行证据约束；[systematic-debugging:181](<D:/Code/dsh-plugins/dsh-superpower/skills/systematic-debugging/SKILL.md#L181>) 至第 197 行保留症状、修复与验证；[writing-plans:139](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-plans/SKILL.md#L139>) 至第 147 行保留实机复测、交付配置与原始反馈来源。
- 用户明确要求的审阅：[brainstorming:36](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L36>)、第 73、257 行，以及 [writing-plans:175](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-plans/SKILL.md#L175>) 至第 177 行仍明确保留。计划询问模板有适用前提，没有单凭模板认定为新增审批要求。
- 不可逆动作授权：[brainstorming:37](<D:/Code/dsh-plugins/dsh-superpower/skills/brainstorming/SKILL.md#L37>) 至第 39 行保留必要决定与越权阻塞；第 67–73 行规定升级不扩大授权；[using-superpowers:43](<D:/Code/dsh-plugins/dsh-superpower/skills/using-superpowers/SKILL.md#L43>) 要求发现不可逆后果时重评；[writing-plans:175](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-plans/SKILL.md#L175>) 只允许目标、风险和范围未变时沿用已有自主授权。未见本轮新增“设计通过即可自动授权外部发布/不可逆动作”一类规则。

以上是审查发现与最小建议，未实施任何源文件修正。
