# README AI Hook Template

把下面区块合并到目标项目 README 的顶部说明区。项目 README 已存在时不要整文件覆盖，只插入并按项目路径调整。

```markdown
<!-- AI-REPOSITORY-HOOK: START -->
> **AI 开工钩子（强制）**  
> 修改仓库前先读 `AGENTS.md`、`.ai/AI-START-HERE.md`、当前版本 Development Journal 和 Release Lesson。  
> 开工运行 `python3 scripts/check-governance.py --scope development`。  
> AI 收尾运行 `python3 scripts/build-ai-handoff.py`。  
> 不得伪造 GitHub Release、commit、Actions 或线上资产验证证据。
<!-- AI-REPOSITORY-HOOK: END -->
```

该钩子是“提醒入口”，真正硬门禁仍由脚本、测试和 GitHub Actions 执行。
