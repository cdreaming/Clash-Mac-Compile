#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="build/ci"
SIGNING_MODE="${CLASH_SIGNING_MODE:-unsigned}"
SIGNING_IDENTITY="${CLASH_LOCAL_SIGNING_IDENTITY:-Clash_Mac_Compile Local Development}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      [[ $# -ge 2 ]] || { echo "--output requires a path" >&2; exit 2; }
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --signing-mode)
      [[ $# -ge 2 ]] || { echo "--signing-mode requires unsigned or local" >&2; exit 2; }
      SIGNING_MODE="$2"
      shift 2
      ;;
    --signing-identity)
      [[ $# -ge 2 ]] || { echo "--signing-identity requires a name" >&2; exit 2; }
      SIGNING_IDENTITY="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This build requires macOS with the full Xcode installation." >&2
  exit 2
fi

VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION")"
CLIENT_REF="$(tr -d '[:space:]' < "$ROOT/UPSTREAM_CLIENT_REF")"
BUILD_NUMBER="${GITHUB_RUN_NUMBER:-1}"
BUILD_JOBS="${CLASH_BUILD_JOBS:-2}"
SWIFT_OPTIMIZATION_LEVEL="${CLASH_SWIFT_OPTIMIZATION_LEVEL:--O}"

[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Invalid VERSION: $VERSION" >&2; exit 2; }
[[ "$CLIENT_REF" =~ ^[A-Za-z0-9._/-]+$ && "$CLIENT_REF" != -* ]] || {
  echo "Invalid UPSTREAM_CLIENT_REF: $CLIENT_REF" >&2
  exit 2
}
[[ "$BUILD_NUMBER" =~ ^[0-9]+$ ]] || { echo "Invalid build number" >&2; exit 2; }
[[ "$BUILD_JOBS" =~ ^[1-4]$ ]] || { echo "CLASH_BUILD_JOBS must be between 1 and 4" >&2; exit 2; }
[[ "$SWIFT_OPTIMIZATION_LEVEL" == "-O" || "$SWIFT_OPTIMIZATION_LEVEL" == "-Osize" ]] || {
  echo "CLASH_SWIFT_OPTIMIZATION_LEVEL must be -O or -Osize" >&2
  exit 2
}
[[ "$SIGNING_MODE" == "unsigned" || "$SIGNING_MODE" == "local" ]] || {
  echo "Signing mode must be unsigned or local." >&2
  exit 2
}
if [[ "$SIGNING_MODE" == "local" ]]; then
  bash "$ROOT/scripts/check-local-signing-identity.sh" "$SIGNING_IDENTITY"
fi

if [[ "$OUTPUT_DIR" != /* ]]; then OUTPUT_DIR="$ROOT/$OUTPUT_DIR"; fi
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd -P)"
echo "Build output directory: $OUTPUT_DIR"

BUILD_SCRIPT_STATUS="$OUTPUT_DIR/BUILD-SCRIPT-STATUS.txt"
BUILD_RUN_CONTEXT="$OUTPUT_DIR/BUILD-RUN-CONTEXT.txt"
cat > "$BUILD_RUN_CONTEXT" <<EOF
project=Clash_Mac_Compile
version=$VERSION
root=$ROOT
working_directory=$PWD
output_directory=$OUTPUT_DIR
signing_mode=$SIGNING_MODE
build_number=$BUILD_NUMBER
runner_os=$(uname -s)
runner_arch=$(uname -m)
github_run_id=${GITHUB_RUN_ID:-local}
github_run_number=${GITHUB_RUN_NUMBER:-local}
EOF
printf '%s\n' "status=running" "version=$VERSION" "output_directory=$OUTPUT_DIR" > "$BUILD_SCRIPT_STATUS"

WORK_DIR=""
cleanup_build() {
  local build_exit_code="${1:-0}"
  local build_status="failed"
  trap - EXIT
  if [[ "$build_exit_code" -eq 0 ]]; then
    build_status="success"
  fi
  printf '%s\n' "status=$build_status" "exit_code=$build_exit_code" "version=$VERSION" "output_directory=$OUTPUT_DIR" > "$BUILD_SCRIPT_STATUS"
  if [[ -n "$WORK_DIR" && -d "$WORK_DIR" ]]; then
    rm -rf "$WORK_DIR" || true
  fi
  exit "$build_exit_code"
}
trap 'cleanup_build "$?"' EXIT

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/clash-mac-compile.XXXXXX")"
CLIENT_DIR="$WORK_DIR/Clash-Client"
DERIVED_DATA="$WORK_DIR/DerivedData"

if ! command -v xcodegen >/dev/null 2>&1; then
  brew install xcodegen
fi

export GOTOOLCHAIN=auto
export DEVELOPER_DIR="${DEVELOPER_DIR:-$(xcode-select -p)}"

echo "==> Host diagnostics"
uname -a
echo "CPU cores: $(sysctl -n hw.ncpu)"
echo "Memory bytes: $(sysctl -n hw.memsize)"
echo "Build jobs: $BUILD_JOBS"
echo "Swift optimization: $SWIFT_OPTIMIZATION_LEVEL"
echo "Performance profile: runtime-speed-priority"
echo "Target architecture: arm64 only"
if [[ "$SIGNING_MODE" == "local" ]]; then
  echo "Signing: local self-signed identity ($SIGNING_IDENTITY)"
  echo "Distribution: local development only; Apple VPN authorization is not granted"
else
  echo "Signing: disabled"
  echo "Distribution: unsigned macOS app; VPN authorization is not supported by this build"
fi

echo "==> Xcode"
xcodebuild -version
echo "==> Go"
go version
echo "==> Python"
python3 --version
echo "==> Checkout ProjectClash/Clash-Client: $CLIENT_REF"

git init -q "$CLIENT_DIR"
git -C "$CLIENT_DIR" remote add origin https://github.com/ProjectClash/Clash-Client.git
git -C "$CLIENT_DIR" fetch --depth 1 origin "$CLIENT_REF"
git -C "$CLIENT_DIR" checkout --detach FETCH_HEAD
CLIENT_SHA="$(git -C "$CLIENT_DIR" rev-parse HEAD)"
[[ "$CLIENT_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "Unable to resolve upstream Client SHA" >&2; exit 1; }

if [[ "$CLIENT_SHA" != "$CLIENT_REF" ]]; then
  echo "ERROR: fetched Client commit does not match pinned UPSTREAM_CLIENT_REF" >&2
  echo "Expected: $CLIENT_REF" >&2
  echo "Actual:   $CLIENT_SHA" >&2
  exit 1
fi

echo "==> Prepare pinned Clash Kernel and Adapter SDK"
python3 -m venv "$CLIENT_DIR/.build/python-env"
# shellcheck disable=SC1091
source "$CLIENT_DIR/.build/python-env/bin/activate"
python3 -m pip install --disable-pip-version-check PyYAML
python3 "$CLIENT_DIR/scripts/bootstrap.py"

echo "==> Generate Xcode project and build arm64 CLI helper"
python3 "$CLIENT_DIR/scripts/configure.py" \
  --bundle-base com.cdreaming.clash \
  --team ""

echo "==> Migrate macOS Packet Tunnel to direct-distribution System Extension architecture"
python3 "$ROOT/scripts/patch-macos-system-extension.py" --client-dir "$CLIENT_DIR"
(
  cd "$CLIENT_DIR/apple/ClashClient"
  xcodegen generate
)

echo "==> Build native macOS app (arm64, $SIGNING_MODE, runtime-speed priority)"
XCODEBUILD_ARGS=(
  -project "$CLIENT_DIR/apple/ClashClient/ClashClient.xcodeproj"
  -scheme ClashmacOS
  -configuration Release
  -destination 'platform=macOS,arch=arm64'
  -derivedDataPath "$DERIVED_DATA"
  -jobs "$BUILD_JOBS"
  -showBuildTimingSummary
  ARCHS=arm64
  ONLY_ACTIVE_ARCH=YES
  SWIFT_OPTIMIZATION_LEVEL="$SWIFT_OPTIMIZATION_LEVEL"
  MARKETING_VERSION="$VERSION"
  CURRENT_PROJECT_VERSION="$BUILD_NUMBER"
  CLASH_SOURCE_REVISION="$CLIENT_SHA"
)

if [[ "$SIGNING_MODE" == "local" ]]; then
  XCODEBUILD_ARGS+=(
    CODE_SIGNING_ALLOWED=YES
    CODE_SIGNING_REQUIRED=YES
    CODE_SIGN_IDENTITY="$SIGNING_IDENTITY"
    CODE_SIGN_STYLE=Manual
    DEVELOPMENT_TEAM=
    CODE_SIGN_INJECT_BASE_ENTITLEMENTS=NO
  )
else
  XCODEBUILD_ARGS+=(CODE_SIGNING_ALLOWED=NO)
fi

XCODEBUILD_LOG="$OUTPUT_DIR/XCODEBUILD.log"
LINKER_DIAGNOSTICS="$OUTPUT_DIR/LINKER-DIAGNOSTICS.txt"
SYSTEM_EXTENSION_PROJECT_SPEC="$OUTPUT_DIR/ClashClient-project.system-extension.yml"
: "${SYSTEM_EXTENSION_PROJECT_SPEC:?System Extension project spec output path is not set}"
cp "$CLIENT_DIR/apple/ClashClient/project.yml" "$SYSTEM_EXTENSION_PROJECT_SPEC"

echo "==> Build with verbose linker diagnostics"
set +e
xcodebuild -verbose "${XCODEBUILD_ARGS[@]}" build 2>&1 | tee "$XCODEBUILD_LOG"
XCODEBUILD_STATUS=${PIPESTATUS[0]}
set -e

python3 "$ROOT/scripts/summarize-xcode-linker-errors.py" \
  --log "$XCODEBUILD_LOG" \
  --output "$LINKER_DIAGNOSTICS" || true

if [[ "$XCODEBUILD_STATUS" -ne 0 ]]; then
  echo "==> Xcode build failed; collecting System Extension build settings"
  xcodebuild \
    -project "$CLIENT_DIR/apple/ClashClient/ClashClient.xcodeproj" \
    -target ClashmacOSExtension \
    -configuration Release \
    -showBuildSettings -json \
    > "$OUTPUT_DIR/ClashmacOSExtension-BuildSettings.json" \
    2> "$OUTPUT_DIR/ClashmacOSExtension-BuildSettings.stderr.log" || true
  echo "$XCODEBUILD_STATUS" > "$OUTPUT_DIR/XCODEBUILD-EXIT-CODE.txt"
  echo "Xcode build failed with exit code $XCODEBUILD_STATUS" >&2
  echo "Full log: $XCODEBUILD_LOG" >&2
  echo "Linker summary: $LINKER_DIAGNOSTICS" >&2
  exit "$XCODEBUILD_STATUS"
fi

echo "Xcode build succeeded; full linker log retained at $XCODEBUILD_LOG"

PRODUCT_DIR="$DERIVED_DATA/Build/Products/Release"
APP_PATH="$PRODUCT_DIR/Clash.app"
if [[ ! -d "$APP_PATH" ]]; then
  APP_PATH="$(find "$PRODUCT_DIR" -maxdepth 2 -type d -name 'Clash.app' -print -quit)"
fi
[[ -n "$APP_PATH" && -d "$APP_PATH" ]] || {
  echo "Clash.app was not found under $PRODUCT_DIR" >&2
  find "$PRODUCT_DIR" -maxdepth 3 -print >&2 || true
  exit 1
}

APP_EXECUTABLE="$(python3 - "$APP_PATH/Contents/Info.plist" <<'PY'
import plistlib, sys
with open(sys.argv[1], "rb") as f:
    value = plistlib.load(f).get("CFBundleExecutable", "")
    if not isinstance(value, str):
        value = ""
    print(value)
PY
)"
[[ -n "$APP_EXECUTABLE" ]] || {
  echo "CFBundleExecutable is missing from $APP_PATH/Contents/Info.plist" >&2
  exit 1
}

APP_BINARY="$APP_PATH/Contents/MacOS/$APP_EXECUTABLE"
[[ -f "$APP_BINARY" ]] || {
  echo "APP executable does not exist: $APP_BINARY" >&2
  ls -la "$APP_PATH/Contents/MacOS" >&2 || true
  exit 1
}

ARCHS_FOUND="$(lipo -archs "$APP_BINARY")"
echo "APP executable architectures: $ARCHS_FOUND"
[[ "$ARCHS_FOUND" == "arm64" ]] || {
  echo "Expected an arm64-only APP executable, found: $ARCHS_FOUND" >&2
  exit 1
}

xcodebuild \
  -project "$CLIENT_DIR/apple/ClashClient/ClashClient.xcodeproj" \
  -target ClashmacOSExtension \
  -configuration Release \
  -showBuildSettings -json \
  > "$OUTPUT_DIR/ClashmacOSExtension-BuildSettings.json" \
  2> "$OUTPUT_DIR/ClashmacOSExtension-BuildSettings.stderr.log" || true

echo "==> Audit System Extension packaging and VPN activation flow"
python3 "$ROOT/scripts/audit-vpn-architecture.py" \
  --client-dir "$CLIENT_DIR" \
  --app "$APP_PATH" \
  --output "$OUTPUT_DIR/VPN-ARCHITECTURE-REPORT.json"

if [[ "$SIGNING_MODE" == "local" ]]; then
  ZIP_NAME="Clash_Mac_Compile-v${VERSION}-macos-arm64-local-signed.zip"
  rm -f "$OUTPUT_DIR/Clash_Mac_Compile-v${VERSION}-macos-arm64-unsigned.zip"
  bash "$ROOT/scripts/verify-local-signed-app.sh" \
    "$APP_PATH" "$SIGNING_IDENTITY" "$OUTPUT_DIR/LOCAL-SIGNING-REPORT.json"
else
  ZIP_NAME="Clash_Mac_Compile-v${VERSION}-macos-arm64-unsigned.zip"
  rm -f "$OUTPUT_DIR/Clash_Mac_Compile-v${VERSION}-macos-arm64-local-signed.zip"
  rm -f "$OUTPUT_DIR/LOCAL-SIGNING-REPORT.json"
fi
ZIP_PATH="$OUTPUT_DIR/$ZIP_NAME"
rm -f "$ZIP_PATH"
ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ZIP_PATH"

python3 - "$ROOT" "$CLIENT_DIR" "$CLIENT_SHA" "$VERSION" "$BUILD_NUMBER" "$ZIP_NAME" \
  "$OUTPUT_DIR/BUILD-METADATA.json" "$BUILD_JOBS" "$SWIFT_OPTIMIZATION_LEVEL" \
  "$SIGNING_MODE" "$SIGNING_IDENTITY" "$OUTPUT_DIR/VPN-ARCHITECTURE-REPORT.json" <<'PY'
import json, subprocess, sys
from pathlib import Path

root, client, client_sha, version, build_number, artifact, output, build_jobs, swift_optimization, signing_mode, signing_identity, vpn_report_path = sys.argv[1:]
root = Path(root)
client = Path(client)
lock = json.loads((client / "Dependencies.lock.json").read_text(encoding="utf-8"))
vpn_report = json.loads(Path(vpn_report_path).read_text(encoding="utf-8"))

def cmd(*args):
    return subprocess.check_output(args, text=True).strip()

local = signing_mode == "local"
metadata = {
    "project": "Clash_Mac_Compile",
    "project_version": version,
    "build_number": build_number,
    "platform": "macOS",
    "scheme": "ClashmacOS",
    "configuration": "Release",
    "architectures": ["arm64"],
    "build_jobs": int(build_jobs),
    "swift_optimization_level": swift_optimization,
    "performance_profile": "runtime-speed-priority",
    "signing": "local-self-signed" if local else "disabled",
    "signing_identity": signing_identity if local else None,
    "local_signing_report": "LOCAL-SIGNING-REPORT.json" if local else None,
    "team_id": None,
    "apple_developer_identity": False,
    "apple_entitlements_authorized": False,
    "notarized": False,
    "distribution_mode": "local-development-only" if local else "unsigned",
    "vpn_architecture": "macos-system-extension",
    "vpn_activation_flow": "OSSystemExtensionRequest-before-NETunnelProviderManager-save",
    "system_extension_packaged": bool(vpn_report.get("system_extension_packaged")),
    "vpn_architecture_report": "VPN-ARCHITECTURE-REPORT.json",
    "vpn_authorization_supported": bool(vpn_report.get("vpn_authorization_supported", False)) and not local,
    "limitations": [
        "Local self-signed identity verifies local code-signing mechanics only; it is not an Apple Developer ID.",
        "A local self-signed identity does not authorize Network Extension, Packet Tunnel or System Extension installation.",
        "Apple notarization and Gatekeeper developer identity checks are not provided."
    ] if local else [
        "Unsigned build; macOS may require manual user approval to open.",
        "Packet Tunnel / Network Extension VPN authorization is not supported without Apple Developer signing and provisioning."
    ],
    "artifact": artifact,
    "client_repository": "https://github.com/ProjectClash/Clash-Client",
    "client_requested_ref": (root / "UPSTREAM_CLIENT_REF").read_text().strip(),
    "client_commit": client_sha,
    "kernel_repository": lock["kernel"]["repository"],
    "kernel_commit": lock["kernel"]["revision"],
    "adapter_repository": lock["adapter"]["repository"],
    "adapter_commit": lock["adapter"]["revision"],
    "gomobile": lock["gomobile"],
    "gobind": lock["gobind"],
    "xcode_version": cmd("xcodebuild", "-version").replace("\n", " / "),
    "go_version": cmd("go", "version"),
    "build_date_utc": cmd("date", "-u", "+%Y-%m-%dT%H:%M:%SZ")
}
Path(output).write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

(
  cd "$OUTPUT_DIR"
  ASSETS=("$ZIP_NAME" "BUILD-METADATA.json" "VPN-ARCHITECTURE-REPORT.json" \
          "BUILD-RUN-CONTEXT.txt" \
          "XCODEBUILD.log" "LINKER-DIAGNOSTICS.txt" \
          "ClashClient-project.system-extension.yml" "ClashmacOSExtension-BuildSettings.json")
  if [[ -f "LOCAL-SIGNING-REPORT.json" ]]; then
    ASSETS+=("LOCAL-SIGNING-REPORT.json")
  fi
  shasum -a 256 "${ASSETS[@]}" > SHA256SUMS.txt
)

python3 - "$OUTPUT_DIR" "$VERSION" "$ZIP_NAME" "$SIGNING_MODE" <<'PY'
import json, sys
from pathlib import Path
output = Path(sys.argv[1])
version, app_zip, signing_mode = sys.argv[2:]
required = [
    app_zip,
    "BUILD-METADATA.json",
    "VPN-ARCHITECTURE-REPORT.json",
    "SHA256SUMS.txt",
    "BUILD-SCRIPT-STATUS.txt",
    "BUILD-RUN-CONTEXT.txt",
]
missing = [name for name in required if not (output / name).is_file() or (output / name).stat().st_size == 0]
if missing:
    raise SystemExit("Build output validation failed; missing or empty files: " + ", ".join(missing))
manifest = {
    "project": "Clash_Mac_Compile",
    "project_version": version,
    "output_directory": str(output),
    "distribution_mode": "local-development-only" if signing_mode == "local" else "unsigned",
    "app_artifact": app_zip,
    "required_files": required,
    "files": sorted(p.name for p in output.iterdir() if p.is_file()),
}
(output / "BUILD-OUTPUT-MANIFEST.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print("Build output manifest:", output / "BUILD-OUTPUT-MANIFEST.json")
for name in required:
    print(f"Verified output: {output / name} ({(output / name).stat().st_size} bytes)")
PY

echo "Build complete:"
echo "  APP: $ZIP_PATH"
echo "  Output manifest: $OUTPUT_DIR/BUILD-OUTPUT-MANIFEST.json"
echo "  Metadata: $OUTPUT_DIR/BUILD-METADATA.json"
echo "  VPN architecture report: $OUTPUT_DIR/VPN-ARCHITECTURE-REPORT.json"
echo "  Xcode build log: $OUTPUT_DIR/XCODEBUILD.log"
echo "  Linker diagnostics: $OUTPUT_DIR/LINKER-DIAGNOSTICS.txt"
echo "  Architecture: arm64"
if [[ "$SIGNING_MODE" == "local" ]]; then
  echo "  Signing: local self-signed ($SIGNING_IDENTITY)"
  echo "  Signature verification: passed"
  echo "  VPN authorization: not granted by local certificate"
  echo "  Local report: $OUTPUT_DIR/LOCAL-SIGNING-REPORT.json"
else
  echo "  Signing: disabled"
  echo "  VPN authorization: unsupported in unsigned build"
fi
