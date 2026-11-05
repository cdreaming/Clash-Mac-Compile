#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in {label} ({path}): {exc.msg} "
            f"at line {exc.lineno}, column {exc.colno}, character {exc.pos}. "
            "Check that the file contains exactly one JSON object and no literal \\n suffix."
        ) from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must contain a JSON object: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Attach the unsigned arm64 macOS APP and metadata to a GitHub Release package"
    )
    parser.add_argument("--dist", default="dist")
    parser.add_argument("--source", default="build/release")
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    dist = (root / args.dist).resolve()
    source = (root / args.source).resolve()
    manifest_path = dist / "RELEASE-MANIFEST.json"
    if not manifest_path.is_file():
        raise RuntimeError("RELEASE-MANIFEST.json missing; run scripts/build-release.py first")

    zip_name = f"Clash_Mac_Compile-v{args.version}-macos-arm64-unsigned.zip"
    required = [source / zip_name, source / "BUILD-METADATA.json"]
    for item in required:
        if not item.is_file():
            raise RuntimeError(f"Required macOS release asset missing: {item}")

    metadata = load_json(source / "BUILD-METADATA.json", "BUILD-METADATA.json")
    if metadata.get("distribution_mode") != "unsigned":
        raise RuntimeError("This project version only accepts an explicitly unsigned APP build.")
    if metadata.get("signing") != "disabled" or metadata.get("vpn_authorization_supported") is not False:
        raise RuntimeError("APP metadata must clearly identify disabled signing and unsupported VPN authorization.")

    manifest = load_json(manifest_path, "RELEASE-MANIFEST.json")
    if manifest.get("project_version") != args.version:
        raise RuntimeError("Release manifest version does not match requested version")

    for item in required:
        shutil.copy2(item, dist / item.name)

    assets = sorted(
        path.name for path in dist.iterdir()
        if path.is_file() and path.name not in {"SHA256SUMS.txt", "RELEASE-MANIFEST.json"}
    )
    manifest["assets"] = sorted(assets + ["SHA256SUMS.txt", "RELEASE-MANIFEST.json"])
    manifest["macos_app"] = zip_name
    manifest["distribution_mode"] = "unsigned"
    manifest["vpn_authorization_supported"] = False
    manifest["release_notice"] = (
        "Unsigned macOS app. Packet Tunnel / Network Extension VPN authorization is not supported."
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    sums = []
    for name in sorted(assets + ["RELEASE-MANIFEST.json"]):
        sums.append(f"{sha(dist / name)}  {name}")
    (dist / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")

    print(f"Attached unsigned macOS assets: {zip_name}, BUILD-METADATA.json")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Attach release assets failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
