#!/usr/bin/env python3
"""Check that invalid executable identity cannot produce comparison evidence."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "comparisons", Path(__file__).with_name("reproduce-assisted-cases.py")
)
comparisons = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(comparisons)


class VersionEvidenceTests(unittest.TestCase):
    def invoke(self, stdout, returncode=0):
        """Run the reporting entry point with a controlled version response."""
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            arguments = ["comparisons", "--texio", sys.executable, "--output", str(output)]
            result = subprocess.CompletedProcess([], returncode, stdout, "")
            captured = io.StringIO()
            with patch.object(sys, "argv", arguments), \
                    patch.object(comparisons, "run", return_value=result), \
                    patch.object(comparisons, "compare_case", return_value={}) as compare, \
                    contextlib.redirect_stdout(captured), \
                    contextlib.redirect_stderr(io.StringIO()):
                status = comparisons.main()
            return status, output.exists(), captured.getvalue(), compare.call_count

    def test_invalid_version_cannot_create_a_report_or_run_cases(self):
        """Fail before fixture comparisons and report creation on bad identity."""
        for stdout, code in [("texio 0.1.3\n", 1), ("", 0), (" \n", 0),
                             ("other 0.1.3\n", 0), ("texio \n", 0),
                             ("texio 0.1.3\nextra\n", 0)]:
            with self.subTest(stdout=stdout, returncode=code):
                self.assertEqual(self.invoke(stdout, code), (1, False, "", 0))

    def test_other_versions_are_accepted_and_reused_in_report(self):
        """Comparisons may target an executable other than the checkout version."""
        for version in ["0.1.2", "0.1.3", "0.2.0-rc.1+local"]:
            with self.subTest(version=version):
                status, exists, stdout, count = self.invoke(f"texio {version}\n")
                self.assertEqual((status, exists), (0, True))
                self.assertGreater(count, 0)
                self.assertEqual(json.loads(stdout)["texio_version"], f"texio {version}")


if __name__ == "__main__":
    unittest.main()
