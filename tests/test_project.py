from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ProjectTests(unittest.TestCase):
    def run_cmd(self, *args, cwd=ROOT):
        return subprocess.run(list(args), cwd=cwd, text=True, capture_output=True)

    def test_project_identity_and_version(self):
        profile = json.loads((ROOT / ".ai/PROJECT-PROFILE.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["project_name"], "Clash_Mac_Compile")
        self.assertEqual(profile["project_slug"], "clash-mac-compile")
        self.assertEqual(profile["repository"], "cdreaming/Clash-Mac-Compile")
        self.assertRegex((ROOT / "VERSION").read_text().strip(), r"^\d+\.\d+\.\d+$")

    def test_build_configuration(self):
        result = self.run_cmd(sys.executable, "scripts/check-build-config.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_build_script_and_workflow_contract(self):
        script = (ROOT / "scripts/build-macos-app.sh").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/build-macos.yml").read_text(encoding="utf-8")
        self.assertIn("ProjectClash/Clash-Client.git", script)
        self.assertIn("scripts/bootstrap.py", script)
        self.assertIn("scripts/configure.py", script)
        self.assertIn("ClashmacOS", script)
        self.assertIn("CODE_SIGNING_ALLOWED=NO", script)
        self.assertIn("ARCHS=arm64", script)
        self.assertIn("ONLY_ACTIVE_ARCH=YES", script)
        self.assertIn('-jobs "$BUILD_JOBS"', script)
        self.assertIn("lipo -verify_arch arm64", script)
        self.assertNotIn("x86_64", script)
        self.assertIn("runs-on: xcode-27", workflow)
        self.assertIn("actions/upload-artifact@", workflow)
        self.assertIn("macos-arm64", workflow)
        self.assertNotIn("cancel-in-progress: true", workflow)
        self.assertIn("timeout-minutes: 240", workflow)
        self.assertIn('CLASH_BUILD_JOBS: "2"', workflow)
        self.assertIn('go-version: "1.26.10"', workflow)


    def test_build_script_refuses_non_macos_hosts(self):
        import platform
        if platform.system() == "Darwin":
            self.skipTest("macOS host is allowed to run the build script")
        result = self.run_cmd("bash", "scripts/build-macos-app.sh", "--output", "build/test")
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires macOS", result.stderr)

    def test_release_rejects_mutable_upstream_branch(self):
        with tempfile.TemporaryDirectory() as td:
            copy = Path(td) / "repo"
            ignore = shutil.ignore_patterns(".git", ".dev-state", "dist", "build",
                                            "tmp", "__pycache__", ".pytest_cache",
                                            ".venv", "venv")
            shutil.copytree(ROOT, copy, ignore=ignore)
            (copy / "UPSTREAM_CLIENT_REF").write_text("main\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "scripts/check-build-config.py", "--release"],
                cwd=copy, text=True, capture_output=True
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("full 40-character commit SHA", result.stderr)

    def test_attach_release_assets_updates_manifest_and_checksums(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dist = root / "dist"
            build = root / "build"
            dist.mkdir()
            build.mkdir()
            (dist / "project-source.zip").write_bytes(b"source")
            (dist / "validation.md").write_text("validation\n", encoding="utf-8")
            manifest = {
                "project": "Clash_Mac_Compile",
                "project_version": "0.0.3",
                "assets": ["project-source.zip", "validation.md"]
            }
            (dist / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            (build / "Clash_Mac_Compile-v0.0.3-macos-arm64.zip").write_bytes(b"app zip")
            (build / "BUILD-METADATA.json").write_text('{"client_commit":"abc"}\n', encoding="utf-8")

            result = self.run_cmd(
                sys.executable, str(ROOT / "scripts/attach-release-assets.py"),
                "--dist", str(dist), "--source", str(build), "--version", "0.0.3"
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            updated = json.loads((dist / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
            actual = {p.name for p in dist.iterdir() if p.is_file()}
            self.assertEqual(set(updated["assets"]), actual)
            for line in (dist / "SHA256SUMS.txt").read_text().splitlines():
                digest, name = line.split(maxsplit=1)
                self.assertEqual(hashlib.sha256((dist / name.strip()).read_bytes()).hexdigest(), digest)

if __name__ == "__main__":
    unittest.main()
