# Security Policy

## Secret 管理

禁止提交 Apple Developer 证书、私钥、`.p12`、Provisioning Profile、GitHub PAT、`.env`、真实订阅链接、代理配置和用户数据。

## GitHub Actions

- Build / CI workflow 仅授予 `contents: read`。
- Release workflow 才授予 `contents: write`。
- Release 资产不包含签名密钥。
- 对生产使用，建议将第三方 Action 固定到完整 commit SHA，并定期审查供应链。

## 上游源码

- 正式 Release 必须固定 `UPSTREAM_CLIENT_REF` 为 40 位 commit SHA。
- Kernel / Adapter revisions 以 Client 的 `Dependencies.lock.json` 为准。
- 上游源码在临时目录检出和构建，不应将其缓存目录或构建产物提交到本项目。

## 签名

首版禁用代码签名。未来如启用自动签名，只能通过 GitHub Secrets 或受控签名服务注入密钥；日志不得输出证书内容或密码。

## 漏洞报告

请勿在公开 Issue 中提交真实代理订阅、访问令牌、私钥或用户流量日志。


## Weekly release automation

The weekly workflow uses the repository-scoped `GITHUB_TOKEN` with `contents: write` to commit version metadata, create a tag, and publish a GitHub Pre-release. It builds only pinned upstream Client commits and records the actual commit in `BUILD-METADATA.json`.

Do not store a personal access token or Apple signing credential for this workflow. If branch protection blocks `github-actions[bot]` from pushing to `main`, the workflow should fail rather than force-push.
