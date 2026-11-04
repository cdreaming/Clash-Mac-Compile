# Clash_Mac_Compile v0.0.3 Release Notes

## 发布摘要

v0.0.3 针对 v0.0.2 云端构建在 SwiftCompile 阶段长时间运行后被取消的问题，先将目标收敛为 Apple Silicon arm64，并降低 Xcode 并行编译压力。

## 用户可见变化

- 只构建 Apple Silicon `arm64`，暂不生成 Intel `x86_64` 版本。
- Xcode 并行任务最多 2 个，默认 `CLASH_BUILD_JOBS=2`。
- 使用 `ONLY_ACTIVE_ARCH=YES`，构建后检查主程序 arm64 架构。
- Build workflow 不再自动取消同一分支上已运行的构建。
- Build / Release workflow 超时提高至 240 分钟。
- 增加 Runner CPU / 内存诊断和 Xcode 构建耗时摘要。
- Release 资产命名改为 `macos-arm64`。

## 保持不变

- 官方 Client commit：`e3e647283b1593a61dba622f13cd499deeda9b8b`。
- Go 工具链：1.26.10。
- Kernel / Adapter 版本仍由该 Client commit 的 `Dependencies.lock.json` 锁定。
- Swift 并发检查和编译错误保持启用。

## 已知边界

- 这些调整是资源优化措施，不保证必然解决所有 Runner 取消问题。
- GitHub macOS Runner 的真实 Xcode 构建尚未执行。
- 首版仍为无签名构建，不代表可直接安装或启用 Network Extension / VPN。
- Intel Mac 不在本版支持范围内。

## 发布资产

- `clash-mac-compile-v0.0.3-source.zip`
- `Clash_Mac_Compile-v0.0.3-macos-arm64.zip`（由 GitHub macOS Runner 生成）
- `BUILD-METADATA.json`
- `SHA256SUMS.txt`
