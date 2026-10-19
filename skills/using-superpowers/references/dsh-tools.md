# DeepSeek Harness (DSH) 工具映射

技能正文用动作描述，在 DSH 上映射到以下工具。无对应物的动作按说明降级，不臆造工具名。

## 动作 → 工具

| 技能动作 | DSH 工具 |
| --- | --- |
| 读/写/改文件（`Read`/`Write`/`Edit`/`NotebookEdit`） | `read` / `write` / `edit` |
| 找文件 / 搜内容（`Glob` / `Grep`） | `glob` / `grep` |
| 执行命令（`Bash`） | `pwsh`（须遵守下方命令执行约定） |
| 编程式操作、并发调用工具、跑脚本 | `run_code` |
| 任务清单（`TodoWrite`） | `todo_write`（每次提交完整清单） |
| 派发子代理（`Task` / `Agent`） | `subagent`（独立上下文）或 `subagent_fork`（继承当前会话） |
| 多代理协作 | Agent Teams：`spawn_teammate` + `team_task_*` + `send_message` + `wait_agent` |
| 加载技能（`Skill`） | `skill`（或用户输入 `/技能名`） |
| 后台任务 | `run_in_background: true` → `job_output` / `job_kill` |
| 联网搜索 / 抓取（`WebSearch` / `WebFetch`） | `web_search` / `web_fetch` |
| 询问用户 / 计划模式 / 长期目标 / 交付文件 | `ask_user_question` / `exit_plan_mode` / `create_goal` / `present` |

## 子代理与计划模式

- **子代理：** `subagent` 在独立上下文执行自包含任务，不共享父会话历史，派发时必须提供完整提示词与上下文；并行独立任务优先用后台 `subagent` 并发执行。需要任务板协作时用 Agent Teams。
- **计划模式：** 用 `exit_plan_mode` 提交计划审批；进入 plan mode 前的技能规则照常适用。

## 命令执行（本仓库强约束）

本仓库全局约定禁止把 PowerShell 当普通 shell 使用：命令一律用 `run_code` 执行 Node.js，或仅用 `pwsh -Command "python <脚本>"` 启动 Python 脚本。

| 上游写法 | 本仓库写法 |
| --- | --- |
| `bash scripts/foo.sh` | `run_code` 执行等价 JS，或 `pwsh -Command "python scripts/foo.py"` |
| `chmod`、`jq`、`sed` 等外部工具 | 改用 Python / Node 原生实现 |
| `/tmp` 等 Unix 路径 | 用工作区临时目录或 `os.tmpdir()`；Python 临时脚本须在 `finally` 中自删 |

## DSH 不具备的机制

- **Hooks / 自定义 slash command：** 无 SessionStart 等 hook，通过插件 system prompt 或 `AGENTS.md` 约定；用 `/技能名` 替代 `/superpowers:*`。
- **路径与指令文件：** `CLAUDE.md` 对应 `AGENTS.md`（用户级 `~/.dsh/AGENTS.md`）；`~/.claude/` 对应 `~/.dsh/`（会话 `~/.dsh/sessions`、技能 `~/.dsh/skills` 或 `<项目根>/.dsh/skills`）。
- **Worktree 工具：** 无原生 worktree 工具，用 `git worktree` 脚本执行。
- **Frontmatter：** 只认 `name`（英文 kebab-case）与 `description`，可选 `whenToUse`、`metadata`、`disable-model-invocation`、`user-invocable`；忽略 `allowed-tools` 等字段。
