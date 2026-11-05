# Clash_Mac_Compile v0.1.1 · System Extension Linker 诊断与依赖修复版

## 发布摘要

v0.1.1 针对 v0.1.0 的 `ClashmacOSExtension.systemextension` Link 阶段失败，修正 System Extension 内部动态框架的嵌入方式和 Framework runpath，并增加 Xcode 完整链接日志、目标 Build Settings 和自动错误摘要。

用户提供的日志只包含失败 target 和 exit code 65，没有 `ld` 的具体错误行。因此本版针对已知的扩展 bundle 层级变化修正依赖布局，同时保留完整诊断证据；不能在未运行 GitHub macOS Runner 前宣称原始 linker 根因已被最终证实。

## 本版主要变化

- 将 `ClashMacCore` framework 从仅链接、不嵌入改为嵌入 Packet Tunnel System Extension 自身。
- 将 System Extension 的 `LD_RUNPATH_SEARCH_PATHS` 设置为 `@executable_path/../Frameworks`，对应 `Contents/MacOS` 到扩展自身 `Contents/Frameworks` 的 bundle 相对路径。
- 保留主 APP 对 `ClashMacCore` 的原有嵌入，避免破坏主 APP 的依赖。
- 新增 `scripts/summarize-xcode-linker-errors.py`，提取 `Undefined symbols`、`duplicate symbol`、`framework/library not found`、`ld:` 和 `clang linker command failed` 等诊断及上下文。
- Xcode 构建启用 `-verbose`，将完整输出保存为 `XCODEBUILD.log`。
- 构建失败时保存 `XCODEBUILD-EXIT-CODE.txt`、`ClashmacOSExtension-BuildSettings.json`、stderr 和 `LINKER-DIAGNOSTICS.txt`。
- 构建成功时也保存最终生成的 System Extension project spec 和 resolved Build Settings。
- Build、Release、Weekly workflow 均增加 `if: always()` 诊断 Artifact 上传步骤；即使 Xcode 构建失败，也可以从 Actions Artifact 下载日志。
- VPN 架构审计增加 provider framework embed 与 runpath 检查。

## 构建配置

- Apple Silicon `arm64`。
- Swift Release `-O`。
- Xcode 并行任务默认 2。
- GitHub Actions 仍然无签名。
- 本地自签名开发模式继续保留。
- 不降低 linker 检查，不删除 Clash Core、Adapter 或 Packet Tunnel 代码来规避错误。

## 诊断文件

GitHub Actions 的 `Xcode linker diagnostics` Artifact 包含：

| 文件 | 用途 |
|---|---|
| `XCODEBUILD.log` | 完整 verbose Xcode build / linker 命令和错误输出 |
| `LINKER-DIAGNOSTICS.txt` | 自动提取的错误摘要与上下文 |
| `XCODEBUILD-EXIT-CODE.txt` | 原始 Xcode 退出码 |
| `ClashmacOSExtension-BuildSettings.json` | 扩展 target 的解析后 Build Settings |
| `ClashmacOSExtension-BuildSettings.stderr.log` | Build Settings 查询 stderr |
| `ClashClient-project.system-extension.yml` | 应用 System Extension 补丁后的 XcodeGen project spec |

## VPN 与签名边界

本版仍然没有 Apple Developer ID、Apple Team ID、Apple 授权 entitlement、Provisioning Profile 或公证。System Extension 依赖布局修正和架构审计不代表 VPN 系统授权已经可用。

## 发布资产

- `Clash_Mac_Compile-v0.1.1-macos-arm64-unsigned.zip`
- `Clash_Mac_Compile_v0.1.1_source.zip`
- `BUILD-METADATA.json`
- `VPN-ARCHITECTURE-REPORT.json`
- `SHA256SUMS.txt`

Linker 诊断日志作为 GitHub Actions Artifact 保存，不作为公开 Release 必需资产。

## 许可证

保留 ProjectClash 上游 GPL-3.0 及所有第三方依赖许可。
