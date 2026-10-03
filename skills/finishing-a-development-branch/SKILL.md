---
name: finishing-a-development-branch
description: 当实现已完成、必需检查与所选开发模式的验收通过，你需要决定如何集成这些工作时使用（本地合并回基础分支、Push 并创建 PR、保留分支，或清理 worktree）
---

# 完成开发分支

## 概览

**核心原则：** 验证测试 → 探测环境 → 给出选项 → 执行所选方案 → 清理。

**开始时宣告：** “我正在使用 finishing-a-development-branch 技能来完成这项工作。”

## Step 1：验证验收证据

项目有测试套件时，运行要求的完整套件（`npm test` / `cargo test` / `pytest` / `go test ./...`）。

同时核对所选开发模式的完成证据：运行时模式还须同场景实机与交付配置复测；自动套件不能替代这些记录。项目没有自动套件时如实记录，按约定的实机验收判断，不为过门禁创建空测试。

**如果必需验证失败或缺失**，报告具体缺口并停下——菜单只在约定验收完成后才出现：

```
测试失败（<N> 个失败）。必须在完成之前修复：

[展示失败输出]
```

**如果必需检查与所选模式的验收均通过：** 继续 Step 2。

## Step 2：探测环境

```python
import os, subprocess

def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()

GIT_DIR = os.path.realpath(git("rev-parse", "--git-dir"))
GIT_COMMON = os.path.realpath(git("rev-parse", "--git-common-dir"))
# 现在就取值——此时仍在工作区内；Step 5 会切换目录，
# 而 Step 6 的清理需要用到这个值
WORKTREE_PATH = git("rev-parse", "--show-toplevel")
```

这决定了展示哪个菜单，以及清理如何进行：

| 状态 | 菜单 | 清理 |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON`（普通仓库） | 标准 3 个选项 | 没有 worktree 需要清理 |
| `GIT_DIR != GIT_COMMON`，具名分支 | 标准 3 个选项 | 基于来源判定（见 Step 6） |
| `GIT_DIR != GIT_COMMON`，detached HEAD | 精简的 2 个选项（无合并） | 由外部管理——保持原样 |

## Step 3：确定基础分支

基础分支就是这项工作 fork 出来的那个分支——通常在计划、对话或该分支的
upstream 里已经写明。如果还不知道，就问：“这个分支是从 <your best guess>
分出来的——对吗？”合并前先确认：合到错误的基础分支上，撤销的代价很高。

## Step 4：给出选项

**普通仓库和具名分支 worktree——严格给出这 3 个选项：**

```
实现已完成。你想怎么做？

1. 在本地合并回 <base-branch>
2. Push 并创建 Pull Request
3. 保持分支原样（我稍后自己处理）

选哪一项？
```

**detached HEAD——严格给出这 2 个选项：**

```
实现已完成。你处于 detached HEAD（由外部管理的工作区）。

1. Push 为新分支并创建 Pull Request
2. 保持原样（我稍后自己处理）

选哪一项？
```

严格按上面写好的菜单呈现——简洁，每个选项都来自上面的列表。丢弃这些工作
只发生在使用者明确要求时（见下文“如果使用者要求丢弃这些工作”）。等待他们的
回答；集成方式由他们决定。

## Step 5：执行所选方案

### 方案 1：本地合并

```python
import os, subprocess

def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()

# 取主仓库根目录，避免 cwd 停在 worktree 里
MAIN_ROOT = git("-C", os.path.join(git("rev-parse", "--git-common-dir"), ".."), "rev-parse", "--show-toplevel")
os.chdir(MAIN_ROOT)

# 先合并——在删除任何东西之前确认成功
git("checkout", "<base-branch>")
git("pull")
git("merge", "<feature-branch>")

# 在合并结果上验证测试
subprocess.run("<test command>", shell=True, check=True)
```

如果合并结果上测试失败：停下，保留 worktree 和分支不动，然后排查——什么都
还没有 push，所以这次合并是本地的、可以恢复。

一旦合并结果全绿：清理 worktree（Step 6），然后删除分支：

```python
subprocess.run(["git", "branch", "-d", "<feature-branch>"], check=True)
```

### 方案 2：Push 并创建 PR

```python
subprocess.run(["git", "push", "-u", "origin", "<feature-branch>"], check=True)
# 处于 detached HEAD 时，在远端指名新分支：
# subprocess.run(["git", "push", "origin", "HEAD:refs/heads/<new-branch>"], check=True)
```

然后用代码托管平台的工具，针对 <base-branch> 创建 pull/merge request——有
CLI 就用它的 CLI，否则用大多数平台在 push 时打印的创建 URL——如果仓库里存在
PR 模板与约定就遵循它们，并把 URL 报告给使用者。

保留 worktree——使用者要在那里根据 PR 反馈迭代。

### 方案 3：保持原样

报告：“保留分支 <name>。worktree 保存在 <path>。”

### 如果使用者要求丢弃这些工作

这条路径只作为对“明确要求把工作扔掉”的响应而存在。先确认：

```
这会永久删除：
- 分支 <name>
- 所有 commit：<commit-list>
- 位于 <path> 的 worktree

