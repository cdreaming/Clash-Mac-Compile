# Build Information

- 项目名称：Clash_Mac_Compile
- 项目版本：以根目录 `VERSION` 为准（当前版本 `0.1.3`）
- GitHub 仓库：`cdreaming/Clash-Mac-Compile`
- 上游客户端：`ProjectClash/Clash-Client`
- 上游客户端 Ref：`e3e647283b1593a61dba622f13cd499deeda9b8b`
- Scheme：`ClashmacOS`
- Configuration：`Release`
- Architecture：`arm64`
- Swift optimization：`-O`
- Xcode jobs：`2`

## Build workflow

Build / Release / Weekly execute build and output verification in the same Actions step, using an absolute output path under `GITHUB_WORKSPACE`.

- Build workflow output: `${GITHUB_WORKSPACE}/build/ci`
- Release / Weekly output: `${GITHUB_WORKSPACE}/build/release`

## Persistent status and context

- `BUILD-WORKFLOW-STATUS.txt`: final workflow step status and exit code.
- `BUILD-WORKFLOW-CONTEXT.txt`: GitHub workspace, working directory, output directory and version.
- `BUILD-SCRIPT-STATUS.txt`: build script final status and actual exit code.
- `BUILD-RUN-CONTEXT.txt`: project root, working directory, output directory, runner and signing mode.

Both workflow and build script use EXIT traps so failure evidence remains available.

## Required outputs

- `Clash_Mac_Compile-vX.Y.Z-macos-arm64-unsigned.zip`
- `BUILD-METADATA.json`
- `VPN-ARCHITECTURE-REPORT.json`
- `SHA256SUMS.txt`
- `BUILD-OUTPUT-MANIFEST.json`
- `BUILD-SCRIPT-STATUS.txt`
- `BUILD-RUN-CONTEXT.txt`

Before Release attachment, `verify-build-outputs.py` validates output files, version, signing mode and build script status.

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

Build / Release / Weekly upload linker diagnostics and status/context with `if: always()`.

## Signing limitation

GitHub builds are unsigned. Local self-signing does not provide Apple Developer ID, Apple-authorized Network Extension entitlement, provisioning profile or notarization. A successful build does not prove VPN authorization.
