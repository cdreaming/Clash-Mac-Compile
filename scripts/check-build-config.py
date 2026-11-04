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
    parser = argparse.ArgumentParser(description="Validate unsigned Clash_Mac_Compile build configuration")
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

    build_script = ROOT / "scripts/build-macos-app.sh"
    build_workflow = ROOT / ".github/workflows/build-macos.yml"
    release_workflow = ROOT / ".github/workflows/release.yml"
    weekly_workflow = ROOT / ".github/workflows/upstream-weekly.yml"
    for path in (build_script, build_workflow, release_workflow, weekly_workflow):
        if not path.is_file():
            raise RuntimeError(f"Required build file missing: {path.relative_to(ROOT)}")

    script_text = build_script.read_text(encoding="utf-8")
    for token in (
        "ProjectClash/Clash-Client.git",
        "scripts/bootstrap.py",
        "scripts/configure.py",
        "ClashmacOS",
        "CODE_SIGNING_ALLOWED=NO",
        "ARCHS=arm64",
        "ONLY_ACTIVE_ARCH=YES",
        '-jobs "$BUILD_JOBS"',
        "lipo -archs",
        'SWIFT_OPTIMIZATION_LEVEL="$SWIFT_OPTIMIZATION_LEVEL"',
        '"distribution_mode": "unsigned"',
        '"vpn_authorization_supported": False',
    ):
        if token not in script_text:
            raise RuntimeError(f"Build script is missing required unsigned build feature: {token}")

    for forbidden in (
        "CODE_SIGNING_ALLOWED=YES",
        "Developer ID Application",
        "APPLE_TEAM_ID",
        "APPLE_CERTIFICATE",
        "PROVISIONING_PROFILE",
        "notarytool",
        "notarize-macos-app",
        "CLASH_SIGNING_MODE",
    ):
        if forbidden in script_text:
            raise RuntimeError(f"Signing configuration must be removed from build script: {forbidden}")

    if "lipo -verify_arch" in script_text:
        raise RuntimeError("Do not use the legacy lipo -verify_arch argument order with Xcode 27")
    if "x86_64" in script_text:
        raise RuntimeError("This version must build Apple Silicon arm64 only")

    build_text = build_workflow.read_text(encoding="utf-8")
    if "runs-on: xcode-27" not in build_text:
        raise RuntimeError("Build workflow must use xcode-27")
    if "actions/upload-artifact@v6" not in build_text:
        raise RuntimeError("Build workflow must use upload-artifact v6")
    if 'CLASH_SWIFT_OPTIMIZATION_LEVEL: "-O"' not in build_text:
        raise RuntimeError("Build workflow must prioritize Swift runtime speed")
    if 'CLASH_BUILD_JOBS: "2"' not in build_text:
        raise RuntimeError("Build workflow must limit Xcode jobs to 2")
    if "macos-arm64-unsigned" not in build_text:
        raise RuntimeError("Build workflow must label its unsigned APP artifact")
    if "CODE_SIGNING_ALLOWED=NO" not in script_text:
        raise RuntimeError("Unsigned build must explicitly prevent Xcode from requesting a signing identity")

    for name, workflow_text in (
        ("Build", build_text),
        ("Release", release_workflow.read_text(encoding="utf-8")),
        ("Weekly", weekly_workflow.read_text(encoding="utf-8")),
    ):
        if "APPLE_TEAM_ID" in workflow_text or "APPLE_CERTIFICATE" in workflow_text or "APPLE_NOTARY" in workflow_text:
            raise RuntimeError(f"{name} workflow must not require Apple Developer secrets")
        if "import-apple-signing-assets" in workflow_text or "notarize-macos-app" in workflow_text:
            raise RuntimeError(f"{name} workflow must not invoke Apple signing or notarization scripts")

    release_text = release_workflow.read_text(encoding="utf-8")
    if "scripts/check-build-config.py --release" not in release_text:
        raise RuntimeError("Release workflow must enforce immutable upstream source")
    if "scripts/attach-release-assets.py" not in release_text:
        raise RuntimeError("Release workflow must attach the unsigned APP and metadata")

    weekly_text = weekly_workflow.read_text(encoding="utf-8")
    for token in ('schedule:', 'timezone: "America/Los_Angeles"', 'contents: write',
                  "scripts/prepare-weekly-upstream-release.py", "--prerelease",
                  "scripts/verify-github-release.sh"):
        if token not in weekly_text:
            raise RuntimeError(f"Weekly workflow is missing required feature: {token}")

    if args.release and not SHA.fullmatch(ref):
        raise RuntimeError(
            "Release requires UPSTREAM_CLIENT_REF to be a full 40-character commit SHA; "
            "branch names such as main are mutable."
        )

    print(f"Build configuration OK: version={version}, upstream_client_ref={ref}, signing=disabled")
    if not SHA.fullmatch(ref):
        print("WARNING: upstream ref is mutable; pin a full commit SHA before Release.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Build configuration failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
