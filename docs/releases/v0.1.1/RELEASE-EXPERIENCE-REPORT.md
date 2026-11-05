# Clash_Mac_Compile v0.1.1 Release Experience Report

## 故障证据

v0.1.0 GitHub 日志只提供 `Ld ... ClashmacOSExtension.systemextension` 和 exit code 65，没有具体 linker diagnostics。

## 已知风险点

固定上游 Client 的 Packet Tunnel 原先是 App Extension，依赖 `ClashMacCore` 时设置 `embed: false`，并沿用旧 `.appex` 层级的 runpath。迁移为 `.systemextension` 后，扩展 bundle 的目录层级改变，不能继续假设 host app 的 Frameworks 相对路径不变。

## 修复

- System Extension 自身嵌入 `ClashMacCore.framework`。
- runpath 指向扩展自己的 `Contents/Frameworks`。
- 加入 `audit-vpn-architecture.py` 对 framework embed 和 runpath 的结构验证。
- 构建日志使用 verbose 模式完整保存。
- 失败时收集目标 Build Settings、XcodeGen spec、退出码和 Linker error summary。
- Build / Release / Weekly 在失败时仍上传诊断 Artifact。

## 防回归

- provider target 必须嵌入 ClashMacCore framework。
- provider runpath 必须包含 `@executable_path/../Frameworks`。
- Xcode Linker 错误必须从完整日志提取上下文。
- CI 不得在 Xcode build 失败时删除临时工作目录之前丢失日志。
- 不得通过删除核心框架、弱化 linker 检查或跳过 provider target 来规避失败。

## 遗留

当前无法仅凭 exit code 65 断言 v0.1.0 的精确 linker 根因。v0.1.1 首次 GitHub 构建应检查 `Xcode linker diagnostics` Artifact；若仍失败，使用其中的 `Undefined symbols` / `ld:` 行做下一轮针对性修复。
