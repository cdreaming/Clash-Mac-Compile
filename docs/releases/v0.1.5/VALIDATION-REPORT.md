# Clash_Mac_Compile v0.1.5 Validation Report

## 验证环境

- Python 3.13。
- 当前源码制作环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户，未执行真实 Xcode build 或 Artifact 上传。

## 实际执行并通过

| 检查 | 结果 |
|---|---|
| Python scripts / tests 语法 | PASS |
| `bash -n scripts/build-macos-app.sh` | PASS |
| `bash -n scripts/build-local-signed-app.sh` | PASS |
| `scripts/check-build-config.py --release` | PASS |
| `tests.test_build_script_status` | PASS，4/4 |
| `tests.test_workflow_shell` | PASS，3/3 |
| `tests.test_project.ProjectTests.test_project_identity_and_version` | PASS |
| `tests.test_project.ProjectTests.test_build_configuration` | PASS |
| `tests.test_project.ProjectTests.test_build_script_and_workflow_contract` | PASS |
| CI / Build / Release / Weekly workflow YAML | PASS，4 个 workflow |
| Repository Structure | PASS，write + check |
| Source Manifest | PASS，write + check |
| `scripts/check-governance.py --scope development` | PASS |
| `scripts/dev-session.py validate` | PASS |
| `scripts/build-release.py`（干净副本） | PASS；生成 v0.1.5 source ZIP |\n| ZIP CRC / SHA-256 / 私钥扫描 | PASS；无 P12 / PFX / KEY / PEM / Provisioning Profile |

说明：`tests.test_build_outputs`、`tests.test_linker_diagnostics`、`tests.test_vpn_architecture`、`tests.test_packaging` 和完整 `tests.test_project` 在本轮没有完成重跑，不计为通过。Python 启动时出现独立的 Spreadsheet warmup 诊断输出，但已标记 PASS 的命令均以 exit code 0 完成。

## 故障与修复

用户日志：
`build-macos-app.sh: line 208: SYSTEM_EXTENSION_PROJECT: unbound variable`

根因：
- 脚本声明 `SYSTEM_EXTENSION_PROJECT_SPEC`，复制 project.yml 时却使用 `SYSTEM_EXTENSION_PROJECT`。
- 在 `set -u` 下触发未定义变量错误，发生在 `xcodebuild` 启动之前。

状态文件问题：
- 初始和最终状态写入曾使用双反斜杠格式，导致字面 `\n` 写入文件而非真实换行。
- 验证器无法将 status、exit_code、version 和 output_directory 解析为独立字段。

v0.1.5 修复：
1. 统一使用 `SYSTEM_EXTENSION_PROJECT_SPEC`，并增加非空断言。
2. 状态文件改用 `printf '%s\n'`，每个字段单独一行。
3. EXIT trap 改为 `trap 'cleanup_build "$?"' EXIT`，将原始退出码显式传入清理函数。
4. 新增构建脚本状态回归测试，模拟 exit code 65 并检查 `status=failed`。

## 尚未执行 / 未验证

- GitHub `xcode-27` Runner 的真实 v0.1.5 Xcode 编译。
- APP 和 System Extension 实际嵌入、签名和运行。
- GitHub Actions Artifact 在线上传与下载。
- Apple Developer ID / Network Extension entitlement / provisioning profile / notarization。
- macOS VPN 激活和授权窗口。
- 性能基准。

## 结论

v0.1.5 已修复日志明确指出的未定义变量和状态文件换行问题，并通过专门的脚本状态和 workflow shell 回归测试。真实 GitHub macOS Runner 编译仍需上传后验证。
