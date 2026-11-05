# Build Information

- 项目名称：Clash_Mac_Compile
- 项目版本：以根目录 `VERSION` 为准（当前版本 `0.1.4`）
- GitHub 仓库：`cdreaming/Clash-Mac-Compile`
- 上游客户端：`ProjectClash/Clash-Client`
- 上游客户端 Ref：`e3e647283b1593a61dba622f13cd499deeda9b8b`
- Scheme：`ClashmacOS`
- Configuration：`Release`
- Architecture：`arm64`
- Swift optimization：`-O`
- Xcode jobs：`2`

## Build workflow

Build / Release / Weekly execute macOS build and output verification in one Actions step, using an absolute output path under `GITHUB_WORKSPACE`.

- Build output: `${GITHUB_WORKSPACE}/build/ci`
- Release / Weekly output: `${GITHUB_WORKSPACE}/build/release`
- State files: `BUILD-WORKFLOW-STATUS.txt`, `BUILD-WORKFLOW-CONTEXT.txt`, `BUILD-SCRIPT-STATUS.txt`, `BUILD-RUN-CONTEXT.txt`.

Workflow state writes use `printf '%s\n'` without line continuations. `check-build-config.py` parses the actual YAML run blocks and executes `bash -n`; `tests/test_workflow_shell.py` simulates successful and failed build steps.

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

Build / Release / Weekly upload linker diagnostics and workflow/script status/context with `if: always()`.

## Signing limitation

GitHub builds are unsigned. Local self-signing does not provide Apple Developer ID, Apple-authorized Network Extension entitlement, provisioning profile or notarization. A successful build does not prove VPN authorization.
