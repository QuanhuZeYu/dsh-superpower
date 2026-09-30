# dsh-superpower

面向 DeepSeek Harness（DSH）的 Superpowers 技能集合。

本项目基于 obra/superpowers v6.4.1 的技能内容，经过 DSH 专项适配与中文化，提供 15 个可直接加载的技能，包括：

- brainstorming
- control-loop
- diagnosing-superpowers
- dispatching-parallel-agents
- executing-plans
- finishing-a-development-branch
- receiving-code-review
- requesting-code-review
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
