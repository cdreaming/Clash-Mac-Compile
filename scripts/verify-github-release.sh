#!/usr/bin/env bash
set -Eeuo pipefail
VERSION="${1:?version required}"
TAG="${2:-}"
: "${GH_TOKEN:?GH_TOKEN required}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY required}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$TAG" ]]; then TAG="$(python3 -c 'import json;print(json.load(open("dist/RELEASE-MANIFEST.json"))["expected_tag"])')"; fi
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
gh release download "$TAG" --repo "$GITHUB_REPOSITORY" --dir "$TMP"
python3 - "$ROOT" "$TMP" <<'PY'
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]); online=Path(sys.argv[2])
m=json.loads((root/"dist/RELEASE-MANIFEST.json").read_text())
if {p.name for p in online.iterdir() if p.is_file()} != set(m["assets"]): raise SystemExit("online asset set mismatch")
for line in (online/"SHA256SUMS.txt").read_text().splitlines():
    h,n=line.split(maxsplit=1); p=online/n.strip()
    if hashlib.sha256(p.read_bytes()).hexdigest()!=h: raise SystemExit(f"checksum mismatch: {n}")
print("Online assets: OK")
PY
