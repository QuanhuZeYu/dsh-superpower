# dsh-superpower

面向 DeepSeek Harness（DSH）的 Superpowers 技能集合。

本项目基于 obra/superpowers v6.4.1 的技能内容，经过 DSH 专项适配与中文化，提供 17 个可直接加载的技能（其中 15 个来自上游，另含 DSH 专项 control-loop 与 runtime-driven-development），包括：

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

- [TDD](skills/test-driven-development/SKILL.md)：稳定契约、纯逻辑或使用者指定测试先行时，先取得有效失败测试，再做最小实现。
- [运行时驱动开发](skills/runtime-driven-development/SKILL.md)：真实环境、设备、UI、时序和集成问题，以日志探针、开发期断言和实机反馈推进；允许先建立最小实现，不强制先写自动化测试。

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
