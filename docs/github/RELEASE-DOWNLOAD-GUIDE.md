# GitHub Releases 下载说明

GitHub Releases 页面是长期下载入口：

<https://github.com/cdreaming/Clash-Mac-Compile/releases>

每个 Release 说明区列出版本、上游 Client commit、变更摘要、macOS 架构、安装方式、无签名状态和 VPN 限制。

## 下载资产

| 文件 | 用途 |
|---|---|
| `Clash_Mac_Compile-vX.Y.Z-macos-arm64-unsigned.zip` | Apple Silicon macOS 原生 APP（无签名） |
| `Clash_Mac_Compile_vX.Y.Z_source.zip` | 完整构建工程源码 |
| `BUILD-METADATA.json` | Client / Kernel / Adapter commit、Xcode、Go 和优化配置 |
| `SHA256SUMS.txt` | SHA-256 校验 |
| `RELEASE-MANIFEST.json` | Release 资产清单 |

普通用户下载 APP ZIP；开发者下载 source ZIP。本地开发者可以在自己的 Mac 上单独生成 local-signed 测试包，但它不会上传到 GitHub Releases。

## 安装说明

1. 在 Releases 页面选择版本。
2. 阅读该版本 macOS 要求、架构和已知限制。
3. Apple Silicon Mac 下载 `macos-arm64-unsigned.zip`。
4. 解压并确认包含 `Clash.app`。
5. 将 APP 移入 `/Applications`。
6. 无签名 APP 可能被 macOS 阻止启动；本项目不提供签名或公证，是否允许启动取决于系统安全策略。

## 本地自签名开发包（不在 Releases 中）

导入本地示例 P12 到 macOS 登录钥匙串后，可在项目源码根目录执行：

```bash
bash scripts/check-local-signing-identity.sh
bash scripts/build-local-signed-app.sh --output build/local-signed
```

生成的 `macos-arm64-local-signed.zip` 仅供开发者本机验证 Xcode 代码签名；它不是 Apple Developer ID，也不进入正式 Release。不要将本地 P12 或私钥提交到 Git。

## VPN / Packet Tunnel 限制

本项目当前 GitHub 构建不使用 Apple Developer Team、Developer ID 证书、Provisioning Profile 或 Apple 公证服务。v0.1.0 已将 Packet Tunnel 架构迁移为 System Extension，但 unsigned 产物仍不能激活 VPN。

- APP 可以由 GitHub Actions 编译并上传到 Releases。
- “重试，并允许添加 VPN 配置”可能不会弹出系统授权提示。
- Network Extension / Packet Tunnel 无法保证安装或启动，VPN 代理功能不可视为可用。
- 不要把无签名构建当作完整可用的 VPN 客户端。

## 配置目录

官方 Client 的配置存储设计使用 App Group 容器。预期路径：

`~/Library/Group Containers/group.com.cdreaming.clash/`

App Group 容器需要有效 entitlement；无签名构建可能没有该容器。不要手动创建目录伪造权限。

## Weekly Preview 与 Stable

- Weekly Preview：上游 Client 有新提交时自动构建并创建 GitHub Pre-release。
- Stable：由项目维护者确认后，使用正式 Release 流程发布。
- 若上游没有新提交，周度检查跳过构建。
- 所有版本都保持无签名，并在下载说明中明确 VPN 限制。
