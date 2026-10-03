#!/usr/bin/env python3
# 一次调用里结束内联计划执行中的一个任务：运行该任务的测试命令、把完整输出留在
# 工作区、打印尾部，并且 —— 只有命令成功时 —— 才把完成行追加到台账。命令失败就
# 什么都不记：任务不算完成。
#
# 用法：pwsh -Command "python task-done.py PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]"
#   BASE 是 task-start.py 打印出来的 SHA；完成行记录 BASE..HEAD。
# 退出码：测试命令的退出码。
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

USAGE = "usage: task-done.py PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]"
TAIL_LINES = 5

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


def git(*args):
    """跑一条 git 命令，返回（退出码, 去掉首尾空白的 stdout）。"""
    proc = run(["git", *args], stdout=subprocess.PIPE)
    return proc.returncode, proc.stdout.strip()


def quote(arg):
    """按原脚本的做法渲染参数：含空白、双引号、分号、竖线或 & 时套单引号。"""
    return "'%s'" % arg if re.search(r'[\s";|&]', arg) else arg


def run_test_command(args, log_path):
    """运行测试命令，stdout 与 stderr 一起写进日志文件，返回退出码。"""
    with open(log_path, "wb") as log:
        try:
            return subprocess.run(
                args, stdout=log, stderr=subprocess.STDOUT
            ).returncode
        except OSError as exc:
            # Windows 上 npm、pnpm、yarn 是 .cmd 垫片，CreateProcess 直接找不到，
            # 于是退回由 shell 解析命令行 —— 等价于原脚本交给 shell 执行的行为。
            line = subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)
            try:
                return subprocess.run(
                    line, shell=True, stdout=log, stderr=subprocess.STDOUT
                ).returncode
            except OSError:
                log.write(("%s: %s\n" % (args[0], exc)).encode("utf-8", "replace"))
                return 127  # shell 的 command not found


def main(argv):
    if len(argv) < 5 or argv[3] != "--":
        print(USAGE, file=sys.stderr)
        return 2

    plan, n, base = argv[0], argv[1], argv[2]
    command = argv[4:]

    rc, _ = git("rev-parse", "--verify", "--quiet", base)
    if rc != 0:
        print("BASE 无效：%s" % base, file=sys.stderr)
        return 2

    workspace = run(
        [sys.executable, str(SDD_SCRIPTS / "sdd-workspace.py"), plan],
        stdout=subprocess.PIPE,
    )
    if workspace.returncode != 0:
        return workspace.returncode
    workspace_dir = Path(workspace.stdout.strip())

    log_path = workspace_dir / ("task-%s-tests.log" % n)
    ledger = workspace_dir / "progress.md"

    # 按一个人会敲的样子渲染命令，用于台账行。
    rendered = " ".join(quote(a) for a in command)

    rc = run_test_command(command, log_path)

    # 读回日志：先把换行统一成 \n（Windows 上的子进程会把 \n 写成 \r\n，否则回车
    # 会跟着最后一个非空行进台账），再打印尾部 5 行、取出最后一个非空行。
    text = (
        log_path.read_bytes()
        .decode("utf-8", "replace")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )
    lines = text.split("\n")
    sys.stdout.write("\n".join(lines[-TAIL_LINES:]))

    if rc != 0:
        print(
            "task-done.py: 测试命令退出码 %d；Task %s 未记录（完整输出：%s）"
            % (rc, n, log_path),
            file=sys.stderr,
        )
        return rc

    non_blank = [line for line in lines if line.strip()]
    if not non_blank:
        # 原脚本在 set -e + pipefail 下遇到这种日志会直接以非零退出，什么都不记。
        print(
            "task-done.py: 测试命令没有输出任何非空行；Task %s 未记录（完整输出：%s）"
            % (n, log_path),
            file=sys.stderr,
        )
        return 1
    last = non_blank[-1]

    rc, base7 = git("rev-parse", "--short=7", base)
    if rc != 0:
        return rc
    rc, head7 = git("rev-parse", "--short=7", "HEAD")
    if rc != 0:
        return rc

    # 台账一律用 \n 写，与原脚本的 printf 输出逐字节一致。
    if not ledger.exists():
        with ledger.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write("# SDD 台账 — 计划：%s\n" % plan)
    line = "任务 %s：完成（commits %s..%s，tests: %s → %s）" % (
        n,
        base7,
        head7,
        rendered,
        last,
    )
    with ledger.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")
    print("ledger: %s" % line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
