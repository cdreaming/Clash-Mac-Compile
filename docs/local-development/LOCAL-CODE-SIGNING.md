# 本地自签名开发模式

## 目标

v0.0.8 增加可选的本地自签名代码签名，用于在开发 Mac 上验证 Xcode 对主 APP、嵌套 App Extensions 的签名流程。

本模式使用独立生成的 `Clash_Mac_Compile Local Development` 自签名身份。证书和私钥不包含在源码 ZIP 中，也不应提交到 Git 或上传到 GitHub Actions。

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

## 上游扩展类型

当前锁定的 ProjectClash Client 工程在 `apple/ClashClient/project.yml` 中将 `ClashmacOSExtension` 声明为 `app-extension`，并声明 `packet-tunnel-provider` entitlement。该项目不是一个已转换为 macOS System Extension 的工程。

本版本不会擅自将上游 App Extension 改写成 System Extension，也不会把自签名身份冒充成 System Extension 的 Apple 授权。若未来要实现 GitHub Releases 分发且真正激活 Packet Tunnel，必须先根据 Apple 支持的 macOS 分发方式调整上游架构，并取得 Apple 授权的能力和签名材料。

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

若身份没有出现，检查 P12 是否成功导入登录钥匙串，以及证书是否被 macOS 识别为 Code Signing identity。

## 本地构建

在开发 Mac 上进入项目根目录：

```bash
bash scripts/check-local-signing-identity.sh
bash scripts/build-local-signed-app.sh --output build/local-signed
```

如证书名称不同：

```bash
bash scripts/build-local-signed-app.sh \
  --signing-identity "Clash_Mac_Compile Local Development" \
  --output build/local-signed
```

默认无签名构建仍然可用：

```bash
bash scripts/build-macos-app.sh --output build/ci
```

本地签名构建输出：

```text
build/local-signed/
  Clash_Mac_Compile-v0.0.8-macos-arm64-local-signed.zip
  BUILD-METADATA.json
  LOCAL-SIGNING-REPORT.json
  SHA256SUMS.txt
```

该 `local-signed` ZIP 仅用于本机开发测试，不会由 GitHub Release workflow 上传。

## 检查结果

`LOCAL-SIGNING-REPORT.json` 记录：

- 本地签名身份名称。
- 主 APP 与嵌套扩展签名是否验证通过。
- 签名中是否嵌入 App Group / Packet Tunnel entitlement 字段。
- Team Identifier。
- Apple Developer identity、Apple entitlement authorization 和 Notarization 状态。

本地自签名模式下，`apple_developer_identity`、`apple_entitlements_authorized`、`notarized` 和 `network_extension_vpn_authorization_supported` 均为 `false`。不要将 entitlement 字段存在误认为 Apple 已批准该 entitlement。

## GitHub Actions 与 Releases

- Build、Release、Weekly Preview 保持无签名构建，不访问开发者本地钥匙串。
- GitHub Releases 只接受 `distribution_mode=unsigned` 的 APP 资产。
- `local-development-only` 产物会被 Release 附加脚本拒绝。
- 不要将 `.p12`、`.pfx`、`.key`、`.pem`、`.mobileprovision` 或 `.provisionprofile` 放入项目目录。源码打包会拒绝这些敏感文件。

## 证书安全

P12 文件包含私钥。只用于个人开发 Mac；不要发给他人、不要提交到 Sourcetree、不要放进 GitHub Secrets。若泄露，请在「钥匙串访问」中删除该身份并重新生成。
