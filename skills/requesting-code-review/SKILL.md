---
name: requesting-code-review
description: 在完成任务、实现重大功能或合并之前使用，用于核实工作成果是否满足需求
---

# 请求代码评审

派发独立上下文的代码评审子代理（`subagent`），在缺陷连锁扩散前将其捕获。评审者只接收精确构造的上下文与 diff，绝不继承你的会话历史。

## 触发时机

- **必须请求：** `subagent-driven-development` 每个任务完成后、重大功能实现后、合并到主分支前。
- **按需请求：** 排错卡壳需要新视角、大规模重构前建立基线、复杂 bug 修复后。

## 操作步骤

1. **确定 Git 范围：** 获取起始 `BASE_SHA`（如任务起始点或 `git merge-base origin/main HEAD`）与当前 `HEAD_SHA = git rev-parse HEAD`。
2. **派发评审子代理：** 使用 [code-reviewer.md](code-reviewer.md) 模板派发 `subagent`，填入 `{DESCRIPTION}`、`{PLAN_OR_REQUIREMENTS}`、`{BASE_SHA}` 与 `{HEAD_SHA}`。
3. **分诊与响应：**
   - **Critical：** 立即修复。
   - **Important：** 在推进依赖该结果的工作或交付前修复并验证（独立已授权工作可继续）。
   - **Minor：** 记录备忘，留待后续处理。
   - **误报与范围外问题：** 任何轮次均可凭具体代码/运行反证驳回误报并记录适用版本；范围外发现若危及安全、数据完整性或当前验收，仍须作为阻塞项处理。
