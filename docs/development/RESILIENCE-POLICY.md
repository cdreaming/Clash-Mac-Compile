# Development Resilience and Risk Policy

## L1：普通小改

文档、单点 UI、纯函数小修。无需频繁 checkpoint，完成后跑对应最小测试。

## L2：跨文件功能

跨模块、状态、配置、持久化、升级逻辑。至少一个关键 checkpoint；应有单元 + 集成/smoke，并记录根因与验证。

## L3：发布与高风险

Release、安装/升级/卸载、数据迁移、权限、secret、供应链、长回归、可能破坏用户数据的操作。

必须：

- heartbeat；
- hard timeout；
- 持久日志；
- checkpoint；
- clean-room 模拟；
- 需要时做故障注入和回滚验证。

## 中断恢复

按顺序读取 `VERSION` → Development Journal → Release Checklist → Release Lesson → `.dev-state/last-command.json`（若存在）→ 最近测试输出。

`.dev-state` 可以丢失，不能成为唯一事实源。

## 原子与安全

状态写入使用临时文件替换；交接包排除 `.git`、`.dev-state`、`dist`、runtime、secret、token 与本地配置。
