#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IDENTITY="${CLASH_LOCAL_SIGNING_IDENTITY:-Clash_Mac_Compile Local Development}"
OUTPUT_DIR="build/local-signed"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      [[ $# -ge 2 ]] || { echo "--output requires a path" >&2; exit 2; }
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --signing-identity)
      [[ $# -ge 2 ]] || { echo "--signing-identity requires a name" >&2; exit 2; }
      IDENTITY="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

bash "$ROOT/scripts/check-local-signing-identity.sh" "$IDENTITY"
exec bash "$ROOT/scripts/build-macos-app.sh" \
  --signing-mode local \
  --signing-identity "$IDENTITY" \
  --output "$OUTPUT_DIR"
