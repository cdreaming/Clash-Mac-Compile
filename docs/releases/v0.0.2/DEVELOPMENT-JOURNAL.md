# Clash_Mac_Compile v0.0.2 Development Journal

<!-- DEVELOPMENT-SESSION-STATUS: complete -->
<!-- DEVELOPMENT-LAST-CHECKPOINT: CP-003 -->
<!-- DEVELOPMENT-COMPLETION-SOURCE: ai-delivery -->

## 当前目标

修复 v0.0.1 正式 Release 因 `UPSTREAM_CLIENT_REF=main` 被安全检查拦截的问题，并交付可复现的 v0.0.2 源码工程。

## 上游版本锁定

- Client repository: https://github.com/ProjectClash/Clash-Client
- Client commit: `e3e647283b1593a61dba622f13cd499deeda9b8b`
- Commit date: 2026-10-28
- Kernel / Adapter revisions: 由该 Client commit 的 `Dependencies.lock.json` 固定。
- Go toolchain: 1.26.10。

## 检查点

### CP-001 · 定位 v0.0.1 Release 阻断

- 原因：`UPSTREAM_CLIENT_REF` 为可移动分支 `main`。
- 决策：保留 `check-build-config.py --release` 安全门禁，不删除检查。

### CP-002 · 固定上游与升级版本

- 项目版本升级至 `0.0.2`。
- `UPSTREAM_CLIENT_REF` 更新为上述 40 位官方 Client commit。
- Build / Release workflow 的 Go 版本更新为 1.26.10。
- 更新 README、Build Info、上游构建文档和变更记录。

### CP-003 · 本地验证与交付

- 运行项目配置、Release SHA、Python/Shell/YAML、项目测试、Candidate Gate 和源码打包检查。
- GitHub macOS Runner 的真实 Xcode 构建尚待用户推送后执行。

## 完成摘要

v0.0.2 源码工程已完成并通过本地 Candidate Gate。此状态不代表 GitHub Actions 已经成功编译 APP，也不代表 Release 已发布。
