# Clash_Mac_Compile v0.0.2 Release Notes

## 发布摘要

v0.0.2 修复 v0.0.1 正式发布流程的上游版本可复现性阻断，固定官方 Clash-Client 源码提交，并同步其 Go 工具链要求。

## 用户可见变化

- `UPSTREAM_CLIENT_REF` 固定为 `e3e647283b1593a61dba622f13cd499deeda9b8b`。
- Clash-Client 依赖的 Kernel 与 Adapter 继续由该提交的 `Dependencies.lock.json` 锁定。
- GitHub Actions Build 与 Release 均使用 Go 1.26.10。
- 正式 Release 保留完整 40 位 SHA 校验；不再因为 `main` 是可移动分支而在 0 秒失败。
- 更新 Sourcetree 上传、上游升级和版本管理说明。

## 兼容性与迁移

从 v0.0.1 升级时，直接使用本版完整源码包覆盖/替换本地项目文件时，应保留 Git 仓库历史；建议将 v0.0.2 作为新提交推送到 `main`，然后创建 `v0.0.2` 标签。

## 已知边界

- 首版仍是无签名构建，不保证 Gatekeeper、公证、Network Extension 安装或 VPN 实机行为。
- GitHub macOS Runner 的 Xcode 构建尚未在本地执行，需用户推送后由 GitHub Actions 验证。
- `xcode-27` Runner 可用性以 GitHub 官方镜像状态为准。

## 发布资产

- `clash-mac-compile-v0.0.2-source.zip`
- `Clash_Mac_Compile-v0.0.2-macos-universal.zip`（由 GitHub macOS Runner 生成）
- `BUILD-METADATA.json`
- `SHA256SUMS.txt`
