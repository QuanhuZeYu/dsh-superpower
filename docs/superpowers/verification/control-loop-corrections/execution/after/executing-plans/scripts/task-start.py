#!/usr/bin/env python3
# 一次调用里开始内联计划执行中的一个任务：提取该任务的简报（经由
# subagent-driven-development 的 task-brief.py，让两个技能共用同一个工作区），
# 并记录 BASE —— 该任务评审范围所切的 commit。一次工具调用而不是两次，因为内联
# 会话里的每次调用都是一次重读全部上下文的回合。
#
# 用法：python task-start.py PLAN_FILE TASK_NUMBER
# 输出：
#   brief: <该任务简报文件的路径>
#   base:  <HEAD 的完整 SHA>
import re
import subprocess
import sys
from pathlib import Path

USAGE = "usage: task-start.py PLAN_FILE TASK_NUMBER"

SDD_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "subagent-driven-development" / "scripts"
)


def tolerate_unencodable_output():
    """管道输出遇到区域设置编不出的字符时退化为替代字符，而不是崩溃。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


tolerate_unencodable_output()


def run(args, **kwargs):
    """跑一个子进程，文本输出一律按 UTF-8 解码，解不出来的字节用替代字符。"""
    return subprocess.run(
        args, text=True, encoding="utf-8", errors="replace", **kwargs
    )


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2

    plan, n = argv

    # task-brief.py 的 stderr 直接透传到本脚本的 stderr，只捕获它的 stdout。
    brief_out = run(
        [sys.executable, str(SDD_SCRIPTS / "task-brief.py"), plan, n],
        stdout=subprocess.PIPE,
    )
    if brief_out.returncode != 0:
        return brief_out.returncode

    # 从 task-brief.py 的中文输出取路径；保留英文旧输出兼容。
    # 路径可含空格或冒号，末尾行数标记界定边界。
    brief = "\n".join(
        re.findall(r"^(?:已写入 |wrote )(.*)(?:：[0-9]+ 行|: [0-9]+ lines)$", brief_out.stdout, re.M)
    )
    if not brief:
        print(
            "task-brief.py 没有报告简报路径：%s" % brief_out.stdout.rstrip("\n"),
            file=sys.stderr,
        )
        return 1

    print("brief: %s" % brief)

    head = run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
    if head.returncode != 0:
        return head.returncode
    print("base: %s" % head.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
