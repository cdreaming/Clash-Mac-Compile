# AI Start Here

## 开工恢复

按顺序读取：`VERSION` → `TEMPLATE_VERSION` → `AGENTS.md` → `.ai/PROJECT-PROFILE.json` → 当前 Development Journal → 当前 Release Lesson。

```bash
python3 scripts/check-governance.py --scope development
python3 scripts/dev-session.py status
```

## 项目约束

- 主工程必须来自 `ProjectClash/Clash-Client`。
- 内核和 Adapter 由 Client 的 `Dependencies.lock.json` 固定。
- `UPSTREAM_CLIENT_REF=main` 仅适合快速构建；正式 Release 必须固定 40 位 commit SHA。
- macOS APP 构建只允许在 macOS + 完整 Xcode 环境执行。
- 无签名编译不代表可正常安装、启用 VPN 或通过公证。
- 每轮改动必须提升 `VERSION`，并更新版本归档文档。

## 收尾

完善开发日志、Release Notes、Validation Report、Release Checklist、Release Experience Report、Release Lesson、CHANGELOG 和受影响的架构/构建文档，然后运行：

```bash
python3 scripts/build-ai-handoff.py
```

测试结论只允许真实通过、真实失败、未执行。
