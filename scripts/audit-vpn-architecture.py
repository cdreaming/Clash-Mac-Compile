#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
import subprocess
import sys
from pathlib import Path

import yaml


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True)


def code_signature(bundle: Path) -> dict:
    result = run("codesign", "-dv", "--verbose=4", str(bundle))
    detail = result.stderr + "\n" + result.stdout
    team = None
    for line in detail.splitlines():
        if line.startswith("TeamIdentifier="):
            team = line.split("=", 1)[1].strip()
            break
    signature = "adhoc" if "Signature=adhoc" in detail or ("flags=0x" in detail and "adhoc" in detail) else "unknown"
    if "Authority=Developer ID Application:" in detail:
        signature = "developer-id"
    elif "Authority=Clash_Mac_Compile Local Development" in detail:
        signature = "local-self-signed"
    return {
        "verified": result.returncode == 0,
        "team_identifier": team,
        "signature_type": signature,
        "detail": detail.strip(),
    }


def signed_entitlements(bundle: Path) -> dict:
    result = run("codesign", "-d", "--entitlements", ":-", "--xml", str(bundle))
    raw = result.stdout.encode("utf-8", errors="replace")
    if not raw.strip():
        raw = result.stderr.encode("utf-8", errors="replace")
    try:
        value = plistlib.loads(raw)
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit Clash macOS Packet Tunnel System Extension packaging and authorization readiness."
    )
    parser.add_argument("--client-dir", required=True, type=Path)
    parser.add_argument("--app", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    client = args.client_dir.resolve()
    spec_path = client / "apple/ClashClient/project.yml"
    auth_path = client / "apple/ClashClient/Sources/VPNStartAuthorization.swift"
    activator_path = client / "apple/ClashClient/Sources/ClashMacSystemExtensionActivator.swift"

    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    targets = spec.get("targets", {})
    app_target = targets.get("ClashmacOS", {})
    extension_target = targets.get("ClashmacOSExtension", {})
    project_bundle_base = spec.get("settings", {}).get("base", {}).get("CLASH_BUNDLE_BASE", "")
    app_entitlements = app_target.get("entitlements", {}).get("properties", {})
    extension_entitlements = extension_target.get("entitlements", {}).get("properties", {})
    app_groups = set(app_entitlements.get("com.apple.security.application-groups", []))
    provider_groups = set(extension_entitlements.get("com.apple.security.application-groups", []))
    shared_app_groups = sorted(app_groups.intersection(provider_groups))
    dependencies = app_target.get("dependencies", [])
    app_deps = [item.get("sdk") for item in dependencies if isinstance(item, dict) and item.get("sdk")]
    provider_dependencies = extension_target.get("dependencies", [])
    provider_core_dependency = next(
        (item for item in provider_dependencies
         if isinstance(item, dict) and item.get("target") == "ClashMacCore"),
        None
    )
    provider_runpaths = extension_target.get("settings", {}).get("base", {}).get("LD_RUNPATH_SEARCH_PATHS", [])
    if isinstance(provider_runpaths, str):
        provider_runpaths = [provider_runpaths]
    provider_dependency = next(
        (item for item in dependencies
         if isinstance(item, dict) and item.get("target") == "ClashmacOSExtension"),
        None
    )

    auth_source = auth_path.read_text(encoding="utf-8") if auth_path.is_file() else ""
    activator_source = activator_path.read_text(encoding="utf-8") if activator_path.is_file() else ""

    raw_provider_id = extension_target.get("settings", {}).get("base", {}).get("PRODUCT_BUNDLE_IDENTIFIER", "")
    raw_app_id = app_target.get("settings", {}).get("base", {}).get("PRODUCT_BUNDLE_IDENTIFIER", "")
    expected_provider_id = raw_provider_id.replace("$(CLASH_BUNDLE_BASE)", str(project_bundle_base))
    expected_app_id = raw_app_id.replace("$(CLASH_BUNDLE_BASE)", str(project_bundle_base))

    report = {
        "project": "Clash_Mac_Compile",
        "expected_app_bundle_identifier": expected_app_id,
        "provider_target_type": extension_target.get("type"),
        "provider_bundle_identifier": expected_provider_id,
        "provider_extension_point": extension_target.get("info", {}).get("properties", {})
                    .get("NSExtension", {}).get("NSExtensionPointIdentifier"),
        "app_network_extension_entitlements": app_entitlements.get("com.apple.developer.networking.networkextension", []),
        "provider_network_extension_entitlements": extension_entitlements.get("com.apple.developer.networking.networkextension", []),
        "app_system_extension_install_entitlement": app_entitlements.get("com.apple.developer.system-extension.install", False),
        "app_groups": sorted(app_groups),
        "provider_app_groups": sorted(provider_groups),
        "shared_app_groups": shared_app_groups,
        "shared_app_group_available": bool(shared_app_groups),
        "system_extensions_framework_linked": "SystemExtensions.framework" in app_deps,
        "provider_embedded_by_host_app": bool(provider_dependency and provider_dependency.get("embed") is True),
        "provider_core_framework_embedded": bool(provider_core_dependency and provider_core_dependency.get("embed") is True),
        "provider_framework_runpaths": provider_runpaths,
        "provider_framework_runpath_valid": "@executable_path/../Frameworks" in provider_runpaths,
        "activation_request_in_vpn_start_flow": "ClashMacSystemExtensionActivator.activate" in auth_source,
        "activation_helper_present": activator_path.is_file() and "OSSystemExtensionRequest.activationRequest" in activator_source,
        "vpn_manager_save_flow_present": "IPStackProfileWriter.awaitConfirmation" in auth_source,
        "distribution_architecture_ready": False,
        "system_extension_packaged": False,
        "system_extension_bundle_identifier": None,
        "app_bundle_identifier": None,
        "app_bundle_identifier_matches_project": False,
        "provider_bundle_identifier_matches_app": False,
        "app_signature": None,
        "provider_signature": None,
        "app_entitlements": {},
        "provider_entitlements": {},
        "apple_developer_id": False,
        "apple_entitlements_authorized": False,
        "provisioning_profile_present": False,
        "vpn_authorization_supported": False,
        "limitations": [
            "A System Extension target and activation request do not grant Apple Developer entitlements.",
            "The current GitHub build is unsigned; a local self-signed identity is not an Apple Developer ID.",
            "A valid Developer ID signature, Apple-authorized Network Extension entitlement and provisioning profile are required for direct distribution activation."
        ],
    }

    structural_checks = {
        "provider_target_type": extension_target.get("type") == "system-extension",
        "provider_extension_point": report["provider_extension_point"] == "com.apple.networkextension.packet-tunnel",
        "app_network_extension_entitlements": "packet-tunnel-provider-systemextension" in report["app_network_extension_entitlements"],
        "provider_network_extension_entitlements": "packet-tunnel-provider-systemextension" in report["provider_network_extension_entitlements"],
        "app_system_extension_install_entitlement": report["app_system_extension_install_entitlement"] is True,
        "shared_app_group_available": report["shared_app_group_available"],
        "system_extensions_framework_linked": report["system_extensions_framework_linked"],
        "provider_embedded_by_host_app": report["provider_embedded_by_host_app"],
        "provider_core_framework_embedded": report["provider_core_framework_embedded"],
        "provider_framework_runpath_valid": report["provider_framework_runpath_valid"],
        "activation_request_in_vpn_start_flow": report["activation_request_in_vpn_start_flow"],
        "activation_helper_present": report["activation_helper_present"],
        "vpn_manager_save_flow_present": report["vpn_manager_save_flow_present"],
    }
    report["structural_checks"] = structural_checks
    report["distribution_architecture_ready"] = all(structural_checks.values())

    if args.app:
        app = args.app.resolve()
        app_info = plistlib.loads((app / "Contents/Info.plist").read_bytes())
        app_bundle_id = app_info.get("CFBundleIdentifier")
        system_extensions_dir = app / "Contents/Library/SystemExtensions"
        extensions = list(system_extensions_dir.glob("*.systemextension")) if system_extensions_dir.is_dir() else []
        provider = None
        for candidate in extensions:
            try:
                info = plistlib.loads((candidate / "Contents/Info.plist").read_bytes())
            except Exception:
                continue
            if info.get("CFBundleIdentifier") == expected_provider_id:
                provider = candidate
                break

        report["app_bundle_identifier"] = app_bundle_id
        report["app_bundle_identifier_matches_project"] = app_bundle_id == expected_app_id
        report["provider_bundle_identifier_matches_app"] = expected_provider_id == f"{app_bundle_id}.packet-tunnel"
        report["system_extension_packaged"] = provider is not None
        report["system_extension_bundle_identifier"] = expected_provider_id if provider else None
        report["app_signature"] = code_signature(app)
        report["app_entitlements"] = signed_entitlements(app)
        app_profile_present = (
            (app / "Contents/embedded.provisionprofile").is_file()
            or (app / "Contents/embedded.provisioningprofile").is_file()
        )

        if provider:
            report["provider_signature"] = code_signature(provider)
            report["provider_entitlements"] = signed_entitlements(provider)
        app_team = (report["app_signature"] or {}).get("team_identifier")
        provider_team = (report["provider_signature"] or {}).get("team_identifier") if provider else None
        app_ne = report["app_entitlements"].get("com.apple.developer.networking.networkextension", [])
        provider_ne = report["provider_entitlements"].get("com.apple.developer.networking.networkextension", [])
        app_install = report["app_entitlements"].get("com.apple.developer.system-extension.install", False)
        app_signed_groups = set(report["app_entitlements"].get("com.apple.security.application-groups", []))
        provider_signed_groups = set(report["provider_entitlements"].get("com.apple.security.application-groups", []))
        report["signed_app_groups_match"] = bool(app_signed_groups.intersection(provider_signed_groups))
        provider_profile_present = bool(provider and (
            (provider / "Contents/embedded.provisionprofile").is_file()
            or (provider / "Contents/embedded.provisioningprofile").is_file()
        ))
        report["provisioning_profile_present"] = app_profile_present or provider_profile_present
        developer_id = (report["app_signature"] or {}).get("signature_type") == "developer-id"
        report["apple_developer_id"] = bool(developer_id and app_team and app_team == provider_team)
        report["apple_entitlements_authorized"] = bool(
            report["apple_developer_id"]
            and "packet-tunnel-provider-systemextension" in app_ne
            and "packet-tunnel-provider-systemextension" in provider_ne
            and app_install
            and report["signed_app_groups_match"]
            and report["provisioning_profile_present"]
        )
        report["vpn_authorization_supported"] = bool(
            report["distribution_architecture_ready"]
            and report["system_extension_packaged"]
            and report["app_bundle_identifier_matches_project"]
            and report["provider_bundle_identifier_matches_app"]
            and report["apple_entitlements_authorized"]
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not report["distribution_architecture_ready"]:
        failed = [key for key, passed in structural_checks.items() if not passed]
        print("VPN architecture audit failed: " + ", ".join(failed), file=sys.stderr)
        return 1
    if args.app and not report["system_extension_packaged"]:
        print("VPN architecture audit failed: System Extension is not embedded in Contents/Library/SystemExtensions.", file=sys.stderr)
        return 1
    if args.app and (not report["app_bundle_identifier_matches_project"] or not report["provider_bundle_identifier_matches_app"]):
        print("VPN architecture audit failed: app/provider Bundle IDs do not match the configured family.", file=sys.stderr)
        return 1

    print("VPN architecture audit: PASS")
    print(f"  Provider target: {report['provider_target_type']}")
    print(f"  Provider bundle ID: {expected_provider_id}")
    print(f"  System Extension embedded: {report['system_extension_packaged']}")
    print(f"  Apple authorization: {'verified' if report['vpn_authorization_supported'] else 'NOT VERIFIED / NOT AUTHORIZED'}")
    print(f"  Report: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"VPN architecture audit failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
