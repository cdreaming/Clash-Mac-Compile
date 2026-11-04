# Repository Structure

> 本文件由 `scripts/update-repository-structure.py` 从真实文件系统和 `.ai/REPOSITORY-CATALOG.json` 生成。每次开发新增、删除、移动文件都必须更新。

## 目录与文件

`├── .ai/` — AI 机器可读治理层；保存开工入口、项目配置、模板导出清单和仓库职责目录。
`│   ├── AI-START-HERE.md` — AI 每轮开工、上游版本锁定、验证和收尾入口。
`│   ├── PROJECT-PROFILE.json` — 项目机器配置；保存名称、slug、私库、质量命令、simulation 开关和 Release 资产。
`│   ├── REPOSITORY-CATALOG.json` — 逐目录/逐文件职责机器目录；是自动生成 Repository Structure 的说明事实源。
`│   └── TEMPLATE-MANIFEST.json` — 通用治理模板导出清单；排除 Clash_Mac_Compile 项目专属配置。
`├── .github/` — GitHub 仓库自动化与协作配置；保存 AI 指令、PR 模板和 Actions 工作流。
`│   ├── workflows/` — GitHub Actions 工作流；分别执行通用质量门禁、macOS APP 自动构建和正式 Release。
`│   │   ├── build-macos.yml` — Push/PR/手动触发的 macOS Xcode 原生 APP 构建和 Artifact 上传工作流。
`│   │   ├── ci.yml` — main Push/PR 的通用质量门禁，并运行模板治理回归测试。
`│   │   └── release.yml` — 固定上游 commit 后构建 APP、生成 Release 资产、发布并验证的工作流。
`│   ├── copilot-instructions.md` — GitHub Copilot 的项目专属开发规则。
`│   └── pull_request_template.md` — PR 检查模板；要求标记风险等级、真实验证和经验沉淀。
`├── docs/` — 长期文档根目录；保存架构、开发规则、GitHub 说明、Release 规则、版本归档和模板。
`│   ├── architecture/` — 项目构建架构文档；描述官方 Client、Kernel、Adapter 与 GitHub Runner 的构建关系。
`│   │   └── ARCHITECTURE.md` — 本项目自动构建拓扑、组件职责、版本事实源和安全边界。
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
`│   │   └── UPSTREAM-BUILD.md` — ProjectClash 三仓职责、官方 bootstrap/configure、Go 自动工具链和 macOS universal 构建说明。
`│   ├── github/` — GitHub Actions、Sourcetree 上传、Artifact 下载与费用说明。
`│   │   ├── GITHUB-ACTIONS-SETUP.md` — Sourcetree 首次上传、Actions 触发、Artifact 下载和 Release 锁定步骤。
`│   │   ├── PRIVATE-REPOSITORY-SETUP.md` — 私有 GitHub 仓库创建、Sourcetree 初始化、gh/PAT 认证下载和凭据安全说明。
`│   │   └── REPOSITORY-RULESETS.md` — 单人 direct-push 与团队 PR 两种仓库保护策略，以及 tag/Action/immutable release 建议。
`│   ├── release/` — 跨版本 Release 治理；保存生命周期、操作步骤和发布知识库。
`│   │   ├── RELEASE-KNOWLEDGE-BASE.md` — Release Lesson 与 Experience Report 的沉淀规则；把发布事故转成自动防回归资产。
`│   │   ├── RELEASE-LIFECYCLE.md` — 版本开发、候选、正式发布、归档、supersede 的机器状态与生命周期规则。
`│   │   └── RELEASE-OPERATIONS.md` — 正式发布操作说明；覆盖 AI 候选、本地测试、Sourcetree、tag、GitHub workflow 和归档。
`│   ├── release-lessons/` — 跨版本事故与经验库；把根因转化成下一版自动防回归规则。
`│   │   ├── README.md` — 版本经验索引；要求 AI 每轮读取当前经验并在收尾更新。
`│   │   ├── TEMPLATE.md` — 发布经验标准模板；定义目标、事故、根因、决策、防回归、验证和遗留边界。
`│   │   ├── v0.0.1.md` — 当前版本发布经验；记录风险、根因、决策和防回归规则。
`│   │   └── v0.0.2.md` — v0.0.2 发布经验；将 main 可移动引用造成的 Release 阻断转化为 SHA 防回归规则。
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
`│   ├── attach-release-assets.py` — 将 macOS APP ZIP 与构建元数据并入 Release manifest 和 SHA-256。
`│   ├── bootstrap-project.py` — 把通用模板初始化为具体项目；重置项目历史并强制真实业务测试/simulation 重新配置。
`│   ├── build-ai-handoff.py` — AI 唯一正式收尾入口；完成开发状态、candidate gate、Release build 并导出三类交接包。
`│   ├── build-macos-app.sh` — 在 macOS Runner 下载锁定 Client、构建 Kernel/Adapter SDK、生成 Xcode 工程并编译 universal Clash.app。
`│   ├── build-release.py` — 确定性 Release 构建器；生成项目源码 ZIP、验证报告、可选安装资产、manifest 和 SHA-256。
`│   ├── build-source-manifest.py` — 生成/校验源码 SHA-256 清单；拒绝 symlink 和 Secret 进入受管源码集合。
`│   ├── check-build-config.py` — 校验项目版本、仓库身份、构建工作流及正式 Release 的上游 SHA 锁定。
`│   ├── check-governance.py` — development/candidate/release/archive 四级治理门禁；验证结构、文档、状态和远端证据语义。
`│   ├── dev-safe-run.py` — 高风险长任务安全执行器；提供 heartbeat、hard timeout、持久日志和退出状态。
`│   ├── dev-session.py` — 版本开发会话状态机；支持 start、checkpoint、status、complete 和归档版本防重开。
`│   ├── finalize-release-archive.py` — 仅用真实 GitHub URL、tag commit、Actions 与线上验证结果把 Release 归档标记为 complete。
`│   ├── prepare-republish.py` — 重新打开已发布版本；保存旧 Release 证据并准备 revision 或 force-overwrite。
`│   ├── prepare-version.py` — 创建下一项目版本；生成全套版本文档、可选深度升级计划并同步结构/manifest。
`│   ├── run-quality-gates.py` — 统一质量门禁执行器；串行运行治理、静态、单元、集成、smoke、安全和模拟。
`│   ├── run-simulated-environment.py` — 建立没有 Git/缓存/Secret 的 clean-room 临时工作区并运行真实项目 simulation。
`│   ├── set-release-disposition.py` — 把未正式发布的旧版本按事实标记为 superseded/abandoned/failed，不阻塞后续开发。
`│   ├── update-repository-structure.py` — 同步职责 catalog 并自动生成/校验逐文件逐目录 Repository Structure。
`│   └── verify-github-release.sh` — GitHub Release 后置验证；认证下载线上资产并检查集合、SHA-256、Release Notes 和可选匿名探针。
`├── tests/` — 项目配置、构建脚本契约和 Release 资产校验测试。
`│   ├── test_governance.py` — 治理回归与故障注入测试；验证 hook、结构、ASCII 命名、测试开关和未登记文件拦截。
`│   ├── test_packaging.py` — 打包回归测试；验证 ZIP CRC/权限、Secret 排除、资产集合、SHA-256 和确定性源码包。
`│   └── test_project.py` — 项目配置、构建 workflow、Release 上游 SHA 限制和资产清单的单元测试。
`├── .editorconfig` — 统一 UTF-8、LF、末尾换行和空白规则，减少跨编辑器/跨平台无意义 Diff。
`├── .gitattributes` — 固定 Git 文本文件 LF 行尾，避免 Windows/Linux/Sourcetree 交接时脚本换行损坏。
`├── .gitignore` — 排除本地状态、构建产物、缓存、虚拟环境、Secret、运行时数据和 IDE 文件。
`├── AGENTS.md` — 仓库级 AI 规则与 Clash_Mac_Compile 专属上游、签名和验证约束。
`├── BUILD-INFO.md` — 项目版本、上游源码引用、Xcode Scheme、架构和产物说明。
`├── CHANGELOG.md` — 按项目版本记录构建系统和功能变化。
`├── README.md` — 项目说明、GitHub Actions 自动编译流程、Sourcetree 上传步骤、版本和签名限制。
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
