# Clash_Mac_Compile v0.0.2 Release Experience Report

## 版本目标

修复 v0.0.1 因可移动上游分支被 Release 安全检查阻断的问题。

## 关键决策

- 保留完整 40 位 SHA 检查，不通过放宽规则解决问题。
- 固定官方 Client commit `e3e647283b1593a61dba622f13cd499deeda9b8b`。
- 依赖版本由该 Client commit 内的 `Dependencies.lock.json` 管理。
- Go toolchain 固定为 1.26.10，匹配该 Client 源码要求。

## 风险与改进

- 上游 Client 后续提交可能改变 Go、Xcode 或依赖要求；升级前必须审查 README、`Dependencies.lock.json` 和构建脚本。
- `xcode-27` Runner 当前为预览镜像，仍需观察首次真实云端构建。

## 后续建议

首次 v0.0.2 GitHub Actions 构建成功后，保存 `BUILD-METADATA.json`，作为后续更新上游版本时的基准证据。
