#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把某个任务的完整文本从实现计划抽取到一个文件里，供实现者一次读取，
好让任务文本不必经由主控的上下文粘贴。

用法：task-brief.py PLAN_FILE TASK_NUMBER [OUTFILE]
默认 OUTFILE：<repo-root>/.superpowers/sdd/<计划基名>/task-<N>-brief.md
（按计划、按工作树；同一工作树里同一计划的并发运行共享它）。
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_HEADING = re.compile(r"^#+[ \t]+Task[ \t]+[0-9]+")


def die(message, code=2):
    print(message, file=sys.stderr)
    sys.exit(code)


def workspace_dir(plan):
    """调用同目录的 sdd-workspace.py，返回本计划的工作区路径。"""
    script = os.path.join(HERE, "sdd-workspace.py")
    try:
        proc = subprocess.run(
            [sys.executable, script, plan], capture_output=True, text=True,
        )
    except OSError as exc:
        die("无法运行 %s：%s" % (script, exc))
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        sys.exit(proc.returncode)
    return proc.stdout.strip()


def extract(plan, number, out):
    """抽出编号为 number 的任务的完整文本，写入 out，返回写入的行数。

    与上游 awk 的语义一致：围栏代码块内的 Task 标题不算标题；遇到别的
    任务标题时结束当前任务的收集。
    """
    with open(plan, encoding="utf-8", errors="replace") as handle:
        raw = handle.read()
    lines = raw.split("\n")
    if lines and lines[-1] == "":
        lines.pop()

    wanted = re.compile(r"^#+[ \t]+Task[ \t]+" + re.escape(number) + r"([^0-9]|$)")
    infence = False
    intask = False
    kept = []
    for line in lines:
        if line.startswith("```"):
            infence = not infence
        if not infence and TASK_HEADING.match(line):
            intask = bool(wanted.search(line))
        if intask:
            kept.append(line)

    content = "".join(line + "\n" for line in kept)
    with open(out, "w", encoding="utf-8", newline="") as handle:
        handle.write(content)
    return content.count("\n")


def main():
    if len(sys.argv) not in (3, 4):
        die("用法：task-brief.py PLAN_FILE TASK_NUMBER [OUTFILE]")

    plan = sys.argv[1]
    number = sys.argv[2]
    if not os.path.isfile(plan):
        die("没有这个计划文件：%s" % plan)

    if len(sys.argv) == 4:
        out = sys.argv[3]
    else:
        out = os.path.join(workspace_dir(plan), "task-%s-brief.md" % number)

    count = extract(plan, number, out)
    if count == 0:
        die("在 %s 里找不到任务 %s（没有匹配 'Task %s' 的标题）" % (plan, number, number), 3)

    print("已写入 %s：%d 行" % (out, count))


if __name__ == "__main__":
    main()
