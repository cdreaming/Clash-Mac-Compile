# Clash_Mac_Compile v0.1.4 Validation Report

## 验证环境

- Python 3.13。
- 当前源码制作环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户，未触发真实 Xcode build 或 Artifact 上传。

## 实际执行并通过

| 检查 | 结果 |
|---|---|
| Build / Release / Weekly / CI workflow YAML | PASS，4 个 workflow |
| 三条 build run block 的 Bash 语法 | PASS |
| 双反斜杠行尾续行检查 | PASS |
| `tests.test_workflow_shell` | PASS，3/3；包含成功与 exit code 65 失败模拟 |
| `scripts/check-build-config.py --release` | PASS |
| Python scripts / tests 语法 | PASS |
| Build / local wrapper Shell 语法 | PASS |
| `tests.test_project` | 14/15 个方法单独通过；Weekly SHA 版本递增测试在 50 秒限制内超时，未计为通过 |
| Repository Structure | PASS，write |
| Source Manifest | PASS，write |
| `scripts/check-governance.py --scope development` | PASS |
| `scripts/dev-session.py validate` | PASS |
| `tests.test_vpn_architecture` / Linker / Build Outputs / Packaging | 本版未完成重跑；相关实现未修改 |
| `scripts/build-release.py`（干净副本） | 待最终打包 |
| ZIP / SHA-256 / 私钥扫描 | 待最终打包 |

说明：Python 启动时会打印文件生成环境的 Spreadsheet warmup 诊断信息。若测试超时，按未验证处理，不将其标记为通过。

## 故障与根因

用户提供的 GitHub Actions 日志：
`...sh: line 5: /Users/runner/work/Clash-Mac-Compile/Clash-Mac-Compile: is a directory`
`exit code 126`

v0.1.3 workflow YAML `run: |` 中多行 `printf` 行尾使用了两个反斜杠。Bash 不会将双反斜杠 + 换行解释为命令续行，导致后续参数 / 重定向脱离 `printf` 命令，Shell 将 workspace 路径误当作命令执行。失败发生在 `build-macos-app.sh` 启动之前。

## v0.1.4 修复

1. 从 v0.1.3 原始源码恢复 Build / Release / Weekly workflow，避免修改 Release 状态解析和 Weekly 版本准备步骤。
2. 仅按 `Build and verify native macOS app` step 名精确修改三个 workflow。
3. 状态写入改用 `printf '%s\n'` 多参数，不使用行尾反斜杠续行。
4. `check-build-config.py` 解析实际 YAML，提取 build run block 执行 `bash -n`，拒绝双反斜杠续行。
5. `tests.test_workflow_shell.py` 对三条 workflow 执行 Bash 语法检查，并模拟成功与 exit code 65 失败，验证 EXIT trap 状态和退出码。

## 尚未执行 / 未验证

- GitHub `xcode-27` Runner 的真实 v0.1.4 Xcode 编译。
- GitHub Actions Artifact 在线上传和下载。
- APP / System Extension 实际嵌入、签名和运行。
- Apple Developer ID / Network Extension entitlement / provisioning profile / notarization。
- macOS VPN 激活和授权窗口。
- 性能基准。

## 结论

v0.1.4 已修复日志明确显示的 GitHub Actions Bash 语法问题，三条实际 build shell block 均通过 `bash -n` 和成功 / 失败状态模拟。真实云端 Xcode 编译和 Artifact 上传仍需 GitHub Runner 验证。
