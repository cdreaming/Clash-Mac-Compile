# Clash_Mac_Compile v0.0.8 Release Experience Report

## 开发过程

在 v0.0.7 无签名构建基础上增加 opt-in 本地自签名模式。开发证书独立于源码 ZIP，不进入 GitHub Actions。普通 CI / Release / Weekly 继续走 unsigned 路径。

## 有效做法

- 通过 macOS Keychain `security find-identity -v -p codesigning` 检查本地身份。
- Xcode 构建通过明确的 `--signing-mode local` 启用签名；默认模式仍为 unsigned。
- 对主 APP 和嵌套 App Extension 运行 `codesign --verify --strict`。
- 将本地签名结果写入 `LOCAL-SIGNING-REPORT.json`，不把签名通过误认为 entitlement 已获 Apple 授权。
- Release 附加脚本只接受 unsigned 资产，避免将个人自签名包发布给其他用户。

## 风险与改进

- 本地自签名证书没有 Apple Team ID，不能授予 Network Extension / Packet Tunnel entitlement。
- 当前锁定的官方 macOS 工程仍声明 `ClashmacOSExtension` 为 `app-extension`；本版没有将其改成 System Extension。
- 本地 Xcode / Keychain 行为需要在目标 Mac 实测；当前源码生成环境不是 macOS。

## 发布操作经验

GitHub Actions 继续不访问开发者个人 Keychain。用户需要在本机导入示例 P12 后执行 `scripts/build-local-signed-app.sh`。本地 `local-signed.zip` 不作为 GitHub Release 资产。

## 后续建议

若未来需要 VPN 真正可用，先根据 Apple 当前支持的 macOS Packet Tunnel 分发模型评估上游扩展架构，再取得 Apple 授权的签名身份和 entitlement。
