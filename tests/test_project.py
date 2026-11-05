from __future__ import annotations
import hashlib
import json
import os
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
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "0.1.2")

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
        self.assertIn("patch-macos-system-extension.py", script)
        self.assertIn("audit-vpn-architecture.py", script)
        self.assertIn("xcodegen generate", script)
        self.assertIn("VPN-ARCHITECTURE-REPORT.json", script)
        self.assertIn("xcodebuild -verbose", script)
        self.assertIn('tee "$XCODEBUILD_LOG"', script)
        self.assertIn("PIPESTATUS[0]", script)
        self.assertIn("ClashmacOSExtension-BuildSettings.json", script)
        self.assertIn("LINKER-DIAGNOSTICS.txt", script)
        self.assertIn('OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd -P)"', script)
        self.assertIn("BUILD-OUTPUT-MANIFEST.json", script)
        self.assertIn("Build output validation failed", script)
        self.assertIn("ClashmacOS", script)
        self.assertIn("CODE_SIGNING_ALLOWED=NO", script)
        self.assertIn("CODE_SIGNING_ALLOWED=YES", script)  # opt-in local development mode
        self.assertIn('SIGNING_MODE="${CLASH_SIGNING_MODE:-unsigned}"', script)
        self.assertIn("CLASH_SIGNING_MODE", script)
        self.assertNotIn("Developer ID Application", script)
        self.assertNotIn("APPLE_TEAM_ID", script)
        self.assertIn("local-self-signed", script)
        self.assertIn('"apple_entitlements_authorized": False', script)
        self.assertIn("ARCHS=arm64", script)
        self.assertIn("ONLY_ACTIVE_ARCH=YES", script)
        self.assertIn('SWIFT_OPTIMIZATION_LEVEL="$SWIFT_OPTIMIZATION_LEVEL"', script)
        self.assertIn('-jobs "$BUILD_JOBS"', script)
        self.assertIn("lipo -archs", script)
        self.assertNotIn("lipo -verify_arch", script)
        self.assertNotIn("x86_64", script)
        self.assertIn('"distribution_mode": "local-development-only" if local else "unsigned"', script)
        self.assertIn('"vpn_authorization_supported": bool(vpn_report.get("vpn_authorization_supported", False)) and not local', script)

        self.assertIn("runs-on: xcode-27", workflow)
        self.assertIn("actions/upload-artifact@v6", workflow)
        self.assertIn("VPN-ARCHITECTURE-REPORT.json", script)
        self.assertIn("path: build/ci/", workflow)
        self.assertIn("Upload Xcode linker diagnostics", workflow)
        self.assertIn("Verify macOS build outputs", workflow)
        self.assertIn("verify-build-outputs.py", workflow)
        self.assertIn("path: build/ci/", workflow)
        self.assertIn('CLASH_SIGNING_MODE: "unsigned"', workflow)
        self.assertIn("if: always()", workflow)
        self.assertIn("macos-arm64-unsigned", workflow)
        self.assertIn('CLASH_SWIFT_OPTIMIZATION_LEVEL: "-O"', workflow)
        self.assertIn('CLASH_BUILD_JOBS: "2"', workflow)
        self.assertIn('go-version: "1.26.10"', workflow)
        self.assertNotIn("APPLE_", workflow + release + weekly)
        self.assertNotIn("CLASH_LOCAL_SIGNING_IDENTITY", workflow + release + weekly)
        self.assertNotIn("CLASH_LOCAL_SIGNING_IDENTITY", workflow + release + weekly)
        self.assertNotIn("import-apple-signing-assets", release + weekly)
        self.assertNotIn("notarize-macos-app", release + weekly)
        self.assertNotIn('CLASH_SIGNING_MODE: "signed"', release + weekly)
        self.assertIn("scripts/attach-release-assets.py", release)
        self.assertIn("Upload Xcode linker diagnostics", release)
        self.assertIn("Verify macOS build outputs", release)
        self.assertIn("verify-build-outputs.py", release)
        self.assertIn('CLASH_SIGNING_MODE: "unsigned"', release)
        self.assertIn("if: always()", release)
        self.assertIn("scripts/attach-release-assets.py", weekly)
        self.assertIn("Verify macOS build outputs", weekly)
        self.assertIn("verify-build-outputs.py", weekly)
        self.assertIn('CLASH_SIGNING_MODE: "unsigned"', weekly)
        self.assertNotIn("cancel-in-progress: true", workflow)
        self.assertIn("timeout-minutes: 240", workflow)


    def test_local_signing_scripts_are_opt_in_and_do_not_change_github_release(self):
        wrapper = (ROOT / "scripts/build-local-signed-app.sh").read_text(encoding="utf-8")
        checker = (ROOT / "scripts/check-local-signing-identity.sh").read_text(encoding="utf-8")
        verifier = (ROOT / "scripts/verify-local-signed-app.sh").read_text(encoding="utf-8")
        build = (ROOT / "scripts/build-macos-app.sh").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/build-macos.yml").read_text(encoding="utf-8")
        release = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        weekly = (ROOT / ".github/workflows/upstream-weekly.yml").read_text(encoding="utf-8")

        self.assertIn("--signing-mode local", wrapper)
        self.assertIn("security find-identity -v -p codesigning", checker)
        self.assertIn("codesign --verify --strict", verifier)
        self.assertIn("Clash_Mac_Compile Local Development", wrapper + checker)
        self.assertIn('SIGNING_MODE="${CLASH_SIGNING_MODE:-unsigned}"', build)
        self.assertIn("CODE_SIGNING_ALLOWED=YES", build)
        self.assertIn("CODE_SIGNING_ALLOWED=NO", build)
        self.assertIn('"distribution_mode": "local-development-only" if local else "unsigned"', build)
        self.assertIn('"apple_entitlements_authorized": False', build)
        self.assertIn('"vpn_authorization_supported": bool(vpn_report.get("vpn_authorization_supported", False)) and not local', build)

        for workflow_text in (workflow, release, weekly):
            self.assertNotIn("CLASH_LOCAL_SIGNING_IDENTITY", workflow_text)
            self.assertIn('CLASH_SIGNING_MODE: "unsigned"', workflow_text)
            self.assertNotIn("CLASH_LOCAL_SIGNING_IDENTITY", workflow_text)
            self.assertNotIn("APPLE_TEAM_ID", workflow_text)
        self.assertIn("scripts/attach-release-assets.py", release)
        self.assertIn("scripts/attach-release-assets.py", weekly)

    def test_local_signing_identity_checker_requires_macos(self):
        import platform
        if platform.system() == "Darwin":
            self.skipTest("macOS host can inspect the local Keychain")
        result = self.run_cmd("bash", "scripts/check-local-signing-identity.sh")
        self.assertEqual(result.returncode, 2)
        self.assertIn("require macOS Keychain", result.stderr)

    def test_build_metadata_writer_emits_strict_json(self):
        script = (ROOT / "scripts/build-macos-app.sh").read_text(encoding="utf-8")
        start_marker = '  "$SIGNING_MODE" "$SIGNING_IDENTITY" "$OUTPUT_DIR/VPN-ARCHITECTURE-REPORT.json" <<\'PY\'\n'
        self.assertIn(start_marker, script)
        start = script.index(start_marker) + len(start_marker)
        end = script.index("\nPY\n", start)
        metadata_writer = script[start:end]

        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "project"
            client = Path(td) / "client"
            fake_bin = Path(td) / "bin"
            root.mkdir()
            client.mkdir()
            fake_bin.mkdir()
            (root / "UPSTREAM_CLIENT_REF").write_text("a" * 40 + "\n", encoding="utf-8")
            (client / "Dependencies.lock.json").write_text(json.dumps({
                "kernel": {"repository": "https://example.invalid/kernel", "revision": "b" * 40},
                "adapter": {"repository": "https://example.invalid/adapter", "revision": "c" * 40},
                "gomobile": "v0.0.1",
                "gobind": "v0.0.1"
            }), encoding="utf-8")

            for name, output in {
                "xcodebuild": "Xcode 27.0\nBuild version 17A1\n",
                "go": "go version go1.26.10 darwin/arm64\n",
                "date": "2026-11-05T00:00:00Z\n",
            }.items():
                tool = fake_bin / name
                tool.write_text("#!/bin/sh\nprintf '%b' " + repr(output) + "\n", encoding="utf-8")
                tool.chmod(0o755)

            output = root / "BUILD-METADATA.json"
            vpn_report = root / "VPN-ARCHITECTURE-REPORT.json"
            vpn_report.write_text(json.dumps({
                "distribution_architecture_ready": True,
                "system_extension_packaged": True,
                "vpn_authorization_supported": False
            }), encoding="utf-8")
            env = os.environ.copy()
            env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
            result = subprocess.run(
                [sys.executable, "-c", metadata_writer,
                 str(root), str(client), "a" * 40, "0.1.2", "1",
                 "Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip",
                 str(output), "2", "-O", "unsigned",
                 "Clash_Mac_Compile Local Development", str(vpn_report)],
                cwd=ROOT, env=env, text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            raw = output.read_text(encoding="utf-8")
            self.assertTrue(raw.endswith("\n"))
            self.assertFalse(raw.endswith("\\n"))
            parsed = json.loads(raw)
            self.assertEqual(parsed["distribution_mode"], "unsigned")
            self.assertEqual(parsed["signing"], "disabled")
            self.assertEqual(parsed["xcode_version"], "Xcode 27.0 / Build version 17A1")
            self.assertEqual(parsed["vpn_architecture"], "macos-system-extension")
            self.assertFalse(parsed["vpn_authorization_supported"])

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
            self.assertEqual((copy / "VERSION").read_text().strip(), "0.1.3")
            self.assertEqual((copy / "UPSTREAM_CLIENT_REF").read_text().strip(), new_sha)
            release_notes = copy / "docs/releases/v0.1.3/RELEASE-NOTES.md"
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
            (dist / "Clash_Mac_Compile_v0.1.2_source.zip").write_bytes(b"source")
            (dist / "RELEASE-MANIFEST.json").write_text(json.dumps({
                "project": "Clash_Mac_Compile",
                "project_version": "0.1.2",
                "assets": ["Clash_Mac_Compile_v0.1.2_source.zip"]
            }), encoding="utf-8")
            (build / "Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip").write_bytes(b"unsigned app")
            (build / "BUILD-METADATA.json").write_text(json.dumps({
                "signing": "disabled",
                "team_id": None,
                "distribution_mode": "unsigned",
                "vpn_architecture": "macos-system-extension",
                "vpn_authorization_supported": False,
                "limitations": ["Apple Developer signing is required to activate the System Extension."]
            }), encoding="utf-8")
            (build / "VPN-ARCHITECTURE-REPORT.json").write_text(json.dumps({
                "provider_target_type": "system-extension",
                "distribution_architecture_ready": True,
                "system_extension_packaged": True,
                "vpn_authorization_supported": False
            }), encoding="utf-8")
            (build / "BUILD-OUTPUT-MANIFEST.json").write_text(json.dumps({
                "project_version": "0.1.2",
                "app_artifact": "Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip",
                "required_files": ["Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip"]
            }), encoding="utf-8")
            result = self.run_cmd(
                sys.executable, str(ROOT / "scripts/attach-release-assets.py"),
                "--dist", str(dist), "--source", str(build), "--version", "0.1.2"
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((dist / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["distribution_mode"], "unsigned")
            self.assertFalse(manifest["vpn_authorization_supported"])
            self.assertTrue((dist / "SHA256SUMS.txt").is_file())


    def test_attach_release_assets_rejects_local_signed_app(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dist = root / "dist"
            build = root / "build"
            dist.mkdir()
            build.mkdir()
            (dist / "Clash_Mac_Compile_v0.1.2_source.zip").write_bytes(b"source")
            (dist / "RELEASE-MANIFEST.json").write_text(json.dumps({
                "project": "Clash_Mac_Compile",
                "project_version": "0.1.2",
                "assets": ["Clash_Mac_Compile_v0.1.2_source.zip"]
            }), encoding="utf-8")
            (build / "Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip").write_bytes(b"local signed app")
            (build / "BUILD-METADATA.json").write_text(json.dumps({
                "signing": "local-self-signed",
                "signing_identity": "Clash_Mac_Compile Local Development",
                "team_id": None,
                "distribution_mode": "local-development-only",
                "vpn_authorization_supported": False
            }), encoding="utf-8")
            (build / "VPN-ARCHITECTURE-REPORT.json").write_text(json.dumps({
                "provider_target_type": "system-extension",
                "distribution_architecture_ready": True,
                "system_extension_packaged": True,
                "vpn_authorization_supported": False
            }), encoding="utf-8")
            (build / "BUILD-OUTPUT-MANIFEST.json").write_text(json.dumps({
                "project_version": "0.1.2",
                "app_artifact": "Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip",
                "required_files": ["Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip"]
            }), encoding="utf-8")
            result = self.run_cmd(
                sys.executable, str(ROOT / "scripts/attach-release-assets.py"),
                "--dist", str(dist), "--source", str(build), "--version", "0.1.2"
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("explicitly unsigned", result.stderr)

    def test_attach_release_assets_reports_invalid_metadata_json_location(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dist = root / "dist"
            build = root / "build"
            dist.mkdir()
            build.mkdir()
            (dist / "Clash_Mac_Compile_v0.1.2_source.zip").write_bytes(b"source")
            (dist / "RELEASE-MANIFEST.json").write_text(json.dumps({
                "project": "Clash_Mac_Compile",
                "project_version": "0.1.2",
                "assets": ["Clash_Mac_Compile_v0.1.2_source.zip"]
            }), encoding="utf-8")
            (build / "Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip").write_bytes(b"app")
            (build / "BUILD-METADATA.json").write_text('{"valid": true}\\n\\n', encoding="utf-8")
            (build / "VPN-ARCHITECTURE-REPORT.json").write_text(json.dumps({
                "provider_target_type": "system-extension",
                "distribution_architecture_ready": True,
                "system_extension_packaged": True,
                "vpn_authorization_supported": False
            }), encoding="utf-8")
            (build / "BUILD-OUTPUT-MANIFEST.json").write_text(json.dumps({
                "project_version": "0.1.2",
                "app_artifact": "Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip",
                "required_files": ["Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip"]
            }), encoding="utf-8")
            result = self.run_cmd(
                sys.executable, str(ROOT / "scripts/attach-release-assets.py"),
                "--dist", str(dist), "--source", str(build), "--version", "0.1.2"
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BUILD-METADATA.json", result.stderr)
            self.assertIn("line 1", result.stderr)
            self.assertIn("character", result.stderr)

    def test_attach_release_assets_updates_manifest_and_checksums(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dist = root / "dist"
            build = root / "build"
            dist.mkdir()
            build.mkdir()
            (dist / "Clash_Mac_Compile_v0.1.2_source.zip").write_bytes(b"source")
            (dist / "validation.md").write_text("validation\n", encoding="utf-8")
            manifest = {
                "project": "Clash_Mac_Compile",
                "project_version": "0.1.2",
                "assets": ["Clash_Mac_Compile_v0.1.2_source.zip", "validation.md"]
            }
            (dist / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            (build / "Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip").write_bytes(b"app zip")
            (build / "BUILD-METADATA.json").write_text(json.dumps({
                "client_commit": "abc",
                "signing": "disabled",
                "team_id": None,
                "distribution_mode": "unsigned",
                "vpn_architecture": "macos-system-extension",
                "vpn_authorization_supported": False
            }) + "\n", encoding="utf-8")

            (build / "VPN-ARCHITECTURE-REPORT.json").write_text(json.dumps({
                "provider_target_type": "system-extension",
                "distribution_architecture_ready": True,
                "system_extension_packaged": True,
                "vpn_authorization_supported": False
            }), encoding="utf-8")
            (build / "BUILD-OUTPUT-MANIFEST.json").write_text(json.dumps({
                "project_version": "0.1.2",
                "app_artifact": "Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip",
                "required_files": ["Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip"]
            }), encoding="utf-8")
            result = self.run_cmd(
                sys.executable, str(ROOT / "scripts/attach-release-assets.py"),
                "--dist", str(dist), "--source", str(build), "--version", "0.1.2"
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            updated = json.loads((dist / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
            actual = {p.name for p in dist.iterdir() if p.is_file()}
            self.assertEqual(set(updated["assets"]), actual)
            for line in (dist / "SHA256SUMS.txt").read_text().splitlines():
                digest, name = line.split(maxsplit=1)
                self.assertEqual(hashlib.sha256((dist / name.strip()).read_bytes()).hexdigest(), digest)

    def test_source_release_rejects_local_private_key_material(self):
        with tempfile.TemporaryDirectory() as td:
            copy = Path(td) / "repo"
            ignore = shutil.ignore_patterns(".git", ".dev-state", "dist", "build",
                                            "tmp", "__pycache__", ".pytest_cache",
                                            ".venv", "venv")
            shutil.copytree(ROOT, copy, ignore=ignore)
            local_signing = copy / "LocalSigning"
            local_signing.mkdir()
            (local_signing / "identity.p12").write_bytes(b"private-key-placeholder")
            result = subprocess.run(
                [sys.executable, "scripts/build-release.py"],
                cwd=copy, text=True, capture_output=True
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("拒绝敏感文件", result.stderr)
            self.assertIn("identity.p12", result.stderr)

if __name__ == "__main__":
    unittest.main()
