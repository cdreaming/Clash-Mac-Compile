# Build Information

- 项目名称：Clash_Mac_Compile
- 项目版本：以根目录 `VERSION` 为准（当前版本 `0.1.0`）
- 治理模板版本：`1.1.1`
- GitHub 仓库：`cdreaming/Clash-Mac-Compile`
- 目标平台：macOS
- 上游客户端：`ProjectClash/Clash-Client`
- 上游客户端 Ref：`e3e647283b1593a61dba622f13cd499deeda9b8b`
- Xcode Scheme：`ClashmacOS`
- 构建配置：Release
- Swift 优化级别：`-O`
- Xcode 并行编译任务：最多 2
- 目标架构：`arm64`

## macOS VPN 架构

- Packet Tunnel target：XcodeGen `system-extension`。
- Extension bundle ID：`$(CLASH_BUNDLE_BASE).packet-tunnel`。
- Network Extension entitlement：`packet-tunnel-provider-systemextension`。
- Host app entitlement：`com.apple.developer.system-extension.install=true`。
- Host app links `SystemExtensions.framework`。
- System Extension embedded under `Contents/Library/SystemExtensions`。
- VPN start flow requests `OSSystemExtensionRequest` activation before saving the VPN configuration.
- Build output includes `VPN-ARCHITECTURE-REPORT.json` for structure / signature / entitlement audit.

## 签名与授权边界

- GitHub Build / Release / Weekly：unsigned，不需要 Apple Developer Secrets。
- 本地开发：可选 self-signed Code Signing identity，只用于代码签名流程测试。
- 自签名不提供 Apple Team ID、Apple 授权 Network Extension entitlement、Provisioning Profile 或 Notarization。
- 当前无 Apple Developer 授权时，`vpn_authorization_supported=false`；System Extension 架构迁移不等于 VPN 激活成功。

## 构建入口

- GitHub unsigned：`scripts/build-macos-app.sh --output build/ci`
- 本地 self-signed：`scripts/build-local-signed-app.sh --output build/local-signed`
- 上游架构补丁：`scripts/patch-macos-system-extension.py`
- VPN 架构审计：`scripts/audit-vpn-architecture.py`

## 产物

- `Clash_Mac_Compile-vX.Y.Z-macos-arm64-unsigned.zip`
- `Clash_Mac_Compile-vX.Y.Z-macos-arm64-local-signed.zip`（仅本机）
- `Clash_Mac_Compile_vX.Y.Z_source.zip`
- `BUILD-METADATA.json`
- `VPN-ARCHITECTURE-REPORT.json`
- `SHA256SUMS.txt`

## 安全

P12、PFX、私钥和 Provisioning Profile 不得提交到仓库或源码 ZIP。GitHub Releases 不上传本地自签名产物。
