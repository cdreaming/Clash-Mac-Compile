# __PROJECT_NAME__ macOS 双实现发布配置

## 工作流

`AI 开发 → 源代码 + __PREVIEW_VARIANT__ portable → GitHub → __PREVIEW_VARIANT__.pkg + __NATIVE_VARIANT__.pkg`

用户在交付后自行测试；发现问题进入下一版本。除非项目明确要求，不设置人工“确认发布”阻塞点。

## Preview Variant

- 名称：`__PREVIEW_VARIANT__`
- 技术栈：__PREVIEW_STACK__
- Shared App Builder：`__PREVIEW_APP_BUILDER__`
- Portable Build：`__PREVIEW_PORTABLE_BUILD__`
- Release Lock：`__RELEASE_LOCK__`
- 锁定工具链：__PREVIEW_TOOLCHAIN__

## Native Variant

- 名称：`__NATIVE_VARIANT__`
- 技术栈：__NATIVE_STACK__
- GitHub/macOS Build：`__NATIVE_BUILD__`

## GitHub 资产

- `__PRODUCT__-v__VERSION__-__PREVIEW_VARIANT__-arm64.pkg`
- `__PRODUCT__-v__VERSION__-__NATIVE_VARIANT__-arm64.pkg`

## 一致性定义

- 严格对照：portable `__PREVIEW_VARIANT__` ↔ GitHub `__PREVIEW_VARIANT__.pkg`。
- `__NATIVE_VARIANT__.pkg` 为独立 UI 实现；要求功能/设计目标一致，但不承诺像素级相同。
