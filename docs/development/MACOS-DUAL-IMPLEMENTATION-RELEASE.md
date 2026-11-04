# macOS 双实现快速预览 + GitHub 双 PKG 发布规则

本规则用于同时维护两套 macOS UI 实现、但又希望 ChatGPT Web 能快速提供可安装预览包的项目。

## 固定工作流

```text
AI 开发
→ 交付完整源代码 + Preview Variant portable installer
→ 用户自行安装验证（不设置“确认发布”阻塞点）
→ 上传 GitHub
→ GitHub 同时构建 Preview Variant.pkg + Native Variant.pkg
→ Bug/设计偏差进入下一版本修复
```

推荐命名示例：

- Preview Variant：`GoWebUI`（Go + AppKit/JXA + WKWebView/Web UI），ChatGPT Web/Linux 可直接交叉编译。
- Native Variant：`SwiftUI`（SwiftUI + AppKit），只在 macOS/Xcode runner 构建。

## 关键约束

1. **Preview portable 与对应 GitHub PKG 必须共用同一个 App builder。** 不允许“preview 一套脚本、GitHub Go 版另一套脚本”。
2. **两套实现必须在资产名中明确区分。** 例如 `Product-v1.2.3-GoWebUI-arm64.pkg` 与 `Product-v1.2.3-SwiftUI-arm64.pkg`。
3. **一致性比较对象只在同实现之间成立。** Preview GoWebUI ↔ GitHub GoWebUI.pkg 可以要求严格一致；SwiftUI.pkg 是独立实现，不能用 GoWebUI preview 证明其像素级表现。
4. **共享发布输入。** 两套实现共享 VERSION、build number、Release Notes、品牌图标和协议/数据模型版本。
5. **Preview 实现使用 Release Lock。** 对 UI 源码、运行时源码、品牌资产、App builder、打包脚本和关键工具链版本生成 hash lock；GitHub 构建前必须 `--check`。
6. **固定工具链。** 如果 preview 的 UI 表现可能受编译器/运行时影响，应锁定具体版本（例如 Go 1.23.2，而不是只写 1.23）。
7. **用户验收不是发布门禁。** 模板默认允许“交付后自行测试，问题在下一版本修复”；除非项目 profile 另行声明人工批准步骤。
8. **安装目标策略必须写清。** 两个 PKG 可以二选一安装到同一 `/Applications/Product.app`（后安装覆盖前一个），也可以使用不同 Bundle ID/应用名允许并存；必须在项目 Architecture/Release 文档中明确。

## PROJECT-PROFILE 配置

模板的 `.ai/PROJECT-PROFILE.json` 提供可选 `release.macos_dual_implementation` 配置。启用后至少应声明：

- preview variant 名称；
- portable build command / asset；
- preview 与 GitHub pkg 共用的 App builder；
- release lock 路径和校验命令；
- 两个 GitHub pkg variant 的名称和资产 pattern；
- 是否允许用户验收后再发布（默认 `false`，即不阻塞）。

治理门禁会检查 schema 完整性，但不会替具体项目发明技术栈命令。
