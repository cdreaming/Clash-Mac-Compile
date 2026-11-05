# Clash_Mac_Compile v0.1.2 Validation Report

## 验证环境

- Python 3.13。
- 当前源码制作环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户，未触发真实 Xcode build 或 GitHub Artifact 上传。

## 实际执行并通过

| 检查 | 结果 |
|---|---|
| Python scripts / tests 语法 | PASS |
| Build / local wrapper Shell 语法 | PASS |
| CI / Build / Release / Weekly YAML | PASS，4 个 workflow |
| `scripts/check-build-config.py --release` | PASS |
| `tests.test_project` | PASS，15 个测试方法逐项执行（分批运行） |
| `tests.test_vpn_architecture` | PASS，4 tests |
| `tests.test_linker_diagnostics` | PASS，2 tests |
| `tests.test_build_outputs` | PASS，3 tests |
| `tests.test_packaging` | PASS，6 tests |
| 关键治理回归 | PASS，3 项单独通过；第 4 项在当前执行时限内未完成 |
| Repository Structure | PASS，write + check |
| Source Manifest | PASS，write + check |
| `scripts/check-governance.py --scope development` | PASS |
| `scripts/dev-session.py validate` | PASS |
| `scripts/build-release.py`（干净副本） | PASS；生成 v0.1.2 source ZIP |
| ZIP / SHA-256 / 私钥扫描 | PASS；ZIP CRC 完整，未发现 P12 / PFX / KEY / PEM / Provisioning Profile |

说明：Python 进程启动时会打印文件生成环境的 Spreadsheet warmup 诊断信息，但上表标记 PASS 的命令均以 exit code 0 完成。治理测试未完成的项目不计为通过。

## 故障与修复

用户提供的 GitHub Actions 日志：
`No files were found with the provided path: build/ci/Clash_Mac_Compile-v0.1.1-macos-arm64-unsigned.zip ...`

该日志只证明 Artifact 上传器没有找到指定路径，不能单独证明 Xcode 编译成功或失败。

v0.1.2 修复：
1. `build-macos-app.sh` 将 `--output` 规范化为绝对路径，并打印实际目录。
2. 构建成功后验证 APP ZIP、BUILD-METADATA、VPN 架构报告和 SHA256SUMS 均存在且非空。
3. 生成 `BUILD-OUTPUT-MANIFEST.json`，记录版本、分发模式和 APP ZIP 名称。
4. 新增 `verify-build-outputs.py`，在 Build / Release / Weekly 上传或附件之前验证文件、版本、分发模式和 ZIP 文件名。
5. Build workflow 改为上传单一路径 `build/ci/`，不再分别列出多个精确路径。
6. Build / Release / Weekly 显式设置 `CLASH_SIGNING_MODE=unsigned`，固定 ZIP 文件名。
7. Release attachment 验证并上传 `BUILD-OUTPUT-MANIFEST.json`。

## 尚未执行 / 未验证

- GitHub `xcode-27` Runner 的真实 v0.1.2 Xcode 编译。
- GitHub Actions Artifact 在线上传和下载。
- APP 中 System Extension 的真实嵌入和签名验证。
- Apple Developer ID / Network Extension entitlement / provisioning profile / notarization。
- macOS 15.7.7 System Extension 激活和 VPN 配置授权。
- 性能基准。

## 结论

本版增加构建输出清单、上传前校验和单目录 Artifact 上传，以消除多条精确文件路径不一致的脆弱性。真实 GitHub Runner 是否生成 APP ZIP 并成功上传，仍需用户上传后验证。
