# Clash_Mac_Compile v0.0.4 Release Notes

## 发布摘要

v0.0.4 修复 Xcode 27.1 下 APP 已经编译成功、但后置 `lipo -verify_arch` 检查因参数顺序不兼容而失败的问题。

## 用户可见变化

- Xcode Build 成功后，先验证 `CFBundleExecutable` 与实际主程序文件。
- 使用 `lipo -archs` 读取架构，不再调用 Xcode 27 不兼容的旧式 `lipo -verify_arch` 命令。
- 严格要求主执行文件架构为 `arm64`。
- 修复后仍保持 Apple Silicon 单架构与最多 2 个 Xcode 构建任务。
- Release 工作流同步使用低并行任务配置。

## 已知边界

- 本地测试不能代替 GitHub macOS Runner 的真实 Xcode 构建。
- 首版产物仍然无签名；Network Extension、VPN 安装、Apple 公证和实机流量仍需单独验证。
- Intel Mac 不在本版支持范围内。

## 预期产物

- `Clash_Mac_Compile-v0.0.4-macos-arm64.zip`
- `BUILD-METADATA.json`
- `SHA256SUMS.txt`
