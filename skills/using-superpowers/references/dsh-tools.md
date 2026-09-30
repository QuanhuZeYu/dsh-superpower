# DeepSeek Harness (DSH) 工具映射

技能正文用动作描述（"派发一个子代理"、"建一条 todo"、"读文件"、"跑一条命令"）。在 DSH 上这些动作落到下面的工具。**没有对应物的动作，按各节说明降级处理，不要臆造工具名。**

## 动作 → 工具

| 技能里的动作 | DSH 对应 |
| --- | --- |
| 读文件（`Read`） | `read` |
| 写文件（`Write`） | `write` |
| 改文件（`Edit`） | `edit` |
| 按路径找文件（`Glob`） | `glob` |
| 搜内容（`Grep`） | `grep` |
| 执行命令（`Bash`） | `pwsh`（DSH 的命令工具，见"命令执行"一节的额外约定） |
| 批量/编程式操作、跑脚本 | `run_code`（一次调用里执行 JavaScript，并可并发调用其它工具） |
| 任务清单（`TodoWrite`） | `todo_write`（每次提交完整清单，没有局部更新） |
| 派发子代理（`Task` / `Agent` / `Subagent (general-purpose):`） | `subagent`（独立上下文，只回传结果）或 `subagent_fork`（继承当前会话） |
| 多代理协作 | Agent Teams：`spawn_teammate` + `team_task_create`/`team_task_update` + `send_message` + `wait_agent` |
| 加载技能（`Skill`） | `skill`；用户也可直接输入 `/技能名` 显式调用 |
| 后台长任务 | `run_code` / `pwsh` 的 `run_in_background` → `job_output` / `job_kill` |
| 网络搜索（`WebSearch`） | `web_search` |
| 抓网页（`WebFetch`） | `web_fetch` |
| 问用户（`AskUserQuestion`） | `ask_user_question` |
| 计划模式（`ExitPlanMode`） | `exit_plan_mode`（DSH 有 plan mode） |
| 长期目标 | `create_goal` / `get_goal` / `update_goal` |
| 交付文件 | `present` |
| 改 notebook（`NotebookEdit`） | 无对应工具，用 `write` / `edit` 直接改文件 |

## 子代理

DSH 原生提供子代理：`subagent` 在独立上下文里执行一个自包含任务并只回传结果；`subagent_fork` 继承当前会话已完成的内容。技能里所有"派发子代理 / dispatch a subagent / Task(...)"一律映射到这两者；派发时要给完整、自包含的提示词，因为子代理看不到你的会话。

需要"队长 + 队员 + 任务板"式协作时用 Agent Teams（`spawn_teammate`、`team_task_*`、`send_message`、`wait_agent`）。技能里"并行派发多个独立任务"的语义优先用后台 `subagent` 实现，收到通知后再汇总。

## 计划模式与目标

DSH 有 plan mode（用 `exit_plan_mode` 提交计划请求批准）和跨轮次的 goal。技能里"进入计划模式之前先做 brainstorming"等规则照旧适用。

## 命令执行：本仓库的额外约定

DSH 执行命令的工具是 `pwsh`。但**本仓库的 AGENTS.md 全局约定禁止直接使用 PowerShell**：命令一律写成 Python 或 Node 脚本执行；确需 PowerShell 时，只允许用它启动 Python 脚本。技能正文里的 `Bash` 示例按此改写：

| 上游写法 | 本仓库写法 |
| --- | --- |
| `bash scripts/foo.sh` | 用 `run_code` 执行等价 JavaScript，或 `pwsh -Command "python scripts/foo.py"` 启动 Python |
| `chmod +x`、`jq`、`tmux`、`sed` 等 | 改用 Python / Node 等价实现，不引入外部 shell 工具依赖 |
| 后台命令（`run_in_background: true`） | `run_code` / `pwsh` 的 `run_in_background`，用 `job_output` 取结果、`job_kill` 终止 |
| `/tmp` 之类的 Unix 路径 | 用工作区内的临时目录，或 Node 的 `os.tmpdir()`；临时文件用完自删 |

临时脚本必须自删除：脚本自身在 `finally` 里删掉自己，异常路径也不能留垃圾。

## 不存在的机制

- **hooks**：DSH 没有 SessionStart / PreToolUse / PostToolUse 等 hook。上游靠 SessionStart hook 做的 bootstrap，在 DSH 上要换成插件注入的 system prompt section，或写进 `AGENTS.md` 的约定。
- **自定义 slash command**：DSH 没有 `/superpowers:brainstorm` 这类命令。替代是技能目录里的 `/技能名` 显式调用（技能默认 `user-invocable`）。
- **`CLAUDE.md`**：DSH 的工作区指令文件是 `AGENTS.md`（用户级为 `~/.dsh/AGENTS.md`）。读到 `CLAUDE.md` 时按 `AGENTS.md` 理解。
- **`~/.claude/`**：DSH 的家目录是 `~/.dsh/`——会话记录 `~/.dsh/sessions`、用户级技能根 `~/.dsh/skills`、项目级技能根 `<项目根>/.dsh/skills`。
- **worktree 工具**：DSH 没有原生 worktree 工具，`using-git-worktrees` 里的操作用 `git` 命令脚本完成（遵守上面的命令约定）。
- **`allowed-tools` 等 frontmatter**：DSH 只认 `name`（必须英文 kebab-case）与 `description`，可选 `whenToUse`、`metadata`、`disable-model-invocation`、`user-invocable`；Claude Code 的专有字段会被忽略，别依赖它们生效。
