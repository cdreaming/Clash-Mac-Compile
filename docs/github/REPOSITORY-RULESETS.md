# Repository Rulesets

## 单人 Sourcetree 模式

为保留 Sourcetree 直接 Push `main`：

- 禁止 force push；
- 禁止删除；
- 限制 push 角色为维护者；
- 不强制 PR；
- Push 后由 `Quality Gate` 验证。

硬门禁重点放在本地 candidate gate 与 tag Release gate，避免“CI 还没运行就不允许第一次 direct push”的循环。

## 严格团队模式

团队项目建议：

- main 必须 PR；
- require status checks；
- 要求 `Quality Gate`；
- require branch up to date；
- 禁止 force push/delete；
- 可加 review、signed commits、code scanning。

Required status check 的 job 名要唯一稳定。

## Release

tag `v*` 应限制创建/更新/删除。若 GitHub 支持，建议启用 immutable releases；正式发布按 draft → 上传全部资产 → publish。

## Actions

CI 使用 `contents: read`；Release 仅按需要用 `contents: write`。高安全仓库应把 Action 固定到完整 commit SHA。
