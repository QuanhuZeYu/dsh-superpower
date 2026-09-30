# 清理记录（移除非 DSH 内容）

执行时间：2026-09-23T06:19:34.886Z
依据：范围 C（全量中文化）+ 要求"瘦身、清除非 DSH 部分"（不保留英文副本）。

## 已删除：15 个文件，约 84 KB

| 文件 | 原因 |
| --- | --- |
| `using-superpowers/references/{antigravity,claude-code,codex,gemini,hermes,muse,pi}-tools.md` | 其它 harness 的工具映射；DSH 只保留 `dsh-tools.md` |
| `verification-before-completion/SKILL.upstream.en.md` | 英文备份，按要求瘦身 |
| `brainstorming/visual-companion.md` | 依赖 Claude Code 的可视化伴侣说明 |
| `brainstorming/scripts/{frame-template.html,helper.js,server.cjs,start-server.sh,stop-server.sh}` | 该伴侣的 Node 服务与 **bash 启动脚本**；与 DSH/Windows 环境及本仓库"禁止 PowerShell、改用 Python/Node"的约定不符 |
| `diagnosing-superpowers/references/github-issues.md` | 面向上游 GitHub 仓库的报 issue 流程，与本地 DSH 使用场景无关 |

清理后：**62 个文件、365,633 字符**（原 77 个文件、433,876 字符）。

## 保留但需改造（在翻译阶段一并处理）

| 文件 | 处理 |
| --- | --- |
| `writing-skills/anthropic-best-practices.md`（46K） | 保留通用技能写作原则，去掉 Claude/Anthropic 平台假设 |
| `writing-skills/examples/CLAUDE_MD_TESTING.md` | 改名 `AGENTS_MD_TESTING.md`，改为 DSH 版本 |
| `executing-plans/scripts/{task-start,task-done}` | 改 Python |
| `subagent-driven-development/scripts/{sdd-workspace,task-brief,review-package}` | 改 Python |
| `systematic-debugging/find-polluter.sh` | 改 Python |
| `diagnosing-superpowers/references/session-discovery.md` | 改为 DSH 会话记录（`~/.dsh/sessions`） |

## 连带影响

- `brainstorming/SKILL.md` 中对 `visual-companion.md` 与 `scripts/` 的引用，在翻译时必须同步移除。
- `using-superpowers/SKILL.md` 的 Platform Adaptation 段已改为仅 DSH。

## 恢复方式

上游随时可取：`https://codeload.github.com/obra/superpowers/tar.gz/refs/tags/v6.4.1`（tag / commit 见 `UPSTREAM.md`）。
