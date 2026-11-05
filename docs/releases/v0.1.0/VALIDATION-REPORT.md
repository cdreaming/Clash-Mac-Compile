# Clash_Mac_Compile v0.1.0 Validation Report

## 验证环境

- Python 3.13。
- 当前源码制作环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户，未执行真实 XcodeGen、Xcode 编译或 System Extension 激活。

## 实际执行并通过

| 检查 | 结果 |
|---|---|
| Python scripts / tests 语法检查 | PASS |
| Build / local wrapper / identity / signature verifier Shell 语法 | PASS |
| CI / Build / Release / Weekly workflow YAML | PASS，4 个 workflow |
| Build config 与 Release immutable SHA gate | PASS |
| Repository Structure 检查 | PASS |
| Source Manifest 检查 | PASS |
| `tests.test_project` | PASS，15/15 |
| `tests.test_vpn_architecture` | PASS，4/4 |
| `tests.test_packaging` | PASS，6/6 |
| 关键治理回归 | PASS，4 项 |
| `scripts/check-governance.py --scope development` | PASS |
| `scripts/dev-session.py validate` | PASS |
| `scripts/build-release.py`（干净源码副本） | PASS；生成 v0.1.0 源码 ZIP |
| ZIP / SHA-256 / 私钥文件审计 | PASS；未发现 P12 / PFX / KEY / PEM / Provisioning Profile |

说明：Python 进程启动时会打印当前文件生成环境的 Spreadsheet warmup 诊断信息，但上述测试命令均以 exit code 0 完成。

## 已核对的上游源码事实

固定上游 commit：`e3e647283b1593a61dba622f13cd499deeda9b8b`。

该提交的 `apple/ClashClient/project.yml` 中：
- `ClashmacOSExtension` 原类型为 `app-extension`。
- provider bundle ID 为 `$(CLASH_BUNDLE_BASE).packet-tunnel`。
- extension point 为 `com.apple.networkextension.packet-tunnel`。
- 主 APP 与 provider 原先使用 `packet-tunnel-provider` entitlement。
- 主 APP 原本已 embed `ClashmacOSExtension` target。
- `Sources/VPNStartAuthorization.swift` 的 `perform` 方法在 `IPStackProfileWriter.awaitConfirmation(operation: save, ...)` 中执行原有 VPN preference 保存确认。

本版构建补丁将上述 macOS target 迁移为 `system-extension`，保持 provider Bundle ID 和 App Group 关系，更新 entitlement，并在原有 VPN preference 保存之前增加系统扩展激活请求。

## System Extension 迁移内容

- XcodeGen target 类型：`system-extension`。
- provider entitlement：`packet-tunnel-provider-systemextension`。
- host app entitlement：`com.apple.developer.system-extension.install=true`。
- host app 链接 `SystemExtensions.framework`。
- host app 显式 embed provider target。
- App 与 provider 的 App Groups 必须有交集。
- `VPNStartAuthorization.perform` 在保存 VPN 配置前调用 `OSSystemExtensionRequest.activationRequest`。
- 系统要求用户批准时，激活请求保持等待；完成后才继续原有 VPN 配置保存。
- 构建后检查 `Contents/Library/SystemExtensions`、Bundle ID、签名、Entitlements、App Groups 和 Apple 授权状态。
- Build / Release / Weekly 上传 `VPN-ARCHITECTURE-REPORT.json`。

## 授权边界

- GitHub Actions 构建仍为 unsigned。
- 本地示例 P12 是自签名证书，没有 Apple Team ID。
- 自签名不授予 Apple Network Extension / System Extension entitlement。
- 没有 Apple Developer ID、Apple 授权的 entitlement / provisioning profile 和公证，macOS 仍可能拒绝激活 System Extension。
- 本地结构测试通过不代表真实 XcodeGen / Xcode 构建或 VPN 授权成功。

## 尚未执行 / 未验证

- GitHub `xcode-27` Runner 的真实 v0.1.0 Xcode 编译。
- XcodeGen 对上游真实 `project.yml` 的实际 System Extension target 生成。
- APP 中 `.systemextension` 的真实嵌入位置和签名验证。
- Apple Developer ID、Network Extension entitlement、Provisioning Profile 和 Notarization。
- macOS 15.7.7 上 System Extension 用户批准和 VPN 配置弹窗。
- Instruments / Go pprof 真实性能基准。
- GitHub Releases 在线资产上传和下载。

## 结论

v0.1.0 已完成源码级 System Extension 迁移补丁、VPN 启动激活接线、架构审计和回归测试。当前没有 Apple Developer 授权，因此不能宣称 VPN 已可用。云端 Xcode 构建和实际 macOS 系统授权必须在后续真实环境验证。
