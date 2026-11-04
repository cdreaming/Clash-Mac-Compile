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

    build_script = ROOT / "scripts/build-macos-app.sh"
    workflow = ROOT / ".github/workflows/build-macos.yml"
    release_workflow = ROOT / ".github/workflows/release.yml"
    for path in (build_script, workflow, release_workflow):
        if not path.is_file():
            raise RuntimeError(f"Required build file missing: {path.relative_to(ROOT)}")

    script_text = build_script.read_text(encoding="utf-8")
    required_script_tokens = (
        "ProjectClash/Clash-Client.git",
        "scripts/bootstrap.py",
        "scripts/configure.py",
        "ClashmacOS",
        "CODE_SIGNING_ALLOWED=NO",
        "ARCHS=arm64",
        "ONLY_ACTIVE_ARCH=YES",
        '-jobs "$BUILD_JOBS"',
        "lipo -verify_arch arm64",
        "CLASH_BUILD_JOBS",
    )
    for token in required_script_tokens:
        if token not in script_text:
            raise RuntimeError(f"Build script is missing required step: {token}")
    if "x86_64" in script_text:
        raise RuntimeError("This version must build Apple Silicon arm64 only")

    workflow_text = workflow.read_text(encoding="utf-8")
    if "cancel-in-progress: true" in workflow_text:
        raise RuntimeError("Build workflow must not cancel an in-progress build automatically")
    if "macos-arm64" not in workflow_text:
        raise RuntimeError("Build workflow must publish an arm64-only artifact")
    if "runs-on: xcode-27" not in workflow_text:
        raise RuntimeError("Build workflow must use the xcode-27 macOS runner")
    if "timeout-minutes: 240" not in workflow_text:
        raise RuntimeError("Build workflow timeout must be 240 minutes")
    if 'CLASH_BUILD_JOBS: "2"' not in workflow_text:
        raise RuntimeError("Build workflow must limit Xcode parallel jobs to 2")
    if "actions/upload-artifact@" not in workflow_text:
        raise RuntimeError("Build workflow must upload its build artifact")

    release_text = release_workflow.read_text(encoding="utf-8")
    if "scripts/check-build-config.py --release" not in release_text:
        raise RuntimeError("Release workflow must enforce immutable upstream source")

    if args.release and not SHA.fullmatch(ref):
        raise RuntimeError(
            "Release requires UPSTREAM_CLIENT_REF to be a full 40-character commit SHA; "
            "branch names such as main are mutable."
        )

    print(f"Build configuration OK: version={version}, upstream_client_ref={ref}")
    if not SHA.fullmatch(ref):
        print("WARNING: upstream ref is mutable; pin a full commit SHA before Release.", file=sys.stderr)
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Build configuration failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
