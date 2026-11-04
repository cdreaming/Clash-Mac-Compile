# Clash_Mac_Compile v0.0.7 · 无签名简化版

## 发布摘要

本版本根据用户决定，移除 Apple Developer、Developer ID、Provisioning Profile 和 Apple 公证设置，统一使用无签名方式编译和发布 macOS arm64 原生 APP。

继续保留 Swift `-O` 运行速度优先、arm64 单架构、每周上游检查、自动 Patch 版本、Git Tag、GitHub Pre-release 和 Releases 下载说明。

## 下载资产

| 文件 | 推荐对象 | 说明 |
|---|---|---|
| `Clash_Mac_Compile-v0.0.7-macos-arm64-unsigned.zip` | Apple Silicon Mac 用户 | 无签名 macOS 原生 APP |
| `Clash_Mac_Compile_v0.0.7_source.zip` | 开发者 / 维护者 | 完整构建工程源码 |
| `BUILD-METADATA.json` | 排障 / 复现构建 | 上游 Client / Kernel / Adapter SHA、Xcode、Go 和优化配置 |
| `SHA256SUMS.txt` | 所有下载者 | 资产 SHA-256 校验 |
| `RELEASE-MANIFEST.json` | 自动化 / 审计 | Release 资产清单 |

## 性能策略

- Swift Release 使用 `-O`。
- Apple Silicon `arm64` 单架构。
- Xcode 并行任务最多 2。
- Go 内核继续使用官方 Client `Dependencies.lock.json` 固定版本。
- `-O` 是编译策略，不代表已实测性能提升；实际 CPU、内存、启动和 UI 流畅度需要目标 Mac 实测。

## 无签名与 VPN 功能限制

本项目不使用 Apple Developer Program、Developer ID 证书、Provisioning Profile 或 Apple 公证服务。

- APP 可以通过 GitHub Actions 编译并上传 GitHub Releases。
- macOS 可能提示无法验证开发者或阻止打开；是否允许启动取决于系统安全策略。
- 点击“重试，并允许添加 VPN 配置”时，macOS 可能不会弹出系统授权提示。
- Network Extension / Packet Tunnel 无法保证安装或启动，VPN 代理功能不可视为可用。
- 本版本主要用于验证 APP 编译产物和可运行的非 VPN GUI 功能。

## 安装说明

1. 下载 `Clash_Mac_Compile-v0.0.7-macos-arm64-unsigned.zip`。
2. 解压并确认包含 `Clash.app`。
3. 将 APP 移入 `/Applications`。
4. macOS 可能阻止无签名 APP 启动；本项目不提供签名或公证。
5. 不要把该版本视为完整 VPN 客户端。

## 配置目录

官方 Client 的配置存储设计使用 App Group 容器。预期路径：

`~/Library/Group Containers/group.com.cdreaming.clash/`

但 App Group 容器需要有效 entitlement；无签名构建可能没有该容器。不要手动创建目录伪造权限。

## 每周上游自动更新

每周一 09:17（America/Los_Angeles）检查 ProjectClash/Clash-Client `main`。没有新 commit 时跳过；有新 commit 时自动递增 Patch、固定 SHA、构建无签名 APP、提交 main、创建 Tag 并发布 GitHub Pre-release。

所有周度版本均为无签名 Preview；Stable 也采用无签名策略。
