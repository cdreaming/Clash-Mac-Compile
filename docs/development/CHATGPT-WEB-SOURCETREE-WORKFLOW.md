# ChatGPT Web + Sourcetree Private Repository Workflow

## 角色边界

- ChatGPT Web：读取完整 ZIP，开发、测试、打包。
- Sourcetree：保留 `.git`、审查 Diff、Commit、Push、创建/Push tag。
- GitHub：保存私库、运行 CI/Release、记录远端发布事实。
- 本地机器：最终实机安装和人工验收。

ChatGPT Web 不应假设能持续读取私有 GitHub。

## 每轮输入

首选只上传：

```text
project-source-vX.Y.Z.zip
+ 本轮需求
```

若需要从其它项目同步最新通用规则，再附：

```text
governance-template-vA.B.C.zip
```

## AI 输出

`python3 scripts/build-ai-handoff.py` 生成：

```text
dist/handoff/<slug>-project-source-vX.Y.Z.zip
dist/handoff/governance-template-vA.B.C.zip
dist/handoff/<slug>-ai-handoff-vX.Y.Z.zip
dist/<slug>-vX.Y.Z-source.zip
dist/SHA256SUMS.txt
```

项目如配置安装程序，安装资产也进入 `dist/`。

## Sourcetree 回填

1. 把 AI 项目源码包解压到临时目录。
2. 本地执行项目真实测试。
3. 备份原 Git 工作树。
4. 用临时目录覆盖原工作树，但保留 `.git`。
5. Sourcetree 审查 Added / Modified / Deleted。
6. 确认无 secret、runtime、本地配置。
7. Commit、Push `main`。
8. 等 GitHub `Quality Gate`。

## 正式发布

CI 成功后用 Sourcetree 创建并 Push `vX.Y.Z` tag。Release workflow 自动严格门禁、构建、发布、重新下载线上资产校验并归档。

已发布版本出现 Bug 必须提升版本，不能覆盖旧 tag/Release。
