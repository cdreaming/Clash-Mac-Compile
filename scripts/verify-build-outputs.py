#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify expected macOS build outputs before artifact upload or Release attachment.")
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--mode", choices=("unsigned", "local"), default="unsigned")
    args = parser.parse_args()

    directory = args.directory.resolve()
    expected_app = (
        f"Clash_Mac_Compile-v{args.version}-macos-arm64-"
        f"{'unsigned' if args.mode == 'unsigned' else 'local-signed'}.zip"
    )
    required = [
        expected_app,
        "BUILD-METADATA.json",
        "VPN-ARCHITECTURE-REPORT.json",
        "SHA256SUMS.txt",
        "BUILD-OUTPUT-MANIFEST.json",
        "BUILD-SCRIPT-STATUS.txt",
        "BUILD-RUN-CONTEXT.txt",
    ]

    print(f"Build output directory: {directory}")
    if directory.is_dir():
        items = sorted(directory.rglob("*"))
        files = [item for item in items if item.is_file()]
        if files:
            for item in files:
                print(f"  {item.relative_to(directory)} ({item.stat().st_size} bytes)")
        else:
            print("  <directory exists but contains no files>")
    else:
        print("  <directory does not exist>")

    status_file = directory / "BUILD-SCRIPT-STATUS.txt"
    if status_file.is_file():
        status_text = status_file.read_text(encoding="utf-8", errors="replace")
        print("Build script status:")
        print(status_text.rstrip())
        status = {}
        for line in status_text.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                status[key.strip()] = value.strip()
        if status.get("status") != "success" or status.get("exit_code") != "0":
            print("Build script did not report a successful exit.", file=sys.stderr)
            return 1
    else:
        context = directory / "BUILD-RUN-CONTEXT.txt"
        if context.is_file():
            print("Build run context:")
            print(context.read_text(encoding="utf-8", errors="replace").rstrip())
        print(
            "BUILD-SCRIPT-STATUS.txt is missing. The build script may not have started, "
            "may have used another output directory, or may be from an older source revision.",
            file=sys.stderr,
        )
        return 1

    missing = [
        name for name in required
        if not (directory / name).is_file() or (directory / name).stat().st_size == 0
    ]
    if missing:
        print(
            "Build output verification failed. Missing or empty files: "
            + ", ".join(missing),
            file=sys.stderr,
        )
        print(
            "The build script ran but did not produce every required output. Inspect BUILD-SCRIPT-STATUS.txt, "
            "BUILD-RUN-CONTEXT.txt and the Xcode linker diagnostic files.",
            file=sys.stderr,
        )
        return 1

    try:
        metadata = json.loads((directory / "BUILD-METADATA.json").read_text(encoding="utf-8"))
        manifest = json.loads((directory / "BUILD-OUTPUT-MANIFEST.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid build JSON: {exc}", file=sys.stderr)
        return 1

    expected_distribution = "unsigned" if args.mode == "unsigned" else "local-development-only"
    if metadata.get("project_version") != args.version:
        print("BUILD-METADATA.json project_version does not match VERSION.", file=sys.stderr)
        return 1
    if metadata.get("distribution_mode") != expected_distribution:
        print(
            f"Unexpected distribution_mode: {metadata.get('distribution_mode')!r}; expected {expected_distribution!r}",
            file=sys.stderr,
        )
        return 1
    if manifest.get("project_version") != args.version:
        print("BUILD-OUTPUT-MANIFEST.json project_version does not match VERSION.", file=sys.stderr)
        return 1
    if manifest.get("app_artifact") != expected_app:
        print("BUILD-OUTPUT-MANIFEST.json app_artifact does not match the expected ZIP name.", file=sys.stderr)
        return 1
    if expected_app not in manifest.get("required_files", []):
        print("BUILD-OUTPUT-MANIFEST.json does not list the APP ZIP as a required output.", file=sys.stderr)
        return 1

    print("Build output verification: PASS")
    print(f"APP artifact: {directory / expected_app}")
    print(f"Distribution mode: {expected_distribution}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
