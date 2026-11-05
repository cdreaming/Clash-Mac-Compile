# Clash_Mac_Compile v0.1.3 · 构建步骤闭环与失败证据修复版

## 发布摘要

v0.1.3 针对 v0.1.2 的 GitHub Actions 中 `verify-build-outputs.py` 执行时五个构建产物全部缺失的问题，重构 Build / Release / Weekly 的构建步骤。现在 macOS 构建和输出验证在同一个 GitHub Actions step 中执行，使用同一个绝对输出目录；构建失败时不会再继续执行一个独立的 verify step，而是直接保留退出状态、工作目录上下文和可用诊断文件。

## 本版主要变化

- Build / Release / Weekly 将 Xcode 构建与 `verify-build-outputs.py` 合并为单个 `Build and verify native macOS app` step。
- 统一使用 `${{ github.workspace }}/build/ci` 或 `${{ github.workspace }}/build/release` 作为绝对输出目录。
- 每个 workflow 在调用构建脚本之前创建 `BUILD-WORKFLOW-STATUS.txt` 和 `BUILD-WORKFLOW-CONTEXT.txt`。
- workflow shell EXIT trap 记录成功 / 失败状态、退出码和输出目录。
- `build-macos-app.sh` 在输出目录中写入 `BUILD-RUN-CONTEXT.txt` 与 `BUILD-SCRIPT-STATUS.txt`；EXIT trap 记录脚本真实退出码，并在失败时保留诊断文件。
- `verify-build-outputs.py` 递归列出实际输出目录内容，检查脚本状态和必需文件，并区分构建脚本未启动、构建失败、输出路径错误和产物缺失。
- Build / Release / Weekly 增加 `Report build outcome and output directory` always-run 步骤，打印构建 step outcome、目录文件列表和 status/context。
- Xcode linker diagnostics Artifact 同时包含 workflow/script 状态和上下文文件。
- Release 附件脚本要求 `BUILD-SCRIPT-STATUS.txt` 确认 exit code 0，防止失败构建被错误发布。
- 保留 v0.1.0 System Extension 迁移、v0.1.1 Framework embed/runpath 修正和 v0.1.2 输出清单。

## 故障解释

v0.1.2 的错误说明五个文件均未出现在验证步骤指定的目录中。该现象不应简单归咎于上传 glob。v0.1.3 将构建与验证放在同一个 step，消除两个 step 间对工作目录、输出目录和执行条件的歧义，并保留脚本退出证据。真实根因仍须以 GitHub Actions 的 build step outcome 和 status/context 文件确认。

## 目标构建配置

- Apple Silicon `arm64`。
- Swift Release `-O`。
- Xcode 并行任务 2。
- GitHub Build / Release / Weekly 显式 unsigned。
- 保留 System Extension 和 ClashMacCore framework embed/runpath。
- 保留 verbose Xcode log 和 linker diagnostics。

## 新增诊断文件

| 文件 | 用途 |
|---|---|
| `BUILD-WORKFLOW-STATUS.txt` | GitHub workflow 构建步骤最终状态和退出码 |
| `BUILD-WORKFLOW-CONTEXT.txt` | GitHub workspace、工作目录、输出目录和版本 |
| `BUILD-SCRIPT-STATUS.txt` | `build-macos-app.sh` 的真实退出状态和退出码 |
| `BUILD-RUN-CONTEXT.txt` | 构建脚本根目录、工作目录、输出目录、版本、Runner 和签名模式 |

## 发布资产

- `Clash_Mac_Compile-v0.1.3-macos-arm64-unsigned.zip`
- `Clash_Mac_Compile_v0.1.3_source.zip`
- `BUILD-METADATA.json`
- `BUILD-OUTPUT-MANIFEST.json`
- `BUILD-SCRIPT-STATUS.txt`
- `BUILD-RUN-CONTEXT.txt`
- `VPN-ARCHITECTURE-REPORT.json`
- `SHA256SUMS.txt`

## VPN / 签名边界

GitHub 构建仍然 unsigned。System Extension 架构通过不代表 Apple Network Extension entitlement 已授权；正式 VPN 激活仍需要 Apple Developer ID、授权 entitlement / provisioning profile 和公证。

## 许可证

保留 ProjectClash 上游 GPL-3.0 及所有第三方依赖许可。
