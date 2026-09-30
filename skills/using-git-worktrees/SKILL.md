---
name: using-git-worktrees
description: 在开始需要与当前工作区隔离的功能开发前，或在执行实现计划之前使用 —— 用 git worktree 确保存在一个隔离工作区
---

# 使用 Git worktree

## 概述

确保工作在隔离的工作区里进行。DSH 没有原生 worktree 工具，隔离工作区一律用 `git worktree` 手工创建。

**核心原则：** 先检测是否已经隔离，再用 `git worktree` 创建。绝不与 harness 对抗。

**命令执行约定（DSH）：** 本技能的 git 操作全部写成 Python 脚本执行，用 `pwsh -Command "python <脚本>"` 启动（本仓库禁止把 PowerShell 当 shell 使用）；一步就能完成的检查可以直接用 `run_code` 跑等价 JavaScript。临时脚本必须在 `finally` 里删掉自己。

**开始时声明：**“正在使用 using-git-worktrees 技能搭建隔离工作区。”

## 步骤 0：检测是否已经隔离

**创建任何东西之前，先检查自己是否已经处在隔离的工作区里。**

```python
import os, subprocess

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()

GIT_DIR = os.path.realpath(git("rev-parse", "--git-dir"))
GIT_COMMON = os.path.realpath(git("rev-parse", "--git-common-dir"))
BRANCH = git("branch", "--show-current")
```

**子模块防护：** 在 git 子模块里 `GIT_DIR != GIT_COMMON` 同样成立。下结论说“已经在 worktree 里”之前，先确认自己不在子模块中：

```python
# 如果这里返回了路径，说明你在子模块里而不是 worktree 里 —— 按普通仓库处理
print(git("rev-parse", "--show-superproject-working-tree"))
```

**如果 `GIT_DIR != GIT_COMMON`（且不在子模块里）：** 你已经在一个链接的 worktree 里。跳到步骤 2（项目初始化）。绝不再创建另一个 worktree。

按分支状态汇报：
- 在某个分支上：“已经处在隔离工作区 `<path>`，位于分支 `<name>`。”
- 分离头指针（detached HEAD）：“已经处在隔离工作区 `<path>`（detached HEAD，由外部管理）。收尾时需要创建分支。”

**如果 `GIT_DIR == GIT_COMMON`（或处在子模块里）：** 你在一个普通的仓库检出中。

使用者是否已经在指令里表明过 worktree 偏好？如果没有，创建 worktree 之前先征求同意：

> “需要我搭一个隔离的 worktree 吗？它能保护你当前的分支不被改动。”

对已经声明的偏好直接遵从，不要再问。如果使用者不同意，就地工作并跳到步骤 2。

## 步骤 1：创建隔离工作区

**DSH 没有原生 worktree 工具，所以只有一条路径：用 `git worktree` 创建。**

### 1a. 用 git worktree 创建（DSH 唯一方式）

**用 git 手工创建 worktree。**

#### 目录选择

按下面的优先级来。使用者的显式偏好永远优先于观察到的文件系统状态。

1. **先查你的指令里是否声明了 worktree 目录偏好。** 如果使用者已经指定，直接用，不要再问。

2. **检查项目里是否已有 worktree 目录：**
   ```python
   # 优先：.worktrees（隐藏目录）
   # 备选：worktrees
   for d in (".worktrees", "worktrees"):
       if os.path.isdir(d):
           print(d)
   ```
   如果找到就用它。两者都存在时，`.worktrees` 胜出。

3. **如果没有任何其它指引**，默认用项目根目录下的 `.worktrees/`。

#### 安全校验（仅限项目内目录）

**创建 worktree 之前必须先确认该目录已被忽略：**

```python
# 等价命令：git check-ignore -q .worktrees || git check-ignore -q worktrees
ignored = any(
    subprocess.run(["git", "check-ignore", "-q", d]).returncode == 0
    for d in (".worktrees", "worktrees")
)
```

**如果没有被忽略：** 加到 .gitignore，提交这次改动，然后继续。

**为什么关键：** 防止把 worktree 的内容误提交进仓库。

#### 创建 worktree

```python
# 按选定的位置拼出路径
path = f"{LOCATION}/{BRANCH_NAME}"

# 等价命令：git worktree add <path> -b <BRANCH_NAME>
subprocess.run(["git", "worktree", "add", path, "-b", BRANCH_NAME], check=True)
os.chdir(path)
```

**沙箱降级：** 如果 `git worktree add` 因为权限错误失败（沙箱拒绝），告诉使用者沙箱阻止了 worktree 创建，你改为在当前目录工作。然后就地做项目初始化和基线测试。

## 步骤 2：项目初始化

自动检测并运行对应的初始化：

```python
# Node.js
if os.path.exists("package.json"):
    run("npm install")

# Rust
if os.path.exists("Cargo.toml"):
    run("cargo build")

# Python
if os.path.exists("requirements.txt"):
    run("pip install -r requirements.txt")
if os.path.exists("pyproject.toml"):
    run("poetry install")

# Go
if os.path.exists("go.mod"):
    run("go mod download")
```

## 步骤 3：验证干净的基线

跑测试，确认工作区从干净状态开始：

```python
# 用项目对应的命令
# npm test / cargo test / pytest / go test ./...
```

**如果测试失败：** 报告失败，询问是继续还是先排查。

**如果测试通过：** 报告就绪。

### 报告

```
Worktree 已就绪：<full-path>
测试通过（<N> 个测试，0 个失败）
可以开始实现 <feature-name>
```

## 快速参考

| 情形 | 动作 |
|-----------|--------|
| 已经在一个链接的 worktree 里 | 跳过创建（步骤 0） |
| 处在子模块里 | 按普通仓库处理（步骤 0 防护） |
| DSH 没有原生 worktree 工具 | 用 `git worktree` 创建（步骤 1a） |
| 使用者已在指令里声明目录偏好 | 直接使用，不再询问（步骤 1a） |
| `.worktrees/` 存在 | 使用它（先确认已被忽略） |
| `worktrees/` 存在 | 使用它（先确认已被忽略） |
| 两者都存在 | 使用 `.worktrees/` |
| 两者都不存在 | 查指令文件，再默认 `.worktrees/` |
| 目录未被忽略 | 加到 .gitignore + 提交 |
| 创建时权限错误 | 沙箱降级，就地工作 |
| 基线测试失败 | 报告失败 + 询问 |
| 没有 package.json/Cargo.toml | 跳过依赖安装 |

## 常见自我合理化

| 借口 | 现实 |
|--------|---------|
| “我明显不在 worktree 里 —— 不用查” | 跑步骤 0。harness 创建的隔离和子模块都会骗过肉眼；检测命令才能定论。 |
| “DSH 没有原生工具，所以随手 `git worktree add` 就行” | 原生工具会接管目录位置、建分支和清理；DSH 上这些必须由 `git worktree` 脚本显式完成，而且创建前必须先跑步骤 0。跳过检测是头号错误 —— 它会产生 harness 看不到、也管不了的幽灵状态。 |
| “worktree 目录肯定早就被忽略了” | 跑 `git check-ignore`。没被忽略的 worktree 目录会把整棵树提交进仓库。 |
| “目录叫什么名字都行” | 显式指令优先于项目内已有的目录，后者又优先于 `.worktrees/` 默认值。 |
| “工作区是全新的 —— 基线测试可以等等” | 脏基线会让之后每一次失败都变得含糊。现在就跑测试；带着失败继续要由使用者拍板。 |
