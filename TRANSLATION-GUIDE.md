# 翻译与 DSH 适配规范（所有子任务共用）

适用范围：`dsh-superpower/skills/` 下的全部文件。
目标：把上游 obra/superpowers **v6.4.1** 的技能内容全量中文化，同时把 Claude Code 专有内容改写成 DSH 等价物。**不保留英文副本。**

## 一、硬性规则

1. frontmatter 的 `name` **绝对不改**（英文 kebab-case，DSH 用它当技能名）；`description` 译成中文，保留"何时使用"的触发语义与关键词，长度尽量控制在 500 字符内。
2. 结构 1:1 保留：标题层级、列表层级、表格行列、代码块数量与语言标注、HTML 标签（`<EXTREMELY-IMPORTANT>`、`<SUBAGENT-STOP>` 等）。
3. 命令、路径、代码、标识符、文件内工具名保留原文，不翻译。
4. 语气强度等量保留：`MUST`/`NEVER`/`ALWAYS`/`ABSOLUTELY` → "必须 / 绝不 / 永远 / 绝对"，不得弱化。
5. 除第三节的适配改写外，不新增、不删减内容；不写"译者注"。
6. 不得残留成段英文（代码块、命令、术语、专有名词除外）。

## 二、术语表（统一译法）

| 英文 | 中文 |
| --- | --- |
| skill | 技能 |
| subagent / sub-agent | 子代理 |
| dispatch (a subagent) | 派发 |
| controller session | 主控会话 |
| plan / plan document | 计划 / 计划文档 |
| code review | 代码评审 |
| evidence | 证据 |
| verification | 验证 |
| red flag | 危险信号 |
| rationalization | 自我合理化 |
| checklist | 清单 |
| workspace | 工作区 |
| ledger / task brief | 台账 / 任务简报 |
| implementer / reviewer | 实现者 / 评审者 |
| baseline | 基线 |
| acceptance criteria | 验收标准 |
| human partner | **使用者**（唯一译法；不要用"你的搭档"这类变体） |

保留英文（不译）：TDD、worktree、linter、diff、commit、PR、prompt、token、cache、Agent Teams、red-green（可写"红-绿"）。

## 三、DSH 适配规则（与翻译同时完成）

完整映射见 `skills/using-superpowers/references/dsh-tools.md`。要点：

1. **工具名**：Read→`read`、Write→`write`、Edit→`edit`、Glob→`glob`、Grep→`grep`、TodoWrite→`todo_write`、Skill→`skill`、WebFetch→`web_fetch`、WebSearch→`web_search`、AskUserQuestion→`ask_user_question`、ExitPlanMode→`exit_plan_mode`。"用 X 工具"的句子统一换成 DSH 工具名。
2. **子代理**：`Task`/`Agent`/"dispatch a subagent" → `subagent`（独立上下文）或 `subagent_fork`（继承会话）。上游子代理提示词模板的抬头（如 `Subagent (general-purpose):`）改成"子代理（subagent）："。
3. **并行编排**：保留"并行"语义，实现写成"后台并发派发 `subagent` 后汇总"，或 DSH 原生 Agent Teams（`spawn_teammate` / `team_task_*` / `send_message` / `wait_agent`）。
4. **hooks**：DSH 没有 hook 机制。依赖 SessionStart / PreToolUse 的段落改写为"由 `AGENTS.md` 约定承担"，无法等价时删除该机制说明。
5. **slash command**：`/superpowers:xxx` 一律删除或改为"加载 `xxx` 技能"（DSH 支持用户直接输入 `/技能名` 显式调用）。
6. **路径**：`CLAUDE.md` → `AGENTS.md`；`~/.claude/...` → `~/.dsh/...`；会话记录 `~/.dsh/sessions`；用户级技能根 `~/.dsh/skills`、项目级 `<项目根>/.dsh/skills`。
7. **命令执行**：DSH 的命令工具是 `pwsh`，但本仓库 AGENTS.md 禁止直接使用 PowerShell。所有 `Bash`/bash/Unix shell 步骤改写为：
   - 一步能完成的 → `run_code`（执行 JavaScript，可在一次调用里并发调用多个工具）
   - 需要独立脚本的 → Python 脚本 + `pwsh -Command "python <脚本>"` 启动
   - 脚本必须自删除（`finally` 里删自己）；临时目录用工作区内目录或 Node 的 `os.tmpdir()`
   - 不引入 `jq`/`sed`/`tmux`/`chmod` 等 shell 工具依赖
8. **worktree**：DSH 没有原生 worktree 工具，涉及创建/切换/清理的步骤写成 `git worktree` 命令（通过脚本执行）。
9. **其它 harness**：出现 Codex / Pi / Cursor / Gemini / Hermes / Antigravity / Muse / OpenCode 的内容**删除**，只保留 DSH 语境。
10. **Anthropic/Claude 专有资料**：删除纯平台内容，通用方法论保留。

## 四、脚本与示例类文件

| 文件 | 处理 |
| --- | --- |
| `executing-plans/scripts/task-start`、`task-done` | 改写为 `task-start.py`、`task-done.py`（保留原功能，仅用 Python 3 标准库） |
| `subagent-driven-development/scripts/sdd-workspace`、`task-brief`、`review-package` | 同上，改 `.py` |
| `systematic-debugging/find-polluter.sh` | 改写为 `find-polluter.py` |
| `writing-skills/render-graphs.js` | 保留 Node 脚本，注释与提示中文化；顶部注明依赖 graphviz `dot`（可选） |
| `writing-skills/examples/CLAUDE_MD_TESTING.md` | 改名 `examples/AGENTS_MD_TESTING.md`，内容改为 DSH 版本，并同步更新所有引用 |
| `*.dot`、`*.ts` 示例 | 保留，注释中文化 |

**改文件名后必须 grep 旧名并更新全部引用。**

## 五、每个子任务的自检与报告

1. `name` 未变；`description` 为中文。
2. 用 grep 自查无残留：`\bTask\b`、`TodoWrite`、`\bBash\b`、`CLAUDE\.md`、`~/\.claude`、`/superpowers:`、`Claude Code`、`Anthropic`（保留的上游资料除外）。
3. 与上游同名文件对比结构：标题数、表格数、代码块数一致（因适配而删除的段落需在报告中逐条说明）。
4. 报告内容：改动的文件清单、删除的机制段落、改名的文件与引用更新位置、遗留问题。
