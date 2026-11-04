#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description="Attach the macOS app ZIP to the template Release manifest")
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

    zip_name = f"Clash_Mac_Compile-v{args.version}-macos-universal.zip"
    required = [source / zip_name, source / "BUILD-METADATA.json"]
    for item in required:
        if not item.is_file():
            raise RuntimeError(f"Required macOS release asset missing: {item}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("project_version") != args.version:
        raise RuntimeError("Release manifest version does not match requested version")

    for item in required:
        shutil.copy2(item, dist / item.name)

    assets = sorted(
        p.name for p in dist.iterdir()
        if p.is_file() and p.name not in {"SHA256SUMS.txt", "RELEASE-MANIFEST.json"}
    )
    manifest["assets"] = sorted(assets + ["SHA256SUMS.txt", "RELEASE-MANIFEST.json"])
    manifest["macos_app"] = zip_name
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    sums = []
    for name in sorted(assets + ["RELEASE-MANIFEST.json"]):
        sums.append(f"{sha(dist / name)}  {name}")
    (dist / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"Attached macOS assets: {zip_name}, BUILD-METADATA.json")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Attach release assets failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
