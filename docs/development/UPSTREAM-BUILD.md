# ProjectClash 上游构建说明

## 上游仓库关系

| 仓库 | 职责 | 本项目处理方式 |
|---|---|---|
| `ProjectClash/Clash-Client` | Apple 原生应用与扩展 | 构建时检出 `UPSTREAM_CLIENT_REF` |
| `ProjectClash/Clash` | Go 内核和 Apple SDK | 由 Client 的 `Dependencies.lock.json` 锁定 |
| `ProjectClash/Clash-Adapter` | Apple 网络桥接层 | 由 Client 的 `Dependencies.lock.json` 锁定 |

不要直接从三个仓库各自的 `main` 分支拼装依赖。Client 的锁文件是依赖版本事实源。

## 工具链要求

Client README 要求 Go 自动工具链选择，或使用其锁定 Kernel 对应的 Go 版本。当前构建脚本导出 `GOTOOLCHAIN=auto`，GitHub workflow 安装该 Client 提交要求的 Go `1.26.10`；构建脚本同时启用 `GOTOOLCHAIN=auto`。

## 官方构建流程

本项目遵循 Client README 的源代码构建步骤：

```bash
python3 -m venv .build/python-env
source .build/python-env/bin/activate
python3 -m pip install PyYAML
python3 scripts/bootstrap.py
python3 scripts/configure.py --bundle-base com.cdreaming.clash
xcodebuild \
  -project apple/ClashClient/ClashClient.xcodeproj \
  -scheme ClashmacOS \
  -configuration Release \
  -destination 'platform=macOS' \
  CODE_SIGNING_ALLOWED=NO \
  build
```

`bootstrap.py` 会检出 Client 锁定的 Kernel / Adapter，安装锁定版本的 gomobile/gobind，并从源码生成五切片 `Clash.xcframework`。`configure.py` 生成 Xcode 工程并构建 macOS CLI helper。

## v0.0.3 低资源构建策略

- 只构建 Apple Silicon `arm64`，不再同时编译 `x86_64`。
- `xcodebuild -jobs 2` 限制同时执行的编译任务数量。
- `ONLY_ACTIVE_ARCH=YES` 只构建当前目标架构。
- Build workflow 不再使用 `cancel-in-progress: true`，避免新提交自动取消正在执行的构建。
- 240 分钟超时为长时间首次构建留出空间。

这些调整旨在降低 Runner 的资源压力；仍需由 GitHub Actions 实际运行结果验证是否解决取消问题。

## 为什么需要 macOS Runner

原生 APP 使用 Swift、Xcode、macOS SDK、Network Extension 和 Apple 平台 XCFramework。普通 Ubuntu Runner 不能代替完整 Xcode 环境。本项目使用 GitHub 的 `xcode-27` Runner（macOS 27 / Xcode 27）；构建脚本显式请求 `arm64 only`，并用 `lipo` 验证主程序包含两个架构。该镜像目前属于 Public Preview，可能存在队列或稳定性问题，Runner 可用性以 GitHub 官方镜像状态为准。

## 上游版本策略

`UPSTREAM_CLIENT_REF` 当前固定为 `e3e647283b1593a61dba622f13cd499deeda9b8b`，来自官方 Client 的 2026-10-28 源码提交。正式 Release 使用完整 40 位 SHA，因此不会因上游 `main` 分支前移而改变本版源码。Client 依赖的 Kernel 和 Adapter commit 则继续由 `Dependencies.lock.json` 固定。


## v0.0.3 架构范围说明

v0.0.3 的 `ClashmacOS` APP / Extension Xcode 构建仅使用 `arm64`，不再对 APP target 编译 `x86_64`。但本项目保留官方 Client 的 `scripts/bootstrap.py` 原样执行：该脚本会调用 Kernel 的 `make lib_apple`，并验证完整五个平台 XCFramework。当前锁定的 Kernel builder 的 macOS SDK slice 仍包含 `macos/arm64` 与 `macos/amd64` 两个内核切片。

因此，v0.0.3 的“arm64-only”指最终 macOS APP 架构，不代表跳过官方 SDK 中其它 Apple 平台或 Kernel 的 macOS amd64 slice。我们不篡改上游 SDK 构建与 provenance 校验，以免产生不完整或无法验证的 XCFramework。<https://github.com/ProjectClash/Clash-Client/blob/e3e647283b1593a61dba622f13cd499deeda9b8b/scripts/bootstrap.py> <https://github.com/ProjectClash/Clash/blob/4b7d5f53cff448f01cd5012b5e3f7eddc7d43e33/cmd/build_libbox/main.go>
