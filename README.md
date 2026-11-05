# Clash_Mac_Compile

<!-- AI-REPOSITORY-HOOK: START -->
> **AI 开工钩子（强制）**
> 修改仓库前依次读取：`AGENTS.md` → `.ai/AI-START-HERE.md` → `.ai/PROJECT-PROFILE.json` → 当前版本 `DEVELOPMENT-JOURNAL.md` → 当前版本 Release Lesson。
> 开工：`python3 scripts/check-governance.py --scope development`
> 收尾：`python3 scripts/build-ai-handoff.py`
> 不得把本地静态检查写成 GitHub macOS Runner 已编译；不得伪造 GitHub Actions、Release、签名或安装测试证据。
<!-- AI-REPOSITORY-HOOK: END -->

**项目版本：以根目录 `VERSION` 为准（当前版本 `0.1.0`）**  
**目标平台：macOS**  
**GitHub：** <https://github.com/cdreaming/Clash-Mac-Compile>

## 项目目标

使用 ProjectClash 官方 Apple 客户端及其锁定的 Clash 内核、Adapter 源码，通过 GitHub Actions 的 macOS + Xcode Runner 自动编译原生 `Clash.app`。

本仓库是**构建与自动化包装工程**，不复制或改写官方客户端源码。每次构建时，工作流会按 `UPSTREAM_CLIENT_REF` 下载官方 `Clash-Client`；官方 Client 的 `Dependencies.lock.json` 再固定 Clash Kernel 和 Clash Adapter 的具体提交。

### 上游组件

