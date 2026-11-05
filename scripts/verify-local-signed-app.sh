#!/usr/bin/env bash
set -Eeuo pipefail

APP_PATH="${1:?Usage: verify-local-signed-app.sh /path/to/Clash.app 'identity name' [report.json]}"
IDENTITY="${2:?Signing identity name required}"
REPORT_PATH="${3:-}"

[[ -d "$APP_PATH" ]] || { echo "APP not found: $APP_PATH" >&2; exit 1; }
command -v codesign >/dev/null 2>&1 || { echo "codesign is unavailable." >&2; exit 2; }

verify_one() {
  local bundle="$1"
  local detail="$2"

  codesign --verify --strict --verbose=2 "$bundle"
  codesign -dv --verbose=4 "$bundle" 2>"$detail"
  if ! grep -Fq "Authority=$IDENTITY" "$detail"; then
    echo "Bundle is not signed by the requested local identity: $bundle" >&2
    cat "$detail" >&2
    return 1
  fi
}

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/clash-local-signature.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT
APP_DETAIL="$TMP_DIR/app-details.txt"
verify_one "$APP_PATH" "$APP_DETAIL"

EXTENSION_PATHS=()
while IFS= read -r -d '' path; do
  EXTENSION_PATHS+=("$path")
done < <(find "$APP_PATH/Contents" -type d \( -name '*.appex' -o -name '*.systemextension' \) -prune -print0)

if [[ "${#EXTENSION_PATHS[@]}" -eq 0 ]]; then
  echo "No embedded app/system extension bundle was found; local VPN extension signing cannot be verified." >&2
  exit 1
fi

for index in "${!EXTENSION_PATHS[@]}"; do
  verify_one "${EXTENSION_PATHS[$index]}" "$TMP_DIR/extension-$index-details.txt"
done

if [[ -n "$REPORT_PATH" ]]; then
  python3 - "$APP_PATH" "$IDENTITY" "$APP_DETAIL" "$REPORT_PATH" "${EXTENSION_PATHS[@]}" <<'PY'
import json, plistlib, subprocess, sys
from pathlib import Path

app, identity, detail_path, report_path, *extensions = sys.argv[1:]
detail = Path(detail_path).read_text(encoding="utf-8", errors="replace")
team = None
for line in detail.splitlines():
    if line.startswith("TeamIdentifier="):
        team = line.split("=", 1)[1].strip()
        break

def entitlement_text(bundle):
    result = subprocess.run(
        ["codesign", "-d", "--entitlements", ":-", bundle],
        text=True, capture_output=True
    )
    return (result.stdout or "") + "\n" + (result.stderr or "")

app_entitlements = entitlement_text(app)
extension_records = []
for extension in extensions:
    details = subprocess.run(
        ["codesign", "-dv", "--verbose=4", extension],
        text=True, capture_output=True
    )
    entitlements = entitlement_text(extension)
    extension_records.append({
        "path": extension,
        "signature_verified": True,
        "authority_matches_local_identity": identity in details.stderr,
        "packet_tunnel_entitlement_embedded": "packet-tunnel-provider" in entitlements,
        "app_group_entitlement_embedded": "com.apple.security.application-groups" in entitlements,
    })

record = {
    "signing_mode": "local-self-signed",
    "signing_identity": identity,
    "team_identifier": team,
    "app_signature_verified": True,
    "app_group_entitlement_embedded": "com.apple.security.application-groups" in app_entitlements,
    "packet_tunnel_entitlement_embedded": "packet-tunnel-provider" in app_entitlements,
    "extensions": extension_records,
    "apple_developer_identity": False,
    "apple_entitlements_authorized": False,
    "network_extension_vpn_authorization_supported": False,
    "notarized": False,
    "warning": "A local self-signed identity verifies local code-signing mechanics only. It does not grant Apple Network Extension or System Extension authorization."
}
Path(report_path).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
fi

echo "Local signature verification: PASS"
echo "Apple Developer authorization / VPN authorization: NOT GRANTED by this local certificate"
