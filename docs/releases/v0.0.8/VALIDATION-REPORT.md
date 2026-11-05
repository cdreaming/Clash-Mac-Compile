# Clash_Mac_Compile v0.0.8 Validation Report

## 验证环境

- Python 3.13。
- 当前源码制作环境不是 macOS / Xcode / Keychain。
- 未访问用户 GitHub 账户，未触发 GitHub macOS Runner 构建。

## 已真实执行并通过

| 检查 | 结果 |
|---|---|
| Python scripts / tests 语法检查 | PASS |
| `bash -n scripts/build-macos-app.sh` | PASS |
| `bash -n scripts/build-local-signed-app.sh` | PASS |
| `bash -n scripts/check-local-signing-identity.sh` | PASS |
| `bash -n scripts/verify-local-signed-app.sh` | PASS |
| `python3 scripts/check-build-config.py` | PASS |
| `python3 scripts/check-build-config.py --release` | PASS；上游 Ref 为完整 40 位 SHA |
| CI / Build / Release / Weekly workflow YAML | PASS，4 个 workflow |
| Repository Structure 检查 | PASS |
| Source Manifest 检查 | PASS |
| `python3 -m unittest -q tests.test_project` | PASS，13 tests |
| `python3 -m unittest -q tests.test_packaging` | PASS，6 tests |
| 关键治理回归测试 | PASS，4 项（development governance、structure current、revision republish、preflight atomicity） |
| `python3 scripts/dev-session.py validate` | PASS |
| `python3 scripts/build-release.py` | PASS；生成 v0.0.8 source ZIP |
| ZIP CRC / SHA-256 / 敏感私钥文件扫描 | PASS；未发现 P12 / PFX / KEY / PEM / Provisioning Profile |

关键治理回归测试包括：开发治理、Repository Structure、已发布版本 revision 重发布、缺少开发日志时预检不得半更新状态。完整 `tests.test_governance` 套件在当前执行环境超过 60 秒限制，未标记为通过。

## 本地签名模式

- 默认构建模式仍为 `unsigned`。
- 本地开发可显式调用 `scripts/build-local-signed-app.sh`。
- 本地签名身份从 macOS Keychain 获取，不进入仓库。
- `verify-local-signed-app.sh` 检查主 APP 和嵌套扩展签名。
- `LOCAL-SIGNING-REPORT.json` 明确记录 `apple_developer_identity=false`、`apple_entitlements_authorized=false`、`notarized=false` 和 `network_extension_vpn_authorization_supported=false`。
- GitHub Build / Release / Weekly 不读取本地 Keychain 或 P12。
- Release 资产附加只接受 unsigned APP，拒绝 local-development-only 产物。
- 源码打包拒绝 `.p12`、`.pfx`、`.key`、`.pem`、`.mobileprovision` 和 `.provisionprofile`。

## 尚未执行 / 未验证

- 用户 Mac 上 Keychain 是否识别本地自签名 identity。
- 用户 Mac 上 Xcode 是否能使用该 identity 对主 APP 与嵌套扩展签名。
- 实际 APP 的 codesign 输出和 `LOCAL-SIGNING-REPORT.json`。
- GitHub `xcode-27` Runner 的真实 arm64 Xcode 构建。
- 无签名 APP 的 Gatekeeper / GUI 启动行为。
- Network Extension / Packet Tunnel VPN 系统授权：本地自签名不授予 Apple entitlement，不作为验收目标。
- Apple 公证：本版不配置。
- Instruments / Go pprof 真实性能基准。
- GitHub Releases 在线资产上传、下载和 SHA-256 复核。

## 重要架构边界

当前锁定的 ProjectClash Client XcodeGen 工程将 `ClashmacOSExtension` 声明为 `app-extension`，并使用 `packet-tunnel-provider` entitlement。本版没有擅自改写上游为 System Extension。自签名证书不授予该 entitlement，也不能证明 macOS 会显示 VPN 授权弹窗。

## 性能边界

Swift `-O` 是运行速度优先的编译策略，不等于已经实测性能提升。CPU、内存、启动、网络和 UI 流畅度仍需在目标 Mac 使用 Instruments / Go pprof 测量。

## 结论

v0.0.8 本地签名开发路径、GitHub 无签名隔离和敏感私钥保护已通过源码级测试。用户 Mac 上的实际 Xcode / Keychain 签名仍需在 macOS 实机验证；VPN 系统授权不能由本地自签名获得。
