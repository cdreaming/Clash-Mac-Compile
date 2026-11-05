from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts/build-macos-app.sh"


class BuildScriptStatusTests(unittest.TestCase):
    def setUp(self):
        self.text = BUILD_SCRIPT.read_text(encoding="utf-8")

    def test_system_extension_project_spec_uses_declared_variable(self):
        self.assertRegex(
            self.text,
            r'SYSTEM_EXTENSION_PROJECT_SPEC="\$OUTPUT_DIR/ClashClient-project\.system-extension\.yml"',
        )
        self.assertIn('cp "$CLIENT_DIR/apple/ClashClient/project.yml" "$SYSTEM_EXTENSION_PROJECT_SPEC"', self.text)
        self.assertNotIn('"$SYSTEM_EXTENSION_PROJECT"', self.text)

    def test_status_files_use_real_newlines_not_literal_backslash_n(self):
        self.assertIn("printf '%s\\n'", self.text)
        for line in self.text.splitlines():
            if "printf" in line and "status=" in line:
                self.assertNotIn("\\\\n", line, f"literal escaped newline remains: {line}")

    def test_exit_trap_preserves_nonzero_exit_code(self):
        match = re.search(r"(?ms)^cleanup_build\(\) \{\n(.*?)^\}", self.text)
        self.assertIsNotNone(match, "cleanup_build function was not found")
        function_body = "cleanup_build() {\n" + match.group(1) + "\n}"
        with tempfile.TemporaryDirectory() as td:
            status_path = Path(td) / "BUILD-SCRIPT-STATUS.txt"
            harness = f'''#!/usr/bin/env bash
set -Eeuo pipefail
VERSION=0.1.5
OUTPUT_DIR={str(Path(td))!r}
BUILD_SCRIPT_STATUS={str(status_path)!r}
WORK_DIR=""
{function_body}
trap 'cleanup_build "$?"' EXIT
exit 65
'''
            result = subprocess.run(["bash"], input=harness, text=True, capture_output=True)
            self.assertEqual(result.returncode, 65, result.stdout + result.stderr)
            values = {}
            for line in status_path.read_text(encoding="utf-8").splitlines():
                key, value = line.split("=", 1)
                values[key] = value
            self.assertEqual(values.get("status"), "failed")
            self.assertEqual(values.get("exit_code"), "65")
            self.assertEqual(values.get("version"), "0.1.5")

    def test_build_script_passes_bash_syntax(self):
        result = subprocess.run(["bash", "-n", str(BUILD_SCRIPT)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
