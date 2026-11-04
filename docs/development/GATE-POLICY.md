# Gate Policy

v1.1.0 的核心原则：

> **门禁负责防止错误发布，不负责阻止继续开发；生命周期负责记录事实，不负责把仓库锁死。**

## Development

开发阶段以“能继续工作”为第一目标。上一版本 `pending / failed / abandoned / superseded`、Repository Structure 漂移、source manifest 漂移、Release 文档不完整等治理问题只发出 WARNING，不阻止写代码、修 Bug、开新版本。

只有关键机器状态损坏（例如 VERSION 无法解析、PROJECT-PROFILE.json 损坏、当前版本目录完全缺失）才硬失败。

## Candidate

真实测试或 simulation 已配置但执行失败时硬失败。若项目尚未配置真实测试/simulation，默认阻止 candidate，但用户可明确使用：

```bash
python3 scripts/run-quality-gates.py   --scope candidate   --override-quality-config   --override-reason "用户明确接受本次风险"
```

AI 不得自行使用 override。

## Release

正式发布硬拦：

- tag / VERSION / RELEASE_REVISION 不匹配；
- 已配置测试真实失败；
- 构建失败；
- 安装/Release 资产缺失或损坏；
- Secret / 私钥进入发布包；
- GitHub 线上资产 SHA-256 校验失败。

上一版本是否 complete 不是当前 Release 的硬前置条件。

## Governance Override

`RELEASE-READY-STATUS: draft` 等明确治理阻止项，可由用户使用 `--override-governance --override-reason "..."` 继续。

普通治理 override **不能**绕过 Secret、真实测试失败、构建失败、损坏资产或线上 SHA-256 失败。

## 已发布版本继续修改

优先使用 Release Revision：

```text
v1.2.0
v1.2.0-r1
v1.2.0-r2
```

项目 `VERSION` 仍为 `1.2.0`，根目录 `RELEASE_REVISION` 保存修订号。

真正覆盖原 tag/Release 的 `force-overwrite` 只允许用户明确选择；如果 GitHub immutable releases 阻止覆盖，应改用 revision。
