#!/usr/bin/env python3
"""二分查找：找出是哪个测试创建了不该出现的文件/状态。

用法: python find-polluter.py <要检查的文件或目录> <测试文件匹配模式>
示例: python find-polluter.py '.git' 'src/**/*.test.ts'
"""

import glob
import os
import shutil
import subprocess
import sys
from datetime import datetime


def find_test_files(pattern: str) -> list[str]:
    """把 find -path 的匹配语义搬到 Python 的 glob 上，返回排好序的测试文件。"""
    pattern = pattern.removeprefix("./")
    # find -path 无法让 '**/' 匹配零级目录，所以像 src/**/*.test.ts 这样的模式
    # 会漏掉 src/top.test.ts；再按折叠掉 '**/' 的模式匹配一次，覆盖直接位于
    # 基准目录下的文件。
    candidates = {pattern}
    if "**/" in pattern:
        candidates.add(pattern.replace("**/", ""))

    files: set[str] = set()
    for candidate in candidates:
        for path in glob.glob(candidate, recursive=True):
            if os.path.isfile(path):
                files.add(path)
    return sorted(files)


def print_pollution_details(path: str) -> None:
    """打印污染物的基本信息（等价于原来的 ls -la）。"""
    stat = os.stat(path)
    print("  路径:", os.path.abspath(path))
    print("  类型:", "目录" if os.path.isdir(path) else "文件")
    print("  大小:", stat.st_size, "字节")
    print("  修改时间:", datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"))
    if os.path.isdir(path):
        for entry in sorted(os.listdir(path))[:20]:
            print("   -", entry)


def main() -> int:
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <要检查的文件> <测试文件匹配模式>")
        print(f"示例: {sys.argv[0]} '.git' 'src/**/*.test.ts'")
        return 1

    pollution_check = sys.argv[1]
    test_pattern = sys.argv[2]

    print(f"🔍 正在查找创建了以下内容的测试: {pollution_check}")
    print(f"测试文件模式: {test_pattern}")
    print()

    test_files = find_test_files(test_pattern)
    total = len(test_files)

    print(f"找到 {total} 个测试文件")
    print()

    npm = shutil.which("npm")
    if npm is None:
        print("❌ 找不到 npm，请先安装 Node.js")
        return 1

    for count, test_file in enumerate(test_files, start=1):
        # 污染已经存在就跳过
        if os.path.exists(pollution_check):
            print(f"⚠️  在第 {count}/{total} 个测试之前，污染就已经存在")
            print(f"   跳过: {test_file}")
            continue

        print(f"[{count}/{total}] 正在测试: {test_file}")

        # 运行测试：输出丢弃，失败与否都不影响判断
        subprocess.run(
            [npm, "test", test_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        # 检查污染是否出现
        if os.path.exists(pollution_check):
            print()
            print("🎯 找到污染源！")
            print(f"   测试: {test_file}")
            print(f"   创建了: {pollution_check}")
            print()
            print("污染详情:")
            print_pollution_details(pollution_check)
            print()
            print("要深入调查:")
            print(f"  npm test {test_file}    # 只跑这个测试")
            print(f"  # 阅读 {test_file}，检查测试代码")
            return 1

    print()
    print("✅ 没有找到污染源 —— 所有测试都是干净的！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
