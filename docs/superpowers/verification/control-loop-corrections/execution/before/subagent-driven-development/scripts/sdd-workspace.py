#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析并确保 SDD 为单个计划存放短生命周期产物的工作区目录：
任务简报、实现者报告、评审包与进度台账。打印该计划目录的绝对路径。

每个计划一个目录（.superpowers/sdd/<计划基名>/），这样同一工作树里的后续
计划永远不会读到或覆盖另一个计划的产物。把过期的台账误读成当前进度会让
主控跳过整个任务序列——按计划隔离从结构上消除了这种失败。

两个计划同名时基名 slug 会冲突（docs/alpha/plan.md 对 docs/beta/plan.md），
因此每个工作区在 plan-path 标记里记录自己所属计划的路径（库内用仓库相对
路径，库外用绝对路径）。属于别的计划的工作区会被跳过，并用计划父目录名
消歧，再不行用计数器。没有标记的工作区早于标记方案，会被当前计划认领，
好让在途工作区继续解析——这意味着这种遗留工作区上的第一次冲突是认领而
非识别；可以接受，无标记工作区会随计划完成而消亡。

工作区放在工作树里（而不是 .git/ 下）：.git/ 是版本控制的内部目录，代理
产物不应写进受版本控制的数据目录。.superpowers/sdd/ 下一个自忽略的
.gitignore 让每个计划的工作区都不出现在 `git status` 里、也不会被误提交，
同时不改动任何被跟踪的文件。

工作区位置的唯一真源，好让 task-brief.py 与 review-package.py 不会漂移到
不同的目录。

用法：sdd-workspace.py PLAN_FILE
"""
import os
import subprocess
import sys


def die(message, code=2):
    print(message, file=sys.stderr)
    sys.exit(code)


def main():
    if len(sys.argv) != 2:
        die("用法：sdd-workspace.py PLAN_FILE")

    plan = sys.argv[1]
    if not os.path.isfile(plan):
        die("没有这个计划文件：%s" % plan)

    slug = os.path.basename(plan)
    if slug.endswith(".md"):
        slug = slug[:-3]
    if not slug or slug in (".", ".."):
        die("无法从该计划推导出工作区名：%s" % plan)

    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        die("git rev-parse --show-toplevel 失败：%s" % exc)
    if not root:
        die("git rev-parse --show-toplevel 没有输出")
    root = os.path.abspath(root)
    base = os.path.join(root, ".superpowers", "sdd")

    # 规范化计划路径（物理目录，好让同一计划的相对/绝对/../ 写法比较相等），
    # 并把它表达为标记值：计划位于仓库根之下时用仓库相对路径，否则用绝对路径。
    plan_dir = os.path.realpath(os.path.dirname(plan) or ".")
    plan_abs = os.path.join(plan_dir, os.path.basename(plan))
    root_prefix = root.rstrip(os.sep) + os.sep
    if plan_abs.startswith(root_prefix):
        plan_id = os.path.relpath(plan_abs, root).replace(os.sep, "/")
    else:
        plan_id = plan_abs

    def owns(directory):
        """当 directory 是（或成为）本计划的工作区时为真：已有标记必须点名本
        计划；没有标记意味着新建工作区或标记方案之前的遗留工作区，两种情况
        都由本计划写入标记来认领。"""
        marker = os.path.join(directory, "plan-path")
        if os.path.exists(marker):
            try:
                with open(marker, encoding="utf-8") as handle:
                    return handle.read().strip() == plan_id
            except OSError:
                return False
        os.makedirs(directory, exist_ok=True)
        with open(marker, "w", encoding="utf-8", newline="") as handle:
            handle.write(plan_id + "\n")
        return True

    target = os.path.join(base, slug)
    if not owns(target):
        parent = os.path.basename(plan_dir)
        target = os.path.join(base, "%s-%s" % (slug, parent))
        if not owns(target):
            n = 2
            while not owns(os.path.join(base, "%s-%s-%d" % (slug, parent, n))):
                n += 1
            target = os.path.join(base, "%s-%s-%d" % (slug, parent, n))

    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, ".gitignore"), "w", encoding="utf-8", newline="") as handle:
        handle.write("*\n")

    print(os.path.abspath(target))


if __name__ == "__main__":
    main()
