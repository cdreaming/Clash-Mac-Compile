# Version Changelog

## v0.0.2

- 将 ProjectClash/Clash-Client 固定到官方 commit `e3e647283b1593a61dba622f13cd499deeda9b8b`。
- 将 GitHub Actions Go 工具链固定为该客户端提交要求的 Go 1.26.10。
- 正式 Release 前置检查可通过完整 40 位 SHA 校验，避免使用可移动的 `main` 分支。
- 更新 v0.0.2 开发、验证、发布说明与 Sourcetree 上传文档。

## v0.0.1

- 基于 AI Project Development Template v1.1.1 初始化项目治理结构。
- 新增 ProjectClash 官方 Clash-Client 下载、依赖准备和 macOS 原生构建脚本。
- 新增 GitHub Actions macOS Runner 自动编译工作流。
- 新增上游 commit 元数据、通用架构构建、Artifact 上传和 Release 资产校验。
- 首版采用无签名编译；自动签名与 VPN 实机验证暂不在范围内。
