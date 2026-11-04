# Version Changelog

## v0.0.6

- 移除 Apple Developer / Developer ID / Provisioning Profile / Apple Notary 相关脚本、Secrets 和 workflow steps。
- Build、Release、Weekly 统一使用无签名 arm64 构建，无需 Apple Developer 账户。
- APP ZIP 命名增加 `-unsigned`，构建元数据标记 `distribution_mode=unsigned`、`vpn_authorization_supported=false`。
- GitHub Releases 正式上传无签名 APP、源码包、构建元数据、SHA-256 和明确的下载 / VPN 限制说明。
- 保留 Swift `-O` 运行速度优先、arm64、Xcode 并行任务最多 2、每周上游检查和自动 Patch / Tag / Pre-release。

## v0.0.5

- Release Swift 优化改为 `-O`，优先运行速度与交互流畅度；保留 arm64 与最多 2 个 Xcode 并行任务。
- 增加 App Group 配置目录诊断脚本和 macOS 数据目录说明。
- 增加 Instruments / Go pprof 性能基准策略，不虚构未经测量的性能收益。
- 增加每周一 09:17（America/Los_Angeles）检查 ProjectClash Client 的工作流；仅在上游 commit 变化时递增 Patch、构建、提交、打 tag 并发布 Pre-release。
- GitHub Releases 增加 APP、符合 `Clash_Mac_Compile_v0.0.*_source.zip` 命名规则的源码包、构建元数据、SHA-256 和完整下载说明。
- 升级 GitHub Actions 至 Node 24 兼容版本，并关闭无根目录 go.sum 时不适用的 setup-go 缓存。

## v0.0.4

- 修复 Xcode 27 的 `lipo -verify_arch` 参数顺序不兼容问题。
- 改用 `lipo -archs <APP executable>` 获取架构列表，并明确验证结果仅为 `arm64`。
- 增加 Info.plist 主执行文件名称、执行文件路径和文件存在性检查。
- 修正 Release 资产名称及测试夹具，保持 `macos-arm64` 一致。
- Release 工作流同步设置 `CLASH_BUILD_JOBS=2`，与普通 Build 工作流保持一致。

## v0.0.3

- 将 macOS 构建目标收敛为 Apple Silicon `arm64`，暂不构建 Intel `x86_64`。
- 将 Xcode 并行编译任务限制为 2，并使用 `ONLY_ACTIVE_ARCH=YES`。
- 移除 Build workflow 的自动取消并发策略，避免新提交自动终止进行中的构建。
- 将构建超时调整为 240 分钟，增加主机资源诊断和构建耗时摘要。
- 更新 APP Artifact 命名为 `macos-arm64`，同步 Release 资产打包与校验。
- 增加 arm64 构建契约检查和回归测试。

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
