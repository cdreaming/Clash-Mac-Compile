# AI Handoff Contract

## 输入契约

完整项目 ZIP 应包含 `VERSION`、`AGENTS.md`、`.ai/`、`docs/`、`scripts/`、业务源码与测试。当前轮次不依赖 `.git` 才能理解开发事实。

## 输出契约

AI 最终交付至少包含：

- 项目源码 ZIP；
- 治理模板 ZIP；
- 合并 AI handoff ZIP；
- Release 源码包；
- SHA-256；
- 当前版本验证与发布文档。

## 状态语义

`DEVELOPMENT-SESSION-STATUS: complete` 只表示该源码快照开发阶段完成，不代表 CI、tag、GitHub Release 或线上资产验证已经发生。

远端发布事实只能由真实 GitHub workflow 写入。

## 真实性

测试、构建、发布结论必须能追溯到真实命令或真实远端证据；无法验证就写“未执行/未验证”。
