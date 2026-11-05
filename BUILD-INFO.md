# Build Information

- 项目名称：Clash_Mac_Compile
- 项目版本：以根目录 `VERSION` 为准（当前版本 `0.1.2`）
- GitHub 仓库：`cdreaming/Clash-Mac-Compile`
- 上游客户端：`ProjectClash/Clash-Client`
- 上游客户端 Ref：`e3e647283b1593a61dba622f13cd499deeda9b8b`
- Scheme：`ClashmacOS`
- Configuration：`Release`
- Architecture：`arm64`
- Swift optimization：`-O`
- Xcode jobs：`2`

## Build outputs

Default GitHub build command:

```bash
bash scripts/build-macos-app.sh --output build/ci
```

The script resolves the output directory to an absolute path, prints it, verifies all required output files, and writes `BUILD-OUTPUT-MANIFEST.json`.

Required unsigned outputs:

- `Clash_Mac_Compile-vX.Y.Z-macos-arm64-unsigned.zip`
- `BUILD-METADATA.json`
- `VPN-ARCHITECTURE-REPORT.json`
- `SHA256SUMS.txt`
- `BUILD-OUTPUT-MANIFEST.json`

Before Artifact upload or Release attachment:

```bash
python3 scripts/verify-build-outputs.py --directory build/ci --version X.Y.Z --mode unsigned
```

GitHub Build / Release / Weekly explicitly set `CLASH_SIGNING_MODE=unsigned`. Build workflow uploads the single directory `build/ci/` as one Artifact path.

## VPN architecture

- Packet Tunnel target: XcodeGen `system-extension`.
- Provider entitlement: `packet-tunnel-provider-systemextension`.
- Host app entitlement: `com.apple.developer.system-extension.install=true`.
- Provider embeds `ClashMacCore.framework` and uses `@executable_path/../Frameworks`.
- System Extension activation is requested before VPN preferences are saved.
- `VPN-ARCHITECTURE-REPORT.json` records structural and authorization state.

## Linker diagnostics

- `XCODEBUILD.log`
- `LINKER-DIAGNOSTICS.txt`
- `XCODEBUILD-EXIT-CODE.txt`
- `ClashmacOSExtension-BuildSettings.json`
- `ClashClient-project.system-extension.yml`

Build / Release / Weekly upload linker diagnostics with `if: always()`.

## Signing limitation

GitHub builds are unsigned. Local self-signing does not provide Apple Developer ID, Apple-authorized Network Extension entitlement, provisioning profile or notarization. A successful build does not prove VPN authorization.
