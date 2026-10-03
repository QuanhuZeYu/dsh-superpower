"""核对 task-start 消费 task-brief 实际 CLI 输出的契约。"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[5]
START = ROOT / "skills/executing-plans/scripts/task-start.py"
BRIEF = ROOT / "skills/subagent-driven-development/scripts/task-brief.py"

class TaskStartContract(unittest.TestCase):
    def test_real_wrapper_under_legacy_encoding(self):
        # 使用真实 git 工作区，但 HEAD 只放定位用占位值，不创建提交。
        version = subprocess.run(["git", "--version"], capture_output=True, text=True)
        self.assertEqual(version.returncode, 0, version.stderr)
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "中文 工作区"
            initialized = subprocess.run(["git", "init", "--quiet", str(repo)], capture_output=True, text=True)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            (repo / ".git" / "HEAD").write_text("a" * 40 + "\n", encoding="ascii")
            plan = repo / "plan file.md"
            plan.write_text("# Plan\n\n## Task 1: 校验\n拒绝空 ID\n", encoding="utf-8")
            legacy_env = {**os.environ, "PYTHONIOENCODING": "gbk", "PYTHONUTF8": "0"}
            actual = subprocess.run([sys.executable, str(START), str(plan), "1"], cwd=repo, env=legacy_env, capture_output=True)
            stdout = actual.stdout.decode("gbk", errors="replace")
            stderr = actual.stderr.decode("gbk", errors="replace")
            self.assertEqual(actual.returncode, 0, stderr)
            self.assertIn("base: " + "a" * 40, stdout)
            brief_lines = [line[7:] for line in stdout.splitlines() if line.startswith("brief: ")]
            self.assertEqual(len(brief_lines), 1, stdout)
            self.assertIn("拒绝空 ID", Path(brief_lines[0]).read_text(encoding="utf-8"))

    def test_real_brief_output_with_spaces(self):
        spec = importlib.util.spec_from_file_location("task_start", START)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / "计划 文件.md"
            brief = Path(directory) / "task brief.md"
            plan.write_text("# Plan\n\n## Task 1: 校验\n拒绝空 ID\n", encoding="utf-8")
            actual = subprocess.run([sys.executable, str(BRIEF), str(plan), "1", str(brief)], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            self.assertEqual(actual.returncode, 0, actual.stderr)
            self.assertIn("拒绝空 ID", brief.read_text(encoding="utf-8"))
            calls = []
            def invoke(args, **kwargs):
                calls.append(args)
                if args[0] == "git":
                    return subprocess.CompletedProcess(args, 0, "a" * 40 + "\n")
                return actual
            output, errors = StringIO(), StringIO()
            with patch.object(module, "run", side_effect=invoke), redirect_stdout(output), redirect_stderr(errors):
                result = module.main([str(plan), "1"])
            self.assertEqual(result, 0, errors.getvalue())
            self.assertIn("brief: " + str(brief), output.getvalue())
            self.assertIn("base: " + "a" * 40, output.getvalue())
            self.assertEqual(calls[-1], ["git", "rev-parse", "HEAD"])

    def test_legacy_english_output(self):
        spec = importlib.util.spec_from_file_location("task_start_legacy", START)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = StringIO()
        replies = [subprocess.CompletedProcess([], 0, "wrote D:/my dir/task brief.md: 2 lines\n"), subprocess.CompletedProcess([], 0, "b" * 40)]
        with patch.object(module, "run", side_effect=replies), redirect_stdout(output):
            result = module.main(["plan.md", "1"])
        self.assertEqual(result, 0)
        self.assertIn("brief: D:/my dir/task brief.md", output.getvalue())

    def test_missing_brief_does_not_report_base(self):
        spec = importlib.util.spec_from_file_location("task_start_invalid", START)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = StringIO()
        with patch.object(module, "run", return_value=subprocess.CompletedProcess([], 0, "unexpected output\n")) as run, redirect_stdout(output), redirect_stderr(StringIO()):
            result = module.main(["plan.md", "1"])
        self.assertEqual(result, 1)
        self.assertNotIn("base:", output.getvalue())
        self.assertEqual(run.call_count, 1)

if __name__ == "__main__":
    unittest.main()
