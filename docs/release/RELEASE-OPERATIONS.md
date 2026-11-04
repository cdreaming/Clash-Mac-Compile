# Release Operations

## 正常开发

```bash
python3 scripts/check-governance.py --scope development
```

治理债务优先 WARNING，不锁开发。

## AI 候选交付

```bash
python3 scripts/build-ai-handoff.py
```

真实测试/simulation 未配置时默认阻止 candidate；只有用户明确接受风险才使用 `--override-quality-config`。

## Sourcetree / GitHub

1. 本地测试 AI 交付包。
2. Sourcetree 审查 Diff、Commit、Push main。
3. 等 GitHub Quality Gate。
4. 正常版本 Push `vX.Y.Z`。
5. Release Revision Push `vX.Y.Z-rN`。
6. GitHub 自动 build → draft → upload → publish → 线上重新下载验证 → archive。

## 旧版本未闭环

不阻止当前开发或 Release。可稍后用 `set-release-disposition.py` 按真实情况归档为 `superseded / abandoned / failed`。

## 已发布版本重新开发

优先 `prepare-republish.py --mode revision`。

真正覆盖同名 Release 的 `force-overwrite` 只允许用户手工触发；若 immutable release 拒绝覆盖，改用 revision。

## Override

治理 override 与 quality-config override 必须写原因。真实测试失败、构建失败、Secret、资产损坏、线上 SHA 失败不可被普通 override 绕过。
