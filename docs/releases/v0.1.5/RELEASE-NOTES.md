# Clash_Mac_Compile v0.1.5 · System Extension 构建脚本变量与退出状态修复版

## 发布摘要

v0.1.5 修复 v0.1.4 GitHub Runner 构建时出现的 `SYSTEM_EXTENSION_PROJECT: unbound variable`。构建脚本实际声明的是 `SYSTEM_EXTENSION_PROJECT_SPEC`，复制 project.yml 时却引用了未声明的 `SYSTEM_EXTENSION_PROJECT`。同时修复构建状态文件使用双反斜杠输出字面 `\n`，导致状态解析器无法读取独立字段的问题。

## 本版修复

- 将 project.yml 复制目标统一为已声明变量 `SYSTEM_EXTENSION_PROJECT_SPEC`，并在复制前执行非空断言。
- 构建脚本的初始状态和 EXIT trap 最终状态统一使用 `printf '%s\n'`，确保每个 key/value 独占一行。
- EXIT trap 改为 `trap 'cleanup_build "$?"' EXIT`，在进入函数前将原始退出码作为参数传递。
- `cleanup_build` 依据明确传入的退出码写入 `status=success|failed` 和 `exit_code=0|非零`，不再把状态判断与局部变量初始化混在一起。
- 新增 `tests/test_build_script_status.py`，检查变量声明与引用一致、状态输出没有字面反斜杠 n，并真实运行 EXIT trap 的非零退出模拟。
- 保留 v0.1.4 的 Build / Release / Weekly workflow Shell 修复和 shell 语法回归测试。

## 故障证据

用户提供的 GitHub Actions 日志：
`build-macos-app.sh: line 208: SYSTEM_EXTENSION_PROJECT: unbound variable`

该错误发生在 `xcodebuild` 启动之前，直接原因是变量名不一致，不是 Xcode Linker 或 Apple 签名问题。

同一日志中的 `BUILD-SCRIPT-STATUS.txt` 把多个字段写在一行，显示为 `status=success\nexit_code=0...`，因此验证器无法把 `status` 和 `exit_code` 解析为独立字段。本版修复真实换行输出，并将 EXIT trap 的退出码显式传参。

## 保留构建设置

- macOS / Apple Silicon `arm64`。
- Swift Release `-O`，Xcode jobs 2。
- GitHub Actions unsigned。
- macOS System Extension 架构和 `ClashMacCore.framework` embed/runpath。
- verbose Xcode linker diagnostics。
- 构建与输出验证在同一个 Actions step。
- workflow 与 build script 独立状态和上下文文件。

## 验证

本版执行 Bash 语法检查、变量引用静态测试、状态文件格式测试和 EXIT trap 非零退出码模拟。真实 GitHub macOS Runner 的完整 Xcode 编译仍需上传后验证。

## 发布资产

- `Clash_Mac_Compile-v0.1.5-macos-arm64-unsigned.zip`
- `Clash_Mac_Compile_v0.1.5_source.zip`
- `BUILD-METADATA.json`
- `BUILD-OUTPUT-MANIFEST.json`
- `BUILD-SCRIPT-STATUS.txt`
- `BUILD-RUN-CONTEXT.txt`
- `VPN-ARCHITECTURE-REPORT.json`
- `SHA256SUMS.txt`

## 签名边界

GitHub 构建仍然 unsigned。System Extension 结构检查通过不等于 Apple Network Extension entitlement 已授权；正式 VPN 激活仍需要 Apple Developer ID、授权 entitlement / provisioning profile 和公证。
