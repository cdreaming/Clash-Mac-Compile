# Clash_Mac_Compile v0.0.1 Release Notes

## 发布摘要

首版建立 ProjectClash 官方 Clash macOS 原生 APP 的 GitHub Actions 自动编译工程。

## 用户可见变化

- 基于官方 `Clash-Client` 原生 macOS Scheme `ClashmacOS`。
- 由官方 Client `Dependencies.lock.json` 锁定 Clash Kernel 与 Adapter。
- GitHub `xcode-27` macOS Runner 自动构建 Release APP。
- 构建目标包含 Apple Silicon arm64 与 Intel x86_64。
- 上传 APP ZIP、上游版本元数据与 SHA-256。
- 增加 Sourcetree 上传说明、项目版本治理和正式 Release 工作流。

## 兼容性与迁移

上游 macOS 部署目标以所锁定 Client 的 `project.yml` 为准；当前官方 Client 声明 macOS 13.0。项目包装版本 `0.0.1` 与官方 APP 的 App Store 版本是两个不同版本体系。

## 已知边界

- 首版产物为无签名编译，不保证 Gatekeeper 放行、正常安装或 VPN / Network Extension 可用。
- 尚未在真实 GitHub macOS Runner 上执行本项目 workflow。
- 尚未在真实 Mac 上安装或验证网络流量。
- `UPSTREAM_CLIENT_REF` 首版使用 `main`；正式 Release 前必须固定完整 commit SHA。

## 发布资产

- `clash-mac-compile-v0.0.1-source.zip`
- `Clash_Mac_Compile-v0.0.1-macos-universal.zip`（由 GitHub macOS Runner 生成）
- `BUILD-METADATA.json`
- `SHA256SUMS.txt`
