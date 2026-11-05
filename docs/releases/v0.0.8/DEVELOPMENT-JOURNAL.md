# Clash_Mac_Compile v0.0.8 Development Journal

<!-- DEVELOPMENT-SESSION-STATUS: complete -->
<!-- DEVELOPMENT-LAST-CHECKPOINT: CP-004 -->
<!-- DEVELOPMENT-COMPLETION-SOURCE: ai-delivery -->

## 当前目标

在保留 GitHub 无签名构建的前提下，增加本地自签名开发模式，使用单独提供的自签名 P12 在开发 Mac 上验证 Xcode 代码签名流程；明确区分本地签名与 Apple Network Extension 授权。

## 已完成

- 版本升级为 v0.0.8。
- 新增本地 Keychain identity 检查脚本。
- 新增本地签名构建 wrapper。
- `build-macos-app.sh` 增加 opt-in local 模式，默认仍为 unsigned。
- 新增主 APP / 嵌套扩展签名校验和 JSON 报告。
- GitHub Build / Release / Weekly workflow 不使用本地证书或私钥。
- Release 资产附加仍只接受 unsigned APP。
- 源码包拒绝 `.p12`、`.pfx`、`.key` 和 Provisioning Profile 等敏感文件。
- 新增本地签名与 Apple entitlement 授权的边界说明。

## 检查点记录

### CP-001 · 本地自签名开发模式

- 已完成：建立本地 Keychain identity 检查、本地签名构建和签名验证脚本；保持 GitHub 无签名发布路径。
- 下一步：执行 Python / Shell / YAML / 项目 / 打包测试；macOS 本机 Xcode 签名实验由用户执行。
- 验证状态：源码级检查待最终验证；当前环境不是 macOS，不能执行 Xcode 或 Keychain 签名。

### CP-002 · 本地签名模式与 GitHub 发布隔离验证

- 时间：2026-11-05 06:08:45 UTC
- 已完成：13 项项目测试、6 项打包测试、4 项关键治理测试通过；Python/Shell/YAML/Build Config/Release SHA 检查通过；本地自签名只在开发 Mac 可选使用，GitHub Releases 继续 unsigned。
- 下一步：上传 v0.0.8 后验证 GitHub macOS Runner；在用户 Mac 导入 P12 后执行本地 Xcode 签名实验。
- 验证状态：源码级测试通过；当前环境非 macOS，Keychain/Xcode 实际签名未执行。

### CP-003 · 自动完成开发阶段

- 时间：2026-11-05 06:09:10 UTC
- 已完成：v0.0.8 本地自签名开发模式、GitHub unsigned 发布隔离、私钥防泄漏和验证文档已完成。13 项项目测试、6 项打包测试及 4 项关键治理测试通过；真实 macOS Keychain/Xcode 签名与 VPN 授权仍待用户 Mac 验证。
- 下一步：进入 candidate gate / 用户本地测试 / GitHub CI
- 验证状态：development gate 已通过

### CP-004 · 最终源码打包与安全检查

- 时间：2026-11-05
- 已完成：v0.0.8 源码 ZIP 已生成；13 项项目测试、6 项打包测试和 4 项关键治理测试通过；源码 ZIP 未包含 P12 / PFX / 私钥 / Provisioning Profile。
- 下一步：上传 Sourcetree 后验证 GitHub arm64 云端编译；在用户 Mac 导入本地证书后执行 Xcode 本地签名实验。
- 验证状态：源码包 ZIP 完整性与 SHA-256 通过；真实 macOS Keychain / Xcode 签名未执行。

## 完成摘要

v0.0.8 本地自签名开发模式、GitHub unsigned 发布隔离、私钥防泄漏和验证文档已完成。13 项项目测试、6 项打包测试及 4 项关键治理测试通过；真实 macOS Keychain/Xcode 签名与 VPN 授权仍待用户 Mac 验证。

完成来源：`ai-delivery`。该状态不等于 GitHub Release 已发布。
