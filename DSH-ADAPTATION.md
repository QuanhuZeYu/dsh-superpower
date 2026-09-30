# DSH 适配检查报告

检查对象：`skills/` 下 15 个技能（上游 obra/superpowers v6.4.1），76 个文件。文本总量 **433,876 字符**，其中 `SKILL.md` 本体 **168,882 字符（38.9%）**，其余为 `references/`、`prompts/`、`templates/`、`scripts/` 等支撑文件。

## 一、结论：需要适配，但不都需要大改

不改造直接用的后果：技能能被 DSH 正常加载（frontmatter 合规），但正文里的 `Task`、`TodoWrite`、`Bash`、`Skill` 等 Claude Code 工具名在 DSH 里不存在，模型会照着不存在的工具去调度；`using-superpowers` 的 "Platform Adaptation" 章节也认不出 DSH，不会去读任何映射文件。

按改造量分三档：

| 档位 | 技能 | 原因 |
| --- | --- | --- |
| **必须改** | using-superpowers、subagent-driven-development、dispatching-parallel-agents、executing-plans、writing-plans、requesting-code-review、diagnosing-superpowers、brainstorming、writing-skills | 大量工具名、hooks、slash command、脚本、外部 CLI 依赖 |
| **少量改** | using-git-worktrees、finishing-a-development-branch、systematic-debugging | 主要是 worktree 操作与 CLAUDE.md 引用 |
| **几乎零改** | receiving-code-review、test-driven-development、verification-before-completion | 纯方法论文本，不含工具名 |

## 二、通用替换规则（已落成文件）

已新增 `skills/using-superpowers/references/dsh-tools.md`（沿用上游 pi-tools.md 的格式），并在 `using-superpowers/SKILL.md` 的 Platform Adaptation 清单里登记了 DSH 一行。要点：

1. **工具名**：Read→`read`、Write→`write`、Edit→`edit`、Glob→`glob`、Grep→`grep`、TodoWrite→`todo_write`、Skill→`skill`、WebFetch/WebSearch→`web_fetch`/`web_search`、AskUserQuestion→`ask_user_question`、ExitPlanMode→`exit_plan_mode`。
2. **子代理**：`Task`/`Agent` → `subagent`（独立上下文）或 `subagent_fork`（继承会话）；"并行派发" → 后台 `subagent` + 通知汇总，或用 DSH 原生 Agent Teams（`spawn_teammate`、`team_task_*`、`send_message`、`wait_agent`）。
3. **命令执行**：DSH 的命令工具是 `pwsh`，但**本仓库 AGENTS.md 禁止直接使用 PowerShell** → 技能里的 `Bash` 示例一律改成 Python/Node 脚本（`run_code` 或 `pwsh -Command "python ..."`），临时脚本自删除。
4. **hooks**：DSH 没有 hook 机制。上游 `SessionStart` bootstrap 需换成插件注入的 system prompt section，或写进 `AGENTS.md`。
5. **slash command**：DSH 无自定义命令；替代是技能目录的 `/技能名` 显式调用（DSH 原生支持，技能默认 user-invocable）。
6. **路径与文件名**：`CLAUDE.md` → `AGENTS.md`；`~/.claude/` → `~/.dsh/`（会话记录 `~/.dsh/sessions`、技能根 `~/.dsh/skills`、项目级 `<项目根>/.dsh/skills`）。
7. **worktree**：DSH 无原生工具，`git worktree` 操作改用命令脚本。

## 三、逐技能改造清单（命中行数来自实际扫描）

| 技能 | 文本量 | 主要命中 | 具体要做什么 |
| --- | --- | --- | --- |
| using-superpowers | 21K（本体 3.2K） | subagent 43、Task 7、TodoWrite 2、plan mode 2、Skill 2、hooks 1 | 已登记 dsh-tools.md；正文"announce / todo per item / plan mode"等表述改为 DSH 工具说法 |
| subagent-driven-development | 52K（本体 32.6K） | subagent 101、shell 11、Task 5、worktree 5、hooks 3 | **最重**：controller/implementer/reviewer 派发改 `subagent`/`subagent_fork`；`scripts/`（sdd-workspace、task-brief、review-package）改为 Python/Node；台账路径避开 Claude 目录 |
| dispatching-parallel-agents | 6K | 子代理 12、Task 3 | 并行派发改后台 `subagent`，或 Agent Teams + 任务板 |
| executing-plans | 20K | subagent 18、worktree 5、slash 2 | `scripts/task-start`、`task-done` 改 Python/Node；worktree 依赖改 git 命令 |
| writing-plans | 11K | subagent 8、slash 3、Task 1 | 计划文档目录约定、评审子代理改 `subagent` |
| requesting-code-review | 9K | subagent 11、Task 2、worktree 1 | `code-reviewer` 派发改 `subagent` |
| diagnosing-superpowers | 41K | subagent 26、hooks 5、slash 5、CLAUDE 1 | 会话排查路径改 `~/.dsh/sessions`；hooks 相关删除或改写 |
| brainstorming | 82K | slash 17、shell 7、subagent 3 | 可视化伴侣（`scripts/server.cjs`、`/tmp/brainstorm`、bash 启动脚本、Windows 前台模式说明）需改路径与启动方式 |
| writing-skills | 107K | Anthropic 40、CLAUDE 18、subagent 15 | 技能测试流程原本调用 `claude` CLI，需改成 DSH 子代理 / `skill` 工具；Anthropic 最佳实践文档可保留但显式标注为上游资料 |
| systematic-debugging | 41K | worktree 3、CLAUDE 1 | 少量引用改写 |
| using-git-worktrees | 7K | worktree 40 | 全部操作改 git 命令脚本（本仓库禁 PowerShell） |
| finishing-a-development-branch | 8K | worktree 26 | 同上 |
| test-driven-development | 18K | — | 仅翻译 |
| receiving-code-review | 6K | — | 仅翻译 |
| verification-before-completion | 4K | — | **已完成中文样例**（原文另存 `SKILL.upstream.en.md`） |

