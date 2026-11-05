# 本地自签名开发模式

## 目标

v0.0.8 引入本地自签名代码签名，用于在开发 Mac 上验证 Xcode 对主 APP 和嵌套代码的签名流程。v0.1.0 将 Packet Tunnel target 迁移为 System Extension，并增加系统激活调用。

本模式使用单独生成的 `Clash_Mac_Compile Local Development` 自签名身份。证书和私钥不包含在源码 ZIP 中，也不提交到 Git 或上传到 GitHub Actions。

## 重要限制

本地自签名证书：

- 不是 Apple Developer ID Application。
- 没有 Apple Developer Team ID。
- 不是 Apple 签发的 Provisioning Profile。
- 不授予 Apple Network Extension entitlement。
- 不授予 System Extension 安装权限。
- 不支持 Apple Notary Service 公证。
- 不能保证 Gatekeeper 允许启动，也不能保证 VPN 配置授权弹窗出现。

它只用于验证本地代码签名命令和 Xcode 签名设置。即使签名报告显示 `signature_verified=true`，也不表示 `apple_entitlements_authorized=true`。

## v0.1.0 System Extension 架构

构建时会对固定的 ProjectClash Client checkout 执行 `scripts/patch-macos-system-extension.py`：

- `ClashmacOSExtension` 从上游的 `app-extension` target 转为 XcodeGen `system-extension`。
- 主 APP 和 provider 使用 `packet-tunnel-provider-systemextension`。
- 主 APP 增加 `com.apple.developer.system-extension.install=true` 并链接 `SystemExtensions.framework`。
- 主 APP 显式 embed provider target。
- `VPNStartAuthorization.perform` 在原有 VPN 配置保存之前调用 `OSSystemExtensionRequest.activationRequest`。
- 用户需要批准时，系统激活请求保持等待；扩展激活成功后才继续保存 VPN 配置。

`audit-vpn-architecture.py` 会检查 target 类型、Bundle ID、App Groups、entitlements、激活调用和 APP 中的 `Contents/Library/SystemExtensions` 目录，并输出 `VPN-ARCHITECTURE-REPORT.json`。

## 安装示例证书

1. 下载单独提供的 `Clash_Mac_Compile_Local_Dev_Certificate_v1.zip`。
2. 解压后双击 `Clash_Mac_Compile_Local_Dev.p12`。
3. 选择 macOS「登录」钥匙串。
4. 输入证书包提供的 P12 密码。
5. 打开「钥匙串访问」，确认身份 `Clash_Mac_Compile Local Development` 已导入。
6. 在终端执行：

```bash
security find-identity -v -p codesigning
```

## 本地构建

在开发 Mac 上进入项目根目录：

```bash
bash scripts/check-local-signing-identity.sh
bash scripts/build-local-signed-app.sh --output build/local-signed
```

默认无签名构建仍然可用：

```bash
bash scripts/build-macos-app.sh --output build/ci
```

本地签名构建输出：

```text
build/local-signed/
  Clash_Mac_Compile-v0.1.0-macos-arm64-local-signed.zip
  BUILD-METADATA.json
  VPN-ARCHITECTURE-REPORT.json
  LOCAL-SIGNING-REPORT.json
  SHA256SUMS.txt
```

该 `local-signed` ZIP 仅用于本机开发测试，不会由 GitHub Release workflow 上传。

## 结果解释

`VPN-ARCHITECTURE-REPORT.json` 区分：
- System Extension target / entitlement 配置是否正确。
- provider 是否嵌入 `Contents/Library/SystemExtensions`。
- APP 和 provider Bundle ID、App Groups 是否匹配。
- APP / provider 实际签名身份与 Team Identifier。
- 是否检测到 Apple Developer ID、授权 entitlement 和 provisioning profile。

架构报告显示结构通过，不代表 Apple 已批准 entitlement。

## GitHub Actions 与 Releases

- Build、Release、Weekly Preview 继续无签名构建，不访问开发者本地钥匙串。
- GitHub Releases 只接受 `distribution_mode=unsigned` 的 APP 资产。
- `VPN-ARCHITECTURE-REPORT.json` 会随 Release 上传，明确结构迁移和 Apple 授权状态。
- `local-development-only` 产物会被 Release 附加脚本拒绝。
- 不要将 `.p12`、`.pfx`、`.key`、`.pem`、`.mobileprovision` 或 `.provisionprofile` 放入项目目录。源码打包会拒绝这些敏感文件。

## 正式 VPN 授权

没有 Apple Developer Program 时，GitHub unsigned 和本地 self-signed 构建都不能激活 System Extension。正式直接分发需要 Apple Developer ID、Apple 授权的 Network Extension entitlement / provisioning profile，以及公证流程。

P12 文件包含私钥。只用于个人开发 Mac；不要发给他人、不要提交到 Sourcetree、不要放进 GitHub Secrets。
