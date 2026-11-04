# Clash_Mac_Compile v0.0.5 Release Experience Report

## 设计原则

将运行速度和 UI 流畅度置于二进制体积和构建速度之前，但不牺牲 Swift 安全检查，也不注入未经基准验证的 Go flags。

## 自动化原则

周度工作流先比较上游 Client SHA；无变化就跳过 macOS 构建。发生变化时才递增 Patch，并在构建成功后提交、打 tag 和发布 Pre-release。

## 发布页面

Release notes 作为下载界面说明，明确推荐资产、源码包、兼容架构、安装步骤、配置目录、签名限制和性能测试边界。

## 遗留风险

- 自动提交需要 GitHub Actions 对 main 有写权限，且分支保护允许该机器人提交。
- 自动构建上游最新开发提交的 Weekly Preview 不等同于稳定版。
- `-O` 可能增大产物或延长编译时间；必须依赖实际性能基准决定是否保留。
