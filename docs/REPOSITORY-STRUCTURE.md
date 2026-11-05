# Repository Structure

> 本文件由 `scripts/update-repository-structure.py` 从真实文件系统和 `.ai/REPOSITORY-CATALOG.json` 生成。每次开发新增、删除、移动文件都必须更新。

## 目录与文件

`├── .ai/` — AI 机器可读治理层；保存开工入口、项目配置、模板导出清单和仓库职责目录。
`│   ├── AI-START-HERE.md` — AI 每轮开工、上游版本锁定、验证和收尾入口。
`│   ├── PROJECT-PROFILE.json` — 项目质量门禁配置；包含 Release SHA、Python/Shell 静态检查和项目单元测试命令。
`│   ├── REPOSITORY-CATALOG.json` — 逐目录/逐文件职责机器目录；是自动生成 Repository Structure 的说明事实源。
`│   └── TEMPLATE-MANIFEST.json` — 通用治理模板导出清单；排除 Clash_Mac_Compile 项目专属配置。
`├── .github/` — GitHub 仓库自动化与协作配置；保存 AI 指令、PR 模板和 Actions 工作流。
`│   ├── workflows/` — GitHub Actions 工作流；分别执行通用质量门禁、macOS APP 自动构建和正式 Release。
`│   │   ├── build-macos.yml` — macOS arm64 构建和输出验证在同一 Actions step 执行；记录 workflow/script status/context；always() 报告 outcome 并上传诊断。
`│   │   ├── ci.yml` — main Push/PR 的通用质量门禁，并运行模板治理回归测试。
`│   │   ├── release.yml` — Tag Release workflow；构建和输出验证同一步执行，always() 报告 outcome 并上传失败状态、上下文和 Xcode Linker diagnostics。
`│   │   └── upstream-weekly.yml` — 每周上游 Preview workflow；构建和输出验证同一步执行，always() 报告 outcome 并上传失败状态、上下文和 Xcode Linker diagnostics。
`│   ├── copilot-instructions.md` — GitHub Copilot 的项目专属开发规则。
`│   └── pull_request_template.md` — PR 检查模板；要求标记风险等级、真实验证和经验沉淀。
`├── docs/` — 长期文档根目录；保存架构、开发规则、GitHub 说明、Release 规则、版本归档和模板。
`│   ├── architecture/` — 项目构建架构文档；描述官方 Client、Kernel、Adapter 与 GitHub Runner 的构建关系。
`│   │   └── ARCHITECTURE.md` — 本项目 arm64-only 自动构建拓扑、组件职责、版本事实源和安全边界。
`│   ├── development/` — 项目开发规则与上游构建说明。
`│   │   ├── AI-HANDOFF-CONTRACT.md` — AI 输入/输出交接契约；明确 candidate 完成与 GitHub Release 完成不是同一事实。
`│   │   ├── CHATGPT-WEB-SOURCETREE-WORKFLOW.md` — ChatGPT Web + ZIP + Sourcetree + 私有 GitHub 的完整人工/自动协作流程。
`│   │   ├── DEEP-UPGRADE-POLICY.md` — 深度升级触发条件与强制验证；覆盖兼容、迁移、回滚、卸载、安全和发布影响。
`│   │   ├── GATE-POLICY.md` — 护栏式门禁规则；定义 Development/Candidate/Release 的 WARNING、FAIL、override 与不可绕过边界。
`│   │   ├── MACOS-DUAL-IMPLEMENTATION-RELEASE.md` — macOS 双实现开发/发布强制规则；定义源码+preview portable 交付、GitHub 双 PKG、共享 App builder、release lock、工具链固定和验收边界。
`│   │   ├── REAL-ENVIRONMENT-TEST-POLICY.md` — T0-T5 验证分层；定义静态、单元、集成、clean-room、故障注入和实机测试。
`│   │   ├── REFERENCE-LESSONS.md` — 从长期版本实践中抽象的通用工程经验；作为后续 AI 开工参考规则。
`│   │   ├── RESILIENCE-POLICY.md` — L1/L2/L3 风险和防中断策略；规定 checkpoint、heartbeat、hard timeout 与恢复顺序。
`│   │   ├── SOURCE-BASELINE-AUDIT.md` — 对 mihomo-web-installer-v4.0.0 的 107 个实际项目文件进行全量结构化学习后的抽象报告。
`│   │   ├── TEMPLATE-DESIGN-DECISION.md` — 比较用户提出的两种模板方案并说明采用混合式单一事实源方案的原因。
`│   │   ├── TEMPLATE-EVOLUTION.md` — 通用治理经验如何跨项目沉淀、何时提升 TEMPLATE_VERSION 的规则。
`│   │   └── UPSTREAM-BUILD.md` — ProjectClash 三仓职责、官方 bootstrap/configure、Go 工具链和 arm64 构建说明。
`│   ├── github/` — GitHub Actions、Sourcetree 上传、Artifact 下载与费用说明。
`│   │   ├── GITHUB-ACTIONS-SETUP.md` — Sourcetree 上传、无签名 GitHub Actions 构建、每周上游自动发布、权限和 Releases 下载操作。
`│   │   ├── PRIVATE-REPOSITORY-SETUP.md` — 私有 GitHub 仓库创建、Sourcetree 初始化、gh/PAT 认证下载和凭据安全说明。
`│   │   ├── RELEASE-DOWNLOAD-GUIDE.md` — GitHub Releases 无签名 APP、源码、构建元数据、SHA-256、安装方式和 VPN 功能限制说明。
`│   │   └── REPOSITORY-RULESETS.md` — 单人 direct-push 与团队 PR 两种仓库保护策略，以及 tag/Action/immutable release 建议。
`│   ├── local-development/` — 开发者本机专用工具和本地自签名代码签名说明；私钥不进入仓库。
`│   │   └── LOCAL-CODE-SIGNING.md` — 本地自签名开发模式说明；解释 v0.1.0 System Extension 架构、Keychain 导入、构建、授权边界和私钥安全。
`│   ├── macos/` — macOS App Group 容器、配置文件路径和安装后数据检查说明。
`│   │   └── CONFIGURATION-DIRECTORIES.md` — 说明官方 App Group 配置目录的预期位置，以及无签名构建下容器可能不存在的限制。
`│   ├── performance/` — 运行速度优先的编译策略、Instruments 与 Go pprof 性能基准指南。
`│   │   └── PERFORMANCE-STRATEGY.md` — 运行速度优先的 Swift -O 编译策略及 Instruments / Go pprof 性能测试方法。
`│   ├── release/` — 跨版本 Release 治理；保存生命周期、操作步骤和发布知识库。
`│   │   ├── RELEASE-KNOWLEDGE-BASE.md` — Release Lesson 与 Experience Report 的沉淀规则；把发布事故转成自动防回归资产。
`│   │   ├── RELEASE-LIFECYCLE.md` — 版本开发、候选、正式发布、归档、supersede 的机器状态与生命周期规则。
`│   │   └── RELEASE-OPERATIONS.md` — 正式发布操作说明；覆盖 AI 候选、本地测试、Sourcetree、tag、GitHub workflow 和归档。
`│   ├── release-lessons/` — 跨版本事故与经验库；把根因转化成下一版自动防回归规则。
`│   │   ├── README.md` — 版本经验索引；要求 AI 每轮读取当前经验并在收尾更新。
`│   │   ├── TEMPLATE.md` — 发布经验标准模板；定义目标、事故、根因、决策、防回归、验证和遗留边界。
`│   │   ├── v0.0.1.md` — 当前版本发布经验；记录风险、根因、决策和防回归规则。
`│   │   ├── v0.0.2.md` — v0.0.2 发布经验；将 main 可移动引用造成的 Release 阻断转化为 SHA 防回归规则。
`│   │   ├── v0.0.3.md` — v0.0.3 发布经验；将 arm64-only、有限并行和取消策略形成防回归规则。
`│   │   ├── v0.0.4.md` — v0.0.4 发布经验；将 Xcode 27 lipo 参数兼容性转化为回归检查。
`│   │   ├── v0.0.5.md` — 当前版本发布经验；把事故根因转成可执行防回归规则。
`│   │   ├── v0.0.6.md` — v0.0.6 发布经验；无签名构建不等于 Network Extension / Packet Tunnel 可用。
`│   │   ├── v0.0.7.md` — v0.0.7 发布经验规则；将旧日志兼容和重发布预检故障转化为防回归要求。
`│   │   ├── v0.0.8.md` — v0.0.8 发布经验；记录自签名身份与 Apple 授权 entitlement 的边界及私钥防泄漏规则。
`│   │   ├── v0.0.9.md` — v0.0.9 发布经验；JSON 序列化结果必须通过真实生成和严格解析验证。
`│   │   ├── v0.1.0.md` — v0.1.0 发布经验；System Extension 结构迁移不等于 Apple Developer VPN entitlement 已获授权。
`│   │   ├── v0.1.1.md` — v0.1.1 发布经验；System Extension 的 Frameworks 层级变化需同步调整依赖嵌入与 runpath，Xcode 失败必须保留完整日志。
`│   │   ├── v0.1.2.md` — v0.1.2 发布经验；上传前验证文件、版本和分发模式，GitHub Artifact 使用单目录路径。
`│   │   └── v0.1.3.md` — v0.1.3 发布经验；多产物缺失先查 build outcome 和输出目录，build/verify 同一步并持久化退出码。
`│   ├── releases/` — 各项目版本独立归档根目录；每版都有开发、验证、发布和经验文档。
`│   │   ├── v0.0.1/` — 当前项目版本归档目录；保存开发、验证、发布和经验记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — 当前版本开发日志；保存恢复入口、检查点与开发完成状态。
`│   │   │   ├── RELEASE-CHECKLIST.md` — 当前版本发布检查表；保存风险、生命周期状态和真实发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — 当前版本发布经验报告与模板反馈。
`│   │   │   ├── RELEASE-NOTES.md` — 当前版本中文发布说明。
`│   │   │   └── VALIDATION-REPORT.md` — 当前版本真实验证报告。
`│   │   ├── v0.0.2/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.0.2 开发日志；记录修复可移动上游引用、Go 工具链同步和本地验证结果。
`│   │   │   ├── RELEASE-CHECKLIST.md` — v0.0.2 发布检查表；记录候选门禁状态和待 GitHub 云端验证的发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.0.2 发布经验报告；记录上游版本可复现性改进。
`│   │   │   ├── RELEASE-NOTES.md` — v0.0.2 发布说明；说明固定 Client SHA、Go 1.26.10 和 Release 修复。
`│   │   │   └── VALIDATION-REPORT.md` — v0.0.2 验证报告；区分本地真实通过项与尚未执行的 GitHub 云端 Xcode 构建。
`│   │   ├── v0.0.3/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.0.3 开发日志；记录 SwiftCompile 被取消后的 arm64-only 与低并行度修复。
`│   │   │   ├── RELEASE-CHECKLIST.md` — v0.0.3 发布检查表；记录本地质量门禁和待云端 Xcode 验证的发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.0.3 发布经验；分析 SwiftCompile 被取消并记录资源优化策略。
`│   │   │   ├── RELEASE-NOTES.md` — v0.0.3 发布说明；描述 Apple Silicon arm64 构建、并行任务限制和工作流取消策略调整。
`│   │   │   └── VALIDATION-REPORT.md` — v0.0.3 验证报告；区分本地配置测试与未执行的 GitHub 云端构建。
`│   │   ├── v0.0.4/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.0.4 开发日志；记录 Xcode 27 lipo 后置检查修复。
`│   │   │   ├── RELEASE-CHECKLIST.md` — v0.0.4 发布检查表；记录本地验证和待执行的云端构建证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.0.4 发布经验报告；记录 Xcode Build 成功但后置 lipo 检查失败的根因。
`│   │   │   ├── RELEASE-NOTES.md` — v0.0.4 发布说明；说明 lipo 架构检查改用 lipo -archs。
`│   │   │   └── VALIDATION-REPORT.md` — v0.0.4 验证报告；区分本地测试与待执行的 GitHub macOS Runner 构建。
`│   │   ├── v0.0.5/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.0.5 开发日志；记录运行速度优先、配置诊断、每周上游发布和 Releases 下载说明。
`│   │   │   ├── RELEASE-CHECKLIST.md` — v0.0.5 发布检查表；记录本地源码检查和待执行的 GitHub 云端构建 / 发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.0.5 发布经验报告；记录性能优先构建、每周自动 Preview 和下载页说明策略。
`│   │   │   ├── RELEASE-NOTES.md` — v0.0.5 GitHub Release 下载说明；列出 APP、源码、构建元数据、安装、配置目录、性能与周度 Preview 说明。
`│   │   │   └── VALIDATION-REPORT.md` — v0.0.5 本地真实验证报告；区分已通过的静态、项目、打包测试与未执行的云端构建。
`│   │   ├── v0.0.6/` — 当前项目版本归档目录；保存无签名开发、验证、发布和经验记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.0.6 当前开发日志，包含版本目标、治理修复检查点和完成摘要。
`│   │   │   ├── RELEASE-CHECKLIST.md` — v0.0.6 无签名发布检查表；区分本地源码验证与待执行的 GitHub 云端构建 / 发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.0.6 发布经验；记录 dev-session 缺少完成摘要导致重发布失败的根因和修复。
`│   │   │   ├── RELEASE-NOTES.md` — v0.0.6 签名发布方案已撤回的历史说明，不作为正式可下载版本。
`│   │   │   └── VALIDATION-REPORT.md` — v0.0.6 验证报告；记录开发日志兼容、重发布预检与回归测试结果。
`│   │   ├── v0.0.7/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.0.7 开发日志；记录版本升级、旧日志兼容、重发布预检和回归测试检查点。
`│   │   │   ├── RELEASE-CHECKLIST.md` — v0.0.7 发布检查表；区分源码级完成项和待执行的 GitHub 云端构建 / 发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.0.7 发布经验；记录开发日志格式兼容、预检顺序和防半更新规则。
`│   │   │   ├── RELEASE-NOTES.md` — v0.0.7 用户发布说明；治理兼容修复、无签名 arm64 APP、VPN 限制、下载资产和每周 Preview。
`│   │   │   └── VALIDATION-REPORT.md` — v0.0.7 实际验证报告；记录逐项测试结果并区分未执行的云端构建和 VPN 实机验证。
`│   │   ├── v0.0.8/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.0.8 开发日志；记录本地自签名构建、GitHub unsigned 隔离和授权边界。
`│   │   │   ├── RELEASE-CHECKLIST.md` — 当前版本发布检查表；保存风险、ready/archive 状态和真实发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.0.8 发布经验；记录本地自签名与 GitHub 无签名发布隔离策略。
`│   │   │   ├── RELEASE-NOTES.md` — v0.0.8 本地自签名开发模式说明；GitHub 仍无签名，明确 VPN 授权边界。
`│   │   │   └── VALIDATION-REPORT.md` — v0.0.8 验证报告；记录本地签名开发模式、JSON Extra data 根因修复和实际回归测试结果。
`│   │   ├── v0.0.9/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.0.9 开发日志；记录 JSON Extra data 根因、修复和回归验证。
`│   │   │   ├── RELEASE-CHECKLIST.md` — 当前版本发布检查表；保存风险、ready/archive 状态和真实发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.0.9 发布经验；记录字面量换行后缀导致 JSON Extra data 的根因与防回归方法。
`│   │   │   ├── RELEASE-NOTES.md` — v0.0.9 发布说明；修复 BUILD-METADATA.json 尾部字面量转义导致 Release 附件失败的问题。
`│   │   │   └── VALIDATION-REPORT.md` — v0.0.9 验证报告；记录 metadata writer 严格 JSON 回归、Release 错误定位及尚未执行的云端验证。
`│   │   ├── v0.1.0/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.1.0 开发日志；记录 Packet Tunnel System Extension 迁移、激活调用、架构审计和源码测试。
`│   │   │   ├── RELEASE-CHECKLIST.md` — v0.1.0 发布检查表；区分源码级完成与待执行的 GitHub macOS 构建和 VPN 授权证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.1.0 发布经验；记录 Ad-hoc 签名与 App Extension 限制、System Extension 迁移及授权前提。
`│   │   │   ├── RELEASE-NOTES.md` — v0.1.0 macOS System Extension 架构升级说明、激活流程、GitHub unsigned 与 Apple VPN 授权边界。
`│   │   │   └── VALIDATION-REPORT.md` — v0.1.0 验证报告；记录源码测试结果，区分尚未执行的 XcodeGen、macOS 实机激活和 Apple Developer 授权。
`│   │   ├── v0.1.1/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.1.1 开发日志；记录 System Extension Linker 依赖修正、verbose 日志和失败诊断上传。
`│   │   │   ├── RELEASE-CHECKLIST.md` — 当前版本发布检查表；保存风险、ready/archive 状态和真实发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.1.1 发布经验；记录 App Extension 到 System Extension 后 Framework 嵌入/runpath 迁移及完整 Linker 诊断保留。
`│   │   │   ├── RELEASE-NOTES.md` — v0.1.1 System Extension ClashMacCore framework embed/runpath 修正、Xcode Linker 诊断和失败 Artifact 上传说明。
`│   │   │   └── VALIDATION-REPORT.md` — v0.1.1 验证报告；记录 framework embed/runpath、Linker parser、CI 诊断上传测试和未执行的真实 Xcode Link。
`│   │   ├── v0.1.2/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.1.2 开发日志；记录 Artifact 上传路径缺失根因判断和输出验证修复。
`│   │   │   ├── RELEASE-CHECKLIST.md` — 当前版本发布检查表；保存风险、ready/archive 状态和真实发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.1.2 发布经验；记录 Artifact path not found 的诊断边界和单目录上传修复。
`│   │   │   ├── RELEASE-NOTES.md` — v0.1.2 Build Artifact 输出目录规范化、BUILD-OUTPUT-MANIFEST、上传前验证和单目录 Artifact 上传说明。
`│   │   │   └── VALIDATION-REPORT.md` — v0.1.2 验证报告；记录输出验证器、GitHub workflow 契约和待执行的云端构建。
`│   │   ├── v0.1.3/` — 当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。
`│   │   │   ├── DEVELOPMENT-JOURNAL.md` — v0.1.3 开发日志；记录构建产物全缺失问题与构建验证闭环修复。
`│   │   │   ├── RELEASE-CHECKLIST.md` — 当前版本发布检查表；保存风险、ready/archive 状态和真实发布证据。
`│   │   │   ├── RELEASE-EXPERIENCE-REPORT.md` — v0.1.3 发布经验；构建和验证合并、状态与上下文持久化、失败时 always-run 诊断。
`│   │   │   ├── RELEASE-NOTES.md` — v0.1.3 Build/Verify 同步执行、绝对路径、workflow/script status/context 和失败诊断说明。
`│   │   │   └── VALIDATION-REPORT.md` — v0.1.3 验证报告；区分本地源码测试和待执行的 GitHub macOS Runner 构建。
`│   │   └── README.md` — 每个 vX.Y.Z 版本目录必须包含哪些开发/验证/发布文档的契约说明。
`│   ├── templates/` — 新项目/新版本文档模板；文件名英文，正文尽量使用中文。
`│   │   ├── ARCHITECTURE.template.md` — 项目 Architecture 文档模板；要求组件、数据、安全、生命周期和失败恢复说明。
`│   │   ├── BUILD-INFO.template.md` — 项目构建信息模板；用于记录版本、平台、构建入口、资产和确定性规则。
`│   │   ├── DEEP-UPGRADE-PLAN.template.md` — 深度升级计划模板；覆盖兼容矩阵、迁移、回滚、故障注入、安全和验证。
`│   │   ├── DEVELOPMENT-JOURNAL.template.md` — 每版本开发日志模板；预置开发状态、检查点和恢复入口机器标记。
`│   │   ├── MACOS-DUAL-PROJECT-PROFILE.template.json` — macOS 双实现 PROJECT-PROFILE 配置示例；提供 preview、共享 builder、release lock 与两个 GitHub PKG variant 的机器字段。
`│   │   ├── MACOS-DUAL-RELEASE.template.md` — macOS 双实现项目发布文档模板；用于具体项目记录 preview/native 技术栈、构建入口、资产命名和一致性定义。
`│   │   ├── README-HOOK.template.md` — 现有项目采用治理模板时可合并进 README 的 AI 开工/收尾钩子片段；避免覆盖业务 README。
`│   │   ├── RELEASE-CHECKLIST.template.md` — 每版本发布检查表模板；预置风险、ready/archive 状态和真实证据字段。
`│   │   ├── RELEASE-EXPERIENCE-REPORT.template.md` — 发布经验报告模板；记录实际流程、问题、模板反馈和下一版改进。
`│   │   ├── RELEASE-LESSON.template.md` — 版本经验模板；把事故和根因转换为可执行防回归规则。
`│   │   ├── RELEASE-NOTES.template.md` — 面向用户的中文 Release Notes 模板。
`│   │   ├── SECURITY.template.md` — 项目安全策略模板；覆盖 Secret、权限、供应链、数据删除、CI 和漏洞报告。
`│   │   └── VALIDATION-REPORT.template.md` — 真实验证报告模板；记录环境、命令、结果、故障注入和发布结论。
`│   └── REPOSITORY-STRUCTURE.md` — 自动生成的仓库目录树；逐个文件夹和文件写明职责，并由 CI 校验不漂移。
`├── scripts/` — 项目治理和 macOS 原生 APP 自动构建、配置校验、Release 资产脚本。
`│   ├── attach-release-assets.py` — Release 资产附加脚本；校验 APP ZIP、metadata、VPN 架构报告、BUILD-OUTPUT-MANIFEST 和 BUILD-SCRIPT-STATUS 成功状态。
`│   ├── audit-vpn-architecture.py` — 审计 System Extension target、Bundle ID、App Groups、Network Extension entitlement、provider framework embed、Framework runpath、激活调用链和 APP 嵌入路径。
`│   ├── bootstrap-project.py` — 把通用模板初始化为具体项目；重置项目历史并强制真实业务测试/simulation 重新配置。
`│   ├── build-ai-handoff.py` — AI 唯一正式收尾入口；完成开发状态、candidate gate、Release build 并导出三类交接包。
`│   ├── build-local-signed-app.sh` — 本机自签名构建入口；先检查 Keychain identity，再调用 build-macos-app.sh 的 local 模式，不在 GitHub Actions 中运行。
`│   ├── build-macos-app.sh` — arm64 Swift -O 构建脚本；规范化输出目录，写入 BUILD-RUN-CONTEXT / BUILD-SCRIPT-STATUS 并通过 EXIT trap 保留真实退出码；生成 APP、metadata、VPN report、checksums 和 BUILD-OUTPUT-MANIFEST。
`│   ├── build-release.py` — 生成确定性源码 ZIP、Release manifest 和 SHA-256；拒绝 P12 / PFX / 私钥 / Provisioning Profile 等敏感文件。
`│   ├── build-source-manifest.py` — 生成/校验源码 SHA-256 清单；拒绝 symlink 和 Secret 进入受管源码集合。
`│   ├── check-build-config.py` — 检查构建脚本状态记录、build+verify 同步执行、workflow outcome/context 诊断和 always-upload 契约。
`│   ├── check-governance.py` — development/candidate/release/archive 四级治理门禁；验证结构、文档、状态和远端证据语义。
`│   ├── check-local-signing-identity.sh` — 通过 security find-identity 检查本地 Clash_Mac_Compile Local Development 自签名身份是否在 macOS Keychain 中可用。
`│   ├── dev-safe-run.py` — 高风险长任务安全执行器；提供 heartbeat、hard timeout、持久日志和退出状态。
`│   ├── dev-session.py` — 开发会话状态与检查点工具；兼容旧版日志，自动补齐会话元数据和完成摘要，并提供 validate 预检命令。
`│   ├── finalize-release-archive.py` — 仅用真实 GitHub URL、tag commit、Actions 与线上验证结果把 Release 归档标记为 complete。
`│   ├── patch-macos-system-extension.py` — 将 Packet Tunnel target 迁移为 XcodeGen system-extension，设置 entitlement、OSSystemExtensionRequest 激活、provider 内嵌 ClashMacCore.framework 和正确 Frameworks runpath。
`│   ├── prepare-republish.py` — 重发布前先修复/验证开发日志，再写入历史、Checklist 和 RELEASE_REVISION，避免预检失败造成发布状态半更新。
`│   ├── prepare-version.py` — 创建下一项目版本；生成全套版本文档、可选深度升级计划并同步结构/manifest。
`│   ├── prepare-weekly-upstream-release.py` — 每周上游变化时自动递增 Patch 并生成无签名 Preview 文档；开发日志自动包含完成摘要章节。
`│   ├── run-quality-gates.py` — 统一质量门禁执行器；串行运行治理、静态、单元、集成、smoke、安全和模拟。
`│   ├── run-simulated-environment.py` — 建立没有 Git/缓存/Secret 的 clean-room 临时工作区并运行真实项目 simulation。
`│   ├── set-release-disposition.py` — 把未正式发布的旧版本按事实标记为 superseded/abandoned/failed，不阻塞后续开发。
`│   ├── summarize-xcode-linker-errors.py` — 解析 XCODEBUILD.log，提取 Undefined symbols、duplicate symbol、framework/library not found、ld 和 clang linker 错误及上下文，生成 LINKER-DIAGNOSTICS.txt。
`│   ├── update-repository-structure.py` — 同步职责 catalog 并自动生成/校验逐文件逐目录 Repository Structure。
`│   ├── verify-build-outputs.py` — 验证构建输出文件、版本、分发模式和 APP ZIP；递归列出实际文件，检查 BUILD-SCRIPT-STATUS / BUILD-RUN-CONTEXT，区分脚本未启动、失败和产物缺失。
`│   ├── verify-github-release.sh` — GitHub Release 后置验证；认证下载线上资产并检查集合、SHA-256、Release Notes 和可选匿名探针。
`│   └── verify-local-signed-app.sh` — 使用 codesign 验证主 APP 与嵌套 App Extension 的本地签名，并生成不宣称 Apple entitlement 授权的 JSON 报告。
`├── tests/` — 项目配置、构建脚本契约和 Release 资产校验测试。
`│   ├── test_build_outputs.py` — 构建输出验证测试；覆盖完整输出、缺少 APP ZIP、build script 非零退出码和签名模式不匹配。
`│   ├── test_governance.py` — 治理回归测试；覆盖旧日志缺少完成摘要/会话标记、重发布预检失败时不修改发布状态等场景。
`│   ├── test_linker_diagnostics.py` — Xcode Linker 诊断解析器回归测试；验证 undefined symbols、linker command failed 和无标准错误日志的处理。
`│   ├── test_packaging.py` — 源码包 ZIP、SHA-256、确定性打包和敏感密钥扩展名拒绝测试。
`│   ├── test_project.py` — v0.0.9 项目回归测试；包含本地签名隔离、metadata writer 严格 JSON、Release JSON 错误定位、每周版本递增和私钥防泄漏。
`│   └── test_vpn_architecture.py` — 4 项 VPN 架构回归测试；覆盖上游 XcodeGen target 转换、Entitlements、激活调用、补丁幂等、APP 嵌入路径和 Bundle ID 审计。
`├── .editorconfig` — 统一 UTF-8、LF、末尾换行和空白规则，减少跨编辑器/跨平台无意义 Diff。
`├── .gitattributes` — 固定 Git 文本文件 LF 行尾，避免 Windows/Linux/Sourcetree 交接时脚本换行损坏。
`├── .gitignore` — 排除本地状态、构建产物、缓存、虚拟环境、Secret、运行时数据和 IDE 文件。
`├── AGENTS.md` — 仓库级 AI 规则与 Clash_Mac_Compile 专属上游、签名和验证约束。
`├── BUILD-INFO.md` — v0.1.3 构建信息；记录 workflow/script 状态文件、绝对输出路径和构建验证闭环。
`├── CHANGELOG.md` — 项目各版本变更记录；v0.0.7 记录旧版开发日志兼容、重发布预检和治理回归测试。
`├── README.md` — v0.1.1 项目说明；包含 System Extension 构建、Xcode Linker 日志和失败 Artifact 下载指引。
`├── RELEASE_REVISION` — 同一项目 VERSION 的发布修订号；0 为原始发布，1/2… 对应 r1/r2 受控重发审计序号。
`├── SECURITY.md` — Secret、Apple 签名材料、上游锁定与 GitHub Actions 安全策略。
`├── SHA256SUMS.txt` — 仓库源码 SHA-256 清单；用于发现 AI 交接、结构更新或打包前的源码漂移。
`├── TEMPLATE_VERSION` — 通用治理模板语义版本号；与业务项目 VERSION 独立演进。
`├── THIRD_PARTY_NOTICES.md` — ProjectClash GPL-3.0 与传递依赖许可证、署名和源码提供提醒。
`├── UPSTREAM_CLIENT_REF` — ProjectClash/Clash-Client 固定提交：e3e647283b1593a61dba622f13cd499deeda9b8b；正式 Release 的不可变上游版本事实源。
`└── VERSION` — 当前项目活动语义版本号；版本目录、tag 和 Release 的唯一版本来源。

## 维护规则

1. 新文件先执行 `--sync`，未登记路径会写成 `TODO`。
2. AI 必须把所有 `TODO` 改成真实职责说明。
3. 再执行 `--write` 生成本文件。
4. CI 使用 `--check` 验证完全一致。
