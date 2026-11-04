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