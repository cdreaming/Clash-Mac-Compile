#!/usr/bin/env bash
set -Eeuo pipefail

IDENTITY="${1:-${CLASH_LOCAL_SIGNING_IDENTITY:-Clash_Mac_Compile Local Development}}"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Local macOS code-signing identity checks require macOS Keychain." >&2
  exit 2
fi
command -v security >/dev/null 2>&1 || { echo "security command is unavailable." >&2; exit 2; }

IDENTITIES="$(security find-identity -v -p codesigning 2>&1 || true)"
if ! grep -Fq "\"$IDENTITY\"" <<< "$IDENTITIES"; then
  echo "Local code-signing identity was not found: $IDENTITY" >&2
  echo "Import Clash_Mac_Compile_Local_Dev.p12 into the login Keychain, then run:" >&2
  echo "security find-identity -v -p codesigning" >&2
  echo "$IDENTITIES" >&2
  exit 1
fi

echo "Local code-signing identity found: $IDENTITY"
echo "Scope: local development only; this identity has no Apple Developer Team authorization."
