# Clash_Mac_Compile v0.0.5 · Runtime Speed Priority

## 发布摘要

本版本将运行速度和 UI 流畅度放在首位，并加入每周跟踪 ProjectClash/Clash-Client 开发进度的自动预览发布流程。

## 下载资产

| 文件 | 谁应该下载 | 说明 |
|---|---|---|
| `Clash_Mac_Compile-v0.0.5-macos-arm64.zip` | Apple Silicon Mac 用户 | macOS 原生 APP，arm64 单架构 |
| `Clash_Mac_Compile_v0.0.5_source.zip` | 开发者 / 维护者 | 本版完整构建工程源码 |
| `BUILD-METADATA.json` | 排障 / 复现构建 | 实际 Client、Kernel、Adapter SHA 和工具链信息 |
| `SHA256SUMS.txt` | 所有下载者 | 下载资产 SHA-256 校验 |
| `RELEASE-MANIFEST.json` | 自动化 / 审计 | 本版 Release 资产清单 |

**普通用户建议下载第一个 APP ZIP。** 完整源码 ZIP 用于 Sourcetree、二次开发和复现构建。

## 运行性能优化

- Swift Release 使用 `-O`，优先运行速度，而不是以最小二进制体积为目标。
- 保留 Apple Silicon `arm64` 单架构。
- Xcode 并行任务最多 2，避免 Hosted Runner 峰值资源过高。
- Go 内核继续使用上游锁定版本，不注入未经验证的 Go 编译 flags。
- 增加 Instruments / Go pprof 性能基准方法。当前没有在真实用户 Mac 上完成可重复的性能对照，因此不宣称具体的启动、CPU 或内存提升比例。
- GitHub Actions 升级到 Node 24 兼容版本；关闭不适用的 Go module cache 查找，清理旧 Node.js 与缺少根目录 go.sum 的缓存警告。

## macOS 安装说明

1. 在 Apple Silicon Mac 下载 `Clash_Mac_Compile-v0.0.5-macos-arm64.zip`。
2. 解压 ZIP，确认里面包含 `Clash.app`。
3. 本版本为无签名构建。尚未完成 Developer ID 签名、公证和 Network Extension 正式分发配置；macOS 可能阻止直接打开。不要将此包误认为已公证的正式安装包。
4. VPN / Packet Tunnel、App Groups 和系统扩展能否正常工作，取决于后续正确的 Apple Developer 签名、entitlement 和 provisioning profile。

## 配置文件与数据目录

具备有效 App Groups entitlement 时，预期共享容器为：

```text
~/Library/Group Containers/group.com.cdreaming.clash/
```

官方配置存储工作区位于该容器的 `working/` 下。无签名构建可能没有有效的 App Groups entitlement，因此容器可能尚未创建。

源码包提供检查脚本：

```bash
bash scripts/inspect-macos-data.sh /Applications/Clash.app
```

脚本会读取实际 APP 的签名 entitlement，并检查容器是否存在。不要手动创建容器来替代签名配置，也不要直接编辑正在运行的活动配置文件。

## 每周上游自动更新

- 每周一 09:17（America/Los_Angeles）检查 ProjectClash/Clash-Client `main`。
- 没有新 commit：跳过构建，不产生重复版本。
- 有新 commit：自动递增 Patch 版本、固定 Client SHA、运行质量检查、构建 APP、提交版本更新、创建 `vX.Y.Z` tag，并发布 GitHub Pre-release。
- 周度自动版本默认是 Weekly Preview / Pre-release；Stable Release 仍需维护者确认。

## 上游源码

- Client: `e3e647283b1593a61dba622f13cd499deeda9b8b`（本版初始锁定值；自动周度发布会更新为实际新 SHA）
- Kernel / Adapter: 由 Client 的 `Dependencies.lock.json` 固定。

## 许可证

本项目使用 ProjectClash 上游客户端、Clash Kernel 与 Adapter。分发 APP 或源码时，请保留版权和许可证声明，并遵守 GPL-3.0 及第三方依赖许可要求。
