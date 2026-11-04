# Clash_Mac_Compile v0.0.5 Development Journal

<!-- DEVELOPMENT-SESSION-STATUS: complete -->
<!-- DEVELOPMENT-LAST-CHECKPOINT: CP-004 -->
<!-- DEVELOPMENT-COMPLETION-SOURCE: ai-delivery -->

## 本版目标

以运行速度和 UI 流畅度为首要目标，补齐配置目录诊断、性能基准方法、每周上游自动构建与 GitHub Releases 下载说明。

## 已完成

- Release Swift 优化改为 `-O`，并将优化级别写入 BUILD-METADATA。
- 增加 App Group / 配置目录诊断脚本。
- 增加 Instruments 与 Go pprof 性能策略说明。
- 增加每周检查 ProjectClash Client `main` 的工作流。
- 上游 SHA 变化时自动递增 Patch、运行质量检查、构建 arm64 APP、提交 main、创建 tag 和 Pre-release。
- GitHub Releases 提供 APP、源码包、构建元数据、校验文件和用户下载说明。
- 源码包命名统一为 `Clash_Mac_Compile_vX.Y.Z_source.zip`。

## 验证边界

本地静态检查和项目测试可在源码包制作时执行。真实 macOS Xcode 构建、周度工作流、自动推送、tag、GitHub Release 和线上资产下载验证必须由用户上传后 GitHub Actions 实际执行。
