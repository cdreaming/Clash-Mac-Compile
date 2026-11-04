# Release Lifecycle

## 状态是记录，不是开发锁

开发状态：

```text
active ↔ complete
```

发布归档状态：

```text
pending
├── complete
├── superseded
├── abandoned
└── failed
```

上一版本处于任何状态，都允许新版本继续开发。`pending` 只提示尚未处置，不阻止 `prepare-version.py`。

## 开新版本

```bash
python3 scripts/prepare-version.py --version X.Y.Z --risk L2 --write
```

上一版未闭环时只显示 WARNING。

如果上一版从未正式发布，可按事实关闭：

```bash
python3 scripts/set-release-disposition.py   --version OLD_VERSION   --status superseded   --reason "未正式发布，由新版本取代"   --write
```

也可以使用 `abandoned` 或 `failed`。

## 已发布版本需要补代码

推荐：

```bash
python3 scripts/prepare-republish.py   --mode revision   --reason "发布后发现需要补充代码"   --write
```

它会保存旧 Release 证据、增加 `RELEASE_REVISION`、重新打开开发状态，并把下一次 tag 设为 `vX.Y.Z-rN`。

## 真正覆盖原 Release

用户明确要求时：

```bash
python3 scripts/prepare-republish.py   --mode force-overwrite   --reason "用户明确要求覆盖原 Release"   --write
```

该模式仍增加内部 revision 作为审计记录，但目标 tag 保持 `vX.Y.Z`。正式执行只能走 GitHub `workflow_dispatch` 并填写确认字符串。

## 规则

- 开发永远不因为上一版本 pending 被锁死。
- 正式 Release 仍需要真实测试、构建、资产和线上校验。
- 已发布版本可以修改，但不能静默覆盖历史。
