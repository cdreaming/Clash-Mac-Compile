# Clash_Mac_Compile Architecture

## 构建拓扑

```text
Sourcetree
  → Push main / Pull Request
  → GitHub Actions (xcode-27 macOS Runner)
  → Checkout this build-orchestration repository
  → Clone ProjectClash/Clash-Client at UPSTREAM_CLIENT_REF
  → Client bootstrap.py
      ├─ Clash Kernel at Dependencies.lock.json revision
      ├─ Clash Adapter at Dependencies.lock.json revision
      └─ Build five-slice Clash.xcframework
  → Client configure.py
      ├─ Generate Xcode project
      └─ Build universal macOS CLI helper
  → xcodebuild ClashmacOS (Release, arm64 + x86_64)
  → Clash.app
  → ZIP + BUILD-METADATA.json
  → GitHub Actions Artifact
```

## 组件职责

- 本仓库：版本治理、构建脚本、GitHub Actions、元数据与产物打包。
- Clash-Client：原生 Swift / SwiftUI 应用、macOS 专属逻辑、Network Extension。
- Clash：Go 代理内核、Apple bindings 和 `Clash.xcframework` 构建工具。
- Clash-Adapter：Swift Packet Flow 与 Provider 生命周期桥接。
- GitHub Actions：提供 macOS、Xcode、Go、Python 的构建环境。

## 版本事实源

- 本项目版本：`VERSION`。
- 上游 Client 引用：`UPSTREAM_CLIENT_REF`。
- 实际上游 Client commit：构建时 `git rev-parse HEAD`，写入 `BUILD-METADATA.json`。
- Kernel / Adapter revisions：上游 Client 的 `Dependencies.lock.json`。
- 发布证据：当前版本 `RELEASE-CHECKLIST.md` 与 GitHub Release workflow。

## 安全边界

- 默认 `CODE_SIGNING_ALLOWED=NO`。
- 不在源码包内保存 Apple 证书或密钥。
- Release 必须锁定上游 Client commit SHA。
- 下载的第三方源码在临时目录构建，不写入本项目源码树。
- APP 编译成功不等于签名、安装、VPN 权限或网络行为已验证。
