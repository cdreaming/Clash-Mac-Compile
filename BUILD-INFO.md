# Build Information

- 项目名称：Clash_Mac_Compile
- 项目版本：以根目录 `VERSION` 为准（当前版本 `0.0.7`）
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
- 架构检查：`lipo -archs`（兼容 Xcode 27）
- Build / Release / Weekly Preview：统一无签名构建（`CODE_SIGNING_ALLOWED=NO`）；不需要 Apple Developer Secrets；Packet Tunnel / VPN 系统授权不可用

## 构建入口

- Push / Pull Request / 手动构建：`.github/workflows/build-macos.yml`
- Tag Release：`.github/workflows/release.yml`
- 每周上游检查与自动 Preview：`.github/workflows/upstream-weekly.yml`
- macOS 构建脚本：`scripts/build-macos-app.sh`

## 版本与复现

`VERSION` 管理本项目版本；`UPSTREAM_CLIENT_REF` 管理上游 Client 源码引用。正式 Release 必须将上游引用固定为完整 40 位 commit SHA。Client 内部通过 `Dependencies.lock.json` 固定 Clash Kernel 与 Clash Adapter。

## 构建产物

- `Clash_Mac_Compile-vX.Y.Z-macos-arm64-unsigned.zip`
- `Clash_Mac_Compile_vX.Y.Z_source.zip`
- `BUILD-METADATA.json`
- ``（Release / Weekly Preview）

GitHub Actions Artifact 默认保留 14 天。正式 Release 资产由 Release workflow 长期保存在 GitHub Release 中。

## 无签名构建限制\n\n本项目不导入证书、不使用 provisioning profile、不调用 Apple Notary Service。无签名 APP 仅作为 macOS 编译产物分发；Network Extension / Packet Tunnel 的系统 VPN 授权不能保证成功。\n