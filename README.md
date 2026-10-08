# dsh-superpower

面向 DeepSeek Harness（DSH）的 Superpowers 技能集合，**最大特色是削减 AI 编程中的过度工程化**：让设计、实现、测试和协作流程围绕实际需求与运行反馈收敛。

本项目基于 [obra/superpowers](https://github.com/obra/superpowers) v6.4.1，经过 DSH 专项适配、中文化与流程改进。

## 核心特色：削减过度工程化

从明确目标出发，先跑通最小真实闭环，再用有依据的反例和反馈修正，满足验收后停止。将这条原则贯穿整个开发过程：

- **设计从简。** 先明确目标、职责与不变量，优先复用已有能力。新增抽象、配置、缓存、重试或兼容层须对应已知需求、真实边界或运行反馈。
- **流程与任务相称。** 探针、有界改动和架构性工作采用不同深度的设计与计划；已有授权内的普通技术判断由代理承担，减少重复确认、文档和评审。
- **验证聚焦真实行为。** 复用现有运行入口，针对需求约束、调用边界和真实故障补充必要反例。新增测试应能防住具体回归或替代一次真实验证。
- **保留正确实现。** 自动验证与实机验证都允许先建立最小可运行实现；不为凑先行失败记录撤销正确代码，也不为流程完整性增加无价值测试。
- **以反馈决定下一步。** 按“观测 → 判断误差 → 最小动作 → 验证反馈 → 修正”推进，达到约定验收后收尾。

从简仍须保持职责清晰、遵守已知约束并完成必要验证。每项工程投入都应服务于可说明的需求或可核实的问题。

## 技能集合

提供 17 个可直接加载的技能（其中 15 个来自上游，另含 DSH 专项 control-loop 与 runtime-driven-development）：

- brainstorming
- control-loop
- diagnosing-superpowers
- dispatching-parallel-agents
- executing-plans
- finishing-a-development-branch
- receiving-code-review
- requesting-code-review
- runtime-driven-development
- subagent-driven-development
- systematic-debugging
- test-driven-development
- using-git-worktrees
- using-superpowers
- verification-before-completion
- writing-plans
- writing-skills

## 使用方式

将 skills/ 目录作为 DSH 技能根即可：

- 用户级：~/.dsh/skills/
- 项目级：<项目根>/.dsh/skills/

DSH 会扫描技能根下的一层目录，并加载 <技能名>/SKILL.md。

## 开发模式

两种模式共用“最小真实闭环 → 必要反例 → 反馈修正 → 回归交付”的推进方式，按任务选择反馈通道：

- [自动验证模式（保留 TDD 技能名）](skills/test-driven-development/SKILL.md)：适用于稳定契约、纯逻辑及能够自动运行的场景，以真实路径、独立期望和必要反例验证行为；不强制测试先于实现或反例先失败。
- [运行时驱动开发](skills/runtime-driven-development/SKILL.md)：适用于真实环境、设备、UI、时序和集成问题，以目标实例、日志探针、必要的开发期断言和同场景实测取得反馈。

可以直接说“这次用 runtime-driven-development，主要靠日志探针和实机复测”。未指定时由 [using-superpowers](skills/using-superpowers/SKILL.md) 按任务选择，模式随计划、实现者与评审者传递。两种模式都必须保留真实反馈，不能用静态分析或编译成功替代目标行为的验证。

## 适配内容

- 使用 DSH 原生工具名与子代理接口
- 将 Claude Code 路径与约定替换为 DSH 约定
- 移除其它 harness 的加载资产
- 全量中文化技能正文及支撑文档
- 保留上游 MIT 许可证

详细说明见 DSH-ADAPTATION.md、UPSTREAM.md 和 VERIFY-TODO.md。

## 来源与许可证

上游项目：https://github.com/obra/superpowers，版本 v6.4.1。

本项目沿用上游 MIT 许可证，见 LICENSE。
