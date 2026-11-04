# macOS 配置目录与数据检查

## 设计中的 App Group 容器

当前构建脚本使用 Bundle Base `com.cdreaming.clash`。官方 Client 的配置存储通过 App Group 容器访问。预期 Group ID 为：

```text
group.com.cdreaming.clash
```

在具备有效 App Groups entitlement 的签名安装中，对应容器路径为：

```text
~/Library/Group Containers/group.com.cdreaming.clash/
```

当前官方 `ConfigResourceStore` 的配置工作区位于容器中的 `working/`，包括：

```text
working/
├── active/
│   └── config.yaml
└── store/
    └── profiles/
        └── <profile-id>/
            └── revisions/
```

具体文件、子目录及 profile revision 会随上游 Client 版本演进。不要将此文档视为可绕过应用存储 API 的写入规范。

## 重要：无签名构建的限制

本项目默认 `CODE_SIGNING_ALLOWED=NO`。未签名 APP 可能没有有效的 App Groups entitlement，macOS 因而不会为它创建预期的 Group Container。

因此：
- 上述路径是按构建 Bundle Base 推导的预期容器位置。
- 安装后路径是否存在，以 APP 实际签名 entitlement 和 macOS 容器状态为准。
- 不要手动创建 Group Container 来代替正确签名和 provisioning。
- 不要直接编辑运行中的 `config.yaml`；优先通过 APP 的配置导入、订阅和配置管理功能修改。

## 自动检查

在 Mac 终端运行：

```bash
bash scripts/inspect-macos-data.sh /Applications/Clash.app
```

脚本会读取 APP 的 Bundle ID、执行文件、签名中的 App Groups entitlement，并检查容器是否真实存在。也可以将 APP 路径作为第一个参数传入。

## 常见目录

| 路径 | 作用 |
|---|---|
| `~/Library/Group Containers/<group-id>/` | 共享 App Group 数据，前提是 entitlement 有效 |
| `~/Library/Application Support/` | 常见用户级应用数据目录 |
| `~/Library/Caches/` | 可重建缓存 |
| `~/Library/Logs/` | 用户级日志 |
| `~/Library/Preferences/` | 偏好设置 |

标准目录仅用于定位，不代表 Clash 一定将每种数据存放于其中。
