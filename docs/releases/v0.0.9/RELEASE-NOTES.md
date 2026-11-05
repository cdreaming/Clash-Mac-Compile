# Clash_Mac_Compile v0.0.9 · Release 元数据 JSON 修复版

## 发布摘要

v0.0.9 修复 v0.0.8 在 GitHub Actions 的 APP 编译成功后，`Attach macOS app and build metadata` 阶段因 `BUILD-METADATA.json` 尾部出现字面量 `\\n` 而解析失败的问题。

## 本版主要变化

- 修复 `scripts/build-macos-app.sh` 的 metadata writer：JSON 序列化结果后写入真实换行，而不是字面量反斜杠和 n。
- 修复 Xcode 版本信息格式化：将实际换行转换为 ` / `。
- `scripts/attach-release-assets.py` 对 BUILD-METADATA / RELEASE-MANIFEST 使用统一 JSON loader；遇到格式错误时显示文件路径、错误行、列和字符位置。
- 新增回归测试，直接执行构建脚本内嵌的 metadata writer，再使用 `json.loads` 验证输出。
- 新增无效 metadata JSON 的错误定位测试。
- 保留 v0.0.8 本地自签名开发模式；GitHub Build / Release / Weekly 仍保持无签名。
- 本地 P12 / 私钥继续禁止进入 Git 和源码 ZIP。

## 构建配置

- Apple Silicon `arm64`。
- Swift Release 优化 `-O`。
- Xcode 并行任务默认 2。
- GitHub Actions 继续生成无签名 APP。
- 本地开发仍可选择 `scripts/build-local-signed-app.sh`，仅用于本地签名流程测试。

## 下载资产

| 文件 | 用途 |
|---|---|
| `Clash_Mac_Compile-v0.0.9-macos-arm64-unsigned.zip` | GitHub Actions 编译的 macOS APP |
| `Clash_Mac_Compile_v0.0.9_source.zip` | 完整构建工程源码 |
| `BUILD-METADATA.json` | 上游 SHA 与构建环境 |
| `SHA256SUMS.txt` | 下载文件校验 |
| `RELEASE-MANIFEST.json` | Release 资产清单 |

## VPN 与签名限制

本版没有 Apple Developer ID、Apple Team ID、Apple 授权 Provisioning Profile 或 Notary。自签名只用于本地代码签名开发测试，不授予 Network Extension / Packet Tunnel / System Extension 权限。不能将本地自签名结果视为 VPN 授权成功。

## 许可证

本项目使用 ProjectClash 上游客户端、Clash Kernel 与 Adapter。分发时请保留版权和许可证声明，并遵守 GPL-3.0 及第三方依赖许可。
