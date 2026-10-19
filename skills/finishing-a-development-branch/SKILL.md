---
name: finishing-a-development-branch
description: 当实现已完成、必需检查与所选开发模式的验收通过，你需要决定如何集成这些工作时使用（本地合并回基础分支、Push 并创建 PR、保留分支，或清理 worktree）
---

# 完成开发分支

**核心流程：** 验证验收证据 → 探测 Git 环境与基础分支 → 呈现标准选项 → 执行集成方案 → 安全清理。

开始时宣告：“我正在使用 finishing-a-development-branch 技能完成分支收尾。”

## Step 1：验证验收证据

项目有测试套件时运行要求的完整套件；没有自动套件时按约定实机验收，不为门禁创建空测试。核对当前开发模式的验收证据（运行时模式须含目标实例同场景复测及关闭临时诊断后的交付配置复测）。若必需检查失败或证据缺失，展示具体缺口并补齐，验收通过后再进入集成。

## Step 2 & 3：探测环境与确认基础分支

在当前工作区捕获环境路径（Step 5 切换目录后 Step 6 清理需用）：

```python
import os, subprocess
def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()

GIT_DIR = os.path.realpath(git("rev-parse", "--git-dir"))
GIT_COMMON = os.path.realpath(git("rev-parse", "--git-common-dir"))
WORKTREE_PATH = git("rev-parse", "--show-toplevel")
```

确认该分支 fork 自哪个基础分支（`<base-branch>`）；若不确定，合并前先向使用者确认。

## Step 4：呈现选项并等待决定

- **普通仓库（`GIT_DIR == GIT_COMMON`）或具名分支 worktree：**
  ```text
  实现已完成。你想怎么做？
  1. 在本地合并回 <base-branch>
  2. Push 并创建 Pull Request
  3. 保持分支原样（稍后自行处理）
  ```
- **Detached HEAD worktree（由外部管理）：**
  ```text
  实现已完成。当前处于 detached HEAD。
  1. Push 为新分支并创建 Pull Request
  2. 保持原样（稍后自行处理）
  ```

严格呈现上述对应菜单并等待使用者选择（不主动提议丢弃工作）。

## Step 5：执行所选方案

| 方案 | 执行动作 | Worktree 处置 |
| --- | --- | --- |
| **1. 本地合并** | 切回主仓库根目录（`MAIN_ROOT`）→ `git checkout <base-branch>` → `git pull` → `git merge <feature-branch>` → **在合并结果上重做约定验收**（若失败则停下排查，保留分支与 worktree）→ 通过后执行 Step 6 清理 worktree，再 `git branch -d <feature-branch>` | 清理（Step 6） |
| **2. 创建 PR** | `git push -u origin <feature-branch>`（detached HEAD 用 `HEAD:refs/heads/<new-branch>`），按仓库模板创建 PR 并返回 URL | 保留供后续迭代 |
| **3. 保持原样** | 报告分支名与 worktree 路径 | 保留 |
| **丢弃（仅限使用者明确要求）** | 列出将永久删除的分支、commits 与路径，等待使用者输入确切的 `discard` 确认 → 切回 `MAIN_ROOT` → 执行 Step 6 清理 worktree → `git branch -D <feature-branch>` | 清理（Step 6） |

## Step 6：安全清理 Worktree（仅方案 1 与已确认丢弃）

- 若 `GIT_DIR == GIT_COMMON`：普通仓库，无需清理。
- 若 `WORKTREE_PATH` 位于 `.worktrees/` 或 `worktrees/` 下（Superpowers 创建）：在主仓库根目录执行 `git worktree remove <WORKTREE_PATH>` 与 `git worktree prune`。
  - **若因含未跟踪/修改文件被拒：** 严禁擅自加 `--force`！运行 `git -C <WORKTREE_PATH> status --porcelain -uall` 展示文件列表，请使用者选择：(1) 先 commit 到分支；(2) 移至主仓库根；(3) 确认永久删除。
- 其它位置的 worktree 归宿主环境所有，保持原样不清理。
