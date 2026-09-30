# 上游来源与同步说明

本目录是 [obra/superpowers](https://github.com/obra/superpowers) 官方技能的本地副本，用于二次修改（如适配 DeepSeek Harness）。

## 版本锚点

| 项 | 值 |
|---|---|
| 上游仓库 | https://github.com/obra/superpowers |
| 取值版本 | tag `v6.4.1` |
| commit | `5bf4e78011075bcfc0dc295f0724994cd123ee71` |
| commit 日期 | 2026-09-19T00:31:35Z |
| 拷贝时间 | 2026-09-23T06:06:32.073Z |
| 许可 | MIT（见 [LICENSE](LICENSE)，版权归 Jesse Vincent / Prime Radiant） |

## 本目录内容

- `skills/` —— 上游 `skills/` **原样**拷贝，共 **15** 个技能，76 个文件、约 434 KB。
  - 注意：v6.4.1 比 v6.3.0 多了一个 `diagnosing-superpowers`，所以是 15 个而不是社区移植版常见的 14 个。
  - 技能清单：brainstorming、diagnosing-superpowers、dispatching-parallel-agents、executing-plans、finishing-a-development-branch、receiving-code-review、requesting-code-review、subagent-driven-development、systematic-debugging、test-driven-development、using-git-worktrees、using-superpowers、verification-before-completion、writing-plans、writing-skills
  - 各技能包内资源（`references/`、`scripts/`、`templates/`、`prompts/`、`*.md`）随目录一并保留。
- `LICENSE` —— 上游 MIT 许可原文。修改后再分发时必须保留。

## 未包含的上游内容

`hooks/`、`tests/`、`scripts/`、`docs/`、`index.js`、`.github/`、以及各 harness 的插件清单（`.claude-plugin/`、`.codex-plugin/`、`.cursor-plugin/`、`.devin-plugin/`、`.hermes-plugin/`、`.kimi-plugin/`、`.muse-plugin/`、`.opencode/`、`.pi/`、`gemini-extension.json`）。

原因：这些是 Claude Code 及其它 harness 的加载/打包资产，DSH 侧用不到；技能正文真正引用的包内资源都在 `skills/` 里，已经完整保留。需要时可按下节方法重新取全量。

## 如何同步到新版

1. 取新 tag 的 tarball：`https://codeload.github.com/obra/superpowers/tar.gz/refs/tags/<tag>`
2. 解包后与本地 `skills/` 逐技能 diff，确认要吸收的改动再替换。
3. 更新本文件顶部的 tag / commit / 日期。

## DSH 适配注意事项（改之前先看）

1. **frontmatter 已兼容**：上游每个 `SKILL.md` 只有 `name` + `description`，name 与目录名一致且符合 kebab-case，满足 DSH 的解析要求。已实测：`using-superpowers`（正文 2978 字符）与 `test-driven-development`（9423 字符）都能被本机 DSH 的 `skill` 工具直接加载，`resourceBase` 指向技能目录。
2. **`skills/` 目录本身就是合法的 DSH 技能根**：DSH 只扫描一层 `<root>/<name>/SKILL.md`，所以把 `dsh-superpower/skills` 挂成技能根即可直接用，不需要额外改结构。
3. **工具名需要映射**：上游正文按 Claude Code 工具命名书写，DSH 工具名不同。全量关键词出现次数（含普通词用法，仅供参考）：`subagent` 108、`Skill` 101、`Task` 75、`worktree` 62、`Write` 57、`Read` 56、`hook` 6、`Edit` 5、`Bash` 3、`TodoWrite` 2、`plan mode` 2。重点改造对象是 `subagent-driven-development`、`executing-plans`、`writing-plans`（Task/subagent 密集）和 `using-git-worktrees`、`finishing-a-development-branch`（worktree 密集）。
4. **DSH 没有 hooks 和 slash commands**：上游依赖 SessionStart hook 做 bootstrap、依赖 slash command 做入口的部分（`using-superpowers`、`hooks/`）需要换成 DSH 的 system prompt section 或 "先加载技能" 的约定。
5. **描述长度**：技能 description 会进会话目录，DSH 侧由 profile 的 `catalogDescriptionMaxLength` 截断（默认 500）。

## 已验证记录

- 2026-09-23T06:06:32.073Z：从 tag `v6.4.1` 的 tarball 拷贝完成；15 个技能 frontmatter 校验全部通过；两个代表性技能在 DSH 中加载成功。临时下载目录与临时技能根均已清理，未改动任何 DSH profile 配置。
