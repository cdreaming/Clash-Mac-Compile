from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BuildOutputTests(unittest.TestCase):
    def make_outputs(self, directory: Path):
        app = "Clash_Mac_Compile-v0.1.3-macos-arm64-unsigned.zip"
        (directory / app).write_bytes(b"app zip")
        (directory / "BUILD-METADATA.json").write_text(json.dumps({
            "project_version": "0.1.3",
            "distribution_mode": "unsigned"
        }), encoding="utf-8")
        (directory / "VPN-ARCHITECTURE-REPORT.json").write_text(json.dumps({
            "provider_target_type": "system-extension",
            "distribution_architecture_ready": True,
            "system_extension_packaged": True
        }), encoding="utf-8")
        (directory / "SHA256SUMS.txt").write_text("checksum  app.zip\n", encoding="utf-8")
        (directory / "BUILD-SCRIPT-STATUS.txt").write_text(
            "status=success\nexit_code=0\nversion=0.1.3\n", encoding="utf-8"
        )
        (directory / "BUILD-RUN-CONTEXT.txt").write_text(
            "project=Clash_Mac_Compile\nversion=0.1.3\noutput_directory=test\n",
            encoding="utf-8"
        )
        (directory / "BUILD-OUTPUT-MANIFEST.json").write_text(json.dumps({
            "project_version": "0.1.3",
            "app_artifact": app,
            "required_files": [app, "BUILD-METADATA.json", "VPN-ARCHITECTURE-REPORT.json", "SHA256SUMS.txt"]
        }), encoding="utf-8")
        return app

    def run_verifier(self, directory: Path):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/verify-build-outputs.py"),
             "--directory", str(directory), "--version", "0.1.3", "--mode", "unsigned"],
            cwd=ROOT, text=True, capture_output=True
        )

    def test_verifies_expected_build_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            self.make_outputs(directory)
            result = self.run_verifier(directory)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Build output verification: PASS", result.stdout)

    def test_missing_app_zip_fails_with_explicit_diagnostic(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            app = self.make_outputs(directory)
            (directory / app).unlink()
            result = self.run_verifier(directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(app, result.stderr)
            self.assertIn("Missing or empty files", result.stderr)

    def test_missing_build_script_status_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            self.make_outputs(directory)
            (directory / "BUILD-SCRIPT-STATUS.txt").unlink()
            result = self.run_verifier(directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BUILD-SCRIPT-STATUS.txt is missing", result.stderr)

    def test_nonzero_build_script_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            self.make_outputs(directory)
            (directory / "BUILD-SCRIPT-STATUS.txt").write_text(
                "status=failed\nexit_code=65\nversion=0.1.3\n", encoding="utf-8"
            )
            result = self.run_verifier(directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exit_code=65", result.stdout)
            self.assertIn("did not report a successful exit", result.stderr)

    def test_mode_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            self.make_outputs(directory)
            metadata = json.loads((directory / "BUILD-METADATA.json").read_text(encoding="utf-8"))
            metadata["distribution_mode"] = "local-development-only"
            (directory / "BUILD-METADATA.json").write_text(json.dumps(metadata), encoding="utf-8")
            result = self.run_verifier(directory)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unexpected distribution_mode", result.stderr)


if __name__ == "__main__":
    unittest.main()
