# Private GitHub Repository Setup

## 推荐创建

1. GitHub 新建 **Private** repository。
2. 不额外生成 README/.gitignore。
3. 本地解压模板并运行 `bootstrap-project.py`。
4. Sourcetree 初始化/添加工作副本，配置 remote，首次 Commit/Push `main`。

## GitHub CLI

```bash
gh auth login
gh repo clone OWNER/REPOSITORY
gh release download vX.Y.Z -R OWNER/REPOSITORY
```

私有 Release 下载优先用 `gh`，避免把长期 token 拼进命令和 README。

## Fine-grained PAT

只授权目标仓库；只读安装不要给写权限；token 放环境变量或凭据管理器，不进入 Git、日志、截图或 AI 交接包。

## ChatGPT Web 边界

普通 AI 开发以用户上传 ZIP 为事实源，不要求额外提供 commit SHA、Actions URL、Release URL；这些远端事实在正式 Release 阶段由 GitHub workflow 记录。
