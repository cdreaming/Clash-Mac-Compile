# Clash_Mac_Compile v0.1.0 · macOS System Extension 架构升级版

## 发布摘要

v0.1.0 基于 v0.0.9，将 ProjectClash macOS Packet Tunnel 从 App Extension 构建目标迁移为适用于 macOS 直接分发的 System Extension 架构，并在 VPN 启动前增加系统扩展激活请求。此版本完成源码架构迁移、构建结构检查和报告生成；由于当前用户没有 Apple Developer Program，GitHub 产物仍为 unsigned，不能激活 VPN。

## 本版主要变化

- 新增 `scripts/patch-macos-system-extension.py`，在固定的 ProjectClash Client 源码 checkout 后，将 `ClashmacOSExtension` XcodeGen target 转换为 `system-extension`。
- 将主 APP 与 Packet Tunnel 的 Network Extension entitlement 配置切换为 `packet-tunnel-provider-systemextension`。
- 主 APP 增加 `com.apple.developer.system-extension.install` entitlement 配置。
- 主 APP 链接 `SystemExtensions.framework`，并将 System Extension 嵌入 APP 的 `Contents/Library/SystemExtensions`。
- 新增 `ClashMacSystemExtensionActivator`，使用 `OSSystemExtensionRequest.activationRequest` 和 `OSSystemExtensionManager.shared.submitRequest` 请求激活扩展。
- 在 `VPNStartAuthorization.perform` 中，先完成 System Extension 激活，再继续原有 VPN 配置保存与启动流程。
- 用户需要批准时，调用原有等待状态回调；激活需要重启时返回明确错误。
- 新增 `scripts/audit-vpn-architecture.py`，检查 target 类型、Bundle ID、Entitlements、激活调用链和 APP 实际嵌入目录。
- GitHub Build / Release / Weekly 附加 `VPN-ARCHITECTURE-REPORT.json`。
- 保留 arm64、Swift `-O`、本地自签名开发模式和 GitHub unsigned 发布隔离。

## 两种构建模式

### GitHub Actions

GitHub Build / Release / Weekly 继续使用无签名构建，不需要 Apple Developer Secrets。它会编译并打包 System Extension，并输出架构报告；但由于没有 Apple Developer ID 和 Apple 授权 entitlement / profile，macOS 不会因此接受 VPN System Extension 激活。

### 本地自签名

开发者可使用独立提供的本地 P12 测试 Xcode 代码签名和扩展签名。自签名没有 Apple Team ID，也不能授权 Network Extension 或 System Extension 安装。

## VPN 授权前提

正式启用 GitHub Releases 直接分发 VPN，仍需要：
- Apple Developer Program 会员。
- Apple Developer ID Application 证书。
- Apple 开发者账户中已启用并获准的 Network Extension 能力。
- 与 Team ID、Bundle ID 和扩展类型匹配的 Provisioning Profile / Entitlements。
- 主 APP 和 System Extension 使用同一 Apple Team ID 签名。
- Developer ID 分发所需的 Apple Notarization。

本版不伪造 Apple Team ID、Provisioning Profile 或 entitlement 授权。没有上述授权时，系统扩展可能无法激活，VPN 配置窗口也不会出现。

## 下载资产

| 文件 | 用途 |
|---|---|
| `Clash_Mac_Compile-v0.1.0-macos-arm64-unsigned.zip` | Apple Silicon macOS APP（含 System Extension，未获 Apple 授权） |
| `Clash_Mac_Compile_v0.1.0_source.zip` | 完整构建工程源码 |
| `BUILD-METADATA.json` | 上游 SHA、构建环境、签名和 VPN 架构信息 |
| `VPN-ARCHITECTURE-REPORT.json` | System Extension 结构、嵌入路径、签名和授权状态 |
| `SHA256SUMS.txt` | 下载文件校验 |
| `RELEASE-MANIFEST.json` | Release 资产清单 |

## 安装限制

本版 GitHub APP 是 unsigned 构建，macOS 可能阻止启动。即使 GUI 能启动，System Extension 也不会因为 unsigned 或本地自签名而获得授权。`VPN-ARCHITECTURE-REPORT.json` 会明确记录架构是否正确嵌入，以及 Apple 授权是否已验证。

## 许可证

本项目使用 ProjectClash 上游客户端、Clash Kernel 与 Adapter。分发时请保留版权和许可证声明，并遵守 GPL-3.0 及第三方依赖许可。
