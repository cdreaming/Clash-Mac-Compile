# Clash_Mac_Compile v0.0.9 Validation Report

## 验证环境

- Python 3.13。
- 当前源码制作环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户，未触发远端 Xcode 构建或 Release 发布。

## 实际执行并通过

| 检查 | 结果 |
|---|---|
| Python scripts / tests 语法检查 | PASS |
| Build / local wrapper / identity / signature verifier Shell 语法 | PASS |
| Build config 与 Release immutable SHA gate | PASS |
| CI / Build / Release / Weekly workflow YAML | PASS |
| Repository Structure 与 Source Manifest | PASS |
| `tests.test_project` 的 15 个测试方法逐项运行 | PASS，15/15 |
| `tests.test_packaging` | PASS，6/6 |
| 关键治理回归 | PASS，4 项（development governance、structure current、revision republish、preflight atomicity） |
| metadata writer 专项 | PASS；执行真实嵌入式 writer 后严格解析 JSON |
| Release JSON 错误诊断专项 | PASS；无效 JSON 显示文件路径、行列和字符位置 |
| `scripts/build-release.py` | PASS；生成 v0.0.9 源码 ZIP |
| ZIP CRC / SHA-256 / 私钥文件审计 | PASS |

说明：`tests.test_project` 的 15 个测试方法分别执行均通过；整套命令一次性运行超过当前工具的单次执行时限，因此没有将整套单次运行记为通过。

## 故障根因与修复

GitHub 日志：
`Attach release assets failed: Extra data: line 40 column 2 (char 1638)`

根因：
- `scripts/build-macos-app.sh` 中的 metadata writer 曾使用 `json.dumps(...) + "\\\\n"`。
- 这会把字面量反斜杠和 n 写到 JSON 文件末尾，而不是写入换行符。
- `json.loads` 正常解析完 JSON 对象后，把尾部字符视为额外数据并抛出 `JSONDecodeError: Extra data`。

修复：
- 改为 `json.dumps(...) + "\\n"`，写入真实换行。
- Xcode 版本字段将实际换行转换为 ` / `。
- `attach-release-assets.py` 增加 JSON 文件名、行、列和字符位置的错误诊断。
- 回归测试执行构建脚本内的真实 metadata writer，并严格解析生成文件；另测试损坏 JSON 的诊断输出。

## 尚未执行 / 未验证

- GitHub `xcode-27` Runner 的真实 v0.0.9 Xcode 编译。
- GitHub Release workflow 的在线资产上传。
- 用户 Mac 上的 Keychain / Xcode 本地自签名构建。
- Network Extension / Packet Tunnel VPN 系统授权；本地自签名不授予 Apple entitlement。
- Apple 公证与 Gatekeeper 正式分发。
- Instruments / Go pprof 真实性能基准。

## 结论

v0.0.9 已修复 Release 附件阶段 JSON `Extra data` 的确定性源码错误，并通过 metadata writer 严格 JSON 回归。云端 Xcode 构建和 GitHub Release 上传仍须由用户上传后通过 Actions 实际验证。
