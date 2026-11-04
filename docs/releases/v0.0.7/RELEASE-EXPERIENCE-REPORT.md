# Clash_Mac_Compile v0.0.7 Release Experience Report

用户没有 Apple Developer / Developer ID 证书，因此移除签名、公证和 Provisioning Profile 依赖。

无签名 APP 可以编译并发布，但不能保证 macOS Gatekeeper 允许启动，也不能保证 Network Extension / Packet Tunnel VPN 授权成功。Release 页面和构建元数据必须明确披露这些限制。

保留 Swift `-O`、arm64 单架构、低并行构建、每周上游更新、自动 Patch、Tag 和 GitHub Releases 下载说明。
