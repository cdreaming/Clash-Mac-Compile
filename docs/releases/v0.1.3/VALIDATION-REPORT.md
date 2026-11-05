# Clash_Mac_Compile v0.1.3 Validation Report

## 验证环境

- Python 3.13。
- 当前源码制作环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户，未执行真实 Xcode build 或 Artifact 上传。

## 实际执行并通过

| 检查 | 结果 |
|---|---|
| Python scripts / tests 语法 | PASS |
| Build / local wrapper Shell 语法 | PASS |
| CI / Build / Release / Weekly workflow YAML | PASS，4 个 workflow |
| `scripts/check-build-config.py --release` | PASS |
| `tests.test_project` | PASS，15 个测试方法逐项执行 |
| `tests.test_vpn_architecture` | PASS，4 tests |
| `tests.test_linker_diagnostics` | PASS，2 tests |
| `tests.test_build_outputs` | PASS，5 tests |
| `tests.test_packaging` | PASS，6 tests |
| Repository Structure | PASS，write + check |
| Source Manifest | PASS，write + check |
| `scripts/check-governance.py --scope development` | PASS |
| `scripts/dev-session.py validate` | PASS |
| `scripts/build-release.py`（干净副本） | 待最终打包复核 |
| ZIP / SHA-256 / 私钥扫描 | 待最终打包复核 |

说明：Python 启动时会打印文件生成环境的 Spreadsheet warmup 诊断信息，但上表标记 PASS 的测试命令均以 exit code 0 完成。

## v0.1.2 故障与 v0.1.3 修复

用户提供的错误显示 APP ZIP、BUILD-METADATA、VPN report、SHA256SUMS 和 BUILD-OUTPUT-MANIFEST 全部缺失。该日志未包含前一 build step outcome 或 Xcode log，因此不能判断 Xcode 是否启动或成功。

v0.1.3：
1. 将 Build / Release / Weekly 的 build 和 verify 合并在同一个 Actions step。
2. build 和 verify 使用同一个 `${GITHUB_WORKSPACE}` 绝对输出目录。
3. workflow 在开始时写 `BUILD-WORKFLOW-STATUS.txt`、`BUILD-WORKFLOW-CONTEXT.txt`，并通过 EXIT trap 记录最终状态和退出码。
4. build script 写 `BUILD-SCRIPT-STATUS.txt`、`BUILD-RUN-CONTEXT.txt`，并通过 EXIT trap 记录真实脚本退出码。
5. verify 递归列出输出目录，先检查脚本状态，再验证全部必需文件。
6. always-run report step 打印 build step outcome、目录文件清单和状态。
7. Release attachment 仅接受 script status=success 且 exit_code=0 的构建。

## 尚未执行 / 未验证

- GitHub `xcode-27` Runner 的真实 v0.1.3 Xcode 编译。
- GitHub Actions Artifact 在线上传和下载。
- APP / System Extension 实际嵌入、签名和运行。
- Apple Developer ID / Network Extension entitlement / provisioning profile / notarization。
- macOS 15.7.7 VPN 激活和授权窗口。
- 性能基准。

## 结论

源码级构建与验证闭环、状态记录和诊断上传契约已通过本地测试。真实 GitHub Runner 结果仍待用户上传后验证；不能把本地测试通过表述为 Xcode 云端编译成功。
