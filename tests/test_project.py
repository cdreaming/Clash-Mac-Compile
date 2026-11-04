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
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.0.7")

    def test_build_configuration(self):
        result = self.run_cmd(sys.executable, "scripts/check-build-config.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_build_script_and_workflow_contract(self):
        script = (ROOT / "scripts/build-macos-app.sh").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/build-macos.yml").read_text(encoding="utf-8")
        release = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        weekly = (ROOT / ".github/workflows/upstream-weekly.yml").read_text(encoding="utf-8")

        self.assertIn("ProjectClash/Clash-Client.git", script)
        self.assertIn("scripts/bootstrap.py", script)
        self.assertIn("scripts/configure.py", script)
        self.assertIn("ClashmacOS", script)
        self.assertIn("CODE_SIGNING_ALLOWED=NO", script)
        self.assertNotIn("CODE_SIGNING_ALLOWED=YES", script)
        self.assertNotIn("Developer ID Application", script)
        self.assertNotIn("APPLE_TEAM_ID", script)
        self.assertNotIn("CLASH_SIGNING_MODE", script)
        self.assertIn("ARCHS=arm64", script)
        self.assertIn("ONLY_ACTIVE_ARCH=YES", script)
        self.assertIn('SWIFT_OPTIMIZATION_LEVEL="$SWIFT_OPTIMIZATION_LEVEL"', script)
        self.assertIn('-jobs "$BUILD_JOBS"', script)
        self.assertIn("lipo -archs", script)
        self.assertNotIn("lipo -verify_arch", script)
        self.assertNotIn("x86_64", script)
        self.assertIn('"distribution_mode": "unsigned"', script)
        self.assertIn('"vpn_authorization_supported": False', script)

        self.assertIn("runs-on: xcode-27", workflow)
        self.assertIn("actions/upload-artifact@v6", workflow)
        self.assertIn("macos-arm64-unsigned", workflow)
        self.assertIn('CLASH_SWIFT_OPTIMIZATION_LEVEL: "-O"', workflow)
        self.assertIn('CLASH_BUILD_JOBS: "2"', workflow)
        self.assertIn('go-version: "1.26.10"', workflow)
        self.assertNotIn("APPLE_", workflow + release + weekly)
        self.assertNotIn("import-apple-signing-assets", release + weekly)
        self.assertNotIn("notarize-macos-app", release + weekly)
        self.assertNotIn('CLASH_SIGNING_MODE: "signed"', release + weekly)
        self.assertIn("scripts/attach-release-assets.py", release)
        self.assertIn("scripts/attach-release-assets.py", weekly)
        self.assertNotIn("cancel-in-progress: true", workflow)
        self.assertIn("timeout-minutes: 240", workflow)


    def test_build_script_refuses_non_macos_hosts(self):
        import platform
        if platform.system() == "Darwin":
            self.skipTest("macOS host is allowed to run the build script")
        result = self.run_cmd("bash", "scripts/build-macos-app.sh", "--output", "build/test")
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires macOS", result.stderr)


    def test_weekly_upstream_release_workflow_contract(self):
        workflow = (ROOT / ".github/workflows/upstream-weekly.yml").read_text(encoding="utf-8")
        prep = (ROOT / "scripts/prepare-weekly-upstream-release.py").read_text(encoding="utf-8")
        self.assertIn('timezone: "America/Los_Angeles"', workflow)
        self.assertIn("--client-sha", prep)
        self.assertIn("--prerelease", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("scripts/verify-github-release.sh", workflow)


    def test_weekly_upstream_bumps_patch_on_new_sha(self):
        with tempfile.TemporaryDirectory() as td:
            copy = Path(td) / "repo"
            ignore = shutil.ignore_patterns(".git", ".dev-state", "dist", "build",
                                            "tmp", "__pycache__", ".pytest_cache",
                                            ".venv", "venv")
            shutil.copytree(ROOT, copy, ignore=ignore)
            new_sha = "1" * 40
            result = subprocess.run(
                [sys.executable, "scripts/prepare-weekly-upstream-release.py",
                 "--client-sha", new_sha],
                cwd=copy, text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((copy / "VERSION").read_text().strip(), "0.0.8")
            self.assertEqual((copy / "UPSTREAM_CLIENT_REF").read_text().strip(), new_sha)
            release_notes = copy / "docs/releases/v0.0.8/RELEASE-NOTES.md"
            self.assertTrue(release_notes.is_file())
            notes_text = release_notes.read_text(encoding="utf-8")
            self.assertIn("macos-arm64-unsigned.zip", notes_text)
            self.assertIn("VPN", notes_text)
            self.assertNotIn("signed-notarized", notes_text)
            self.assertNotIn("NOTARIZATION-RESULT.json", notes_text)

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


    def test_attach_release_assets_accepts_unsigned_app_with_limitation_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dist = root / "dist"
            build = root / "build"
            dist.mkdir()
            build.mkdir()
            (dist / "Clash_Mac_Compile_v0.0.7_source.zip").write_bytes(b"source")
            (dist / "RELEASE-MANIFEST.json").write_text(json.dumps({
                "project": "Clash_Mac_Compile",
                "project_version": "0.0.7",
                "assets": ["Clash_Mac_Compile_v0.0.7_source.zip"]
            }), encoding="utf-8")
            (build / "Clash_Mac_Compile-v0.0.7-macos-arm64-unsigned.zip").write_bytes(b"unsigned app")
            (build / "BUILD-METADATA.json").write_text(json.dumps({
                "signing": "disabled",
                "team_id": None,
                "distribution_mode": "unsigned",
                "vpn_authorization_supported": False,
                "limitations": ["VPN authorization requires Apple Developer signing."]
            }), encoding="utf-8")
            result = self.run_cmd(
                sys.executable, str(ROOT / "scripts/attach-release-assets.py"),
                "--dist", str(dist), "--source", str(build), "--version", "0.0.7"
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((dist / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["distribution_mode"], "unsigned")
            self.assertFalse(manifest["vpn_authorization_supported"])
            self.assertTrue((dist / "SHA256SUMS.txt").is_file())


    def test_attach_release_assets_updates_manifest_and_checksums(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dist = root / "dist"
            build = root / "build"
            dist.mkdir()
            build.mkdir()
            (dist / "Clash_Mac_Compile_v0.0.7_source.zip").write_bytes(b"source")
            (dist / "validation.md").write_text("validation\n", encoding="utf-8")
            manifest = {
                "project": "Clash_Mac_Compile",
                "project_version": "0.0.7",
                "assets": ["Clash_Mac_Compile_v0.0.7_source.zip", "validation.md"]
            }
            (dist / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            (build / "Clash_Mac_Compile-v0.0.7-macos-arm64-unsigned.zip").write_bytes(b"app zip")
            (build / "BUILD-METADATA.json").write_text(json.dumps({
                "client_commit": "abc",
                "signing": "disabled",
                "team_id": None,
                "distribution_mode": "unsigned",
                "vpn_authorization_supported": False
            }) + "\n", encoding="utf-8")

            result = self.run_cmd(
                sys.executable, str(ROOT / "scripts/attach-release-assets.py"),
                "--dist", str(dist), "--source", str(build), "--version", "0.0.7"
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
