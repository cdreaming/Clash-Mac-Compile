# Clash_Mac_Compile v0.1.4 · GitHub Actions Shell 续行修复版

## 发布摘要

v0.1.4 修复 v0.1.3 的 Build / Release / Weekly workflow 中多行 `printf` 命令错误使用双反斜杠续行的问题。GitHub Runner 把未正确续行的后续目录参数解析成命令，导致在执行 `build-macos-app.sh` 之前以 exit code 126 失败。

## 本版主要变化

- Build / Release / Weekly 三条 workflow 的构建状态写入统一改用 `printf '%s\n'`。
- 移除所有多行 `printf` 的反斜杠续行写法，避免 YAML block scalar 与 Bash 转义叠加产生错误。
- 状态文件通过多个 `printf` 参数写入：`BUILD-WORKFLOW-STATUS.txt`、`BUILD-WORKFLOW-CONTEXT.txt`。
- EXIT trap 仍然记录 `status`、`exit_code` 和输出目录。
- 修复范围严格限定在 GitHub Actions workflow shell 脚本，不修改 Xcode 编译参数、Clash Kernel 或 System Extension 代码。
- `check-build-config.py` 现在无额外 Python YAML 依赖地提取 Build / Release / Weekly 的实际构建 shell block，执行 `bash -n` 并拒绝双反斜杠行尾续行。
- 新增 `tests/test_workflow_shell.py`：无 PyYAML 依赖地检查三条 workflow 的真实 shell block，并用成功 / 失败模拟验证 EXIT trap 状态和退出码。

## 故障证据

用户提供的 GitHub Actions 日志：
`...sh: line 5: /Users/runner/work/Clash-Mac-Compile/Clash-Mac-Compile: is a directory`
`exit code 126`

v0.1.3 的 YAML `run: |` 中存在行尾 `\\`（两个反斜杠）。Bash 将其解释为转义后的字面反斜杠，而不是行续接符，导致下一行参数没有并入 `printf` 命令，目录路径被尝试作为命令执行。

## 保留功能

- Apple Silicon `arm64`。
- Swift Release `-O`，Xcode jobs 2。
- GitHub unsigned build。
- System Extension 架构迁移和 `ClashMacCore.framework` embed/runpath。
- verbose Xcode linker diagnostics。
- 构建输出 manifest、workflow/script status/context。
- Release 附件只接受 build script 成功退出的产物。
- Weekly 自动检查与版本发布流程。

## 验证

本版对 YAML 中实际的 Build / Release / Weekly `run` block 执行 Bash 语法检查，并模拟 build 成功与 exit code 65 的失败，验证 workflow EXIT trap 保留最终状态。真实 GitHub macOS Runner 构建仍待上传后验证。

## 发布资产

- `Clash_Mac_Compile-v0.1.4-macos-arm64-unsigned.zip`
- `Clash_Mac_Compile_v0.1.4_source.zip`
- `BUILD-METADATA.json`
- `BUILD-OUTPUT-MANIFEST.json`
- `VPN-ARCHITECTURE-REPORT.json`
- `SHA256SUMS.txt`

## 签名限制

GitHub 构建仍然 unsigned。System Extension 架构通过不等于 Apple 已授权 Network Extension；正式 VPN 激活仍需要 Apple Developer ID、授权 entitlement / provisioning profile 和公证。
