# Build Information

- 项目名称：Clash_Mac_Compile
- 项目版本：以根目录 `VERSION` 为准（当前版本 `0.0.9`）
- 治理模板版本：`1.1.1`
- GitHub 仓库：`cdreaming/Clash-Mac-Compile`
- 目标平台：macOS
- 上游客户端：`ProjectClash/Clash-Client`
- 上游客户端 Ref：`e3e647283b1593a61dba622f13cd499deeda9b8b`
- Go 工具链：GitHub Actions 安装 `1.26.10`，构建脚本启用 `GOTOOLCHAIN=auto`
- Xcode Scheme：`ClashmacOS`
- 构建配置：Release
- Swift 优化级别：`-O`（运行速度优先）
- Xcode 并行编译任务：最多 2
- 目标架构：`arm64`（Apple Silicon only）

## 构建模式

- GitHub Build / Release / Weekly Preview：默认无签名，不需要 Apple Developer Secrets。
- 本地开发：可选 `local-self-signed`，使用开发者 Mac Keychain 中的 `Clash_Mac_Compile Local Development` identity。
- 本地自签名产物只用于开发测试，不上传 GitHub Releases。
- 自签名不提供 Apple Team ID、Apple 授权 entitlement、公证或 VPN / Packet Tunnel 授权。

## v0.0.9 Release 修复

`BUILD-METADATA.json` 写入真实换行；Release 资产脚本严格解析 JSON 并报告具体错误位置。新增实际执行 metadata writer 的回归测试，防止 `JSONDecodeError: Extra data` 重现。

## 构建入口

- Push / Pull Request / 手动构建：`.github/workflows/build-macos.yml`
- Tag Release：`.github/workflows/release.yml`
- 每周上游检查与自动 Preview：`.github/workflows/upstream-weekly.yml`
- GitHub 无签名构建：`scripts/build-macos-app.sh --output build/ci`
- 本地自签名构建：`scripts/build-local-signed-app.sh --output build/local-signed`

## 构建产物

- `Clash_Mac_Compile-vX.Y.Z-macos-arm64-unsigned.zip`：GitHub Build / Release
- `Clash_Mac_Compile-vX.Y.Z-macos-arm64-local-signed.zip`：本机开发测试
- `Clash_Mac_Compile_vX.Y.Z_source.zip`：完整源码
- `BUILD-METADATA.json`
- `LOCAL-SIGNING-REPORT.json`：本地签名模式

## 安全

本地 `.p12`、`.pfx`、私钥和 Provisioning Profile 不得提交到仓库。源码打包会拒绝这些敏感文件。不要把本地自签名 ZIP 当作正式 VPN 安装包。
