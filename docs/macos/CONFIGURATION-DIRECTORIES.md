# macOS 配置目录与数据限制

## 官方客户端的预期 App Group 容器

官方 Client 的配置存储使用 App Group 容器。按当前 Bundle Base 推导的预期 Group ID：

```text
group.com.cdreaming.clash
```

如果 macOS 已为 APP 创建该容器，路径为：

```text
~/Library/Group Containers/group.com.cdreaming.clash/
```

官方 `ConfigResourceStore` 的配置工作区位于容器的 `working/` 下，具体文件与子目录会随上游版本变化。

## 无签名构建的限制

本项目不使用 Apple Developer 签名、Provisioning Profile 或公证服务，Xcode 构建使用 `CODE_SIGNING_ALLOWED=NO`。

无签名 APP 不保证拥有有效 App Groups entitlement，因此 macOS 可能不会创建上述 Group Container。不要手动创建目录伪造权限，也不要直接编辑正在运行的配置文件。

VPN / Packet Tunnel 系统授权同样不可保证成功；该版本不作为完整可用 VPN 客户端发布。

## 常见目录

| 路径 | 作用 |
|---|---|
| `~/Library/Group Containers/<group-id>/` | 共享 App Group 数据，需要有效 entitlement |
| `~/Library/Application Support/` | 常见用户级应用数据目录 |
| `~/Library/Caches/` | 可重建缓存 |
| `~/Library/Logs/` | 用户级日志 |
| `~/Library/Preferences/` | 偏好设置 |

标准目录仅用于定位，不代表 Clash 一定将每种数据存放于其中。
