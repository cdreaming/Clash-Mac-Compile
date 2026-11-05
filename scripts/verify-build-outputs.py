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
    ]

    print(f"Build output directory: {directory}")
    if directory.is_dir():
        for item in sorted(directory.iterdir()):
            if item.is_file():
                print(f"  {item.name} ({item.stat().st_size} bytes)")
    else:
        print("  <directory does not exist>")

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
            "The Xcode build step may have stopped before packaging, or --output points to a different directory.",
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
