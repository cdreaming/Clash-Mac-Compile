# Clash_Mac_Compile v0.1.1 Validation Report

## 验证环境

- Python 3.13。
- 当前源码制作环境不是 macOS / Xcode Runner。
- 未访问用户 GitHub 账户，未执行真实 Xcode Link。

## 已执行并通过

| 检查 | 结果 |
|---|---|
| Python scripts / tests 语法检查 | PASS |
| Build / local wrapper / identity / signature verifier Shell 语法 | PASS |
| CI / Build / Release / Weekly workflow YAML | PASS |
| `scripts/check-build-config.py --release` | PASS |
| `tests.test_project` | PASS，15 tests |
| `tests.test_vpn_architecture` | PASS，4 tests |
| `tests.test_linker_diagnostics` | PASS，2 tests |
| `tests.test_packaging` | PASS，6 tests |
| 关键治理回归 | PASS，4 项 |
| Repository Structure / Source Manifest | PASS，已更新并通过 check |
| `scripts/build-release.py`（干净源码副本） | PASS；最终生成 v0.1.1 source ZIP |
| ZIP / SHA-256 / 私钥审计 | PASS；最终源码 ZIP 完整性和敏感文件扫描通过 |

说明：完整 `tests.test_governance` 套件在当前工具执行时限内未完成；实际单独通过的四项关键治理测试已列出，不将整个治理套件标记为通过。Python 启动时会打印文件生成环境的 Spreadsheet warmup 诊断信息，但上述通过的命令均以 exit code 0 完成。

## 依赖修正

固定上游 Client commit：`e3e647283b1593a61dba622f13cd499deeda9b8b`。

上游 `ClashmacOSExtension` 原先：
- target 类型为 `app-extension`。
- 依赖 `ClashMacCore`，但 `embed: false`。
- 使用旧 App Extension bundle layout 的 Framework runpath：
  - `@executable_path/../Frameworks`
  - `@executable_path/../../../../Frameworks`

迁移到 System Extension 后，本版：
- 将 provider 对 `ClashMacCore` 的依赖设置为 `embed: true`。
- 将 provider runpath 统一设置为 `@executable_path/../Frameworks`，指向扩展自身 `Contents/Frameworks`。
- 保留 host app 对 ClashMacCore 的原有嵌入。
- VPN architecture audit 检查 provider 内嵌 framework 和 runpath。

## Linker 诊断改进

`build-macos-app.sh` 使用 `xcodebuild -verbose` 并通过 `tee` 保存完整日志。失败时：
- 保留 `XCODEBUILD.log`。
- 生成 `LINKER-DIAGNOSTICS.txt`。
- 保存 `XCODEBUILD-EXIT-CODE.txt`。
- 查询 `ClashmacOSExtension` 的 `-showBuildSettings -json`。
- 保存补丁后的 `ClashClient-project.system-extension.yml`。

Build / Release / Weekly workflow 均在 `if: always()` 下上传上述诊断 Artifact。

## 尚未执行 / 未验证

- GitHub `xcode-27` Runner 的真实 v0.1.1 System Extension Link。
- v0.1.0 的具体 `ld:` / undefined-symbol 根因（用户尚未提供完整 Linker 日志）。
- 用户 Mac 上 XcodeGen / Xcode 实际构建。
- APP 中 System Extension / ClashMacCore framework 的真实嵌入与签名验证。
- Apple Developer ID、授权 Network Extension entitlement、Provisioning Profile 和 Notarization。
- macOS System Extension 激活和 VPN 配置弹窗。
- Instruments / Go pprof 真实性能基准。

## 结论

v0.1.1 已通过源码级 framework embed/runpath、架构审计、Linker 日志解析和失败 Artifact 上传测试。真实 Xcode Link 是否成功必须由 GitHub macOS Runner 验证；如果仍失败，本版会保留完整 `ld` 命令、错误行和目标 Build Settings，供下一轮精确修复。
