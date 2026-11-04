# Source Baseline Audit

## 学习范围

本模板以用户提供的 `mihomo-web-installer-v4.0.0.zip` 为参考基线。ZIP 一共有 256 个条目；去掉 macOS 的 `__MACOSX` 和 `.DS_Store` 元数据后，对 **107 个实际项目文件**进行了结构化读取与分析。

分析不仅覆盖 README，还覆盖：

- 根目录规则、版本、构建、变更、迁移、安全和测试矩阵；
- `.github` 的 Copilot 指令、CI、Release workflow；
- `docs/architecture`、`docs/development`、`docs/release`、`docs/releases`、`docs/release-lessons`；
- installer / uninstaller；
- Python UI/renderer/panel 代码；
- OpenRC / systemd 示例；
- build / release / handoff / resilience / verification 脚本；
- test suite；
- upstream 配置与版本记录。

## 抽象出的通用能力

参考项目最有价值的不是具体业务代码，而是它在多次版本迭代里逐步形成的工程闭环：

```text
自然语言规则
→ 仓库级 AI 指令
→ 机器状态标记
→ 可执行门禁
→ 真实测试
→ 确定性打包
→ GitHub Release
→ 线上重新验证
→ 发布证据归档
→ 事故经验
→ 新自动防回归规则
```

本模板保留了这个闭环，但把 Mihomo、Linux 服务、具体 upstream、业务 UI 等项目专属实现剥离，改造成技术栈无关的治理层。

## 重点继承的经验

1. 语法检查不能代替动态行为测试。
2. 安装/卸载/迁移涉及删除时必须证明所有权。
3. 下载、缓存和升级资产必须按错误类别处理并验证身份。
4. 服务拆分不能顺带扩大 secret 权限。
5. 版本号必须有唯一事实源。
6. CI 不应依赖源码 executable bit 偶然正确；Release 内要规范化权限。
7. 本机高权限成功不等于 GitHub Runner 成功。
8. README 提示必须尽量转化为自动门禁。
9. 开发完成、Release Ready、Release Archive Complete 必须是不同状态。
10. 正式发布后要重新下载线上资产验证，不能只检查本地 `dist/`。
11. 长任务必须能从仓库和本地状态文件恢复，不能依赖聊天上下文。
12. ChatGPT Web 的离线开发阶段不能要求私有 GitHub 的远端事实。
13. 私有仓库匿名 404 不能解释成资产不存在。
14. Shell 的正常业务状态不要滥用非零退出码，避免与 `set -e` 冲突。
15. 缓存命中也不能绕过安全验证。
16. 下载先进入临时 incoming，验证后原子提交。
17. 确定性构建需要规范化时间戳、权限、顺序和文件集合。
18. 已发布版本不能覆盖，Bug 必须新版本。
19. 上一版本必须真实归档或明确未发布 supersede。
20. Release 事故经验必须转成自动防回归，而不是停留在文章。

## 本模板新增的改进

参考基线已经很成熟，本模板在其上进一步增加：

- 项目版本 `VERSION` 与治理模板版本 `TEMPLATE_VERSION` 分离；
- 仓库内治理作为单一事实源，同时自动导出跨项目治理模板；
- `REPOSITORY-CATALOG.json` 驱动逐目录、逐文件职责树；
- bootstrap 后强制清空模板测试命令，避免治理测试冒充业务测试；
- T0-T5 验证层级与 clean-room 模拟；
- `RELEASE-MANIFEST.json` 定义线上资产集合；
- 单人 Sourcetree direct-push 和团队 PR 两种 ruleset 模式；
- portable governance pack 与 combined AI handoff。

## 没有直接继承的内容

没有把参考项目的 Mihomo 安装逻辑、服务文件、UI 业务代码、upstream 配置、系统路径、真实发布记录或其特定资产复制进通用模板。这样可以避免把一个产品的假设误当成所有项目的规则。
