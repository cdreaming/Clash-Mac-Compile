# Repository-Level AI Development Rules

本文件是仓库级 AI 开发规则入口。通用治理要求沿用模板 v1.1.1。

## 项目专属规则

1. 本项目负责构建自动化，不直接复制、改写或重新发布 ProjectClash 上游源文件。
2. 原生 APP 工程来自 `ProjectClash/Clash-Client`；内核与 Adapter 版本以该 Client commit 内的 `Dependencies.lock.json` 为准。
3. `UPSTREAM_CLIENT_REF` 可用于日常构建分支；正式 Release 必须锁定完整 40 位 commit SHA。
4. 必须保留 `BUILD-METADATA.json` 中的实际上游 Client、Kernel、Adapter 版本记录。
5. 默认无签名构建。不得声称无签名产物已通过 Gatekeeper、公证、Network Extension 安装或 VPN 实机测试。
6. 不得把 Apple 证书、私钥、Provisioning Profile、订阅链接或用户配置提交到仓库。
7. 不得在 Linux 上模拟或声称完成 Xcode / macOS APP 构建。真实 APP 编译证据来自 GitHub macOS Runner 日志和 Artifact。
8. 修改构建脚本、workflow、上游引用策略或版本管理时，必须更新项目文档、测试和 Repository Structure。

## 标准开工

```bash
python3 scripts/check-governance.py --scope development
python3 scripts/dev-session.py status
```

## 标准收尾

```bash
python3 scripts/update-repository-structure.py --write
python3 scripts/build-source-manifest.py --write
python3 scripts/build-ai-handoff.py
```

完整规则见 `.ai/AI-START-HERE.md`。

## v0.0.3 构建约束

- 本版只构建 Apple Silicon `arm64`；不要重新加入 `x86_64`，除非用户明确要求并创建新版本。
- Xcode 并行任务默认最多 2；不要设置 `cancel-in-progress: true`。
- 构建日志必须保留 Xcode build timing summary 和 Runner 资源诊断。
