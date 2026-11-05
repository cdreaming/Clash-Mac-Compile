# Clash_Mac_Compile v0.1.0 Release Experience Report

## 故障证据

用户在 macOS 15.7.7 上检查安装包，主 APP 与 `ClashmacOSExtension.appex` 均为 Ad-hoc 签名，`TeamIdentifier=not set`；`systemextensionsctl list` 未发现 Clash System Extension。当前包因此不能完成 GitHub 直接分发所需的 VPN System Extension 激活。

## 根因

固定的 ProjectClash Client macOS target 将 Packet Tunnel 声明为 `app-extension`，并使用 `packet-tunnel-provider`。Apple TN3134 指出 macOS Packet Tunnel App Extension 仅限 App Store 分发；直接分发需要 System Extension，并使用 Developer ID 和对应 Network Extension entitlement。

## 修复

- 将官方 macOS extension target 转换为 `system-extension`。
- 使用 `packet-tunnel-provider-systemextension` entitlement。
- 主 APP 增加 `com.apple.developer.system-extension.install`。
- 主 APP 链接 SystemExtensions.framework。
- 在 `VPNStartAuthorization.perform` 中先激活系统扩展，再继续原有 VPN 配置保存流程。
- 增加用户批准等待、失败和重启结果处理。
- 增加构建后结构审计与 Release 报告。

## 仍需外部授权

用户尚未加入 Apple Developer Program，因此 GitHub Build / Release 继续 unsigned，本地 P12 仅为自签名。Apple 系统不会因自签名而授予 Network Extension / System Extension 权限。正式 VPN 测试必须在 Apple Developer ID、entitlement 和 profile 配置完成后进行。

## 防回归

- Build 必须验证 XcodeGen target 类型为 system-extension。
- Build 必须验证主 APP / provider entitlement 配置。
- APP 必须将 provider 嵌入 `Contents/Library/SystemExtensions`。
- VPN preference 保存前必须调用 System Extension activation。
- Release 必须上传 VPN architecture report，并明确授权状态。
