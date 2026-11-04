# GitHub Actions 与 Sourcetree 操作

## 首次上传

1. 解压交付给你的 `Clash_Mac_Compile-vX.Y.Z-source.zip`。
2. 用 Sourcetree 添加解压目录为本地仓库。
3. 将远端设为 `https://github.com/cdreaming/Clash-Mac-Compile.git`。
4. 推送 `main` 分支。
5. 在 GitHub 仓库 Settings → Actions → General 中确认允许运行 GitHub Actions。
6. 打开 Actions → `Build macOS App`，检查运行结果。

如果远端仓库不是空仓库，请先在 Sourcetree 解决本地与远端提交历史，不要强制覆盖。

## 自动构建触发条件

- Push 到 `main`。
- Pull Request 指向 `main`。
- Actions 页面手动执行 `Build macOS App`。

## 下载编译产物

打开成功的 workflow run，在页面底部 Artifacts 下载：

- `Clash_Mac_Compile-vX.Y.Z-macos-arm64.zip`
- `BUILD-METADATA.json`

Artifact 默认保留 14 天。需要长期保存时，创建正式 Release。

## 正式 Release 前的上游锁定

本版已将 `UPSTREAM_CLIENT_REF` 固定为完整 40 位 SHA。未来升级上游时，先完成一次 main 构建并审查 `BUILD-METADATA.json`，再把新 SHA 固定到文件，提升项目版本并提交。

## Runner 与费用

`xcode-27` 是 GitHub macOS Runner 镜像的预览标签。macOS Runner 可能消耗 GitHub Actions 分钟或产生额外计费，请在 GitHub Billing / Actions 页面确认账户额度与费用。

## v0.0.3 构建资源策略

v0.0.3 只生成 Apple Silicon arm64 APP。Xcode 并行任务数默认为 2，构建工作流不再自动取消同一分支上正在执行的任务，超时设为 240 分钟。

## Weekly Upstream Preview

`.github/workflows/upstream-weekly.yml` 每周一 09:17（America/Los_Angeles）检查官方 Client `main`。没有变化时只运行轻量检查；发现新 SHA 后才启动 macOS Runner，自动提升 Patch 版本、构建 APP、提交 main、创建 tag 并发布 Pre-release。

手动运行：Actions → Weekly Upstream Check and Preview Release → Run workflow。`force_rebuild` 仅用于明确要求在上游 SHA 不变时重新构建并产生新 Patch 版本。

## GitHub 权限设置

自动周度发布使用本仓库 `GITHUB_TOKEN`，只需要 `contents: write`。请检查 Settings → Actions → General → Workflow permissions，允许 Actions 读写仓库内容。

如果 `main` 分支启用了禁止机器人直接推送的 branch protection / ruleset，周度工作流会在 push 阶段失败，不会创建 Release。请允许 `github-actions[bot]` 写入，或后续将自动发布改为 PR 审核模式。

## Releases 页面下载

正式和 Weekly Preview 均在：

<https://github.com/cdreaming/Clash-Mac-Compile/releases>

Release 说明区会解释 APP ZIP、源码 ZIP、构建元数据、SHA-256、架构、安装方式、配置目录和无签名限制。周度自动版本为 Pre-release；Stable 由维护者确认后发布。
