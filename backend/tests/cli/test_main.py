"""Unit tests for the CLI adapter."""

import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

from backend.cli.main import main


class TestCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

        # Valid constitution
        self.const_path = self.base_path / "constitution.yaml"
        self.const_path.write_text(
            "apiVersion: nce/v1\n"
            "kind: Constitution\n"
            "metadata:\n"
            "  id: test\n"
            "  version: 1.0.0\n"
            "  status: published\n"
            "  author: test\n"
            "  scope: global\n"
            "resolution:\n"
            "  strategy: most-restrictive-wins\n"
            "  default_verdict: block\n"
            "principles: []\n"
            "rules: []\n"
        )

        # Valid request
        self.req_path = self.base_path / "request.json"
        self.req_path.write_text(json.dumps({"api_version": "nce/v1", "action": {"type": "test"}}))

        # Valid audit
        self.audit_path = self.base_path / "audit.json"
        self.audit_path.write_text(json.dumps({"id": "123", "result": {"action": "allow"}}))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @patch("sys.stdout", new_callable=StringIO)
    def test_validate_success(self, mock_stdout: Any) -> None:
        test_args = ["nce", "validate", str(self.const_path)]
        with patch.object(sys, "argv", test_args):
            exit_code = main()

        self.assertEqual(exit_code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("=== Constitution Validated ===", output)
        self.assertIn("ID:      test", output)

    @patch("sys.stderr", new_callable=StringIO)
    def test_validate_fail_missing_file(self, mock_stderr: Any) -> None:
        test_args = ["nce", "validate", "does_not_exist.yaml"]
        with patch.object(sys, "argv", test_args):
            exit_code = main()

        self.assertEqual(exit_code, 1)
        self.assertIn("Error validating constitution", mock_stderr.getvalue())

    @patch("sys.stdout", new_callable=StringIO)
    def test_evaluate_success(self, mock_stdout: Any) -> None:
        test_args = ["nce", "evaluate", str(self.const_path), str(self.req_path)]
        with patch.object(sys, "argv", test_args):
            exit_code = main()

        self.assertEqual(exit_code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("=== Evaluation Complete ===", output)
        self.assertIn("Decision:     BLOCK", output)
        self.assertIn("Winning Rule: SYS-FALLBACK", output)

    @patch("sys.stderr", new_callable=StringIO)
    def test_evaluate_fail_request(self, mock_stderr: Any) -> None:
        test_args = ["nce", "evaluate", str(self.const_path), "missing.json"]
        with patch.object(sys, "argv", test_args):
            exit_code = main()

        self.assertEqual(exit_code, 1)
        self.assertIn("Error loading request", mock_stderr.getvalue())

    @patch("sys.stdout", new_callable=StringIO)
    def test_explain_success(self, mock_stdout: Any) -> None:
        test_args = ["nce", "explain", str(self.audit_path)]
        with patch.object(sys, "argv", test_args):
            exit_code = main()

        self.assertEqual(exit_code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("=== Audit Record ===", output)
        self.assertIn('"id": "123"', output)


if __name__ == "__main__":
    unittest.main()
