# 验收待办（全部技能完成后逐条处理）

由 Lead 在并行翻译过程中登记，最终验收时统一执行。

## 1. 术语统一

- [ ] `你的搭档` → `使用者`：已知 `receiving-code-review/SKILL.md` 有 10 处（52/61/82/83/86/98/121/127/129/198 行），其它已完成文件可能有零星残留。批量替换后需检查语句通顺（如"来自你的搭档" → "来自使用者"）。
- [ ] 复核 `subagent` / `子代理`、`dispatch` / `派发`、`verification` / `验证` 等术语在全库是否唯一。

## 2. 跨文件引用一致性（裁定：统一为中文标题）

上游计划文档 schema 有两个被多处引用的章节名，目前口径不一：

| 上游英文 | 裁定 | 引用位置 |
| --- | --- | --- |
| `## Global Constraints` | 统一改为中文 `## 全局约束` | writing-plans（模板，已保留英文，需改）、subagent-driven-development/SKILL.md:136,140,245、task-reviewer-prompt.md:195、executing-plans:244 |
| `## Review Focus` | 统一改为中文 `## 评审重点` | writing-plans、executing-plans:244、subagent-driven-development |

- [ ] 替换全部引用后，**检查 `subagent-driven-development/scripts/*.py` 是否按英文标题做字符串匹配**；若有，同步改为中文标题（或改为不依赖标题的匹配方式）。
- [ ] 检查 `docs/superpowers/plans/` 这一计划目录约定是否要在 DSH 下改名（当前决定保留，需在最终报告中说明）。

## 2b. 临时目录约定（子代理各写各的，需统一）

- [ ] `requesting-code-review` 自创了 `.dsh/tmp/review-<SHA>`（原为 `/tmp/review-<SHA>`）；检查 `subagent-driven-development`、`executing-plans`、`diagnosing-superpowers` 是否也各自发明了临时目录写法，统一成一种（建议：项目内 `.dsh/tmp/`，或说明用系统临时目录），并保证"临时文件自删"的说法一致。

## 3. worktree 约定一致性

- [ ] `using-git-worktrees`（已完成）与 `finishing-a-development-branch`（已完成）的 worktree 目录优先级（`.worktrees` → `worktrees`）、命名规则、清理命令必须一致；`executing-plans`、`subagent-driven-development` 完成后一并复核。

## 3b. 代码块语言标注

- [x] 已处理：`writing-skills/SKILL.md` 三处 ```bash 围栏中，225 行是伪命令示意（非可执行 shell），已改为 ```text；262、319 行是 `node -e` / `node ./render-graphs.js` 命令行调用，标注 `bash` 合理，保留。
- [ ] 扫一遍全库是否存在"标注与实际内容不符"的围栏（例如 python 围栏里只有注释、bash 围栏里是 node）。

## 3c. 历史路径（裁定：保留）

- [x] 裁定：`systematic-debugging` 的 `CREATION-LOG.md`、`test-pressure-*.md` 等背景/测试资料里保留了上游历史路径（`skills/debugging/systematic-debugging`、`skills/meta/testing-skills-with-subagents`、`skills/testing/test-driven-development`）——这些是历史记录，保留原文不失真，且不被技能正文引用。最终报告里说明即可。
- [ ] 但需确认：**技能正文（SKILL.md 及被正文引用的 references/prompts）里没有指向不存在路径的引用**（脚本的悬空引用检查已覆盖 `path/to/file.ext` 形式）。

## 4. 脚本改写复核

- [ ] 4 个无扩展名 shell 脚本 → Python：`executing-plans/scripts/task-start|task-done`、`subagent-driven-development/scripts/sdd-workspace|task-brief|review-package`、`systematic-debugging/find-polluter.sh`。逐个人工阅读，确认：功能等价、无第三方依赖、临时文件自删、无 PowerShell 依赖，且旧文件名无残留引用。
- [ ] `writing-skills/examples/CLAUDE_MD_TESTING.md` → `AGENTS_MD_TESTING.md` 改名后，全库无 `CLAUDE_MD_TESTING` 残留。

## 5. 残留白名单（验收脚本的已知误报）

- `skills/using-superpowers/references/dsh-tools.md`：映射表左列本来就写 Claude Code 工具名（`Read`/`Bash`/`TodoWrite`…），以及"DSH 没有 `/superpowers:brainstorm` 这类命令"的反例 —— **有意保留**。
- `skills/using-superpowers/references/dsh-tools.md` 里 `chmod`/`jq`/`tmux`/`sed` 出现在"不要引入这些依赖"的对照表里 —— 有意保留。
- 计划模板里的 `pytest`/`git add`/Unix 提示符 `$ npm test`（TDD）属内容示例 —— 可接受。

## 6. 最终验收动作（全部完成）

- [x] `node scripts/verify-translation.mjs`：0 错误、0 悬空引用、5 条警告（3 条有意改写 + 2 条白名单），逐条归类完毕。
- [x] DSH 冒烟测试：`~/.dsh/skills` 建 junction 指向 `dsh-superpower/skills`，`skill` 工具逐个加载 **15/15 通过**（provider=filesystem），随后拆除 junction 恢复环境。
- [x] 术语统一：`你的搭档` → `使用者`（全库 0 残留）；`human partner` 唯一译法。
- [x] 跨文件契约：台账格式统一为中文（含 `task-done.py` 的写入串）；worktree 落点统一 `.worktrees/`；计划 schema 章节名保留英文。
- [x] 代码块标注：`writing-skills` 伪命令示例改 `text`；node 命令行保留 `bash`。
- [x] 清理：临时上游快照 `.tmp-upstream-v641`、`.tmp-superpowers-dl`、`undefined/` 均已删除；`~/.dsh/skills` junction 已移除。
- [x] `DSH-ADAPTATION.md` 更新为最终结论。
