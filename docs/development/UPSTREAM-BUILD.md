# ProjectClash 上游构建说明

## 上游仓库关系

| 仓库 | 职责 | 本项目处理方式 |
|---|---|---|
| `ProjectClash/Clash-Client` | Apple 原生应用与扩展 | 构建时检出 `UPSTREAM_CLIENT_REF` |
| `ProjectClash/Clash` | Go 内核和 Apple SDK | 由 Client 的 `Dependencies.lock.json` 锁定 |
| `ProjectClash/Clash-Adapter` | Apple 网络桥接层 | 由 Client 的 `Dependencies.lock.json` 锁定 |

不要直接从三个仓库各自的 `main` 分支拼装依赖。Client 的锁文件是依赖版本事实源。

## 工具链要求

Client README 要求 Go 自动工具链选择，或使用其锁定 Kernel 对应的 Go 版本。当前构建脚本导出 `GOTOOLCHAIN=auto`，GitHub workflow 安装 `stable` Go；进入 Kernel binding module 时，Go 会自动下载并切换到该提交 `go.mod` 的 `toolchain` 指定版本，避免 Client 的 `main` 更新后固定 Go patch 版本过期。

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

## 为什么需要 macOS Runner

原生 APP 使用 Swift、Xcode、macOS SDK、Network Extension 和 Apple 平台 XCFramework。普通 Ubuntu Runner 不能代替完整 Xcode 环境。本项目使用 GitHub 的 `xcode-27` Runner（macOS 27 / Xcode 27）；构建脚本显式请求 `arm64 + x86_64`，并用 `lipo` 验证主程序包含两个架构。该镜像目前属于 Public Preview，可能存在队列或稳定性问题，Runner 可用性以 GitHub 官方镜像状态为准。

## 上游版本策略

`UPSTREAM_CLIENT_REF` 首版为 `main`，适合快速验证流水线。构建元数据会记录实际 SHA。

正式 Release 前必须将其改成完整 40 位 commit SHA。这样相同项目 tag 不会因为上游分支前移而悄悄换用不同源码。Client 依赖的 Kernel 和 Adapter commit 则继续由 `Dependencies.lock.json` 固定。
