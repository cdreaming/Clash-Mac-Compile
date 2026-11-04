# Clash_Mac_Compile v0.0.7 Development Journal

<!-- DEVELOPMENT-SESSION-STATUS: complete -->
<!-- DEVELOPMENT-LAST-CHECKPOINT: CP-003 -->
<!-- DEVELOPMENT-COMPLETION-SOURCE: user-request -->

## 本版目标

根据用户没有 Apple Developer / Developer ID 证书的情况，移除签名、公证和 Provisioning Profile 相关设置，保持无签名 arm64 自动编译和 GitHub Releases 发布。

## 已完成

- 构建脚本统一为 `CODE_SIGNING_ALLOWED=NO`。
- 移除证书导入、Provisioning Profile、签名校验、公证和临时 keychain 清理脚本。
- Release 和 Weekly Preview 不再读取任何 Apple Developer Secrets。
- APP ZIP 文件名增加 `-unsigned`。
- 构建元数据标记 `distribution_mode=unsigned` 和 `vpn_authorization_supported=false`。
- Release 附加脚本接受无签名 APP，并将 VPN 限制写入 `RELEASE-MANIFEST.json`。
- Releases 下载说明明确列出无签名状态和 VPN / Packet Tunnel 限制。
- 保留 Swift `-O`、arm64、最多 2 个 Xcode 并行任务、每周上游检查、自动版本、Tag 和 Pre-release。

## 已知限制

无签名 APP 的 GUI 是否启动取决于 macOS 安全策略；无签名构建不能保证 Network Extension / Packet Tunnel VPN 系统授权成功。
