---
name: using-git-worktrees
description: 在开始需要与当前工作区隔离的功能开发前，或在执行实现计划之前使用 —— 用 git worktree 确保存在一个隔离工作区
---

# 使用 Git Worktree

**核心原则：** 先检测是否已处于隔离工作区，未隔离时再用 `git worktree` 创建，随后完成依赖初始化与干净基线测试。

**DSH 命令约定：** 一步检查可用 `run_code` 执行 Node.js，多步 git 脚本用 Python 编写并在 `finally` 中自删。开始时声明：“正在使用 using-git-worktrees 技能搭建隔离工作区。”

## 步骤 0：检测当前是否已隔离

创建前必须先运行以下命令检测（防止嵌套创建幽灵 worktree 或被子模块误导）：

```python
import os, subprocess
def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()

GIT_DIR = os.path.realpath(git("rev-parse", "--git-dir"))
GIT_COMMON = os.path.realpath(git("rev-parse", "--git-common-dir"))
SUPERPROJECT = git("rev-parse", "--show-superproject-working-tree")
BRANCH = git("branch", "--show-current")
```

- **已处于链接的 worktree（`GIT_DIR != GIT_COMMON` 且 `SUPERPROJECT == ""`）：** 严禁再新建 worktree！直接汇报当前路径与分支状态（具名分支或 detached HEAD），跳至**步骤 2**。
- **普通仓库或子模块（`GIT_DIR == GIT_COMMON` 或 `SUPERPROJECT != ""`）：** 若使用者已在指令中声明 worktree 偏好则直接执行步骤 1；否则先询问：“需要我搭一个隔离的 worktree 吗？它能保护当前分支不被改动。”（若不同意则就地跳至步骤 2）。

## 步骤 1：创建隔离 Worktree

1. **选择目录（按优先级）：** 使用者显式指定的目录 > 项目内已存在的 `.worktrees` > 已存在的 `worktrees` > 默认 `.worktrees`。
2. **校验 Git 忽略（项目内目录必做）：** 运行 `git check-ignore -q <dir>`。若未被忽略，先将该目录写入 `.gitignore` 并 commit，防止把整个 worktree 误提交进仓库。
3. **创建并切换：** 运行 `git worktree add <dir>/<BRANCH_NAME> -b <BRANCH_NAME>` 并进入该目录。若因沙箱权限报错被拒，向使用者说明并降级为在当前目录就地工作。

## 步骤 2 & 3：项目初始化与基线验证

1. **安装依赖/构建：** 按项目文件自动执行（`package.json` → `npm/pnpm install`；`Cargo.toml` → `cargo build`；`requirements.txt` → `pip install -r requirements.txt`；`pyproject.toml` → `poetry install`；`go.mod` → `go mod download`）。
2. **验证干净基线：** 运行项目测试套件确认初始状态全绿，汇报：`Worktree 已就绪：<path>，基线测试通过（<N> 个通过）`。若基线测试失败，立即报告失败详情并询问使用者是先排查还是继续。
