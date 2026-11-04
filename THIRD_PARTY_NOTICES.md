# Third-Party Notices

本项目是构建自动化包装工程，不将 ProjectClash 上游代码复制进本仓库。

## ProjectClash

- Client: <https://github.com/ProjectClash/Clash-Client>
- Kernel: <https://github.com/ProjectClash/Clash>
- Adapter: <https://github.com/ProjectClash/Clash-Adapter>

上述官方项目当前声明 GPL-3.0。实际构建使用的 Client commit 与 Kernel / Adapter commit 记录在 GitHub Artifact 的 `BUILD-METADATA.json` 中。

分发 `Clash.app` 时，必须保留上游许可证、版权和第三方声明，并按适用 GPL-3.0 条款提供对应源代码。请不要移除 APP 内置的 Legal / License 资源。

## 其他依赖

Swift Packages、Go modules 及其传递依赖的许可证以所锁定上游源码中的声明为准。构建前请检查上游 `LICENSE`、`NOTICE`、`THIRD_PARTY_LICENSES.md` 和包管理器元数据。
