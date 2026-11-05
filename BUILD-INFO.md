# Build Information

- 项目名称：Clash_Mac_Compile
- 项目版本：以根目录 `VERSION` 为准（当前版本 `0.1.5`）
- GitHub 仓库：`cdreaming/Clash-Mac-Compile`
- 上游客户端：`ProjectClash/Clash-Client`
- 上游客户端 Ref：`e3e647283b1593a61dba622f13cd499deeda9b8b`
- Scheme：`ClashmacOS`
- Configuration：`Release`
- Architecture：`arm64`
- Swift optimization：`-O`
- Xcode jobs：`2`

## Build script

- `SYSTEM_EXTENSION_PROJECT_SPEC` is declared and used consistently for the patched XcodeGen project spec.
- The build script checks that the System Extension project spec output path is set before copying.
- `BUILD-SCRIPT-STATUS.txt` is written as one `key=value` pair per line with `printf '%s\n'`.
- `trap 'cleanup_build "$?"' EXIT` passes the original build exit code to the cleanup handler.

## Build workflow

Build / Release / Weekly execute build and output verification in one Actions step, using an absolute output path under `GITHUB_WORKSPACE`.

- Build output: `${GITHUB_WORKSPACE}/build/ci`
- Release / Weekly output: `${GITHUB_WORKSPACE}/build/release`
- Workflow status: `BUILD-WORKFLOW-STATUS.txt`
- Workflow context: `BUILD-WORKFLOW-CONTEXT.txt`
- Script status: `BUILD-SCRIPT-STATUS.txt`
- Script context: `BUILD-RUN-CONTEXT.txt`

## Required outputs

- `Clash_Mac_Compile-vX.Y.Z-macos-arm64-unsigned.zip`
- `BUILD-METADATA.json`
- `VPN-ARCHITECTURE-REPORT.json`
- `SHA256SUMS.txt`
- `BUILD-OUTPUT-MANIFEST.json`
- `BUILD-SCRIPT-STATUS.txt`
- `BUILD-RUN-CONTEXT.txt`

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

## Signing limitation

GitHub builds are unsigned. Local self-signing does not provide Apple Developer ID, Apple-authorized Network Extension entitlement, provisioning profile or notarization. A successful build does not prove VPN authorization.
