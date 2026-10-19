---
name: diagnosing-superpowers
description: 当一次 Superpowers 会话出了问题、使用者想知道原因时使用——重复劳动、无视计划、反复卡壳、结果不佳、某个技能没被触发、"花了太久"、"为什么这么贵"、"它到底在干什么"——或想为当前会话、或按 id / 路径指定的历史会话整理一份带证据的问题报告（DSH 环境）。
---

# 排查 Superpowers

与使用者确认会话问题陈述，读取磁盘会话记录并生成带精确证据引用的报告。**你只报告事实与相关性，绝不诊断 Superpowers 技能缺陷或提议修改技能。**

**核心原则：** 每条发现必须引用 `path:line`（无引用即丢弃）；每个数值必须算自会话记录或实跑命令。全程遵守 `references/context-safety.md`（单行记录可能达 MB 级）与只读原则。

## 工作流

用 `todo_write` 跟踪以下步骤（步骤 5–6 仅在满足条件时执行）：

1. **受理问题：** 一次问一个问题，直至写清：目标会话、轮次范围、期望行为、实际行为及关注的指标（耗时、token、重复动作等）。**在使用者确认问题陈述前，绝不启动步骤 2–6**（若请求已明确指定具体事件或当前运行状态，则直接回答后再追问）。
2. **定位会话：** 按 `references/session-discovery.md` 解析出已核实的绝对路径，用首条人类提示词与时间戳确认历史会话（列出排除的候选及原因），枚举关联子代理会话。创建 `~/.dsh/diagnosing-superpowers/<session-id>/` 告知使用者，并按溯源规则填写 `templates/case.md`。
3. **七维并发分诊：** 先亲自读问题附近的记录（重点关注见下方速查表），再并发派发 7 个 `subagent`，分别传入 `case.md` 绝对路径、`prompts/analyst-common.md` 及 `prompts/` 下的 7 个维度文件（`skill-timeline.md`、`plan-adherence.md`、`repeated-work.md`、`stumbles.md`、`quality-evidence.md`、`request-conflicts.md`、`cost-and-time.md`；长记录按轮次切分）。
4. **生成报告：** 按序填满 `templates/report.md` 写入工作区并展示路径。报告 §7 仅陈述相关性，不评价技能好坏或给使用者提建议。
5. **脱敏导出（仅当使用者明确要求 bundle 时执行）：** 说明三种脱敏级别（`skeleton` 不含工具结果正文、`evidence` 仅含被引用事件正文、`full` 全部保留）供选择。按 `templates/bundle-README.md` 构建，交替派发 `prompts/scrub.md` 与 `prompts/scrub-audit.md` 直至返回 CLEAN。完成对账后展示 scrub 日志与文件清单，**获使用者批准后**再打包归档并提醒逐文件复核。
6. **相似会话排查（仅当被要求时）：** 将已确认发现转为签名，筛选候选并并发派发 `prompts/similar-session.md`，结果追加至报告 §9。

## 抱怨与重点维度速查（7 个维度均须运行）

| 使用者抱怨 | 步骤 3 优先阅读与报告重点 |
| --- | --- |
| “花了太久” / “为什么这么贵？” | `cost-and-time`、`stumbles` |
| “为什么多做这些活？” / “无视了计划” | `repeated-work`、`plan-adherence`（先查压缩事件行） |
| “它到底在干什么？”（仍在跑） / “技能没触发” | `skill-timeline`（仍在跑时标注“仍在进行中”） |
