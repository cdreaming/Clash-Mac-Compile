# Clash_Mac_Compile v0.1.2 · GitHub Actions 构建产物路径修复版

## 发布摘要

v0.1.2 修复 v0.1.1 GitHub Actions 在上传 macOS APP Artifact 时找不到 `build/ci` 下指定文件的问题。构建脚本现在规范化输出目录、验证 APP ZIP / metadata / VPN 架构报告 / checksums，并生成 `BUILD-OUTPUT-MANIFEST.json`。Build workflow 上传整个 `build/ci/` 目录，避免多路径 glob 与单文件路径清单不一致。

## 本版主要变化

- `build-macos-app.sh` 将 `--output` 路径规范化为绝对路径，并在日志中明确打印实际输出目录。
- 构建成功后强制验证版本化 APP ZIP、`BUILD-METADATA.json`、`VPN-ARCHITECTURE-REPORT.json` 和 `SHA256SUMS.txt` 均存在且非空。
- 新增 `BUILD-OUTPUT-MANIFEST.json`，记录版本、输出目录、分发模式、预期 APP ZIP 和构建输出清单。
- 新增 `scripts/verify-build-outputs.py`，在 Artifact 上传和 Release 附件之前验证文件存在、版本、分发模式和 APP 文件名。
- Build workflow 的上传路径改为单一目录 `build/ci/`，避免多路径 artifact glob 的路径解析歧义。
- Build / Release / Weekly 显式设置 `CLASH_SIGNING_MODE=unsigned`，避免 runner 环境变量意外改变产物文件名。
- Release 附件脚本也验证并上传 `BUILD-OUTPUT-MANIFEST.json`。
- 为构建产物缺失增加明确诊断：列出实际输出目录文件和缺失的具体文件，不再只留下 Artifact action 的 “No files were found”。

## 构建与发布方式

- Apple Silicon `arm64`。
- Swift Release `-O`。
- Xcode 并行任务默认 2。
- GitHub Build / Release / Weekly 显式 unsigned。
- 保留 v0.1.0 System Extension 迁移和 v0.1.1 Framework embed/runpath 修正。
- 保留完整 Xcode Linker 日志与失败 Artifact 上传。

## 新增输出

| 文件 | 作用 |
|---|---|
| `BUILD-OUTPUT-MANIFEST.json` | 记录实际构建输出文件、版本和 APP ZIP 文件名 |
| `BUILD-METADATA.json` | 构建环境、上游 SHA 和分发信息 |
| `VPN-ARCHITECTURE-REPORT.json` | System Extension 架构审计 |
| `SHA256SUMS.txt` | 输出文件校验值 |

## VPN 与签名边界

GitHub 构建仍然 unsigned。System Extension 架构正确不等于 Apple 已授权 Network Extension；没有 Apple Developer ID、授权 entitlement / provisioning profile 和公证，VPN 系统激活仍不可保证。

## 发布资产

- `Clash_Mac_Compile-v0.1.2-macos-arm64-unsigned.zip`
- `Clash_Mac_Compile_v0.1.2_source.zip`
- `BUILD-METADATA.json`
- `BUILD-OUTPUT-MANIFEST.json`
- `VPN-ARCHITECTURE-REPORT.json`
- `SHA256SUMS.txt`

## 许可证

保留 ProjectClash 上游 GPL-3.0 及所有第三方依赖许可。
