# Clash_Mac_Compile v0.0.1 Release Experience Report

## 开发过程

基于用户提供的 AI Project Development Template v1.1.1 初始化新项目。项目采用上游 Client 自带的 bootstrap/configure 流程，避免自行拼接 Kernel、Adapter 与 Xcode target。

## 有效做法

- Client 负责锁定 Kernel 与 Adapter，减少三仓版本漂移。
- 用独立的 `UPSTREAM_CLIENT_REF` 控制客户端源码版本。
- 构建元数据记录实际 Client commit 和依赖 revisions。
- CI 每次 push 产出 Artifact；正式 Release 另行固定 commit。
- 无签名构建与可安装 VPN 客户端的能力边界明确分开。

## 风险与改进

- `xcode-27` Runner 当前为 Public Preview，Runner label/容量可能变化。
- 首次 SDK 构建需要下载 Go 依赖并编译五个平台切片，运行时间较长。
- macOS Runner 费用与 GitHub Actions 额度需要用户在账户中确认。
- Apple Network Extension 权限不能靠无签名编译获得。

## 发布操作经验

首次 main 构建只用于验证 CI 链路。正式 Release 前必须将上游 Client ref 固定为完整 SHA，并按项目版本规则更新版本。

## 模板反馈

本轮未发现需要提升通用模板版本的治理经验；新增内容均为 Clash_Mac_Compile 项目专属。

## 后续建议

优先验证 GitHub macOS Runner 的首次构建时间、Xcode 27 镜像稳定性和实际 Artifact；后续再评估签名、公证与 VPN 实机测试。