## 四、中文化方案

范围选项（按工作量从小到大）：

- **A. 只译 SKILL.md 本体**：15 个文件、168,882 字符 —— 这是模型实际加载的部分，性价比最高。
- **B. 本体 + 技能正文直接引用的支撑文档**：再加 `references/`、`prompts/`、`templates/`（不含脚本与测试样例）。
- **C. 全量**：433,876 字符，含 writing-skills 的 107K、brainstorming 的 82K 等大块资料。

约定建议：

- `name` 保持英文 kebab-case **不改**（DSH 要求技能名匹配 `^[a-z0-9]+(?:-[a-z0-9]+)*$`）；`description` 译成中文，但保留"何时使用"的触发语义。
- 英文原文另存为 `SKILL.upstream.en.md`（DSH 只把 `<技能名>/SKILL.md` 当技能，其它文件不会被扫描，也不影响加载），便于和上游 v6.4.1 做 diff。
- 术语表（建议统一）：skill→技能、subagent→子代理、dispatch→派发、plan→计划、plan document→计划文档、code review→代码评审、evidence→证据、verification→验证、red flag→危险信号、rationalization→自我合理化；**TDD、red-green、worktree、linter、diff、commit/PR 等保留英文**。
- 强调性大写（`MUST`、`NEVER`、`EXTREMELY-IMPORTANT` 等标签）保留结构，正文用中文表达同等强度。

## 五、验收方式

1. frontmatter 校验：15 个技能 `name` 不变且合法、`description` 非空。
2. DSH 冒烟测试：把 `skills/` 挂成技能根，用 `skill` 工具逐个加载 15 个技能，确认无解析错误（上游版本已实测可加载）。
3. 结构对齐：与上游逐文件比较标题层级、表格数、代码块数，避免翻译时丢内容。
4. 术语一致性：脚本扫描译文中同一英文术语的译法是否唯一。
5. 残留检查：扫描是否还有 `Task`、`TodoWrite`、`Bash`、`CLAUDE.md`、`~/.claude` 等未映射写法。

## 六、完成情况（最终）

- [x] 上游 obra/superpowers **v6.4.1** 全量技能拷入（15 个技能）
- [x] **范围 C：全量中文化** —— 61 个文件、365,633 字符（清理后）
- [x] **瘦身 + 清除非 DSH 内容**：删除 15 个文件（其它 harness 映射、英文备份、brainstorming 可视化伴侣及其 bash 脚本、上游报 issue 流程），见 `CLEANUP.md`
- [x] **DSH 适配**（与翻译一次完成）：工具名映射（`read`/`write`/`edit`/`glob`/`grep`/`todo_write`/`skill`/`subagent`/`run_code`…）、移除 hooks 与 slash command、路径改 `AGENTS.md`/`~/.dsh`、6 个 shell 脚本改写为 Python（无第三方依赖、临时文件自删）、清除其它 harness 内容
- [x] 新增 `skills/using-superpowers/references/dsh-tools.md`，并在 `using-superpowers/SKILL.md` 的 Platform Adaptation 中登记

### 验收结果

| 验收项 | 结果 |
| --- | --- |
| `scripts/verify-translation.mjs`（frontmatter + 残留 + 悬空引用 + 与上游结构对比） | **0 错误、0 悬空引用**、5 条警告（3 条为 `session-discovery.md` 的有意 DSH 改写带来的结构变化；2 条为白名单：`dsh-tools.md` 映射表左列与 `anthropic-best-practices.md` 的来源说明） |
| DSH 逐个技能加载冒烟 | **15/15 通过**，`provider=filesystem`、`resourceBase` 正确，正文 1.3K–14.9K 字符 |
| 术语统一 | `human partner` → 使用者，全库 0 残留 |
| 跨文件契约 | 台账格式统一为中文（`# SDD 台账 — 计划：…`、`任务 <N>：完成`、`裁决：…`）；worktree 落点统一 `.worktrees/`；计划 schema 章节名 `## Global Constraints` / `## Review Focus` **保留英文**（引用方一致，避免脚本失配） |
| 脚本 | 6 个 Python 脚本（task-start/task-done/sdd-workspace/task-brief/review-package/find-polluter）均由子任务实测，含退出码、边界与冲突消歧用例 |

### 结论

技能包已可在 DSH 中直接使用：把 `skills/` 挂成技能根（`~/.dsh/skills` 或 `<项目根>/.dsh/skills`）即可，DSH 只扫描一层，本目录结构天然匹配。上游同步方法与版本锚点见 `UPSTREAM.md`。
