from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VPNArchitectureTests(unittest.TestCase):
    def make_upstream_fixture(self, root: Path) -> Path:
        client = root / "client"
        app = client / "apple/ClashClient"
        (app / "Sources").mkdir(parents=True)
        (app / "project.yml").write_text(
            """
name: ClashClient
settings:
  base:
    CLASH_BUNDLE_BASE: com.example.clash
targets:
  ClashmacOS:
    type: application
    platform: macOS
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: $(CLASH_BUNDLE_BASE)
    entitlements:
      path: ClashmacOS.entitlements
      properties:
        com.apple.developer.networking.networkextension:
          - packet-tunnel-provider
        com.apple.security.application-groups:
          - group.com.example.clash
    dependencies:
      - target: ClashmacOSExtension
        embed: true
      - sdk: NetworkExtension.framework
  ClashMacCore:
    type: framework
    platform: macOS
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: $(CLASH_BUNDLE_BASE).core
  ClashmacOSExtension:
    type: app-extension
    platform: macOS
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: $(CLASH_BUNDLE_BASE).packet-tunnel
        PRODUCT_NAME: ClashmacOSExtension
    entitlements:
      path: ClashmacOSExtension.entitlements
      properties:
        com.apple.developer.networking.networkextension:
          - packet-tunnel-provider
        com.apple.security.application-groups:
          - group.com.example.clash
    info:
      path: Extension-Info.plist
      properties:
        NSExtension:
          NSExtensionPointIdentifier: com.apple.networkextension.packet-tunnel
  ClashmacOSWidgets:
    type: app-extension
    platform: macOS
    entitlements:
      path: Widgets.entitlements
      properties:
        com.apple.developer.networking.networkextension:
          - packet-tunnel-provider
""",
            encoding="utf-8",
        )
        (app / "Sources/VPNStartAuthorization.swift").write_text(
            """import Foundation

@MainActor
enum VPNStartAuthorization {
    static func perform() async throws {
        do {
            try await IPStackProfileWriter.awaitConfirmation(
                operation: save,
                delay: delay,
                onWaiting: onWaiting
            )
        } catch {
            throw error
        }
    }
}
""",
            encoding="utf-8",
        )
        return client

    def run_script(self, script: str, *args: str):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_patch_converts_packet_tunnel_target_and_wires_activation(self):
        with tempfile.TemporaryDirectory() as td:
            client = self.make_upstream_fixture(Path(td))
            result = self.run_script("patch-macos-system-extension.py", "--client-dir", str(client))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            import yaml
            spec = yaml.safe_load((client / "apple/ClashClient/project.yml").read_text(encoding="utf-8"))
            app = spec["targets"]["ClashmacOS"]
            extension = spec["targets"]["ClashmacOSExtension"]
            widgets = spec["targets"]["ClashmacOSWidgets"]

            self.assertEqual(extension["type"], "system-extension")
            core_dependencies = [
                item for item in extension["dependencies"]
                if isinstance(item, dict) and item.get("target") == "ClashMacCore"
            ]
            self.assertEqual(len(core_dependencies), 1)
            self.assertTrue(core_dependencies[0]["embed"])
            self.assertEqual(
                extension["settings"]["base"]["LD_RUNPATH_SEARCH_PATHS"],
                ["$(inherited)", "@executable_path/../Frameworks"],
            )
            self.assertIn(
                "packet-tunnel-provider-systemextension",
                extension["entitlements"]["properties"]["com.apple.developer.networking.networkextension"],
            )
            self.assertIn(
                "packet-tunnel-provider-systemextension",
                app["entitlements"]["properties"]["com.apple.developer.networking.networkextension"],
            )
            self.assertTrue(app["entitlements"]["properties"]["com.apple.developer.system-extension.install"])
            self.assertIn(
                {"sdk": "SystemExtensions.framework"},
                app["dependencies"],
            )
            self.assertNotIn(
                "com.apple.developer.networking.networkextension",
                widgets["entitlements"]["properties"],
            )

            auth = (client / "apple/ClashClient/Sources/VPNStartAuthorization.swift").read_text(encoding="utf-8")
            activator = (client / "apple/ClashClient/Sources/ClashMacSystemExtensionActivator.swift").read_text(encoding="utf-8")
            self.assertIn("ClashMacSystemExtensionActivator.activate(onWaiting: onWaiting)", auth)
            self.assertIn("OSSystemExtensionRequest.activationRequest", activator)
            self.assertIn("OSSystemExtensionManager.shared.submitRequest", activator)
            self.assertIn("requestNeedsUserApproval", activator)

    def test_patch_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            client = self.make_upstream_fixture(Path(td))
            for _ in range(2):
                result = self.run_script("patch-macos-system-extension.py", "--client-dir", str(client))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            text = (client / "apple/ClashClient/Sources/VPNStartAuthorization.swift").read_text(encoding="utf-8")
            self.assertEqual(text.count("ClashMacSystemExtensionActivator.activate"), 1)

            import yaml
            spec = yaml.safe_load((client / "apple/ClashClient/project.yml").read_text(encoding="utf-8"))
            frameworks = [
                dep for dep in spec["targets"]["ClashmacOS"]["dependencies"]
                if isinstance(dep, dict) and dep.get("sdk") == "SystemExtensions.framework"
            ]
            self.assertEqual(len(frameworks), 1)
            core_dependencies = [
                dep for dep in spec["targets"]["ClashmacOSExtension"]["dependencies"]
                if isinstance(dep, dict) and dep.get("target") == "ClashMacCore"
            ]
            self.assertEqual(len(core_dependencies), 1)
            self.assertTrue(core_dependencies[0]["embed"])

    def test_vpn_architecture_audit_checks_real_bundle_layout_and_bundle_ids(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            client = self.make_upstream_fixture(root)
            patch = self.run_script("patch-macos-system-extension.py", "--client-dir", str(client))
            self.assertEqual(patch.returncode, 0, patch.stdout + patch.stderr)

            app = root / "Clash.app"
            contents = app / "Contents"
            provider = contents / "Library/SystemExtensions/com.example.clash.packet-tunnel.systemextension"
            (contents).mkdir(parents=True)
            (provider / "Contents").mkdir(parents=True)
            import plistlib
            (contents / "Info.plist").write_bytes(plistlib.dumps({
                "CFBundleIdentifier": "com.example.clash",
                "CFBundleExecutable": "Clash"
            }))
            (provider / "Contents/Info.plist").write_bytes(plistlib.dumps({
                "CFBundleIdentifier": "com.example.clash.packet-tunnel",
                "NSExtension": {
                    "NSExtensionPointIdentifier": "com.apple.networkextension.packet-tunnel"
                }
            }))

            fake_bin = root / "bin"
            fake_bin.mkdir()
            codesign = fake_bin / "codesign"
            codesign.write_text(
                "#!/bin/sh\n"
                "case \"$*\" in\n"
                "  *-dv*) printf 'Signature=adhoc\\nTeamIdentifier=not set\\n' >&2 ;;\n"
                "  *) : ;;\n"
                "esac\n",
                encoding="utf-8",
            )
            codesign.chmod(0o755)

            output = root / "VPN-ARCHITECTURE-REPORT.json"
            import os
            env = os.environ.copy()
            env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/audit-vpn-architecture.py"),
                 "--client-dir", str(client), "--app", str(app), "--output", str(output)],
                cwd=ROOT, env=env, text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(report["system_extension_packaged"])
            self.assertTrue(report["app_bundle_identifier_matches_project"])
            self.assertTrue(report["provider_bundle_identifier_matches_app"])
            self.assertFalse(report["vpn_authorization_supported"])
            self.assertEqual(report["app_signature"]["signature_type"], "adhoc")

    def test_vpn_architecture_audit_passes_structural_fixture(self):
        with tempfile.TemporaryDirectory() as td:
            client = self.make_upstream_fixture(Path(td))
            patch = self.run_script("patch-macos-system-extension.py", "--client-dir", str(client))
            self.assertEqual(patch.returncode, 0, patch.stdout + patch.stderr)

            report_path = Path(td) / "VPN-ARCHITECTURE-REPORT.json"
            audit = self.run_script(
                "audit-vpn-architecture.py",
                "--client-dir", str(client),
                "--output", str(report_path),
            )
            self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertTrue(report["distribution_architecture_ready"])
            self.assertFalse(report["vpn_authorization_supported"])
            self.assertEqual(report["provider_target_type"], "system-extension")
            self.assertTrue(report["activation_request_in_vpn_start_flow"])


if __name__ == "__main__":
    unittest.main()
