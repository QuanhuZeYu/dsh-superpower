---
name: requesting-code-review
description: 在完成任务、实现重大功能或合并之前使用，用于核实工作成果是否满足需求
---

# 请求代码评审

派发一个代码评审子代理，在问题连锁扩散之前就把它们抓住。评审者拿到的是精确构造的上下文——绝不是你的会话历史。

**核心原则：** 尽早评审，经常评审。

## 何时请求评审

**必须：**
- 子代理驱动开发的每个任务完成之后
- 完成重大功能之后
- 合并到 main 之前

**可选但值得做：**
- 卡住时（换个新视角）
- 重构之前（基线检查）
- 修复复杂 bug 之后

## 如何请求

**1. 获取 git SHA：**
```python
import subprocess

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()

BASE_SHA = git("rev-parse", "HEAD~1")  # 或：git merge-base origin/main HEAD
HEAD_SHA = git("rev-parse", "HEAD")
```

**2. 派发代码评审子代理：**

派发一个 `subagent` 子代理，填入 [code-reviewer.md](code-reviewer.md) 中的模板

**占位符：**
- `{DESCRIPTION}` - 你构建内容的简要说明
- `{PLAN_OR_REQUIREMENTS}` - 它应当做到什么
- `{BASE_SHA}` - 起始 commit
- `{HEAD_SHA}` - 结束 commit

**3. 根据反馈行动：**
- 立即修复 Critical 问题
- 在继续推进之前修复 Important 问题
- 记下 Minor 问题，留待以后处理
- 如果评审者判断有误，用理由反驳

## 示例

```
[刚完成任务 2：新增校验函数]

你：继续之前，我先请求代码评审。

用 run_code 取 SHA：
  BASE_SHA = git("log", "--oneline", "-1", "--grep=任务 1").split()[0]
  HEAD_SHA = git("rev-parse", "HEAD")

[派发代码评审子代理]
  DESCRIPTION: 新增 verifyIndex() 与 repairIndex()，覆盖 4 种问题类型
  PLAN_OR_REQUIREMENTS: docs/superpowers/plans/deployment-plan.md 中的任务 2
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661

[子代理返回]：
  优点：架构清晰，测试真实
  问题：
    Important：缺少进度指示
    Minor：上报间隔用了魔法数字（100）
  评估：可以继续推进

你：[修复进度指示]
[继续任务 3]
```

## 常见的自我合理化

| 借口 | 事实 |
|--------|---------|
| "我自己看一眼 diff 就行，不用派发评审者" | 你是协调者——就地评审 diff 会烧掉你继续推动工作所需的上下文窗口。派发一个评审子代理：diff 与评估都留在它的上下文里，回到你手里的只有结论。 |
| "评审者需要我的整个会话历史才能理解这次改动" | 交给它精确构造的上下文，绝不交出你的会话历史。这样评审者关注的是工作产物，而不是你的思考过程。 |

## 危险信号

**绝不：**
- 以"这很简单"为由跳过评审
- 无视 Critical 问题
- 带着未修复的 Important 问题继续推进
- 与有效的技术反馈争辩

**如果评审者有误：**
- 用技术理由反驳
- 展示能证明其可行的代码 / 测试
- 请求澄清

模板见：[code-reviewer.md](code-reviewer.md)
