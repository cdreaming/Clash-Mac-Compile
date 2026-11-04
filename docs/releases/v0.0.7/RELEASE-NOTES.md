# Clash_Mac_Compile v0.0.7 · 治理兼容修复版

## 发布摘要

v0.0.7 基于 v0.0.6 无签名版本升级，版本号递增至 `0.0.7`。本版重点修复项目治理脚本从 v0.0.4 起遗留的开发日志格式兼容问题，避免重发布时因缺少 `## 完成摘要` 而失败。

## 本版主要变化

- `dev-session.py` 自动兼容旧版开发日志。
- 缺少 `## 完成摘要` 时自动补齐章节。
- 缺少开发会话元数据时自动补齐默认标记。
- 新增 `python3 scripts/dev-session.py validate` 预检命令。
- `prepare-republish.py` 在修改 Checklist、`RELEASE_REVISION` 和重发布历史之前先执行日志预检。
- 预检失败时不修改发布状态，避免半更新。
- 新增回归测试，覆盖旧日志缺少完成摘要、缺少会话标记以及日志文件缺失的场景。
- 每周自动生成的开发日志现在包含 `## 完成摘要`，避免自动版本升级后再次触发同类错误。

## 构建与性能策略

- Apple Silicon `arm64` 单架构。
- Swift Release 优化级别 `-O`，以运行速度优先。
- Xcode 并行编译任务最多 2。
- 不引入未经基准测试的 Go runtime 参数。
- 保留 ProjectClash 官方 Client 固定 SHA 和依赖锁定。

## 无签名与 VPN 限制

本项目不使用 Apple Developer Program、Developer ID、Provisioning Profile 或 Apple 公证服务。

- GitHub Actions 可以编译无签名 macOS APP 并上传 Releases。
- macOS 可能阻止无签名 APP 启动，具体取决于系统安全策略。
- Network Extension / Packet Tunnel 的 VPN 系统授权不受本版支持，不能保证“重试，并允许添加 VPN 配置”弹出授权提示。
- 本版不绕过 macOS 安全机制，也不把编译成功描述为 VPN 已可用。

## 下载资产

| 文件 | 用途 |
|---|---|
| `Clash_Mac_Compile-v0.0.7-macos-arm64-unsigned.zip` | Apple Silicon macOS 无签名 APP |
| `Clash_Mac_Compile_v0.0.7_source.zip` | 完整源码工程 |
| `BUILD-METADATA.json` | 上游 SHA、Xcode、Go、优化和架构信息 |
| `SHA256SUMS.txt` | 资产 SHA-256 校验 |
| `RELEASE-MANIFEST.json` | Release 资产清单 |

## 安装说明

1. 从 GitHub Releases 下载 `Clash_Mac_Compile-v0.0.7-macos-arm64-unsigned.zip`。
2. 解压并确认包含 `Clash.app`。
3. 将 APP 移入 `/Applications`。
4. macOS 可能提示无法验证开发者或阻止启动；本项目不提供签名或公证。
5. 本版不保证 VPN / Packet Tunnel 可用。

## 自动更新

每周一 09:17（America/Los_Angeles）检查 ProjectClash 官方 Client。上游 SHA 变化时自动递增 Patch、固定 SHA、构建无签名 APP、提交 main、创建 Tag 并发布 GitHub Pre-release；没有上游变化则跳过构建。

## 许可证

本项目基于 ProjectClash 上游客户端、Clash Kernel 与 Adapter。分发时请保留版权声明并遵守 GPL-3.0 及第三方依赖许可。
