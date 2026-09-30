#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成评审包：提交列表、统计摘要，以及带扩展上下文的净 diff，写进评审者
一次读取的文件。使用记录下来的逐任务 BASE（而不是 HEAD~1）可以保住多提交
任务的完整性。

用法：review-package.py PLAN_FILE BASE HEAD [OUTFILE]
默认 OUTFILE：<repo-root>/.superpowers/sdd/<计划基名>/review-<base7>..<head7>.diff
（按区间命名，所以修复之后的复评审会拿到一个不同的新文件）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def die(message, code=2):
    print(message, file=sys.stderr)
    sys.exit(code)


def git_capture(*args):
    """运行 git 并返回 stdout 文本（stderr 直接透传给用户）。"""
    try:
        proc = subprocess.run(["git", *args], capture_output=True, text=True)
    except OSError as exc:
        die("无法运行 git：%s" % exc)
    if proc.returncode != 0:
        die("git %s 失败：%s" % (" ".join(args), proc.stderr.strip() or proc.returncode))
    return proc.stdout


def git_ok(*args):
    """运行 git，只返回是否成功；stderr 直接透传。"""
    try:
        proc = subprocess.run(["git", *args], stdout=subprocess.DEVNULL)
    except OSError:
        return False
    return proc.returncode == 0


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


def ensure_newline(text):
    if text and not text.endswith("\n"):
        return text + "\n"
    return text


def main():
    if len(sys.argv) not in (4, 5):
        die("用法：review-package.py PLAN_FILE BASE HEAD [OUTFILE]")

    plan = sys.argv[1]
    base = sys.argv[2]
    head = sys.argv[3]
    if not os.path.isfile(plan):
        die("没有这个计划文件：%s" % plan)

    if not git_ok("rev-parse", "--verify", "--quiet", base):
        die("无效的 BASE：%s" % base)
    if not git_ok("rev-parse", "--verify", "--quiet", head):
        die("无效的 HEAD：%s" % head)

    # 区间守卫（退出码 3）：分支不对的 HEAD 会得到一个空区间，或一个不以
    # BASE 为根的区间；两者都会静默产出伪造的评审包。
    if not git_ok("merge-base", "--is-ancestor", base, head):
        die("HEAD 不是 BASE 的后代：%s..%s" % (base, head), 3)
    commits = git_capture("rev-list", "--count", "%s..%s" % (base, head)).strip()
    if not commits.isdigit() or int(commits) <= 0:
        die("提交区间为空：%s..%s" % (base, head), 3)

    if len(sys.argv) == 5:
        out = sys.argv[4]
    else:
        short_base = git_capture("rev-parse", "--short", base).strip()
        short_head = git_capture("rev-parse", "--short", head).strip()
        out = os.path.join(
            workspace_dir(plan), "review-%s..%s.diff" % (short_base, short_head)
        )

    log = ensure_newline(git_capture("log", "--oneline", "%s..%s" % (base, head)))
    stat = ensure_newline(git_capture("diff", "--stat", "%s..%s" % (base, head)))
    diff = ensure_newline(git_capture("diff", "-U10", "%s..%s" % (base, head)))
    content = (
        "# Review package: %s..%s\n" % (base, head)
        + "\n"
        + "## Commits\n"
        + log
        + "\n"
        + "## Files changed\n"
        + stat
        + "\n"
        + "## Diff\n"
        + diff
    )
    with open(out, "w", encoding="utf-8", newline="") as handle:
        handle.write(content)

    print("已写入 %s：%s 个提交，%d 字节" % (out, commits, len(content.encode("utf-8"))))


if __name__ == "__main__":
    main()
