from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LinkerDiagnosticsTests(unittest.TestCase):
    def test_extracts_undefined_symbols_and_linker_context(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            log = root / "XCODEBUILD.log"
            report = root / "LINKER-DIAGNOSTICS.txt"
            log.write_text(
                "SwiftCompile normal arm64 SomeFile.swift\\n"
                "Ld /tmp/ClashmacOSExtension.systemextension/Contents/MacOS/ClashmacOSExtension normal arm64\\n"
                "    cd /tmp/project\\n"
                "Undefined symbols for architecture arm64:\\n"
                '  "_MissingSymbol", referenced from:\\n'
                "      _SomeReference in SomeObject.o\\n"
                "ld: symbol(s) not found for architecture arm64\\n"
                "clang: error: linker command failed with exit code 1\\n"
                "** BUILD FAILED **\\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/summarize-xcode-linker-errors.py"),
                 "--log", str(log), "--output", str(report), "--context-lines", "1"],
                cwd=ROOT, text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            content = report.read_text(encoding="utf-8")
            self.assertIn("Undefined symbols for architecture arm64", content)
            self.assertIn("_MissingSymbol", content)
            self.assertIn("linker command failed", content)

    def test_reports_no_standard_linker_errors_without_failing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            log = root / "XCODEBUILD.log"
            report = root / "LINKER-DIAGNOSTICS.txt"
            log.write_text("** BUILD SUCCEEDED **\\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/summarize-xcode-linker-errors.py"),
                 "--log", str(log), "--output", str(report)],
                cwd=ROOT, text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("No standard linker error signature", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
