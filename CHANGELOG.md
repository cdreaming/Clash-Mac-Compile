# Version Changelog

## v0.1.2

- 修复 GitHub Actions Artifact 上传找不到 `build/ci` 文件的问题：构建脚本规范化输出目录，验证 APP ZIP、metadata、VPN report 和 SHA256SUMS。
- 新增 `BUILD-OUTPUT-MANIFEST.json`，记录版本、输出目录、unsigned 模式、APP ZIP 名称和输出文件清单。
- 新增 `scripts/verify-build-outputs.py`，在 Build / Release / Weekly 上传或附加前验证输出文件、版本和分发模式。
- Build workflow 改为上传单一目录 `build/ci/`，避免多路径 artifact glob 路径解析歧义。
- Build / Release / Weekly 显式设置 `CLASH_SIGNING_MODE=unsigned`，确保 APP ZIP 命名一致。
- Release attachment 验证并上传 `BUILD-OUTPUT-MANIFEST.json`。

## v0.1.1

- 修正 Packet Tunnel System Extension 对 `ClashMacCore` framework 的依赖：provider target 改为嵌入 framework，不再依赖 host app 的旧 `.appex` 相对路径。
- 将 provider `LD_RUNPATH_SEARCH_PATHS` 设置为 `@executable_path/../Frameworks`，指向 System Extension 自身的 `Contents/Frameworks`。
- 新增 `scripts/summarize-xcode-linker-errors.py`，提取 Undefined symbols、duplicate symbol、framework/library not found、ld 和 clang linker 错误及上下文。
- Xcode 构建启用 verbose 日志并保留 `XCODEBUILD.log`、`LINKER-DIAGNOSTICS.txt`、退出码、System Extension Build Settings 和补丁后的 XcodeGen project spec。
- Build、Release、Weekly workflow 增加 `if: always()` 诊断 Artifact 上传，确保构建失败时也能取回 linker 日志。
- VPN 架构审计增加 provider framework embed 和 runpath 检查。
- 保留 arm64、Swift `-O`、GitHub unsigned、本地自签名隔离和 Apple VPN 授权边界。

## v0.1.0

- 将 ProjectClash macOS Packet Tunnel target 从 App Extension 迁移为 XcodeGen System Extension。
- 将主 APP 与 provider 的 Network Extension entitlement 改为 `packet-tunnel-provider-systemextension`，并给主 APP 增加 `com.apple.developer.system-extension.install`。
- 主 APP 链接 SystemExtensions.framework；XcodeGen 将 provider 嵌入 `Contents/Library/SystemExtensions`。
- 在 VPN preference 保存之前调用 `OSSystemExtensionRequest.activationRequest`，等待用户批准与扩展激活结果。
- 新增 `patch-macos-system-extension.py`、`audit-vpn-architecture.py` 和 `VPN-ARCHITECTURE-REPORT.json`。
- Build / Release / Weekly 都检查 System Extension 结构并附带架构报告；GitHub 构建仍 unsigned，明确不具备 Apple VPN 授权。
- 保留 arm64、Swift `-O`、本地自签名开发模式和私钥防泄漏。

## v0.0.9

- 修复 v0.0.8 GitHub Release 附件阶段 `BUILD-METADATA.json` 因字面量 `\\n` 后缀而报 `JSONDecodeError: Extra data` 的问题。
- 修复 Xcode 版本字段对真实换行的格式化。
- 为 Release JSON 解析增加文件路径、行列和字符位置诊断。
- 增加执行真实 metadata writer 并严格解析 JSON 的回归测试，以及无效 JSON 诊断测试。
- 保留 v0.0.8 本地自签名开发模式；GitHub Build / Release / Weekly 继续无签名，私钥不进入源码包。

## v0.0.8

- 增加本地自签名开发模式，使用单独提供的 `Clash_Mac_Compile Local Development` identity 在开发 Mac 上验证 Xcode 代码签名。
- 新增本地 Keychain identity 检查、local signed build wrapper、主 APP / 嵌套扩展签名验证和 `LOCAL-SIGNING-REPORT.json`。
- `build-macos-app.sh` 默认仍为 unsigned；仅显式选择 `--signing-mode local` 才启用本地自签名。
- GitHub Build / Release / Weekly 保持 unsigned，不访问开发者本地 Keychain，不接收个人 P12。
- Release 资产附加继续只接受 unsigned APP，拒绝 `local-development-only` 产物。
- 源码打包与 `.gitignore` 增加 P12 / PFX / Provisioning Profile 敏感文件保护。
- 文档明确自签名不授予 Apple Team ID、Network Extension / Packet Tunnel entitlement 或公证。

## v0.0.7

- 基于 v0.0.6 治理兼容修复版升级正式版本号，保留无签名 arm64 构建。
- 修复 `dev-session.py` 对缺少 `## 完成摘要` 和会话元数据的旧日志兼容问题。
- 增加 `dev-session.py validate`，供重发布前执行开发日志预检。
- 调整 `prepare-republish.py` 顺序：预检通过后才写入历史、Checklist 和 `RELEASE_REVISION`。
- 增加旧日志缺少完成摘要、缺少会话标记及缺失日志时不得半更新状态的回归测试。
- 每周自动生成的开发日志增加 `## 完成摘要`，防止上游自动升级后重现治理失败。

## v0.0.6

- 移除 Apple Developer / Developer ID / Provisioning Profile / Apple Notary 相关脚本、Secrets 和 workflow steps。
- Build、Release、Weekly 统一使用无签名 arm64 构建，无需 Apple Developer 账户。
- APP ZIP 命名增加 `-unsigned`，构建元数据标记 `distribution_mode=unsigned`、`vpn_authorization_supported=false`。
- GitHub Releases 正式上传无签名 APP、源码包、构建元数据、SHA-256 和明确的下载 / VPN 限制说明。
- 保留 Swift `-O` 运行速度优先、arm64、Xcode 并行任务最多 2、每周上游检查和自动 Patch / Tag / Pre-release。
- 修复 `dev-session.py` 对缺少 `## 完成摘要` 的旧版开发日志兼容性；重发布前先预检，避免失败时部分修改 Release 状态。

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
