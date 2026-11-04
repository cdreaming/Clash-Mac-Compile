# Clash_Mac_Compile v0.0.3 Release Experience Report

## 本版背景

v0.0.2 的 Actions 日志在大量 Extension Swift 源文件编译期间最终显示 `The operation was canceled`。提供的日志片段没有包含最初取消原因或明确 Swift `error:`，因此不能断言是 Swift 诊断本身导致失败。

## 改进

- 先构建 arm64，减少同时编译的架构数量。
- 将 Xcode 并行任务限制为 2。
- 不自动取消正在运行的 Build workflow。
- 将超时提高至 240 分钟。
- 记录 Runner CPU / 内存、Xcode build timing summary 和构建元数据。

## 仍需验证

首次 v0.0.3 GitHub Actions 运行必须检查完整日志，特别是是否出现 Swift `error:`、Runner 取消事件、内存压力或超时。
