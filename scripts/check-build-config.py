#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SHA = re.compile(r"^[0-9a-fA-F]{40}$")
REF = re.compile(r"^[A-Za-z0-9._/-]+$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Clash_Mac_Compile build configuration")
    parser.add_argument("--release", action="store_true",
                        help="Require an immutable 40-character upstream Client commit")
    args = parser.parse_args()

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        raise RuntimeError("VERSION must be X.Y.Z")

    ref = (ROOT / "UPSTREAM_CLIENT_REF").read_text(encoding="utf-8").strip()
    if not ref or not REF.fullmatch(ref) or ref.startswith("-"):
        raise RuntimeError("UPSTREAM_CLIENT_REF must be a valid branch, tag, or commit reference")

    profile = json.loads((ROOT / ".ai/PROJECT-PROFILE.json").read_text(encoding="utf-8"))
    if profile.get("project_name") != "Clash_Mac_Compile":
        raise RuntimeError("Unexpected project_name in PROJECT-PROFILE.json")
    if profile.get("repository") != "cdreaming/Clash-Mac-Compile":
        raise RuntimeError("Unexpected repository in PROJECT-PROFILE.json")

    required_files = (
        "scripts/build-macos-app.sh",
        "scripts/build-local-signed-app.sh",
        "scripts/check-local-signing-identity.sh",
        "scripts/verify-local-signed-app.sh",
        ".github/workflows/build-macos.yml",
        ".github/workflows/release.yml",
        ".github/workflows/upstream-weekly.yml",
    )
    for rel in required_files:
        if not (ROOT / rel).is_file():
            raise RuntimeError(f"Required build file missing: {rel}")

    script_text = (ROOT / "scripts/build-macos-app.sh").read_text(encoding="utf-8")
    for token in (
        "ProjectClash/Clash-Client.git",
        "scripts/bootstrap.py",
        "scripts/configure.py",
        "ClashmacOS",
        "CODE_SIGNING_ALLOWED=NO",
        "CODE_SIGNING_ALLOWED=YES",
        "ARCHS=arm64",
        "ONLY_ACTIVE_ARCH=YES",
        '-jobs "$BUILD_JOBS"',
        "lipo -archs",
        'SWIFT_OPTIMIZATION_LEVEL="$SWIFT_OPTIMIZATION_LEVEL"',
        '"distribution_mode": "local-development-only" if local else "unsigned"',
        '"apple_entitlements_authorized": False',
        '"vpn_authorization_supported": False',
    ):
        if token not in script_text:
            raise RuntimeError(f"Build script is missing required feature: {token}")

    for forbidden in (
        "APPLE_TEAM_ID",
        "APPLE_CERTIFICATE",
        "PROVISIONING_PROFILE",
        "notarytool",
        "notarize-macos-app",
    ):
        if forbidden in script_text:
            raise RuntimeError(f"Build script must not require Apple Developer credentials: {forbidden}")

    if "lipo -verify_arch" in script_text:
        raise RuntimeError("Do not use the legacy lipo -verify_arch argument order with Xcode 27")
    if "x86_64" in script_text:
        raise RuntimeError("This version must build Apple Silicon arm64 only")

    local_wrapper = (ROOT / "scripts/build-local-signed-app.sh").read_text(encoding="utf-8")
    identity_check = (ROOT / "scripts/check-local-signing-identity.sh").read_text(encoding="utf-8")
    verifier = (ROOT / "scripts/verify-local-signed-app.sh").read_text(encoding="utf-8")
    for token in ("--signing-mode local", "--signing-identity", "check-local-signing-identity.sh"):
        if token not in local_wrapper:
            raise RuntimeError(f"Local signing wrapper missing: {token}")
    if "security find-identity -v -p codesigning" not in identity_check:
        raise RuntimeError("Local signing identity checker must use the macOS Keychain identity list")
    if "codesign --verify --strict" not in verifier:
        raise RuntimeError("Local signed APP verifier must verify the code signature")
    if "local-self-signed" not in script_text or '"apple_entitlements_authorized": False' not in script_text:
        raise RuntimeError("Local signing metadata must distinguish self-signing from Apple authorization")

    build_text = (ROOT / ".github/workflows/build-macos.yml").read_text(encoding="utf-8")
    if "runs-on: xcode-27" not in build_text:
        raise RuntimeError("Build workflow must use xcode-27")
    if "actions/upload-artifact@v6" not in build_text:
        raise RuntimeError("Build workflow must use upload-artifact v6")
    if 'CLASH_SWIFT_OPTIMIZATION_LEVEL: "-O"' not in build_text:
        raise RuntimeError("Build workflow must prioritize Swift runtime speed")
    if 'CLASH_BUILD_JOBS: "2"' not in build_text:
        raise RuntimeError("Build workflow must limit Xcode jobs to 2")
    if "macos-arm64-unsigned" not in build_text:
        raise RuntimeError("GitHub Build workflow must remain unsigned")
    if "CLASH_SIGNING_MODE" in build_text:
        raise RuntimeError("GitHub Build workflow must not attempt to use a developer's local Keychain")
    if "CODE_SIGNING_ALLOWED=NO" not in script_text:
        raise RuntimeError("Unsigned build must explicitly prevent Xcode from requesting a signing identity")

    release_text = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    weekly_text = (ROOT / ".github/workflows/upstream-weekly.yml").read_text(encoding="utf-8")
    for name, workflow_text in (
        ("Build", build_text), ("Release", release_text), ("Weekly", weekly_text)
    ):
        if any(token in workflow_text for token in (
            "APPLE_TEAM_ID", "APPLE_CERTIFICATE", "APPLE_NOTARY",
            "CLASH_LOCAL_SIGNING_IDENTITY", "CLASH_SIGNING_MODE"
        )):
            raise RuntimeError(f"{name} workflow must not require a user's local signing key")
        if "import-apple-signing-assets" in workflow_text or "notarize-macos-app" in workflow_text:
            raise RuntimeError(f"{name} workflow must not invoke Apple signing or notarization scripts")

    if "scripts/check-build-config.py --release" not in release_text:
        raise RuntimeError("Release workflow must enforce immutable upstream source")
    if "scripts/attach-release-assets.py" not in release_text:
        raise RuntimeError("Release workflow must attach the unsigned APP and metadata")
    if "scripts/attach-release-assets.py" not in release_text:
        raise RuntimeError("GitHub Release must attach the unsigned APP through the guarded asset script")

    for token in ('schedule:', 'timezone: "America/Los_Angeles"', 'contents: write',
                  "scripts/prepare-weekly-upstream-release.py", "--prerelease",
                  "scripts/verify-github-release.sh", "scripts/attach-release-assets.py"):
        if token not in weekly_text:
            raise RuntimeError(f"Weekly workflow is missing required feature: {token}")

    if args.release and not SHA.fullmatch(ref):
        raise RuntimeError(
            "Release requires UPSTREAM_CLIENT_REF to be a full 40-character commit SHA; "
            "branch names such as main are mutable."
        )

    print(
        f"Build configuration OK: version={version}, upstream_client_ref={ref}, "
        "GitHub=unsigned, local_signing=optional-self-signed"
    )
    if not SHA.fullmatch(ref):
        print("WARNING: upstream ref is mutable; pin a full commit SHA before Release.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Build configuration failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
