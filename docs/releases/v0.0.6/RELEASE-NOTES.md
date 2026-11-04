# Clash_Mac_Compile v0.0.6 · 无签名 arm64 版本

## 发布摘要

本版本根据用户要求，移除所有 Apple Developer / Developer ID / Provisioning Profile / Apple Notary 设置。项目无需 Apple Developer 账户或证书即可使用 GitHub Actions 编译和发布。

## 下载资产

| 文件 | 推荐对象 | 说明 |
|---|---|---|
| `Clash_Mac_Compile-v0.0.6-macos-arm64-unsigned.zip` | Apple Silicon Mac 用户 | 无签名 macOS 原生 APP |
| `Clash_Mac_Compile_v0.0.6_source.zip` | 开发者 / 维护者 | 完整构建工程源码 |
| `BUILD-METADATA.json` | 排障 / 复现构建 | 上游 Client / Kernel / Adapter SHA、Xcode、Go 和优化配置 |
| `SHA256SUMS.txt` | 所有下载者 | 资产 SHA-256 校验 |
| `RELEASE-MANIFEST.json` | 自动化 / 审计 | Release 资产清单 |

## 运行速度与流畅度优先

- Swift Release 使用 `-O`。
- Apple Silicon `arm64` 单架构。
- Xcode 并行任务最多 2。
- Go 内核继续使用官方 Client `Dependencies.lock.json` 固定版本。
- Instruments / Go pprof 性能基准方法继续保留。
- `-O` 是编译策略，不代表已实测性能提升；实际 CPU、内存、启动和 UI 流畅度需要在目标 Mac 测量。

## 无签名与 VPN 功能限制

本项目不使用 Apple Developer Program、Developer ID 证书、Provisioning Profile 或 Apple 公证服务。

- APP 可以通过 GitHub Actions 编译并上传 GitHub Releases。
- macOS 可能提示无法验证开发者或阻止打开；是否允许启动取决于系统安全策略。
- 点击“重试，并允许添加 VPN 配置”时，macOS 可能不会弹出系统授权提示。
- Network Extension / Packet Tunnel 无法保证安装或启动，VPN 代理功能不可视为可用。
- 本版本不绕过 macOS 的系统授权机制。

## 安装说明

1. 下载 `Clash_Mac_Compile-v0.0.6-macos-arm64-unsigned.zip`。
2. 解压并确认包含 `Clash.app`。
3. 将 APP 移入 `/Applications`。
4. macOS 可能阻止无签名 APP 启动；本项目不提供签名或公证。
5. 不要把该版本视为完整 VPN 客户端。

## 配置目录

官方 Client 的配置存储设计使用 App Group 容器。预期路径：

```text
~/Library/Group Containers/group.com.cdreaming.clash/
```

但 App Group 容器需要有效 entitlement；无签名构建可能没有该容器。不要手动创建目录伪造权限，也不要直接编辑正在运行的配置文件。

## 每周上游自动更新

- 每周一 09:17（America/Los_Angeles）检查 ProjectClash/Clash-Client `main`。
- 没有新 commit：跳过构建。
- 有新 commit：自动递增 Patch、固定 SHA、质量检查、构建无签名 APP、提交 main、创建 Tag 并发布 GitHub Pre-release。
- 所有周度版本均为无签名 Preview；Stable 也采用无签名策略。

## 维护修复

本版同时修复开发治理脚本对旧版开发日志的兼容性。重新发布时，如果开发日志缺少 `## 完成摘要`，工具会自动补齐；重发布脚本会在修改版本状态前先执行预检。

## 许可证

本项目使用 ProjectClash 上游客户端、Clash Kernel 与 Adapter。分发时请保留版权与许可证声明，并遵守 GPL-3.0 及第三方依赖许可要求。