| 仓库 | 作用 |
|---|---|
| [ProjectClash/Clash-Client](https://github.com/ProjectClash/Clash-Client) | macOS 原生 APP、SwiftUI、Network Extension、Xcode 工程 |
| [ProjectClash/Clash](https://github.com/ProjectClash/Clash) | Go 代理内核、Apple SDK 构建工具 |
| [ProjectClash/Clash-Adapter](https://github.com/ProjectClash/Clash-Adapter) | Swift Packet Flow 桥接和 Provider 生命周期适配 |

## 自动编译方式

推送到 `main`、向 `main` 发起 Pull Request，或手动运行工作流，都会触发 `.github/workflows/build-macos.yml`：

1. GitHub 启动 `xcode-27` macOS Runner。
2. 安装 Python、Go、XcodeGen。
3. 检出官方 Clash-Client 指定版本。
4. 执行官方 `scripts/bootstrap.py`，按其 `Dependencies.lock.json` 获取并编译 Clash.xcframework 与 Adapter。
5. 执行官方 `scripts/configure.py`，生成 Xcode 工程并编译 macOS CLI helper。
6. 使用 `ClashmacOS` Scheme、Release 配置，仅构建 `arm64`（Apple Silicon）。Swift Release 优化使用 `-O`，优先运行速度；Xcode 最大并行任务数限制为 2，以控制 Runner 资源。
7. 使用 `lipo -archs` 检查 APP 主执行文件架构（兼容 Xcode 27），通过后将 `Clash.app` 打成 ZIP 并上传为 GitHub Actions Artifact。

构建成功后，在 GitHub 仓库的 **Actions → 对应运行记录 → Artifacts** 下载：

- `Clash_Mac_Compile-vX.Y.Z-macos-arm64-unsigned.zip`
- `BUILD-METADATA.json`（记录实际上游提交、内核/Adapter 锁定版本及构建环境）

## Sourcetree 上传步骤

1. 解压本项目源码 ZIP。
2. 在 Sourcetree 中选择 **Add / 添加本地仓库**，指向解压后的 `Clash_Mac_Compile` 文件夹。
3. 如果本地尚未初始化 Git，使用 Sourcetree 初始化仓库；远端地址设置为 `https://github.com/cdreaming/Clash-Mac-Compile.git`。
4. 检查文件变更，提交并推送到 `main`。
5. 打开 GitHub 的 **Actions** 页面，查看 `Build macOS App`。
6. 等待完成后，从 Artifacts 下载 ZIP。

如果 GitHub 仓库已经有 README、LICENSE 或其他提交，先在 Sourcetree 处理远端与本地历史关系，不要直接覆盖或强推。

## 版本规则

`VERSION` 是项目版本唯一事实源。每一轮功能、脚本或构建配置改动都应提升项目版本，不要复用已发布版本：

```bash
python3 scripts/prepare-version.py --version 0.1.1 --risk L2 --write
```

完成新版本文档更新后再提交。普通 `main` 构建的 Artifact 会带项目版本和 Git commit 标识；v0.0.3 起仅生成 Apple Silicon arm64 产物；v0.0.4 修复 Xcode 27 的后置架构检查；v0.0.5 增加 Swift `-O` 运行速度优先构建与每周上游自动 Preview 发布；v0.0.6 移除 Apple Developer / Developer ID / Provisioning Profile / Notarization，统一为无签名构建；v0.0.7 修复旧版开发日志兼容和重发布预检，增加治理回归测试；v0.0.8 增加本地自签名开发模式；v0.0.9 修复 BUILD-METADATA.json 尾部转义导致 Release 附件失败的问题；v0.1.0 将 macOS Packet Tunnel 迁移为 System Extension 并增加激活流程。

## 上游版本可复现性

`UPSTREAM_CLIENT_REF` 当前固定为官方 Client commit `e3e647283b1593a61dba622f13cd499deeda9b8b`。构建日志和 `BUILD-METADATA.json` 会记录实际解析到的 40 位 Client commit SHA。

- 日常开发：建议保持本文件中的固定 SHA，以便 main CI 与 Release 使用相同源码。
- 升级上游：先审查新的官方 Client commit 和其 `Dependencies.lock.json`，再更新 SHA 并提升本项目版本。
- Release workflow 会拒绝 `main` 等可移动分支，避免同一版本标签在未来悄悄构建出不同源码。

Kernel 与 Adapter 不需要在本项目重复维护版本号；它们由所选 Client commit 内的 `Dependencies.lock.json` 固定。

## macOS System Extension / VPN 架构

v0.1.0 在构建阶段对固定的 ProjectClash Client checkout 应用确定性补丁：

- `ClashmacOSExtension` 从 `app-extension` 转为 `system-extension`。
- 主 APP 与 provider 使用 `packet-tunnel-provider-systemextension` entitlement。
- 主 APP 增加 `com.apple.developer.system-extension.install` 并链接 `SystemExtensions.framework`。
- provider 由 XcodeGen 以 System Extension 产品类型嵌入 `Contents/Library/SystemExtensions`。
- VPN 配置保存前先调用 `OSSystemExtensionRequest.activationRequest`，等待 macOS 用户批准和激活完成，再继续原有 VPN preference 保存流程。
- 构建后生成 `VPN-ARCHITECTURE-REPORT.json`，检查 target、entitlements、激活调用链、扩展嵌入位置和签名身份。

GitHub Build / Release / Weekly 仍然使用 unsigned 构建。系统扩展架构正确不等于 Apple 已授权：没有 Apple Developer ID、Apple 授权的 Network Extension entitlement / provisioning profile 和公证，macOS 仍会拒绝激活 VPN System Extension。

本地开发者可继续导入单独提供的 `Clash_Mac_Compile Local Development` 自签名 P12，运行：

```bash
bash scripts/check-local-signing-identity.sh
bash scripts/build-local-signed-app.sh --output build/local-signed
```

本地自签名仅用于测试代码签名流程，不授予 Apple Team ID、Network Extension 或 System Extension 权限。GitHub Releases 只发布 unsigned APP，不上传本地 P12 或 local-signed 包。详细说明见 `docs/local-development/LOCAL-CODE-SIGNING.md`。

## GitHub Releases 下载

正式下载入口：

<https://github.com/cdreaming/Clash-Mac-Compile/releases>

每个 Release 的说明区提供版本来源、兼容性、安装步骤、配置目录、无签名状态、VPN 限制和资产说明。普通用户优先下载 `Clash_Mac_Compile-vX.Y.Z-macos-arm64-unsigned.zip`；完整构建工程下载 `Clash_Mac_Compile_vX.Y.Z_source.zip`。下载说明同时提供 `VPN-ARCHITECTURE-REPORT.json`，说明 System Extension 是否嵌入及 Apple 授权状态。详细说明见 `docs/github/RELEASE-DOWNLOAD-GUIDE.md`。

## 每周上游自动检查

`.github/workflows/upstream-weekly.yml` 每周一 09:17（America/Los_Angeles）检查 ProjectClash/Clash-Client `main`。没有新 commit 时跳过构建；有新 commit 时自动递增 Patch 版本、固定 Client SHA、运行质量检查、构建 arm64 APP、提交 main、创建 `vX.Y.Z` tag 并发布 GitHub Pre-release。也可以在 Actions 页面手动运行；`force_rebuild` 仅用于明确要求同一上游 SHA 重新构建。

自动化使用仓库 `GITHUB_TOKEN` 的 `contents: write` 权限。若 `main` 分支保护规则禁止 GitHub Actions 直接推送，自动版本提交会被拒绝；请在 GitHub Settings → Actions → General 允许 Actions 写入内容，并按需调整分支保护。自动周度版本默认为 Pre-release，不自动冒充 Stable。

## 性能优化

Release 默认使用 Swift `-O`，优先运行速度而非最小体积；Go 内核沿用上游锁定源码及其 Go 工具链，不注入未经基准验证的运行时 flags。性能优化不等于已实测收益，需用 Instruments / Go pprof 验证。性能优化策略和 Instruments / Go pprof 基准方法见 `docs/performance/PERFORMANCE-STRATEGY.md`。没有可重复基准前，不宣称具体性能提升比例。

## GitHub Release 与本地开发构建

`Build macOS App` 会生成无签名 arm64 APP Artifact。GUI 能否启动取决于 macOS 安全策略；该版本不能保证 Network Extension / Packet Tunnel VPN 系统授权。**普通用户从 GitHub Releases 下载标记为 unsigned 的 APP ZIP。** 本地 self-signed ZIP 只供开发 Mac 测试，不上传 Release。

正式 Release 采用 `vX.Y.Z` tag。Release workflow 无需任何 Apple Developer Secrets，会重新构建 arm64 无签名 APP，并将 APP ZIP、源码 ZIP、构建元数据、SHA-256 和下载说明上传到 GitHub Releases。Release 页面会明确提示无签名状态，以及 Packet Tunnel / VPN 授权不可用的限制。


本版将 `UPSTREAM_CLIENT_REF` 固定为完整 commit SHA。手动 Stable Release 由 tag 工作流发布；周度上游工作流在同一次运行中完成构建、提交、tag 和 Pre-release。

## 本地静态检查

这些检查可以在 macOS 或 Linux 上运行；真正的 Xcode 构建只能在 macOS Runner / Mac 上执行：

```bash
python3 scripts/check-governance.py --scope development
python3 scripts/run-quality-gates.py --scope candidate
python3 scripts/check-build-config.py
bash -n scripts/build-macos-app.sh
python3 scripts/build-ai-handoff.py
```

## 许可证与上游声明

本项目不会把 ProjectClash 上游源码伪装成自有代码。上游客户端、Clash Kernel 和 Adapter 的许可证、NOTICE、第三方依赖声明以各自仓库为准；当前官方项目使用 GPL-3.0。分发编译产物时，请保留其许可证与署名，并确保满足 GPL-3.0 对对应源代码提供的要求。详见 `THIRD_PARTY_NOTICES.md`。


## 开发日志与重新发布兼容性

`dev-session.py` 支持旧版开发日志：如果缺少会话元数据或 `## 完成摘要`，会在开始开发 / 检查时自动补齐。手动检查可运行：

```bash
python3 scripts/dev-session.py validate
python3 scripts/dev-session.py status
```

`prepare-republish.py` 会在写入 Release Checklist、`RELEASE_REVISION` 和历史记录前先运行日志预检。若日志文件缺失，流程会失败且不修改发布状态。相关回归测试位于 `tests/test_governance.py`。
