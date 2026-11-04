# Build Information

- 项目名称：Clash_Mac_Compile
- 项目版本：以根目录 `VERSION` 为准（初始版本 `0.0.1`）
- 治理模板版本：`1.1.1`
- GitHub 仓库：`cdreaming/Clash-Mac-Compile`
- 目标平台：macOS
- 上游客户端：`ProjectClash/Clash-Client`
- 上游客户端 Ref：`UPSTREAM_CLIENT_REF`
- Go 工具链：GitHub Actions 安装 stable，`GOTOOLCHAIN=auto` 跟随锁定 Kernel module
- Xcode Scheme：`ClashmacOS`
- 构建配置：Release
- 目标架构：`arm64` + `x86_64`
- 初始签名策略：无签名构建（`CODE_SIGNING_ALLOWED=NO`）

## 构建入口

- Push / Pull Request / 手动构建：`.github/workflows/build-macos.yml`
- Tag Release：`.github/workflows/release.yml`
- macOS 构建脚本：`scripts/build-macos-app.sh`

## 版本与复现

`VERSION` 管理本项目版本；`UPSTREAM_CLIENT_REF` 管理上游 Client 源码引用。正式 Release 必须将上游引用固定为完整 40 位 commit SHA。Client 内部通过 `Dependencies.lock.json` 固定 Clash Kernel 与 Clash Adapter。

## 构建产物

- `Clash_Mac_Compile-vX.Y.Z-macos-universal.zip`
- `BUILD-METADATA.json`

GitHub Actions Artifact 默认保留 14 天。正式 Release 资产由 Release workflow 长期保存在 GitHub Release 中。
