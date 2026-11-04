# Clash_Mac_Compile v0.0.6 Validation Report

## 本地验证环境

- Python 3.13。
- 当前执行环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户，未触发云端 Xcode 构建或 Release 发布。

## 本地验证环境与实际结果

- Python 3.13。
- 当前执行环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户，未触发云端 Xcode 构建或 Release 发布。

| 检查 | 实际结果 |
|---|---|
| `python3 -m py_compile scripts/*.py tests/*.py` | PASS |
| `bash -n scripts/build-macos-app.sh` | PASS |
| `python3 scripts/check-build-config.py --release` | PASS；上游 Ref 为完整 40 位 SHA |
| CI / Build / Release / Weekly workflow YAML | PASS；4 个 workflow 可解析 |
| `python3 scripts/update-repository-structure.py --check` | PASS |
| `python3 scripts/build-source-manifest.py --check` | PASS |
| `python3 -m unittest -q tests.test_governance` | PASS；10 tests |
| `python3 -m unittest -q tests.test_project` | PASS；9 tests |
| `python3 -m unittest -q tests.test_packaging` | PASS；6 tests |
| `python3 scripts/build-release.py` | PASS；生成 v0.0.6 源码 ZIP |
| ZIP 完整性与打包回归 | PASS |

本地测试使用当前项目源码执行；测试通过不代表 GitHub macOS Runner 已完成 Xcode 构建。

## 重发布治理修复

- `dev-session.py` 自动兼容缺少 `## 完成摘要` 的旧日志。
- `dev-session.py validate` 在重发布前修复并验证开发日志结构。
- `prepare-republish.py` 在任何 Checklist / RELEASE_REVISION / REPUBLISH-HISTORY 写入前先运行预检。
- `tests.test_governance` 覆盖缺少完成摘要的旧日志，以及日志文件缺失时不得半更新 Release 状态。
- 每周自动生成的开发日志包含完成摘要章节。

## 无签名构建策略

- Build / Release / Weekly Preview 均使用 `CODE_SIGNING_ALLOWED=NO`。
- 不需要 Apple Developer Program、Developer ID 证书、Provisioning Profile 或 Notary API Key。
- APP ZIP 名称包含 `-unsigned`。
- 构建元数据标记 `signing=disabled`、`distribution_mode=unsigned`、`vpn_authorization_supported=false`。
- 无签名版本不承诺 VPN / Packet Tunnel 系统授权。

## 尚未执行 / 未验证

- GitHub `xcode-27` Runner 的真实 Xcode 编译。
- macOS 目标机器上无签名 APP 是否能够启动。
- VPN 配置授权和 Packet Tunnel：本版本不支持，不作为验收目标。
- Instruments / Go pprof 的真实运行性能基准。
- GitHub Releases 在线资产上传、下载和 SHA-256 复核。
- 每周 schedule 在用户 GitHub 仓库中的真实触发与自动发布。

## 结论

本地治理测试和源码检查通过后，可交付 v0.0.6 源码包。云端编译及 Release 发布以 GitHub Actions 实际结果为准。
