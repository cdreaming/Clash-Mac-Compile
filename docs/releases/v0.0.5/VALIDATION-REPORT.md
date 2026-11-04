# Clash_Mac_Compile v0.0.5 Validation Report

## 本地验证环境

- Python 3.13。
- 当前文件生成环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户；未触发远端自动发布。

## 已真实执行并通过

| 检查 | 结果 |
|---|---|
| `python3 -m py_compile scripts/*.py tests/*.py` | PASS |
| `bash -n scripts/build-macos-app.sh` | PASS |
| `bash -n scripts/inspect-macos-data.sh` | v0.0.5 当时通过；脚本在 v0.0.6 已移除 |
| `python3 scripts/check-build-config.py` | PASS |
| `python3 scripts/check-build-config.py --release` | PASS |
| PyYAML 解析 CI / Build / Release / Weekly workflow | PASS，4 个 workflow |
| `python3 scripts/update-repository-structure.py --check` | PASS |
| `python3 scripts/build-source-manifest.py --check` | PASS |
| `python3 -m unittest -q tests.test_project` | PASS，8 tests |
| `python3 scripts/build-release.py` | PASS |
| `python3 -m unittest -q tests.test_packaging` | PASS，6 tests |
| 带模拟 APP ZIP / metadata 的 Release 资产回归 | PASS，6 tests；已附加 APP 资产未被测试删除 |
| 上游 SHA 未变化时的周度检测 | PASS，退出码 10 表示跳过版本递增 |

`tests.test_packaging` 验证源码 ZIP、命名规则、确定性打包、SHA-256、资产清单和无运行时密钥；测试已调整为不删除 Release 中已附加的 APP 资产。Candidate / Release orchestration gate 未完整执行；以上是本轮实际执行的独立检查。

## 性能配置

- Swift Release optimization：`-O`。
- Architecture：arm64。
- Xcode build jobs：最多 2。
- 构建元数据会记录优化级别和性能 profile。

`-O` 是运行速度优先的编译器策略，不等于已经测得性能提升。真实 CPU、内存、启动时间、网络吞吐和 UI 流畅度仍需在目标 Mac 上使用 Instruments / Go pprof 测量。

## 每周自动发布

- 周一 09:17 America/Los_Angeles 检查 Client main。
- 无新 SHA 时跳过构建。
- 有新 SHA 时自动递增 Patch、构建、提交 main、创建 tag 和 Pre-release。
- 该 workflow 已通过 YAML 解析和配置契约检查；尚未在用户 GitHub 仓库真实触发。

## 尚未执行 / 未验证

- GitHub `xcode-27` Runner 上的真实 `SWIFT_OPTIMIZATION_LEVEL=-O` 编译。
- 实际 APP Artifact 和 `lipo -archs` 云端输出。
- 周度 schedule 触发、自动 main push、tag 和 GitHub Pre-release。
- Releases 线上资产下载和校验。
- Apple Developer 签名、公证、Gatekeeper。
- App Groups / Network Extension / Packet Tunnel / VPN 实机运行。
- Instruments / Go pprof 真实运行性能基准。

## 结论

v0.0.5 源码工程通过本地静态检查、8 项项目测试和 6 项打包回归测试，可以交付 Sourcetree 上传。云端 APP 构建、周度自动发布和运行性能提升均须由 GitHub Actions 与目标 Mac 实测确认。
