# 独立只读评审

最终结论：未发现尚未解决的 Critical / Important。初审 Important 已由实现者修正，本评审已局部复核关闭。评审者未修改源文；本报告不是新一轮行为验证。

## 已关闭的 Important：好示例示范无条件派发与无依据收益承诺

位置：[SKILL.md:248–249](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/SKILL.md#L248>)。

原文将“始终使用子代理（节省 50-100 倍上下文）。必需：工作流使用 [other-skill-name]。”标为“✅ 好”。具体触发：作者按本节复制交叉引用示例，用于简单检索或成本不适合委派的任务时，会把“始终使用子代理”作为必须遵守的流程，并以未附来源、条件或实际计算的倍数作为收益依据。这与本文按用户结果、代价和适用边界选择方法的要求，以及说服参考不得用强语气代替证据的要求冲突。它是既有遗留，但仍处于本轮明确要求的“规则与示例一致”范围。

最小建议：保留交叉引用的示例目的，将该句改成有条件的引用，如“需要独立且可并行的调查时，参考适用的任务委派技能；按任务成本决定是否委派。”删除无来源倍数。只需按静态矛盾修正并核对引用，不应为此制造行为 RED，也不能因此宣称成本已下降。

局部复核：实现者已将该句改为独立委派适用且预期收益足以覆盖协调成本时引用相关流程。读取源文与 final 对应段确认一致，无条件派发和无来源倍数已删除。验证说明与最终静态记录明确仅经静态复核，after 与实际提示保留。该 Important 关闭。

## 核对通过的重点

- 用户结果、授权、质量、成本和边界先于规则服从：[SKILL.md:14](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/SKILL.md#L14>)、[测试参考:7](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/testing-skills-with-subagents.md#L7>)与[示例:7](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/examples/AGENTS_MD_TESTING.md#L7>)一致。
- 预算停止不等于通过：[SKILL.md:514](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/SKILL.md#L514>)明确不能把未满足验收改为通过；[测试参考:22](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/testing-skills-with-subagents.md#L22>)要求耗尽后重评和披露；[新版原始输出:29](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/skill-testing/candidate-output.md#L29>)和其后完成段也明确区分预算结束、失败及通过。
- 作者不能为结果移动验收：[SKILL.md:22](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/SKILL.md#L22>)要求运行前定义且来自用户目标；[测试参考:56](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/testing-skills-with-subagents.md#L56>)允许修正错误测试设计但须标记失去可比性，禁止挪动标准制造 GREEN。未发现允许以作者便利降低用户验收的条款。
- 未复现不造红，静态修正不冒充行为收益：[SKILL.md:26](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/SKILL.md#L26>)、[测试参考:16](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/testing-skills-with-subagents.md#L16>)、[示例:85](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/examples/AGENTS_MD_TESTING.md#L85>)一致。
- 固定五次、无限堵洞、唯一预设 A、删除用户已有工作的指导已被相应核心条款替换。[说服参考:26](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/persuasion-principles.md#L26>)明确保存现有工作并使用有界验证；元测试只生成待核对假设。
- 参考型技能采用检索、准确性、应用及必要可达性验证；[示例:26](<D:/Code/dsh-plugins/dsh-superpower/skills/writing-skills/examples/AGENTS_MD_TESTING.md#L26>)保留明确范围和独立验收，不把无服从冲突当成无需验证。

## 原始证据与版本核验

完整读取当前四份源文，长文件按 read 分段至 totalLines；读取 before、after、final 快照以及完整实际旧新提示、输出、预登记、静态检查和验证说明。使用 JavaScript 对读取结果作文本比较：

- 当前四文与 final 对应快照逐行一致。
- [旧版实际提示](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/skill-testing/baseline-actual-prompt.txt>)内嵌三文与 before 对应快照一致；[新版实际提示](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/skill-testing/candidate-actual-prompt.txt>)内嵌三文与 after 对应快照一致。两组任务正文相同，末尾指令仅输出文件名不同。
- 初审时 after 与 final 主文仅推荐资料措辞不同；局部修正后另增加上述交叉引用示例调整。测试参考和示例相同。最终说服参考没有进入已测新版提示，故只得到静态审查覆盖。
- [旧版原始输出:5](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/skill-testing/baseline-output.md#L5>)明确“本次未复现预期违规”，并允许静态纠错、保留工作；它仍保留固定五次门槛。[新版原始输出:11](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/skill-testing/candidate-output.md#L11>)按风险、可逆性、波动与预算选择验证，且明示旧版本来成功不足以证明行为改善。现有[验证说明](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/skill-testing/verification-notes.md>)没有把这组对照包装为 RED-GREEN，结论与原文相符。
- [无效截断输出](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/skill-testing/invalid-truncated-output.md>)在参考内部场景上作答，记录明确排除其有效对照资格；没有用它制造旧版失败。

## 验证范围与限制

本评审只判断指定文档在用户修正目标下的静态一致性，以及现有决策证据是否支持报告。未派生子代理、未调用 PowerShell、未修改源文、未执行事故恢复或链接访问，也未验证外部研究。精确模型采样条件未在现有说明中固定，不推断跨模型收益。原始决策输出及输入可核对，但本轮未另行审计运行时会话存档。最终说服参考、主文推荐资料措辞和交叉引用示例修正只得到静态覆盖，不能称为已通过行为复测。

已关闭好示例与方法原则的静态矛盾；未宣称它曾导致实际过度派发，也未宣称修正已改善行为，无需为形式扩大行为测试。
