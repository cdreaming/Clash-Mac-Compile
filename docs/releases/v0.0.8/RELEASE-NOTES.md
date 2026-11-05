# Clash_Mac_Compile v0.0.8 · 本地自签名开发模式版

## 发布摘要

v0.0.8 基于 v0.0.7，增加本地自签名代码签名开发模式。用户无需 Apple Developer Program，即可在自己的 Mac 上测试本地 Code Signing identity、Xcode 签名设置以及主 APP / 嵌套扩展签名校验。

原有 GitHub Actions Build、Release、Weekly Preview 仍然保持无签名，不使用用户本地私钥，也不要求 Apple Developer Secrets。

## 本版变化

- 新增 `scripts/check-local-signing-identity.sh`，检查 macOS Keychain 中的本地签名身份。
- 新增 `scripts/build-local-signed-app.sh`，用 `Clash_Mac_Compile Local Development` 构建本地签名 APP。
- `scripts/build-macos-app.sh` 增加 `unsigned` / `local` 两种模式；默认仍为 unsigned。
- 新增 `scripts/verify-local-signed-app.sh`，验证主 APP 和嵌套扩展的本地签名。
- 新增 `LOCAL-SIGNING-REPORT.json`，明确区分签名验证与 Apple entitlement 授权。
- 本地签名 APP 命名为 `Clash_Mac_Compile-v0.0.8-macos-arm64-local-signed.zip`。
- GitHub Releases 继续只上传无签名 APP，拒绝 local-development-only 资产。
- 源码打包增加 `.p12`、`.pfx`、Provisioning Profile 等敏感文件拦截，防止私钥进入源码包。
- 修复 APP 构建元数据写入器把字面量 `\\n` 追加到 JSON 末尾、导致 Release 资产附加阶段报 `Extra data` 的问题。
- 增加回归测试：执行真实的嵌入式 metadata writer，并使用严格 JSON parser 解析输出；Release JSON 错误现在会指出文件路径和具体行列位置。

## 性能配置

- Apple Silicon `arm64` 单架构。
- Swift Release 使用 `-O`，运行速度优先。
- Xcode 并行任务默认最多 2。
- Go 内核依赖继续使用官方 Client 的 `Dependencies.lock.json` 固定版本。
- 不宣称未经目标 Mac 实测的性能提升。

## 两种构建方式

### GitHub 无签名构建

```bash
bash scripts/build-macos-app.sh --output build/ci
```

生成 `macos-arm64-unsigned.zip`，供 GitHub Actions Artifact / Releases 使用。

### 本地自签名开发构建

先将单独提供的本地示例 `.p12` 导入 macOS 登录钥匙串，再执行：

```bash
bash scripts/check-local-signing-identity.sh
bash scripts/build-local-signed-app.sh --output build/local-signed
```

生成 `macos-arm64-local-signed.zip` 和 `LOCAL-SIGNING-REPORT.json`。该包仅供本机开发实验，不会上传 GitHub Releases。

## VPN / Network Extension 限制

本地自签名身份不是 Apple Developer ID，不包含 Apple Team ID，也没有 Apple 签发的 Provisioning Profile。它不能授予 Network Extension、Packet Tunnel 或 System Extension entitlement，也不能完成 Apple 公证。

当前锁定的 ProjectClash Client 工程将 `ClashmacOSExtension` 定义为 `app-extension`，而不是 macOS System Extension。本版不会将自签名构建描述为 VPN 可用；“重试，并允许添加 VPN 配置”仍可能不弹出系统授权窗口。

若未来要通过 GitHub Releases 分发真正可用的 VPN，需要 Apple 授权的签名与 entitlement，并核查适用于 macOS 的扩展分发架构。

## GitHub Releases 下载资产

| 文件 | 用途 |
|---|---|
| `Clash_Mac_Compile-v0.0.8-macos-arm64-unsigned.zip` | GitHub 构建的无签名 APP |
| `Clash_Mac_Compile_v0.0.8_source.zip` | 完整源码工程 |
| `BUILD-METADATA.json` | 上游 Client / Kernel / Adapter SHA 与构建环境 |
| `SHA256SUMS.txt` | 资产校验 |
| `RELEASE-MANIFEST.json` | Release 资产清单 |

## 许可证

本项目使用 ProjectClash 上游客户端、Clash Kernel 与 Adapter。分发时请保留版权和许可证声明，并遵守 GPL-3.0 及第三方依赖许可。