输入 'discard' 以确认。
```

等待这个确切的确认。收到之后：

```python
import os, subprocess

def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()

MAIN_ROOT = git("-C", os.path.join(git("rev-parse", "--git-common-dir"), ".."), "rev-parse", "--show-toplevel")
os.chdir(MAIN_ROOT)
```

然后清理 worktree（Step 6）并强制删除分支：

```python
subprocess.run(["git", "branch", "-D", "<feature-branch>"], check=True)
```

## Step 6：清理工作区

**在方案 1 和已确认的丢弃中执行。** 方案 2 和方案 3 永远保留 worktree。两个
调用方都已经把目录切换到主仓库根目录——删除 worktree 必须在 worktree 之外
执行——并且要使用 Step 2 在切换目录之前捕获的 `GIT_DIR`/`GIT_COMMON`/
`WORKTREE_PATH` 值。

**如果 `GIT_DIR == GIT_COMMON`：** 普通仓库，没有 worktree 需要清理。结束。

**如果 `WORKTREE_PATH` 位于 `.worktrees/` 或 `worktrees/` 之下：** 这个
worktree 是 Superpowers 创建的——清理由我们负责：

```python
subprocess.run(["git", "worktree", "remove", WORKTREE_PATH], check=True)
# 自愈：清理残留的 worktree 注册信息
subprocess.run(["git", "worktree", "prune"], check=True)
```

**如果删除被拒绝**（`contains modified or untracked files`）：这个 worktree
里存着别处不存在的文件——未 commit 的计划、笔记或草稿。绝不自行决定使用
`--force`。把利害关系展示给使用者，并询问：

```python
subprocess.run(["git", "-C", WORKTREE_PATH, "status", "--porcelain", "-uall"], check=True)
```

```
worktree 删除被拒绝——这些文件从未被 commit：

<file list>

1. 清理前先把它们 commit 到 <branch>
2. 把它们移动到 <main repo root>
3. 删除它们（不可恢复）

选哪一项？
```

执行所选的处理方式，然后删除 worktree。

**其它情况：** 这个工作区归宿主环境所有——保持原样。DSH 没有退出工作区的
工具，因此不要自行清理。

## 速查表

| 方案 | 合并 | Push | 保留 worktree | 清理分支 |
|--------|-------|------|---------------|----------------|
| 1. 本地合并 | 是 | - | - | 是 |
| 2. 创建 PR | - | 是 | 是 | - |
| 3. 保持原样 | - | - | 是 | - |
| 丢弃（仅限明确要求） | - | - | - | 是（强制） |

## 常见的自我合理化

| 借口 | 现实 |
|--------|---------|
| “本次会话早些时候测试是通过的” | 在你要集成的这棵树上跑一遍测试套件。一次全绿只能证明它当时跑的那棵树。 |
| “他们显然想合并” | 集成方式是使用者的决定。给出菜单，然后等待。 |
| “他们看起来已经不想再做这个功能了——我主动提出丢弃吧” | 菜单已经写完整了。只有当使用者明确说出要求时才会丢弃。 |
| “‘行，把它删了吧’也算确认” | 只有键入的 `discard` 一词才授权删除。 |
| “PR 已经提上去了，worktree 现在是杂物” | PR 反馈要在那个 worktree 里修。它会一直保留到工作真正落地。 |
| “另一个 worktree 看起来过期了——我顺手也清了吧” | 只清理 `.worktrees/` 或 `worktrees/` 下的 worktree。其它一切都归宿主所有。 |
| “删除被拒绝了——`--force` 只是把清理做完” | 拒绝意味着有文件只存在于那个 worktree 里。`--force` 会永久销毁它们。展示给使用者并询问。 |
| “合并结果上的失败大概是 flaky” | 合并结果失败就一切暂停。在你排查期间分支和 worktree 保持不动。 |
| “基础分支显然就是 main” | 确认 fork 点，或者直接问。合到错误的基础分支上，撤销代价很高。 |
| “push 被拒了——force-push 就能解决” | push 被拒说明远端已经前进了。先排查；只有在使用者明确要求时才 force-push。 |

