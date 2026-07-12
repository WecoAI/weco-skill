import math
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = REPO_ROOT / "assets" / "evaluate-speed.py"


class EvaluateSpeedTests(unittest.TestCase):
    def run_evaluator(self, baseline_source, candidate_source):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            workspace = project / ".weco"
            workspace.mkdir()
            (workspace / "baseline.py").write_text(
                textwrap.dedent(baseline_source), encoding="utf-8"
            )
            (workspace / "optimize.py").write_text(
                textwrap.dedent(candidate_source), encoding="utf-8"
            )

            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            return subprocess.run(
                [sys.executable, str(EVALUATOR)],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
                check=False,
            )

    @staticmethod
    def metric_lines(result):
        output = f"{result.stdout}\n{result.stderr}"
        return [
            line for line in output.splitlines() if line.strip().startswith("speedup:")
        ]

    def test_wrong_output_fails_without_emitting_metric(self):
        result = self.run_evaluator(
            """
            def TARGET_FUNCTION():
                return 1
            """,
            """
            def TARGET_FUNCTION():
                return 2
            """,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Constraint violated", result.stderr)
        self.assertEqual(self.metric_lines(result), [])

    def test_candidate_exception_emits_no_metric(self):
        result = self.run_evaluator(
            """
            def TARGET_FUNCTION():
                return 1
            """,
            """
            def TARGET_FUNCTION():
                raise RuntimeError("candidate failed")
            """,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.metric_lines(result), [])

    def test_correct_output_emits_one_finite_metric(self):
        result = self.run_evaluator(
            """
            def TARGET_FUNCTION():
                return sum(range(100))
            """,
            """
            def TARGET_FUNCTION():
                return sum(range(100))
            """,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        metrics = self.metric_lines(result)
        self.assertEqual(len(metrics), 1)
        speedup = float(metrics[0].split(":", 1)[1])
        self.assertTrue(math.isfinite(speedup))
        self.assertGreater(speedup, 0)


if __name__ == "__main__":
    unittest.main()
