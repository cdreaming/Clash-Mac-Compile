# Clash_Mac_Compile v0.0.4 Release Experience Report

## 本版经验

Xcode Build 的成功标志与整个 GitHub Actions Job 的成功标志不同。APP 编译完成后，架构检查、打包、Artifact 上传等后置步骤仍然可能失败。

## 本次根因

Xcode 27.1 的 `lipo -verify_arch` 参数解析与旧脚本调用顺序不兼容，导致 Xcode 已成功后仍退出非零。

## 改进

- 以 `lipo -archs` 获取实际架构列表。
- 先验证 Info.plist 中的可执行文件名和路径。
- 架构校验失败时输出可诊断信息。
- 将架构校验与 Xcode Build 成功状态分开记录。

## 后续建议

下一次 GitHub 构建应重点检查 `APP executable architectures: arm64`、ZIP 打包和 Artifact 上传步骤。
