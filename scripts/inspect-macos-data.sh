#!/usr/bin/env bash
set -Eeuo pipefail

APP_PATH="${1:-/Applications/Clash.app}"
EXPECTED_GROUP_ID="${CLASH_APP_GROUP_ID:-group.com.cdreaming.clash}"

if [[ ! -d "$APP_PATH" ]]; then
  echo "APP not found: $APP_PATH" >&2
  echo "Usage: $0 /path/to/Clash.app" >&2
  exit 2
fi

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/clash-data-inspect.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT
INFO_PLIST="$APP_PATH/Contents/Info.plist"
ENTITLEMENTS="$TMP_DIR/entitlements.plist"

if [[ ! -f "$INFO_PLIST" ]]; then
  echo "Info.plist not found: $INFO_PLIST" >&2
  exit 1
fi

python3 - "$INFO_PLIST" <<'PY'
import plistlib, sys
from pathlib import Path
p = Path(sys.argv[1])
with p.open("rb") as f:
    data = plistlib.load(f)
print("Bundle ID:", data.get("CFBundleIdentifier", "(missing)"))
print("Executable:", data.get("CFBundleExecutable", "(missing)"))
print("Minimum macOS:", data.get("LSMinimumSystemVersion", "(not declared)"))
PY

# App Group containers are provisioned by macOS for correctly signed apps
# carrying the corresponding application-groups entitlement.
codesign -d --entitlements :- "$APP_PATH" >"$ENTITLEMENTS" 2>/dev/null || true

GROUP_IDS="$(python3 - "$ENTITLEMENTS" <<'PY'
import plistlib, sys
from pathlib import Path
p = Path(sys.argv[1])
try:
    with p.open("rb") as f:
        data = plistlib.load(f)
    groups = data.get("com.apple.security.application-groups", [])
    if isinstance(groups, list):
        for group in groups:
            if isinstance(group, str):
                print(group)
except Exception:
    pass
PY
)"

if [[ -n "$GROUP_IDS" ]]; then
  echo
  echo "Application Groups found in code signature:"
  while IFS= read -r group; do
    [[ -n "$group" ]] || continue
    container="$HOME/Library/Group Containers/$group"
    echo
    echo "Group: $group"
    echo "Container: $container"
    if [[ -d "$container" ]]; then
      echo "Status: exists"
      for rel in "working/active" "working/store/profiles"; do
        if [[ -d "$container/$rel" ]]; then
          echo "  Found: $container/$rel"
        fi
      done
      find "$container" -maxdepth 5 -type f \( -name 'config.yaml' -o -name 'config.resolved.yaml' -o -name 'manifest.json' \) -print 2>/dev/null | head -100
    else
      echo "Status: not created yet"
    fi
  done <<< "$GROUP_IDS"
else
  echo
  echo "No application-groups entitlement was found in this APP signature."
  echo "Expected build-time App Group (verify against the signed app): $EXPECTED_GROUP_ID"
  echo "Expected container path, only after valid signing/provisioning:"
  echo "  $HOME/Library/Group Containers/$EXPECTED_GROUP_ID"
  echo "This build may be unsigned; macOS may not provision the App Group container."
fi

echo
echo "Standard per-user support locations (not proof that Clash stores its active profile there):"
echo "  $HOME/Library/Application Support/"
echo "  $HOME/Library/Caches/"
echo "  $HOME/Library/Logs/"
