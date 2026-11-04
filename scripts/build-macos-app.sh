#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="build/ci"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      [[ $# -ge 2 ]] || { echo "--output requires a path" >&2; exit 2; }
      OUTPUT_DIR="$2"
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
[[ "$SWIFT_OPTIMIZATION_LEVEL" == "-O" || "$SWIFT_OPTIMIZATION_LEVEL" == "-Osize" ]] || { echo "CLASH_SWIFT_OPTIMIZATION_LEVEL must be -O or -Osize" >&2; exit 2; }

if [[ "$OUTPUT_DIR" != /* ]]; then OUTPUT_DIR="$ROOT/$OUTPUT_DIR"; fi
mkdir -p "$OUTPUT_DIR"

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/clash-mac-compile.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT
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
  echo "ERROR: fetched Client commit does not match the pinned UPSTREAM_CLIENT_REF" >&2
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

echo "==> Generate Xcode project and build the arm64 CLI helper"
python3 "$CLIENT_DIR/scripts/configure.py" --bundle-base com.cdreaming.clash

echo "==> Build native macOS app (unsigned, arm64 only, limited parallelism)"
xcodebuild \
  -project "$CLIENT_DIR/apple/ClashClient/ClashClient.xcodeproj" \
  -scheme ClashmacOS \
  -configuration Release \
  -destination 'platform=macOS,arch=arm64' \
  -derivedDataPath "$DERIVED_DATA" \
  -jobs "$BUILD_JOBS" \
  -showBuildTimingSummary \
  CODE_SIGNING_ALLOWED=NO \
  ARCHS=arm64 \
  ONLY_ACTIVE_ARCH=YES \
  SWIFT_OPTIMIZATION_LEVEL="$SWIFT_OPTIMIZATION_LEVEL" \
  MARKETING_VERSION="$VERSION" \
  CURRENT_PROJECT_VERSION="$BUILD_NUMBER" \
  CLASH_SOURCE_REVISION="$CLIENT_SHA" \
  build

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

if [[ -z "$APP_EXECUTABLE" ]]; then
  echo "CFBundleExecutable is missing from $APP_PATH/Contents/Info.plist" >&2
  exit 1
fi

APP_BINARY="$APP_PATH/Contents/MacOS/$APP_EXECUTABLE"
if [[ ! -f "$APP_BINARY" ]]; then
  echo "APP executable does not exist: $APP_BINARY" >&2
  echo "Contents/MacOS entries:" >&2
  ls -la "$APP_PATH/Contents/MacOS" >&2 || true
  exit 1
fi

# Query the binary's architecture list using lipo's architecture-list mode,
# then assert this build is arm64-only.
ARCHS_FOUND="$(lipo -archs "$APP_BINARY")"
echo "APP executable architectures: $ARCHS_FOUND"
if [[ "$ARCHS_FOUND" != "arm64" ]]; then
  echo "Expected an arm64-only APP executable, found: $ARCHS_FOUND" >&2
  exit 1
fi

ZIP_NAME="Clash_Mac_Compile-v${VERSION}-macos-arm64.zip"
ZIP_PATH="$OUTPUT_DIR/$ZIP_NAME"
rm -f "$ZIP_PATH"
ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ZIP_PATH"

python3 - "$ROOT" "$CLIENT_DIR" "$CLIENT_SHA" "$VERSION" "$BUILD_NUMBER" "$ZIP_NAME" "$OUTPUT_DIR/BUILD-METADATA.json" "$BUILD_JOBS" "$SWIFT_OPTIMIZATION_LEVEL" <<'PY'
import json, subprocess, sys
from pathlib import Path
root, client, client_sha, version, build_number, artifact, output, build_jobs, swift_optimization = sys.argv[1:]
client = Path(client)
lock = json.loads((client / "Dependencies.lock.json").read_text(encoding="utf-8"))
def cmd(*args):
    return subprocess.check_output(args, text=True).strip()
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
    "signing": "disabled",
    "artifact": artifact,
    "client_repository": "https://github.com/ProjectClash/Clash-Client",
    "client_requested_ref": (Path(root) / "UPSTREAM_CLIENT_REF").read_text().strip(),
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
  shasum -a 256 "$ZIP_NAME" > SHA256SUMS.txt
)

echo "Build complete:"
echo "  APP: $ZIP_PATH"
echo "  Metadata: $OUTPUT_DIR/BUILD-METADATA.json"
echo "  Architecture: arm64"
echo "  Signing: disabled"
