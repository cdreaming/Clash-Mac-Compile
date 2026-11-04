# GitHub Releases 下载说明

GitHub Releases 页面是正式下载入口：

<https://github.com/cdreaming/Clash-Mac-Compile/releases>

每个 Release 的说明区会列出版本、上游 Client commit、变更摘要、兼容性、安装步骤、配置目录和已知限制。

## 资产说明

| 文件 | 下载用途 |
|---|---|
| `Clash_Mac_Compile-vX.Y.Z-macos-arm64.zip` | Apple Silicon macOS APP，普通用户优先下载 |
| `Clash_Mac_Compile_vX.Y.Z_source.zip` | 对应版本的完整构建工程源码 |
| `BUILD-METADATA.json` | 实际 Client / Kernel / Adapter commit 与构建环境 |
| `SHA256SUMS.txt` | 所有主要资产的 SHA-256 校验值 |
| `RELEASE-MANIFEST.json` | 本次 Release 的资产清单 |

## 安装步骤

1. 在 Releases 页面选择需要的版本。
2. 阅读该版本说明中的 macOS 最低版本、架构、签名状态和已知限制。
3. Apple Silicon Mac 下载 `macos-arm64.zip`。
4. 解压后检查 `Clash.app`。
5. 首版无签名构建可能被 macOS 安全策略阻止；不要把无签名产物当作已公证应用。正式对外使用前应完成 Developer ID 签名、公证和 Network Extension entitlement 配置。

## 配置目录

具备有效 App Groups entitlement 时，预期容器位于：

```text
~/Library/Group Containers/group.com.cdreaming.clash/
```

当前 `ConfigResourceStore` 的工作区位于 `working/`。无签名构建可能没有有效 App Group 容器；请运行源码包内的 `scripts/inspect-macos-data.sh` 检查实际安装包，不要仅凭目录约定推断。

## Weekly Preview 与 Stable

- Weekly Preview：上游 Client 有新提交时自动构建并创建 GitHub Pre-release。
- Stable：由项目维护者确认后，使用正式 Release 流程发布。
- 若上游没有新提交，周度检查会跳过构建，不产生重复版本。
