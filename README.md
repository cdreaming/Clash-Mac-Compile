# Clash_Mac_Compile

<!-- AI-REPOSITORY-HOOK: START -->
> **AI 开工钩子（强制）**
> 修改仓库前依次读取：`AGENTS.md` → `.ai/AI-START-HERE.md` → `.ai/PROJECT-PROFILE.json` → 当前版本 `DEVELOPMENT-JOURNAL.md` → 当前版本 Release Lesson。
> 开工：`python3 scripts/check-governance.py --scope development`
> 收尾：`python3 scripts/build-ai-handoff.py`
> 不得把本地静态检查写成 GitHub macOS Runner 已编译；不得伪造 GitHub Actions、Release、签名或安装测试证据。
<!-- AI-REPOSITORY-HOOK: END -->

**项目版本：以根目录 `VERSION` 为准（当前版本 `0.0.5`）**  
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

- `Clash_Mac_Compile-vX.Y.Z-macos-arm64.zip`
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
python3 scripts/prepare-version.py --version 0.0.6 --risk L2 --write
```

完成新版本文档更新后再提交。普通 `main` 构建的 Artifact 会带项目版本和 Git commit 标识；v0.0.3 起仅生成 Apple Silicon arm64 产物；v0.0.4 修复 Xcode 27 的后置架构检查；v0.0.5 增加 Swift `-O` 运行速度优先构建与每周上游自动 Preview 发布。

## 上游版本可复现性

`UPSTREAM_CLIENT_REF` 当前固定为官方 Client commit `e3e647283b1593a61dba622f13cd499deeda9b8b`。构建日志和 `BUILD-METADATA.json` 会记录实际解析到的 40 位 Client commit SHA。

- 日常开发：建议保持本文件中的固定 SHA，以便 main CI 与 Release 使用相同源码。
- 升级上游：先审查新的官方 Client commit 和其 `Dependencies.lock.json`，再更新 SHA 并提升本项目版本。
- Release workflow 会拒绝 `main` 等可移动分支，避免同一版本标签在未来悄悄构建出不同源码。

Kernel 与 Adapter 不需要在本项目重复维护版本号；它们由所选 Client commit 内的 `Dependencies.lock.json` 固定。

## 签名与运行限制

当前版本使用 `CODE_SIGNING_ALLOWED=NO`，目标是验证原生 APP 的编译和产物打包，不需要把 Apple Developer 证书放入仓库。

**无签名 ZIP 不等于可完整安装使用的 VPN 客户端。** 正常安装、Network Extension / Packet Tunnel、App Groups、iCloud 等受保护能力需要你自己的 Apple Developer Team、证书和 Provisioning Profile。此版本不会伪造签名、公证或 VPN 实机测试结果。

后续如需自动签名，应通过 GitHub Secrets 配置证书，并按 Apple 的能力与描述文件要求调整工作流；不要提交 `.p12`、私钥或 Provisioning Profile 到 Git。

## GitHub Releases 下载

正式下载入口：

<https://github.com/cdreaming/Clash-Mac-Compile/releases>

每个 Release 的说明区提供版本来源、兼容性、安装步骤、配置目录、签名状态和资产说明。普通用户优先下载 `Clash_Mac_Compile-vX.Y.Z-macos-arm64.zip`；完整构建工程下载 `Clash_Mac_Compile_vX.Y.Z_source.zip`。详细说明见 `docs/github/RELEASE-DOWNLOAD-GUIDE.md`。

## 每周上游自动检查

`.github/workflows/upstream-weekly.yml` 每周一 09:17（America/Los_Angeles）检查 ProjectClash/Clash-Client `main`。没有新 commit 时跳过构建；有新 commit 时自动递增 Patch 版本、固定 Client SHA、运行质量检查、构建 arm64 APP、提交 main、创建 `vX.Y.Z` tag 并发布 GitHub Pre-release。也可以在 Actions 页面手动运行；`force_rebuild` 仅用于明确要求同一上游 SHA 重新构建。

自动化使用仓库 `GITHUB_TOKEN` 的 `contents: write` 权限。若 `main` 分支保护规则禁止 GitHub Actions 直接推送，自动版本提交会被拒绝；请在 GitHub Settings → Actions → General 允许 Actions 写入内容，并按需调整分支保护。自动周度版本默认为 Pre-release，不自动冒充 Stable。

## 性能优化

Release 默认使用 Swift `-O`，优先运行速度而非最小体积；Go 内核沿用上游锁定源码及其 Go 工具链，不注入未经基准验证的运行时 flags。性能优化策略和 Instruments / Go pprof 基准方法见 `docs/performance/PERFORMANCE-STRATEGY.md`。没有可重复基准前，不宣称具体性能提升比例。

## 正式 Release

正式 Release 采用 `vX.Y.Z` tag。Release workflow 在 macOS Runner 上重新构建 APP，将项目源码包、arm64 APP ZIP、构建元数据和 SHA-256 一起上传，并执行线上资产校验。

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
